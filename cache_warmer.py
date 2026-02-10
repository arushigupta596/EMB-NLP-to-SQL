"""Cache warming utility to pre-populate cache with suggested question answers."""
import logging
from datetime import datetime
from typing import Dict, List, Any
from sample_questions import get_all_sample_questions

logger = logging.getLogger(__name__)


class CacheWarmer:
    """Handles cache warming by pre-executing suggested questions."""

    def __init__(self, sql_agent, db_handler, cache_manager, model_name: str):
        """
        Initialize cache warmer.

        Args:
            sql_agent: SQL agent for query execution
            db_handler: Database handler for executing queries
            cache_manager: Cache manager instance
            model_name: Current model name for cache keys
        """
        self.sql_agent = sql_agent
        self.db_handler = db_handler
        self.cache_manager = cache_manager
        self.model_name = model_name

    def warm_cache(self, max_questions: int = None) -> Dict[str, Any]:
        """
        Pre-populate cache with answers to suggested questions.

        Args:
            max_questions: Maximum number of questions to cache (None = all)

        Returns:
            Dictionary with warming statistics
        """
        if not self.cache_manager:
            logger.warning("Cache manager not available - skipping cache warming")
            return {
                'success': False,
                'reason': 'Cache manager not initialized',
                'cached_count': 0,
                'failed_count': 0
            }

        logger.info("Starting cache warming process...")
        start_time = datetime.now()

        # Get all suggested questions
        sample_questions = get_all_sample_questions()
        all_questions = []

        # Flatten questions from all categories
        for category, questions in sample_questions.items():
            all_questions.extend(questions)

        # Limit number of questions if specified
        if max_questions:
            all_questions = all_questions[:max_questions]

        cached_count = 0
        failed_count = 0
        skipped_count = 0

        logger.info(f"Warming cache with {len(all_questions)} suggested questions...")

        for idx, question in enumerate(all_questions, 1):
            try:
                # Check if already cached
                existing = self.cache_manager.get(question, self.model_name)
                if existing:
                    logger.info(f"[{idx}/{len(all_questions)}] Already cached: {question[:50]}...")
                    skipped_count += 1
                    continue

                logger.info(f"[{idx}/{len(all_questions)}] Caching: {question[:50]}...")

                # Execute query
                result = self.sql_agent.query(question)

                # Get data if SQL query was generated
                result_data = None
                if result.get('sql_query'):
                    try:
                        result_data = self.db_handler.execute_query(result['sql_query'])
                    except Exception as e:
                        logger.warning(f"Failed to execute SQL for cache warming: {e}")

                # Store in cache
                self.cache_manager.set(
                    question=question,
                    model_name=self.model_name,
                    sql_query=result.get('sql_query'),
                    answer=result.get('answer', 'Query executed successfully.'),
                    result_data=result_data,
                    execution_time_ms=0  # Not tracking time for cache warming
                )

                cached_count += 1
                logger.info(f"✓ Cached successfully: {question[:50]}...")

            except Exception as e:
                logger.error(f"Failed to cache question '{question[:50]}...': {e}")
                failed_count += 1

        duration = (datetime.now() - start_time).total_seconds()

        stats = {
            'success': True,
            'cached_count': cached_count,
            'skipped_count': skipped_count,
            'failed_count': failed_count,
            'total_questions': len(all_questions),
            'duration_seconds': round(duration, 2)
        }

        logger.info(f"Cache warming completed in {duration:.2f}s - "
                   f"Cached: {cached_count}, Skipped: {skipped_count}, Failed: {failed_count}")

        return stats


def warm_cache_on_startup(components: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """
    Convenience function to warm cache during app startup.

    Args:
        components: Dictionary of initialized system components
        model_name: Current model name

    Returns:
        Cache warming statistics
    """
    cache_manager = components.get('cache_manager')
    if not cache_manager:
        return {
            'success': False,
            'reason': 'Cache not enabled',
            'cached_count': 0
        }

    warmer = CacheWarmer(
        sql_agent=components['sql_agent'],
        db_handler=components['db_handler'],
        cache_manager=cache_manager,
        model_name=model_name
    )

    return warmer.warm_cache()
