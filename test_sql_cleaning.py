"""Test SQL query cleaning function."""
import re

def clean_sql_query(query: str) -> str:
    """Clean SQL query by removing markdown formatting and labels."""
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


# Test cases based on the error
test_queries = [
    'Executive: SELECT * FROM customers',
    'Executive Summary: SELECT * FROM customers',
    'SQLQuery: SELECT * FROM customers',
    'SQL Query: SELECT * FROM customers',
    '```sql\nSELECT * FROM customers\n```',
    'Executive syntax error [SQL: SELECT * FROM customers',
    'Error processing query: (sqlite3.OperationalError) near "Executive": SELECT * FROM customers',
]

print("Testing SQL Query Cleaning:")
print("=" * 60)

for i, test in enumerate(test_queries, 1):
    print(f"\nTest {i}:")
    print(f"  Input:  {test}")
    cleaned = clean_sql_query(test)
    print(f"  Output: {cleaned}")
    print(f"  Valid:  {'SELECT' in cleaned.upper() and 'Executive' not in cleaned}")
