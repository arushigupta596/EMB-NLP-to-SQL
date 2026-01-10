"""LLM handler using LangChain and OpenRouter."""
import os
import re
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
import logging

logger = logging.getLogger(__name__)


def clean_sql_query(query: str) -> str:
    """Clean SQL query by removing markdown formatting and labels.

    Args:
        query: Raw SQL query string that may contain markdown

    Returns:
        Cleaned SQL query
    """
    if not query:
        return query

    # Remove markdown code blocks (```sql ... ``` or ``` ... ```)
    query = re.sub(r'```sql\s*', '', query, flags=re.IGNORECASE)
    query = re.sub(r'```\s*', '', query)

    # Remove "SQLQuery:" prefix if present
    query = re.sub(r'^SQLQuery:\s*', '', query, flags=re.IGNORECASE)

    # Remove "SQL Query:" variations
    query = re.sub(r'^SQL\s*Query:\s*', '', query, flags=re.IGNORECASE)

    # First, remove conversational phrases at the start
    # Match patterns like "I'll help you...", "Here is...", "Let me...", etc.
    # Do this BEFORE attempting to find SQL keywords
    conversational_patterns = [
        r"^I'll\s+help\s+you.*?:\s*",
        r"^I\s+can\s+help.*?:\s*",
        r"^Here\s+is\s+.*?:\s*",
        r"^Here's\s+.*?:\s*",
        r"^Let\s+me\s+.*?:\s*",
        r"^This\s+query\s+.*?:\s*",
        r"^To\s+.*?,\s*",
        r"^To\s+.*?:\s*",
    ]
    for pattern in conversational_patterns:
        query = re.sub(pattern, '', query, flags=re.IGNORECASE | re.DOTALL)

    # Remove any remaining text before SELECT if present
    # Only match SELECT followed by valid SQL keywords (not "create a query")
    if not query.strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH')):
        # Look for SELECT followed by typical SQL patterns (columns, *, etc.)
        # This avoids matching "create" in "create a query"
        select_match = re.search(r'\b(SELECT)\s+(?:DISTINCT\s+)?(?:\*|[\w\.])', query, flags=re.IGNORECASE)
        if select_match:
            # Extract from SELECT onwards
            query = query[select_match.start():]

    # Extract SQL query if it's embedded in other text
    # Stop at explanation phrases that commonly follow SQL
    explanation_markers = [
        r'\n\nThis',
        r'\n\nThe ',
        r'\n\nNote:',
        r'\n\nExplanation:',
        r'\n\nIf you',
        r'\n\nBased',
        r'\nThis query',
        r'\nThis will',
        r'\nThe query',
        r'\nNote:',
        r'\nExplanation:',
        r'\nBased',
        r'\s+This query',
        r'\s+This will',
        r'\s+\nThis',  # Match newline followed by "This"
        r'\s+\nThe',   # Match newline followed by "The"
        r'\s+\nBased',  # Match newline followed by "Based"
        r'Based on',   # Match "Based on" even without newline
        r'Based',      # Match "Based" to catch "Based on the results"
    ]

    # Find the earliest explanation marker
    earliest_pos = len(query)
    for marker in explanation_markers:
        match = re.search(marker, query, re.IGNORECASE)
        if match and match.start() < earliest_pos:
            earliest_pos = match.start()

    # Truncate at the explanation
    if earliest_pos < len(query):
        query = query[:earliest_pos]

    # Also remove any text after a double newline (likely explanation text)
    # Split on double newline and take only the first part
    if '\n\n' in query:
        query = query.split('\n\n')[0]

    # More aggressive: Remove everything after common SQL endings when followed by text
    # This catches cases like "LIMIT 10 This query will..." (single newline or space)
    # Also handles cases after GROUP BY, ORDER BY, etc.
    sql_ending_patterns = [
        r'(LIMIT\s+\d+)\s+[A-Z][a-z].*$',  # LIMIT 10 This...
        r'(LIMIT\s+\d+)\s*\n+\s*[A-Z][a-z].*$',  # LIMIT 10\n\nThis...
        r'(\))\s*\n*\s+This\s+',  # ) This...
        r'(\))\s*\n*\s+The\s+',   # ) The...
        r'(\))\s*\n*\s+Based\s+',  # ) Based...
        r'(\))\s*Based\s+on.*$',   # )Based on...
        r'(ORDER BY\s+\w+(?:\s+(?:ASC|DESC))?)\s*Based\s+on.*$',  # ORDER BY month Based on...
        r'(GROUP BY\s+\w+)\s*Based\s+on.*$',  # GROUP BY x Based on...
        r'(WHERE\s+.+?)\s*Based\s+on.*$',  # WHERE condition Based on...
    ]
    for pattern in sql_ending_patterns:
        query = re.sub(pattern, r'\1', query, flags=re.IGNORECASE | re.DOTALL)

    # Remove any trailing explanatory sentences
    # More aggressive pattern to catch explanations that start mid-line
    query = re.sub(r'\s+(This|The|Note|Explanation|If you|which|that could|Based)[\s\S]*$', '', query, flags=re.IGNORECASE)

    # Remove any lines that don't look like SQL (contain common explanation words)
    lines = query.split('\n')
    sql_lines = []
    for line in lines:
        line_lower = line.lower().strip()
        # Comprehensive list of explanation keywords to filter out
        explanation_keywords = [
            'this query will', 'this will retrieve', 'if you', 'which you could',
            'that could be', 'you can use', 'select the', 'order the results',
            'limit to the', 'provides the', 'can then use', 'to make the',
            'the query provides', 'raw data sorted', 'visual representation',
            'looking for', 'more readable', 'spreadsheet or', 'charting tool',
            'this will:', 'this query:', 'explanation:', 'note that',
            'you can then', 'which will', 'data sorted by', 'chart more readable',
            'based on', 'based upon', 'according to'
        ]
        # If we encounter an explanation line, stop processing
        if line_lower and any(keyword in line_lower for keyword in explanation_keywords):
            break  # Stop here, don't include this or any following lines
        # Add valid SQL lines
        if line.strip():
            sql_lines.append(line)
    query = '\n'.join(sql_lines)

    # Final safety net: Remove any trailing text that looks like English explanation
    # Match patterns like " This query", " The query", " This will", etc. at the end (after valid SQL)
    # Use word boundaries and require specific explanation patterns
    query = re.sub(r'\s+(This|The|It)\s+(query|will|should|can|helps|provides|retrieves|calculates|shows).*$', '', query, flags=re.IGNORECASE)

    # Remove any leading/trailing whitespace
    query = query.strip()

    # One more check: if query contains text after the last closing parenthesis or semicolon
    # that looks like explanation (NOT valid SQL), remove it
    if ')' in query:
        last_paren = query.rfind(')')
        after_paren = query[last_paren+1:].strip()
        # If there's text after the last ), check if it looks like explanation
        if after_paren and not after_paren.startswith(';'):
            # Check if it's explanation text (not SQL keywords like AS, FROM, WHERE, etc.)
            # Only remove if it starts with explanation words, NOT SQL keywords
            sql_keywords = ['as', 'from', 'where', 'join', 'order', 'group', 'having', 'limit', 'union', 'select', 'inner', 'left', 'right', 'on', 'and', 'or']
            first_word = after_paren.split()[0].lower() if after_paren.split() else ''

            # Only truncate if it starts with explanation words, not SQL keywords
            if first_word and first_word not in sql_keywords:
                # Check for explanation words
                if any(word in after_paren.lower() for word in ['this', 'the query', 'will', 'allows', 'provides', 'helps', 'calculates', 'retrieves', 'shows', 'aggregates']):
                    query = query[:last_paren+1]

    # Also check after LIMIT statements if no parenthesis
    if 'LIMIT' in query.upper():
        # Find the last LIMIT and check if there's text after the number
        limit_match = re.search(r'(LIMIT\s+\d+)(.*)$', query, re.IGNORECASE | re.DOTALL)
        if limit_match:
            after_limit = limit_match.group(2).strip()
            # If there's text after LIMIT that looks like explanation
            if after_limit and not after_limit.startswith(';'):
                has_lowercase_text = bool(re.search(r'[a-z]{3,}', after_limit))
                if has_lowercase_text:
                    query = limit_match.group(1)

    return query.strip()


class OpenRouterLLM(ChatOpenAI):
    """Custom LLM class for OpenRouter API."""

    def __init__(self, api_key: str, model: str = "openai/gpt-4-turbo", **kwargs):
        """Initialize OpenRouter LLM.

        Args:
            api_key: OpenRouter API key
            model: Model identifier
            **kwargs: Additional arguments for ChatOpenAI class
        """
        # Validate API key format
        if not api_key or api_key == "your_openrouter_api_key_here":
            raise ValueError(
                "Invalid OpenRouter API key. "
                "Please set a valid API key in your .env file. "
                "Get your key from: https://openrouter.ai/keys"
            )

        # Add OpenRouter-specific HTTP headers
        # These headers are required for proper OpenRouter authentication
        model_kwargs = kwargs.get('model_kwargs', {})
        model_kwargs['extra_headers'] = {
            'HTTP-Referer': 'http://localhost:8501',  # Required by OpenRouter
            'X-Title': 'NLP to SQL Chat Application'   # Optional but recommended
        }
        kwargs['model_kwargs'] = model_kwargs

        super().__init__(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_name=model,
            **kwargs
        )


class CleaningSQLDatabase(SQLDatabase):
    """Custom SQLDatabase that cleans queries before execution."""

    def run(self, command: str, fetch: str = "all", **kwargs):
        """Execute SQL command after cleaning it.

        Args:
            command: SQL command to execute
            fetch: Fetch mode ('all', 'one', or 'cursor')

        Returns:
            Query results
        """
        # Clean the SQL command before execution
        cleaned_command = clean_sql_query(command)
        logger.info(f"🧹 Cleaned SQL before execution: {cleaned_command[:100]}...")

        # Call parent's run method with cleaned command
        return super().run(cleaned_command, fetch=fetch, **kwargs)


class SQLAgentHandler:
    """Handle SQL query generation and execution using LangChain."""

    def __init__(self, db_url: str, api_key: str, model: str = "openai/gpt-4-turbo"):
        """Initialize SQL agent handler.

        Args:
            db_url: SQLAlchemy database URL
            api_key: OpenRouter API key
            model: Model identifier
        """
        # Use our custom CleaningSQLDatabase instead of standard SQLDatabase
        self.db = CleaningSQLDatabase.from_uri(db_url)
        self.llm = OpenRouterLLM(api_key=api_key, model=model, temperature=0)
        self.chain = self._create_sql_chain()

    def _create_sql_chain(self) -> SQLDatabaseChain:
        """Create SQL database chain.

        Returns:
            SQLDatabaseChain instance
        """
        # Custom prompt for better SQL generation
        _DEFAULT_TEMPLATE = """Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.

Use the following format:

Question: Question here
SQLQuery: SQL Query to run (write ONLY the SQL query without any markdown formatting or code blocks)
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use the following tables:
{table_info}

Important Guidelines for SQL:
- Return ONLY the SQL query itself - DO NOT add ANY text after the SQL query ends
- CRITICAL: After writing the SQL query, immediately move to the next section (SQLResult or Answer)
- Do NOT write "This query will...", "The query...", "Based on...", or any explanatory text after the SQL
- Write only pure SQL without backticks, without "sql" language tags, and without markdown formatting
- For sales data: JOIN orderdetails table with orders table, calculate sales as (quantityordered * priceeach)
- For sales reports: Use SUM(quantityordered * priceeach) to get total sales
- Always use proper JOIN syntax when combining tables
- Include relevant GROUP BY clauses for aggregations
- For average calculations (e.g., "average order value"): Use a subquery to calculate totals first, then apply AVG()
  Example: SELECT AVG(order_total) FROM (SELECT ordernumber, SUM(quantity * price) AS order_total FROM orders GROUP BY ordernumber)
- ALWAYS include the complete outer SELECT statement for subqueries - never start with FROM
- End the SQLQuery section immediately after the SQL statement

CRITICAL SQLite-Specific Rules (This is SQLite, NOT MySQL or PostgreSQL):
- DO NOT use DATE_FORMAT() - SQLite uses strftime() instead
  Example: strftime('%Y-%m', orderdate) for year-month, strftime('%m', orderdate) for month
- DO NOT use MONTH(), YEAR() functions - use strftime() instead
- For date formatting: Use strftime('%Y-%m-%d', date_column)
- For month extraction: Use strftime('%m', date_column) or CAST(strftime('%m', date_column) AS INTEGER)
- For year extraction: Use strftime('%Y', date_column)
- ALWAYS prefix column names with table names in JOINs to avoid "ambiguous column name" errors
  Example: orders.ordernumber, orderdetails.ordernumber (NOT just ordernumber)
- SQLite is case-sensitive for LIKE by default, use LOWER() for case-insensitive searches
- SQLite uses || for string concatenation, NOT CONCAT()
- Use CAST(x AS INTEGER) or CAST(x AS REAL) for type conversion

Important Guidelines for Answer:
- Write in plain business language - DO NOT mention SQL, queries, tables, joins, databases, or internal processing
- DO NOT explain column names, technical details, or how data was retrieved
- Keep responses SHORT and CLEAR (1-2 sentences maximum)
- Always lead with the final result, not the method
- Use natural business language as if speaking to a colleague
- For counts/totals: State the number directly (e.g., "There are 25 products" NOT "The query returned 25 products")
- For lists: Provide a brief summary (e.g., "The top 3 products are X, Y, and Z")
- For single values: State the value naturally (e.g., "The average price is $45.99")
- Be conversational and direct, avoiding technical jargon

Question: {input}"""

        PROMPT = PromptTemplate(
            input_variables=["input", "table_info", "dialect"],
            template=_DEFAULT_TEMPLATE
        )

        return SQLDatabaseChain.from_llm(
            llm=self.llm,
            db=self.db,
            prompt=PROMPT,
            verbose=True,
            return_intermediate_steps=True
            # SQL cleaning now happens in CleaningSQLDatabase.run() method
        )

    def query(self, question: str) -> Dict[str, Any]:
        """Execute natural language query.

        Args:
            question: Natural language question

        Returns:
            Dictionary containing query results and metadata
        """
        try:
            logger.info(f"Processing question: {question}")

            result = self.chain(question)

            # Extract components
            response = {
                'question': question,
                'answer': result.get('result', ''),
                'sql_query': None,
                'intermediate_steps': result.get('intermediate_steps', [])
            }

            # IMMEDIATE CLEANING: If the answer contains the full LLM chain format (Question: ... SQLQuery: ...)
            # Extract SQL and clean it up right away before any other processing
            if response['answer']:
                initial_answer = response['answer']
                logger.info(f"Initial answer from LLM: {initial_answer[:200]}")

                # Check if answer contains "Question:" and "SQLQuery:" - this is the raw LLM output format
                # OR if it contains "SQLQuery:" at all (sometimes Question: might be missing)
                if 'SQLQuery:' in initial_answer:
                    logger.info("Detected SQLQuery: in answer - extracting SQL and cleaning")

                    # Extract SQL query from SQLQuery section
                    # Use greedy matching to capture the entire SQL including complex subqueries
                    # Match everything from SELECT to either SQLResult/Answer or end of string
                    sql_match = re.search(r'SQLQuery:\s*(SELECT\s+.*?)(?=\s*SQLResult:|\s*Answer:|\s*$)', initial_answer, re.IGNORECASE | re.DOTALL)
                    if sql_match:
                        raw_sql = sql_match.group(1).strip()
                        response['sql_query'] = clean_sql_query(raw_sql)
                        logger.info(f"Extracted SQL from answer: {response['sql_query'][:100]}...")

                    # Try to extract the Answer: section if it exists
                    answer_match = re.search(r'Answer:\s*(.+?)(?:\Z)', initial_answer, re.IGNORECASE | re.DOTALL)
                    if answer_match:
                        response['answer'] = answer_match.group(1).strip()
                        logger.info(f"Extracted answer section: {response['answer'][:100]}")
                    else:
                        # No Answer section found, clear it - will be generated from data later
                        response['answer'] = ''
                        logger.info("No Answer section found, clearing answer for data-based generation")

            # Extract SQL query from intermediate steps
            # SQLDatabaseChain stores the query in different formats
            if response['intermediate_steps']:
                for step in response['intermediate_steps']:
                    # Check if step is a string containing SQL
                    if isinstance(step, str) and 'SELECT' in step.upper():
                        logger.info(f"Raw SQL from step (string): {step[:200]}")
                        response['sql_query'] = clean_sql_query(step)
                        logger.info(f"Cleaned SQL: {response['sql_query'][:200]}")
                        break
                    # Check if step is a dict with 'sql_cmd' key
                    elif isinstance(step, dict) and 'sql_cmd' in step:
                        logger.info(f"Raw SQL from step (dict): {step['sql_cmd'][:200]}")
                        response['sql_query'] = clean_sql_query(step['sql_cmd'])
                        logger.info(f"Cleaned SQL: {response['sql_query'][:200]}")
                        break

            # If not found in intermediate steps, try to extract from the result
            if not response['sql_query']:
                # Sometimes the chain includes the query in the result
                full_result_text = str(result)
                if 'SELECT' in full_result_text.upper():
                    # Extract SQL using regex (re module imported at top of file)
                    sql_match = re.search(r'(SELECT\s+.+?(?:FROM|$).*?)(?:\n|$)', full_result_text, re.IGNORECASE | re.DOTALL)
                    if sql_match:
                        response['sql_query'] = clean_sql_query(sql_match.group(1).strip())

            # Last resort: check if the answer itself contains SQL query format
            if not response['sql_query'] and response['answer']:
                answer_text = response['answer']
                if 'SQLQuery:' in answer_text or 'SELECT' in answer_text.upper():
                    # Try to extract from "SQLQuery: SELECT ..." format - use greedy matching
                    # Pattern: Match from SQLQuery: to the end of the SQL (before SQLResult/Answer or EOL)
                    sql_match = re.search(r'SQLQuery:\s*(SELECT\s+.*?)(?=SQLResult:|Answer:|\n\n|$)', answer_text, re.IGNORECASE | re.DOTALL)
                    if sql_match:
                        response['sql_query'] = clean_sql_query(sql_match.group(1).strip())
                        # Remove everything from "SQLQuery:" onwards until we hit SQLResult/Answer or end
                        response['answer'] = re.sub(r'SQLQuery:\s*.*?(?=SQLResult:|Answer:|$)', '', answer_text, flags=re.IGNORECASE | re.DOTALL).strip()
                    else:
                        # Try generic SELECT extraction - match from SELECT to end of parentheses if present
                        sql_match = re.search(r'(SELECT\s+.*?)(?=\n\n|Answer:|$)', answer_text, re.IGNORECASE | re.DOTALL)
                        if sql_match:
                            response['sql_query'] = clean_sql_query(sql_match.group(1).strip())
                            # Remove the SQL query from the answer
                            response['answer'] = answer_text.replace(sql_match.group(1), '').strip()

            # Clean up the answer to remove any remaining SQL references
            if response['answer']:
                # Try to extract just the "Answer:" part if it exists
                answer_match = re.search(r'Answer:\s*(.+?)$', response['answer'], re.IGNORECASE | re.DOTALL)
                if answer_match:
                    response['answer'] = answer_match.group(1).strip()
                else:
                    # If no "Answer:" label, clean up the full text
                    # Remove "Question:" prefix and its content
                    response['answer'] = re.sub(r'^Question:\s*.+?(?=SQLQuery:|$)', '', response['answer'], flags=re.IGNORECASE | re.DOTALL)

                    # Remove entire SQLQuery section (from "SQLQuery:" to "SQLResult:" or next section)
                    response['answer'] = re.sub(r'SQLQuery:\s*.*?(?=SQLResult:|Answer:|$)', '', response['answer'], flags=re.IGNORECASE | re.DOTALL)

                    # Remove SQLResult section
                    response['answer'] = re.sub(r'SQLResult:\s*.*?(?=Answer:|$)', '', response['answer'], flags=re.IGNORECASE | re.DOTALL)

                    # Remove any remaining standalone SQL statements (SELECT, INSERT, etc.)
                    response['answer'] = re.sub(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+.*?(?:FROM|INTO|SET|TABLE|WHERE).*?(?=\n\n|\Z)', '', response['answer'], flags=re.IGNORECASE | re.DOTALL)

                    # Remove "Answer:" prefix if present
                    response['answer'] = re.sub(r'^Answer:\s*', '', response['answer'], flags=re.IGNORECASE)

                    # Clean up multiple newlines
                    response['answer'] = re.sub(r'\n{3,}', '\n\n', response['answer'])
                    response['answer'] = response['answer'].strip()

            # Log the answer after cleaning
            logger.info(f"Answer after cleaning: '{response.get('answer', '')}'")

            # If answer is empty after cleaning, try to use the raw result
            if not response.get('answer') or (isinstance(response['answer'], str) and not response['answer'].strip()):
                logger.info("Answer is empty after cleaning, using raw result if available")
                if 'result' in result and result['result'] and str(result['result']).strip():
                    response['answer'] = str(result['result']).strip()
                    logger.info(f"Using raw result as answer: {response['answer'][:100]}")
                else:
                    # Leave answer empty - app.py will generate from data
                    response['answer'] = ""
                    logger.info("No answer available, app.py will generate from data")

            logger.info(f"Query successful: {response['answer'][:100]}...")
            logger.info(f"Extracted SQL: {response['sql_query']}")
            return response

        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return {
                'question': question,
                'answer': f"Error processing query: {str(e)}",
                'sql_query': None,
                'error': str(e)
            }

    def get_table_info(self) -> str:
        """Get information about database tables.

        Returns:
            String containing table information
        """
        return self.db.get_table_info()

    def run_sql_query(self, query: str) -> Any:
        """Run a SQL query directly.

        Args:
            query: SQL query string

        Returns:
            Query results
        """
        return self.db.run(query)


class ChartRequestParser:
    """Parse user requests for chart generation."""

    CHART_KEYWORDS = {
        'bar': ['bar chart', 'bar graph', 'column chart'],
        'line': ['line chart', 'line graph', 'trend'],
        'pie': ['pie chart', 'pie graph', 'distribution'],
        'scatter': ['scatter plot', 'scatter chart', 'correlation'],
        'histogram': ['histogram', 'frequency distribution'],
        'box': ['box plot', 'boxplot'],
        'heatmap': ['heatmap', 'heat map', 'correlation matrix']
    }

    @staticmethod
    def detect_chart_request(text: str) -> Optional[str]:
        """Detect if user is requesting a chart.

        Args:
            text: User input text

        Returns:
            Chart type if detected, None otherwise
        """
        text_lower = text.lower()

        # Check for chart keywords
        chart_indicators = ['chart', 'graph', 'plot', 'visualize', 'visualization', 'show me']
        if not any(indicator in text_lower for indicator in chart_indicators):
            return None

        # Detect chart type
        for chart_type, keywords in ChartRequestParser.CHART_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return chart_type

        # Default to bar chart if chart is requested but type not specified
        return 'bar'

    @staticmethod
    def detect_report_request(text: str) -> bool:
        """Detect if user is requesting a report.

        Args:
            text: User input text

        Returns:
            True if report is requested
        """
        text_lower = text.lower()
        report_keywords = [
            'report', 'generate report', 'create report',
            'detailed report', 'summary report', 'analysis report'
        ]
        return any(keyword in text_lower for keyword in report_keywords)
