"""Test SQL query cleaning with subqueries."""
import re

def clean_sql_query(query: str) -> str:
    """Clean SQL query by removing markdown formatting and labels."""
    if not query:
        return query

    # Remove markdown code blocks
    query = re.sub(r'```sql\s*', '', query, flags=re.IGNORECASE)
    query = re.sub(r'```\s*', '', query)

    # Remove "SQLQuery:" prefix
    query = re.sub(r'^SQLQuery:\s*', '', query, flags=re.IGNORECASE)
    query = re.sub(r'^SQL\s*Query:\s*', '', query, flags=re.IGNORECASE)

    # Remove any text before SELECT/INSERT/UPDATE/DELETE if present
    # But be careful not to remove SELECT if it's part of a valid subquery
    if not query.strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH')):
        query = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\s+', r'\1 ', query, flags=re.IGNORECASE)

    # Extract SQL query if it's embedded in other text
    explanation_markers = [
        r'\n\nThis query',
        r'\n\nThis will',
        r'\n\nThe query',
        r'\n\nNote:',
        r'\n\nExplanation:',
        r'\nThis query',
        r'\nThis will',
        r'\nThe query',
        r'\nNote:',
    ]

    earliest_pos = len(query)
    for marker in explanation_markers:
        match = re.search(marker, query, re.IGNORECASE)
        if match and match.start() < earliest_pos:
            earliest_pos = match.start()

    if earliest_pos < len(query):
        query = query[:earliest_pos]

    if '\n\n' in query:
        query = query.split('\n\n')[0]

    query = re.sub(r'\s+(This|The|Note|Explanation)[\s\S]*$', '', query, flags=re.IGNORECASE)
    query = query.strip()

    return query


# Test with subquery
test_cases = [
    {
        'name': 'Complete subquery',
        'input': 'SELECT AVG(order_total) FROM (SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total FROM orders o JOIN orderdetails od ON o.ordernumber = od.ordernumber GROUP BY o.ordernumber)',
        'should_start_with': 'SELECT AVG',
        'should_contain': 'FROM (SELECT'
    },
    {
        'name': 'Subquery with explanation prefix',
        'input': 'Here is the query: SELECT AVG(order_total) FROM (SELECT o.ordernumber FROM orders o)',
        'should_start_with': 'SELECT AVG',
        'should_contain': 'FROM (SELECT'
    },
    {
        'name': 'Incomplete subquery (starts with FROM)',
        'input': 'FROM (SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total FROM orders o)',
        'should_start_with': 'FROM',
        'should_contain': 'SELECT'
    },
]

print("Testing SQL Subquery Cleaning:")
print("=" * 70)

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print(f"Input: {test['input'][:80]}...")

    cleaned = clean_sql_query(test['input'])
    print(f"Output: {cleaned[:80]}...")

    starts_ok = cleaned.upper().startswith(test['should_start_with'].upper())
    contains_ok = test['should_contain'].upper() in cleaned.upper()

    print(f"  Starts with '{test['should_start_with']}': {starts_ok}")
    print(f"  Contains '{test['should_contain']}': {contains_ok}")

    if starts_ok and contains_ok:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
