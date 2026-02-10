"""Cache warming utility to pre-populate cache with suggested question answers."""
import logging
from datetime import datetime
from typing import Dict, List, Any
from sample_questions import get_all_sample_questions
from query_templates import get_template_sql, has_template
from llm_handler import ChartRequestParser

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

                # Try template first (no API call!)
                sql_query = None
                answer = None
                result_data = None
                used_template = False

                if has_template(question):
                    # Use hardcoded SQL template - NO API CALL!
                    sql_query = get_template_sql(question)
                    logger.info(f"  Using SQL template (no API call)")
                    used_template = True

                    # Execute template SQL directly
                    try:
                        result_data = self.db_handler.execute_query(sql_query)

                        # Detect if this is a chart or report request
                        is_chart_request = ChartRequestParser.detect_chart_request(question) is not None
                        is_report_request = ChartRequestParser.detect_report_request(question)
                        is_professional_report = any(keyword in question.lower() for keyword in [
                            'professional report', 'detailed report', 'comprehensive report',
                            'executive summary', 'financial report', 'analysis report'
                        ])

                        # For chart/report requests, cache with empty answer
                        # The actual chart/report will be generated on-demand
                        if is_chart_request or is_report_request or is_professional_report:
                            answer = ""  # Empty answer - chart/report will be generated fresh
                            logger.info(f"  Chart/report question detected - caching with empty answer")
                        # Generate answer from data (matching process_user_query logic)
                        elif result_data.empty:
                            answer = "No data found for the specified criteria."
                        elif len(result_data) == 1 and len(result_data.columns) == 1:
                            # Single value result (aggregations like COUNT, SUM, AVG)
                            value = result_data.iloc[0, 0]
                            col_name = result_data.columns[0].replace('_', ' ').title()

                            # Format based on column name and value type
                            if isinstance(value, (int, float)):
                                # Check if it's a currency value
                                if any(keyword in col_name.lower() for keyword in ['price', 'amount', 'value', 'total', 'cost', 'revenue', 'sales', 'payment']):
                                    answer = f"The {col_name} is ${value:,.2f}"
                                else:
                                    answer = f"The {col_name} is {value:,}"
                            else:
                                answer = f"The {col_name} is {value}"
                        elif len(result_data) <= 10:
                            # Small result set - provide summary that mentions data table
                            answer = f"Query returned {len(result_data)} result(s)."
                        else:
                            # Large result set
                            answer = f"Found {len(result_data)} result(s)."

                    except Exception as e:
                        logger.error(f"Template SQL failed: {e}")
                        failed_count += 1
                        continue

                else:
                    # Fallback to LLM (API call) for non-template questions
                    try:
                        logger.info(f"  No template found, calling LLM API...")
                        result = self.sql_agent.query(question)

                        # Check if result is an error
                        answer = result.get('answer', '')
                        if 'Error code:' in answer or answer.startswith('Error'):
                            logger.warning(f"Skipping cache for error response: {answer[:100]}")
                            if 'Error code: 402' in answer or 'requires more credits' in answer:
                                logger.error("Insufficient API credits - stopping cache warming")
                                failed_count += 1
                                break
                            failed_count += 1
                            continue

                        sql_query = result.get('sql_query')

                        # Get data if SQL query was generated
                        if sql_query:
                            try:
                                result_data = self.db_handler.execute_query(sql_query)
                            except Exception as e:
                                logger.warning(f"Failed to execute SQL for cache warming: {e}")

                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Failed to cache question '{question[:50]}...': {error_msg}")

                        # Stop on API credit issues
                        if '402' in error_msg or 'credits' in error_msg.lower():
                            logger.error("API credit issue detected - stopping cache warming")
                            failed_count += 1
                            break

                        failed_count += 1
                        continue

                # Store in cache (works for both template and LLM results)
                # Note: answer can be empty string for chart/report requests
                if sql_query and answer is not None:
                    self.cache_manager.set(
                        question=question,
                        model_name=self.model_name,
                        sql_query=sql_query,
                        answer=answer,
                        result_data=result_data,
                        execution_time_ms=0
                    )
                    cached_count += 1
                    source = "template" if used_template else "LLM"
                    logger.info(f"✓ Cached successfully ({source}): {question[:50]}...")
                else:
                    logger.warning(f"Skipping cache - no valid SQL or answer generated")
                    failed_count += 1

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to cache question '{question[:50]}...': {error_msg}")

                # Stop on API credit issues
                if '402' in error_msg or 'credits' in error_msg.lower():
                    logger.error("API credit issue detected - stopping cache warming")
                    failed_count += 1
                    break

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
