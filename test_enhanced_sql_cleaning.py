#!/usr/bin/env python3
"""Test enhanced SQL cleaning logic"""

import sys
sys.path.insert(0, '/Users/arushigupta/Desktop/EMB/Demos/NLP to SQL')

from llm_handler import clean_sql_query

# Test cases from the screenshots
test_cases = [
    {
        "name": "SQL with 'This' explanation",
        "input": """SELECT strftime('%Y-%m', orderdate) AS month, ROUND(SUM(quantityordered * priceeach), 2) AS total_sales
FROM orders JOIN orderdetails ON orders.ordernumber = orderdetails.ordernumber
GROUP BY month ORDER BY month

This query will extract the year and month from the order date""",
        "should_contain": ["SELECT", "FROM orders", "GROUP BY"],
        "should_not_contain": ["This query"]
    },
    {
        "name": "SQL with 'which you could' explanation",
        "input": """SELECT productname, buyprice, msrp FROM products ORDER BY buyprice DESC LIMIT 10 which you could then use to create a bar chart""",
        "should_contain": ["SELECT", "FROM products", "LIMIT 10"],
        "should_not_contain": ["which you could", "bar chart"]
    },
    {
        "name": "SQL with newline + This explanation",
        "input": """SELECT p.productcode, p.productname, SUM(od.quantityordered * od.priceeach) AS total_sales
FROM products p JOIN orderdetails od ON p.productcode = od.productcode
GROUP BY p.productcode
ORDER BY total_sales DESC LIMIT 10

This query will help you identify the top-selling products""",
        "should_contain": ["SELECT", "JOIN", "GROUP BY", "ORDER BY", "LIMIT 10"],
        "should_not_contain": ["This query will help"]
    },
    {
        "name": "Subquery with AVG",
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
    print(f"Input: {test['input'][:80]}...")

    output = clean_sql_query(test['input'])
    print(f"Output: {output[:80]}...")

    # Check what should be in the output
    for phrase in test['should_contain']:
        if phrase in output:
            print(f"  ✅ Contains '{phrase}'")
        else:
            print(f"  ❌ FAIL: Missing '{phrase}'")
            all_passed = False

    # Check what should NOT be in the output
    for phrase in test['should_not_contain']:
        if phrase not in output:
            print(f"  ✅ Removed '{phrase}'")
        else:
            print(f"  ❌ FAIL: Still contains '{phrase}'")
            all_passed = False

    print(f"\n  Full cleaned query:\n  {output}\n")

if all_passed:
    print("\n✅ All tests passed!")
else:
    print("\n❌ Some tests failed")
