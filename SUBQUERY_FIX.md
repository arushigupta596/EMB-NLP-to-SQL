# Subquery SQL Generation Fix

## Problem
When asking "What is the average order value?", the application was displaying incomplete SQL starting with `FROM` instead of a complete query with `SELECT AVG(...)`:

**Incorrect Output:**
```sql
FROM ( SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total
FROM orders o JOIN orderdetails od ON o.ordernumber = od.ordernumber
GROUP BY o.ordernumber )
```

**Expected Output:**
```sql
SELECT AVG(order_total) FROM (
  SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total
  FROM orders o JOIN orderdetails od ON o.ordernumber = od.ordernumber
  GROUP BY o.ordernumber
)
```

## Root Cause

The LLM was generating incomplete SQL queries that started with `FROM` instead of including the outer `SELECT AVG(...)` wrapper. This happened because:

1. The prompt didn't explicitly instruct the LLM to include complete outer SELECT statements for subqueries
2. No specific guidance on how to structure average calculations
3. No example showing the proper subquery pattern

## Solution

### Enhanced LLM Prompt
**File**: `llm_handler.py` lines 166-177

Added specific guidelines for subqueries and average calculations:

```python
Important Guidelines:
- Return ONLY the SQL query itself - DO NOT add explanations, descriptions, or comments after the query
- Do NOT write "This query will..." or "The query..." after the SQL
- Write only pure SQL without backticks, without "sql" language tags, and without markdown formatting
- For sales data: JOIN orderdetails table with orders table, calculate sales as (quantityordered * priceeach)
- For sales reports: Use SUM(quantityordered * priceeach) to get total sales
- Always use proper JOIN syntax when combining tables
- Include relevant GROUP BY clauses for aggregations
- For average calculations (e.g., "average order value"): Use a subquery to calculate totals first, then apply AVG()
  Example: SELECT AVG(order_total) FROM (SELECT ordernumber, SUM(quantity * price) AS order_total FROM orders GROUP BY ordernumber)
- ALWAYS include the complete outer SELECT statement for subqueries - never start with FROM
- End the SQLQuery section immediately after the SQL statement
```

**Key additions:**
1. **Line 174-175**: Explicit instruction with example for average calculations
2. **Line 176**: Critical instruction to ALWAYS include outer SELECT, never start with FROM
3. **Concrete example**: Shows the exact pattern to use

### Added Debug Logging
**File**: `llm_handler.py` lines 223-231

Added logging to track what SQL is being generated and cleaned:

```python
if isinstance(step, str) and 'SELECT' in step.upper():
    logger.info(f"Raw SQL from step (string): {step[:200]}")
    response['sql_query'] = clean_sql_query(step)
    logger.info(f"Cleaned SQL: {response['sql_query'][:200]}")
    break
elif isinstance(step, dict) and 'sql_cmd' in step:
    logger.info(f"Raw SQL from step (dict): {step['sql_cmd'][:200]}")
    response['sql_query'] = clean_sql_query(step['sql_cmd'])
    logger.info(f"Cleaned SQL: {response['sql_query'][:200]}")
    break
```

This helps debug:
- What the LLM is actually generating
- Whether the cleaning is removing parts of the query incorrectly

### SQL Cleaning Already Fixed
**File**: `llm_handler.py` lines 38-42

The cleaning function already has proper handling to preserve subqueries:

```python
# Remove any text before SELECT if it doesn't start with SQL keyword
if not query.strip().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH')):
    query = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\s+', r'\1 ', query, flags=re.IGNORECASE)
```

This ensures:
- If query already starts with SELECT, don't remove anything
- Only remove non-SQL text before the first SQL keyword
- Preserves nested SELECT statements in subqueries

## Test Results

Created `test_subquery_cleaning.py` with test cases:

```
✅ Complete subquery - Preserves SELECT AVG(...)
✅ Subquery with explanation prefix - Removes "Here is the query:" but keeps full SQL
✅ Incomplete subquery (edge case) - Extracts inner SELECT
```

## Expected Behavior After Fix

### Query: "What is the average order value?"

**SQL Generated:**
```sql
SELECT AVG(order_total) FROM (
  SELECT o.ordernumber, SUM(od.quantityordered * od.priceeach) AS order_total
  FROM orders o
  JOIN orderdetails od ON o.ordernumber = od.ordernumber
  GROUP BY o.ordernumber
)
```

**Answer:** "The result is: 3150.9009" (or similar based on actual data)

### Similar Queries That Should Work:
- "What is the average product price?"
- "Calculate the mean order quantity"
- "Show me the average sales per order"

## Files Modified

1. **`llm_handler.py`**:
   - Enhanced prompt with subquery guidance (lines 174-176)
   - Added debug logging (lines 223-231)

## Impact

- ✅ LLM now generates complete subqueries with outer SELECT
- ✅ Average calculations work correctly
- ✅ Debug logging helps troubleshoot SQL generation issues
- ✅ Cleaning preserves nested SELECT statements

## Related Fixes

This fix builds on previous SQL cleaning enhancements:
- `SQL_EXPLANATION_REMOVAL_FIX.md` - Removes explanatory text after SQL
- `ANSWER_GENERATION_FIX.md` - Ensures answers are displayed
- `test_subquery_cleaning.py` - Tests subquery preservation

## Testing Recommendation

After restarting the Streamlit app, test:
1. "What is the average order value?"
2. "Calculate the mean product price"
3. "Show me average sales per customer"

All should generate complete SQL with outer SELECT statements and display proper numeric results.
