"""Database handler for SQLite operations."""
import sqlite3
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.types import Integer, Float, String, DateTime
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

    # Extract SQL query if it's embedded in other text
    # Look for SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER statements
    sql_patterns = [
        r'(SELECT\s+.+?)(?:\n\n|$)',
        r'(INSERT\s+.+?)(?:\n\n|$)',
        r'(UPDATE\s+.+?)(?:\n\n|$)',
        r'(DELETE\s+.+?)(?:\n\n|$)',
        r'(CREATE\s+.+?)(?:\n\n|$)',
        r'(DROP\s+.+?)(?:\n\n|$)',
        r'(ALTER\s+.+?)(?:\n\n|$)',
    ]

    # Try to extract valid SQL statement
    for pattern in sql_patterns:
        match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
        if match:
            query = match.group(1)
            break

    # Remove any text before SELECT/INSERT/UPDATE/DELETE if present
    query = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+', r'\1 ', query, flags=re.IGNORECASE)

    # Remove any text after a double newline (likely explanation text)
    if '\n\n' in query:
        query = query.split('\n\n')[0]

    # Remove any leading/trailing whitespace
    query = query.strip()

    return query


class DatabaseHandler:
    """Handle SQLite database operations."""

    def __init__(self, db_url: str):
        """Initialize database handler.

        Args:
            db_url: SQLAlchemy database URL
        """
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.metadata = MetaData()

    def create_tables_from_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """Create database tables from DataFrames.

        Args:
            dataframes: Dictionary mapping table names to DataFrames
        """
        logger.info(f"Creating {len(dataframes)} tables in database")

        for table_name, df in dataframes.items():
            try:
                # Infer SQLAlchemy types from pandas dtypes
                dtype_mapping = self._get_dtype_mapping(df)

                # Write DataFrame to database
                df.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists='replace',
                    index=False,
                    dtype=dtype_mapping
                )

                logger.info(f"Created table: {table_name} with {len(df)} rows")

            except Exception as e:
                logger.error(f"Error creating table {table_name}: {str(e)}")
                raise

        # Refresh metadata
        self.metadata.reflect(bind=self.engine)

    def _get_dtype_mapping(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Map pandas dtypes to SQLAlchemy types.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary mapping column names to SQLAlchemy types
        """
        dtype_mapping = {}

        for col, dtype in df.dtypes.items():
            if pd.api.types.is_integer_dtype(dtype):
                dtype_mapping[col] = Integer
            elif pd.api.types.is_float_dtype(dtype):
                dtype_mapping[col] = Float
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                dtype_mapping[col] = DateTime
            else:
                # Default to String for object and other types
                dtype_mapping[col] = String

        return dtype_mapping

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame.

        Args:
            query: SQL query string

        Returns:
            DataFrame with query results
        """
        try:
            # Clean the query to remove any markdown formatting
            cleaned_query = clean_sql_query(query)
            logger.info(f"Executing query: {cleaned_query[:100]}...")
            df = pd.read_sql_query(cleaned_query, self.engine)
            logger.info(f"Query returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of dictionaries with column information
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)

        schema_info = []
        for col in columns:
            schema_info.append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable']
            })

        return schema_info

    def get_all_table_schemas(self) -> Dict[str, List[Dict[str, str]]]:
        """Get schema information for all tables.

        Returns:
            Dictionary mapping table names to schema information
        """
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        schemas = {}
        for table_name in table_names:
            schemas[table_name] = self.get_table_schema(table_name)

        return schemas

    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database.

        Returns:
            List of table names
        """
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from a table.

        Args:
            table_name: Name of the table
            limit: Number of rows to retrieve

        Returns:
            DataFrame with sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)

    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the database.

        Returns:
            Dictionary with database information
        """
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        info = {
            'table_count': len(table_names),
            'tables': {}
        }

        for table_name in table_names:
            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            row_count = self.execute_query(count_query)['count'][0]

            # Get schema
            schema = self.get_table_schema(table_name)

            info['tables'][table_name] = {
                'row_count': row_count,
                'column_count': len(schema),
                'columns': schema
            }

        return info

    def close(self):
        """Close database connection."""
        self.engine.dispose()
        logger.info("Database connection closed")
