#!/usr/bin/env python3
"""Test enhanced SQL cleaning logic - standalone version"""

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

    # Remove any text before SELECT if it doesn't start with SQL keyword
    if not query.strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH')):
        query = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\s+', r'\1 ', query, flags=re.IGNORECASE)

    # Extract SQL query if it's embedded in other text
    # Stop at explanation phrases that commonly follow SQL
    explanation_markers = [
        r'\n\nThis',
        r'\n\nThe ',
        r'\n\nNote:',
        r'\n\nExplanation:',
        r'\n\nIf you',
        r'\nThis query',
        r'\nThis will',
        r'\nThe query',
        r'\nNote:',
        r'\nExplanation:',
        r'\s+This query',
        r'\s+This will',
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
    if '\n\n' in query:
        query = query.split('\n\n')[0]

    # Remove any trailing explanatory sentences
    query = re.sub(r'\s+(This|The|Note|Explanation|If you|which|that could)[\s\S]*$', '', query, flags=re.IGNORECASE)

    # Remove any lines that don't look like SQL (contain common explanation words)
    lines = query.split('\n')
    sql_lines = []
    for line in lines:
        line_lower = line.lower().strip()
        # Skip lines that are clearly explanations
        if line_lower and not any(word in line_lower for word in ['this query will', 'this will retrieve', 'if you', 'which you could', 'that could be']):
            sql_lines.append(line)
    query = '\n'.join(sql_lines)

    # Remove any leading/trailing whitespace
    query = query.strip()

    return query


# Test cases
test_cases = [
    {
        "name": "SQL with 'This' explanation after newlines",
        "input": """SELECT strftime('%Y-%m', orderdate) AS month, ROUND(SUM(quantityordered * priceeach), 2) AS total_sales
FROM orders JOIN orderdetails ON orders.ordernumber = orderdetails.ordernumber
GROUP BY month ORDER BY month

This query will extract the year and month""",
        "should_contain": ["SELECT", "FROM orders", "GROUP BY"],
        "should_not_contain": ["This query"]
    },
    {
        "name": "SQL with 'which' explanation inline",
        "input": """SELECT productname, buyprice, msrp FROM products ORDER BY buyprice DESC LIMIT 10 which you could then use""",
        "should_contain": ["SELECT", "FROM products", "LIMIT 10"],
        "should_not_contain": ["which you could"]
    },
    {
        "name": "Subquery with AVG (should preserve)",
        "input": """SELECT AVG(order_total) FROM (
SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total
FROM orders o JOIN orderdetails od ON o.ordernumber = od.ordernumber
GROUP BY o.ordernumber
)""",
        "should_contain": ["SELECT AVG", "FROM (", "SELECT o.ordernumber"],
        "should_not_contain": []
    },
]

print("Testing Enhanced SQL Cleaning:")
print("=" * 70)

all_passed = True
for test in test_cases:
    print(f"\nTest: {test['name']}")
    output = clean_sql_query(test['input'])

    # Check what should be in the output
    passed = True
    for phrase in test['should_contain']:
        if phrase in output:
            print(f"  ✅ Contains '{phrase}'")
        else:
            print(f"  ❌ FAIL: Missing '{phrase}'")
            passed = False
            all_passed = False

    # Check what should NOT be in the output
    for phrase in test['should_not_contain']:
        if phrase not in output:
            print(f"  ✅ Removed '{phrase}'")
        else:
            print(f"  ❌ FAIL: Still contains '{phrase}'")
            passed = False
            all_passed = False

    if passed:
        print(f"  ✅ PASS")
    print(f"\n  Cleaned query:\n  {output}\n")

if all_passed:
    print("\n✅ All tests passed!")
else:
    print("\n❌ Some tests failed")
