"""Cache manager for NLP to SQL queries."""
import hashlib
import json
import pickle
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Comprehensive caching system for NLP to SQL queries.
    Caches both LLM responses (SQL queries) and database results.
    """

    def __init__(
        self,
        cache_db_path: str,
        default_ttl_seconds: int = 86400,  # 24 hours
        max_cache_size_mb: int = 500,
        max_result_size_bytes: int = 10 * 1024 * 1024  # 10MB per result
    ):
        """
        Initialize cache manager with configurable settings.

        Args:
            cache_db_path: Path to cache SQLite database
            default_ttl_seconds: Default time-to-live for cache entries
            max_cache_size_mb: Maximum total cache size
            max_result_size_bytes: Maximum size for individual cached result
        """
        self.cache_db_path = cache_db_path
        self.default_ttl = default_ttl_seconds
        self.max_cache_size = max_cache_size_mb * 1024 * 1024  # Convert to bytes
        self.max_result_size = max_result_size_bytes
        self.conn = None

        # Initialize database
        self._initialize_database()

    def _initialize_database(self):
        """Create cache database and tables if they don't exist."""
        try:
            self.conn = sqlite3.connect(self.cache_db_path, check_same_thread=False)
            cursor = self.conn.cursor()

            # Create cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT NOT NULL UNIQUE,
                    question_normalized TEXT NOT NULL,
                    question_original TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    sql_query TEXT,
                    answer TEXT,
                    result_data BLOB,
                    result_row_count INTEGER,
                    result_columns TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 1,
                    ttl_seconds INTEGER DEFAULT 86400,
                    expires_at TIMESTAMP,
                    data_size_bytes INTEGER,
                    execution_time_ms REAL,
                    is_valid BOOLEAN DEFAULT 1
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_key
                ON query_cache(cache_key)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON query_cache(expires_at)
            """)

            # Create statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    cache_hits INTEGER DEFAULT 0,
                    cache_misses INTEGER DEFAULT 0,
                    total_queries INTEGER DEFAULT 0,
                    hit_rate REAL,
                    total_api_calls_saved INTEGER DEFAULT 0,
                    UNIQUE(date)
                )
            """)

            self.conn.commit()
            logger.info(f"Cache database initialized at {self.cache_db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")
            raise

    def _generate_cache_key(
        self,
        question: str,
        model_name: str
    ) -> Tuple[str, str]:
        """
        Generate cache key from normalized question and model name.

        Args:
            question: User's natural language question
            model_name: LLM model identifier

        Returns:
            Tuple of (cache_key, normalized_question)
        """
        # Normalize question
        normalized = self._normalize_question(question)

        # Create cache key: hash of normalized question + model
        key_string = f"{normalized}|{model_name}"
        cache_key = hashlib.sha256(key_string.encode()).hexdigest()

        return cache_key, normalized

    def _normalize_question(self, question: str) -> str:
        """
        Normalize question for consistent cache keys.

        Transformations:
        - Convert to lowercase
        - Strip leading/trailing whitespace
        - Collapse multiple spaces to single space
        - Remove common punctuation variations
        """
        # Basic normalization
        normalized = question.lower().strip()
        normalized = ' '.join(normalized.split())  # Collapse whitespace
        normalized = normalized.rstrip('?.!')

        return normalized

    def get(
        self,
        question: str,
        model_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for a question.

        Args:
            question: User's natural language question
            model_name: LLM model identifier

        Returns:
            Cached result dictionary or None if not found/expired
        """
        try:
            cache_key, normalized_question = self._generate_cache_key(question, model_name)

            # Query cache database
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT
                    sql_query, answer, result_data, result_row_count,
                    result_columns, created_at, expires_at, data_size_bytes
                FROM query_cache
                WHERE cache_key = ? AND is_valid = 1
            """, (cache_key,))

            row = cursor.fetchone()

            if not row:
                logger.info(f"Cache MISS for key: {cache_key[:16]}...")
                self._record_cache_miss()
                return None

            # Check expiration
            expires_at = datetime.fromisoformat(row[6])
            if datetime.now() > expires_at:
                logger.info(f"Cache EXPIRED for key: {cache_key[:16]}...")
                self._invalidate_entry(cache_key, 'ttl_expired')
                self._record_cache_miss()
                return None

            # Deserialize result data
            result_data = None
            if row[2]:
                try:
                    result_data = pickle.loads(row[2])
                except Exception as e:
                    logger.error(f"Failed to deserialize cached data: {e}")
                    return None

            # Update access statistics
            self._update_access_stats(cache_key)
            self._record_cache_hit()

            logger.info(f"Cache HIT for key: {cache_key[:16]}...")

            return {
                'question': question,
                'sql_query': row[0],
                'answer': row[1],
                'data': result_data,
                'cached': True,
                'cache_metadata': {
                    'created_at': row[5],
                    'row_count': row[3],
                    'columns': json.loads(row[4]) if row[4] else None
                }
            }

        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    def set(
        self,
        question: str,
        model_name: str,
        sql_query: Optional[str],
        answer: str,
        result_data: Optional[pd.DataFrame],
        execution_time_ms: float,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Store query result in cache.

        Args:
            question: User's natural language question
            model_name: LLM model identifier
            sql_query: Generated SQL query
            answer: Natural language answer
            result_data: Query results as DataFrame
            execution_time_ms: Time taken to execute query
            ttl_seconds: Time-to-live override

        Returns:
            True if cached successfully, False otherwise
        """
        try:
            cache_key, normalized_question = self._generate_cache_key(question, model_name)

            # Serialize DataFrame
            result_blob = None
            result_size = 0
            result_row_count = 0
            result_columns = None

            if result_data is not None and not result_data.empty:
                try:
                    result_blob = pickle.dumps(result_data)
                    result_size = len(result_blob)
                    result_row_count = len(result_data)
                    result_columns = json.dumps(result_data.columns.tolist())

                    # Check size limit
                    if result_size > self.max_result_size:
                        logger.warning(
                            f"Result size ({result_size / 1024 / 1024:.2f}MB) "
                            f"exceeds limit ({self.max_result_size / 1024 / 1024:.2f}MB). "
                            "Not caching."
                        )
                        return False

                except Exception as e:
                    logger.error(f"Failed to serialize DataFrame: {e}")
                    return False

            # Calculate expiration
            ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)

            # Check total cache size and evict if necessary
            self._evict_if_necessary(result_size)

            # Insert or replace cache entry
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO query_cache (
                    cache_key, question_normalized, question_original,
                    model_name, sql_query, answer, result_data,
                    result_row_count, result_columns, expires_at,
                    ttl_seconds, data_size_bytes, execution_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key, normalized_question, question, model_name,
                sql_query, answer, result_blob, result_row_count,
                result_columns, expires_at, ttl, result_size, execution_time_ms
            ))
            self.conn.commit()

            logger.info(
                f"Cached result for key: {cache_key[:16]}... "
                f"(size: {result_size / 1024:.2f}KB, rows: {result_row_count})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to cache result: {e}")
            return False

    def clear_all(self) -> int:
        """Clear all cache entries."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM query_cache")
            count = cursor.fetchone()[0]

            cursor.execute("DELETE FROM query_cache")
            self.conn.commit()

            logger.info(f"Cleared {count} cache entries")
            return count

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0

    def clear_expired(self) -> int:
        """Remove expired cache entries."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM query_cache
                WHERE expires_at < ?
            """, (datetime.now(),))
            count = cursor.fetchone()[0]

            cursor.execute("""
                DELETE FROM query_cache
                WHERE expires_at < ?
            """, (datetime.now(),))
            self.conn.commit()

            logger.info(f"Removed {count} expired cache entries")
            return count

        except Exception as e:
            logger.error(f"Failed to clear expired entries: {e}")
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        try:
            cursor = self.conn.cursor()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total_entries,
                    SUM(data_size_bytes) as total_size_bytes,
                    SUM(access_count) as total_accesses,
                    AVG(execution_time_ms) as avg_execution_time
                FROM query_cache
                WHERE is_valid = 1
            """)
            overall = cursor.fetchone()

            # Today's stats
            cursor.execute("""
                SELECT
                    cache_hits, cache_misses, total_queries, hit_rate,
                    total_api_calls_saved
                FROM cache_statistics
                WHERE date = ?
            """, (datetime.now().date(),))
            today = cursor.fetchone()

            return {
                'total_entries': overall[0] or 0,
                'total_size_mb': (overall[1] or 0) / 1024 / 1024,
                'total_accesses': overall[2] or 0,
                'avg_execution_time_ms': overall[3] or 0,
                'today_hits': today[0] if today else 0,
                'today_misses': today[1] if today else 0,
                'today_total': today[2] if today else 0,
                'today_hit_rate': today[3] if today else 0.0,
                'api_calls_saved': today[4] if today else 0
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total_entries': 0,
                'total_size_mb': 0,
                'total_accesses': 0,
                'avg_execution_time_ms': 0,
                'today_hits': 0,
                'today_misses': 0,
                'today_total': 0,
                'today_hit_rate': 0.0,
                'api_calls_saved': 0
            }

    def _evict_if_necessary(self, new_entry_size: int):
        """Evict old entries if cache size limit would be exceeded."""
        try:
            cursor = self.conn.cursor()

            # Get current cache size
            cursor.execute("SELECT SUM(data_size_bytes) FROM query_cache")
            current_size = cursor.fetchone()[0] or 0

            if current_size + new_entry_size > self.max_cache_size:
                # Calculate how much to evict (with 10% buffer)
                target_size = self.max_cache_size * 0.9
                to_evict = current_size + new_entry_size - target_size

                # Select LRU entries to evict
                cursor.execute("""
                    SELECT cache_key, data_size_bytes
                    FROM query_cache
                    ORDER BY last_accessed_at ASC
                """)

                evicted_size = 0
                evicted_keys = []

                for key, size in cursor.fetchall():
                    if evicted_size >= to_evict:
                        break
                    evicted_keys.append(key)
                    evicted_size += size or 0

                # Delete evicted entries
                if evicted_keys:
                    placeholders = ','.join(['?'] * len(evicted_keys))
                    cursor.execute(
                        f"DELETE FROM query_cache WHERE cache_key IN ({placeholders})",
                        evicted_keys
                    )
                    self.conn.commit()

                    logger.info(
                        f"Evicted {len(evicted_keys)} LRU entries "
                        f"({evicted_size / 1024 / 1024:.2f}MB)"
                    )

        except Exception as e:
            logger.error(f"Cache eviction error: {e}")

    def _update_access_stats(self, cache_key: str):
        """Update access count and last accessed timestamp."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE query_cache
                SET access_count = access_count + 1,
                    last_accessed_at = ?
                WHERE cache_key = ?
            """, (datetime.now(), cache_key))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update access stats: {e}")

    def _invalidate_entry(self, cache_key: str, reason: str):
        """Invalidate a cache entry."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE query_cache
                SET is_valid = 0
                WHERE cache_key = ?
            """, (cache_key,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to invalidate entry: {e}")

    def _record_cache_hit(self):
        """Record cache hit in statistics."""
        try:
            today = datetime.now().date()
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO cache_statistics (date, cache_hits, total_queries)
                VALUES (?, 1, 1)
                ON CONFLICT(date) DO UPDATE SET
                    cache_hits = cache_hits + 1,
                    total_queries = total_queries + 1,
                    hit_rate = CAST(cache_hits AS REAL) / total_queries,
                    total_api_calls_saved = cache_hits
            """, (today,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to record cache hit: {e}")

    def _record_cache_miss(self):
        """Record cache miss in statistics."""
        try:
            today = datetime.now().date()
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO cache_statistics (date, cache_misses, total_queries)
                VALUES (?, 1, 1)
                ON CONFLICT(date) DO UPDATE SET
                    cache_misses = cache_misses + 1,
                    total_queries = total_queries + 1,
                    hit_rate = CAST(cache_hits AS REAL) / total_queries
            """, (today,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to record cache miss: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Cache database connection closed")
