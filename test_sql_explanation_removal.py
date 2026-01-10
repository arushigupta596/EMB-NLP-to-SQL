"""Test SQL query cleaning with explanation text removal."""
import re

def clean_sql_query(query: str) -> str:
    """Clean SQL query by removing markdown formatting and labels."""
    if not query:
        return query

    # Remove markdown code blocks
    query = re.sub(r'```sql\s*', '', query, flags=re.IGNORECASE)
    query = re.sub(r'```\s*', '', query)

    # Remove "SQLQuery:" prefix if present
    query = re.sub(r'^SQLQuery:\s*', '', query, flags=re.IGNORECASE)

    # Remove "SQL Query:" variations
    query = re.sub(r'^SQL\s*Query:\s*', '', query, flags=re.IGNORECASE)

    # Remove any text before SELECT/INSERT/UPDATE/DELETE if present
    query = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+', r'\1 ', query, flags=re.IGNORECASE)

    # Extract SQL query if it's embedded in other text
    # Stop at explanation phrases that commonly follow SQL
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

    # Find the earliest explanation marker
    earliest_pos = len(query)
    for marker in explanation_markers:
        match = re.search(marker, query, re.IGNORECASE)
        if match and match.start() < earliest_pos:
            earliest_pos = match.start()

    # Truncate at the explanation
    if earliest_pos < len(query):
        query = query[:earliest_pos]

    # Also remove any text after a double newline
    if '\n\n' in query:
        query = query.split('\n\n')[0]

    # Remove any trailing explanatory sentences
    query = re.sub(r'\s+(This|The|Note|Explanation)[\s\S]*$', '', query, flags=re.IGNORECASE)

    # Remove any leading/trailing whitespace
    query = query.strip()

    return query


# Test case with the actual error
test_query = """SELECT c.customernumber, c.customername, c.contactfirstname || ' ' || c.contactlastname AS contact_name, c.country, c.creditlimit, COUNT(DISTINCT o.ordernumber) AS total_orders, ROUND(SUM(od.quantityordered * od.priceeach), 2) AS total_purchase_value, e.firstname || ' ' || e.lastname AS sales_rep_name, e.jobtitle AS sales_rep_title FROM customers c LEFT JOIN orders o ON c.customernumber = o.customernumber LEFT JOIN orderdetails od ON o.ordernumber = od.ordernumber LEFT JOIN employees e ON c.salesrepemployeenumber = e.employeenumber GROUP BY c.customernumber, c.customername, contact_name, c.country, c.creditlimit, sales_rep_name, sales_rep_title ORDER BY total_purchase_value DESC LIMIT 20

This query will generate a professional report with the following key insights:

Customer identification details
Contact information
Total number of orders
Total purchase value
Assigned sales representative details"""

print("Testing SQL Query Cleaning with Explanation Removal:")
print("=" * 70)
print("\nOriginal (with explanation):")
print(test_query[:200] + "...")
print(f"\nLength: {len(test_query)} characters")

cleaned = clean_sql_query(test_query)

print("\nCleaned (explanation removed):")
print(cleaned)
print(f"\nLength: {len(cleaned)} characters")

# Check if explanation was removed
has_explanation = "This query" in cleaned or "The query" in cleaned
print(f"\nStill contains explanation: {has_explanation}")

if not has_explanation and cleaned.strip().endswith("LIMIT 20"):
    print("✅ PASS - Explanation successfully removed!")
else:
    print("❌ FAIL - Explanation still present or query truncated incorrectly")

# Additional test cases
print("\n" + "=" * 70)
print("\nAdditional Test Cases:")

test_cases = [
    {
        'name': 'Query with double newline',
        'input': 'SELECT * FROM customers LIMIT 10\n\nThis query returns top customers',
        'should_end_with': 'LIMIT 10'
    },
    {
        'name': 'Query with single newline',
        'input': 'SELECT * FROM orders\nThis query gets all orders',
        'should_end_with': 'orders'
    },
    {
        'name': 'Clean query (no explanation)',
        'input': 'SELECT * FROM products',
        'should_end_with': 'products'
    },
]

for test in test_cases:
    cleaned = clean_sql_query(test['input'])
    success = cleaned.strip().endswith(test['should_end_with'])
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test['name']}")
    print(f"  Result: {cleaned}")
