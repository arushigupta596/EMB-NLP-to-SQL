"""SQL query templates for suggested questions - bypasses LLM API."""

SUGGESTED_QUESTION_TEMPLATES = {
    # Basic Queries (5 questions)
    "Show me all customers": "SELECT * FROM customers LIMIT 100",

    "How many orders do we have": "SELECT COUNT(*) AS total_orders FROM orders",

    "What are the top 5 products by price": "SELECT * FROM products ORDER BY buyPrice DESC LIMIT 5",

    "List all employees": "SELECT * FROM employees",

    "Show me the office locations": "SELECT city, country, addressLine1 FROM offices",

    # Aggregation Queries (5 questions)
    "What is the total revenue from all orders": """
        SELECT SUM(quantityOrdered * priceEach) AS total_revenue
        FROM orderdetails
    """,

    "How many customers are in each country": """
        SELECT country, COUNT(*) AS customer_count
        FROM customers
        GROUP BY country
        ORDER BY customer_count DESC
    """,

    "What is the average order value": """
        SELECT AVG(order_total) AS avg_order_value
        FROM (
            SELECT orderNumber, SUM(quantityOrdered * priceEach) AS order_total
            FROM orderdetails
            GROUP BY orderNumber
        ) AS order_totals
    """,

    "Count products by product line": """
        SELECT productLine, COUNT(*) AS product_count
        FROM products
        GROUP BY productLine
        ORDER BY product_count DESC
    """,

    "What is the total payment received": """
        SELECT SUM(amount) AS total_payments
        FROM payments
    """,

    # Analysis Queries (5 questions)
    "Which customers have spent the most": """
        SELECT c.customerName, SUM(od.quantityOrdered * od.priceEach) AS total_spent
        FROM customers c
        JOIN orders o ON c.customerNumber = o.customerNumber
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY c.customerNumber, c.customerName
        ORDER BY total_spent DESC
        LIMIT 10
    """,

    "What are the top selling products": """
        SELECT p.productName, SUM(od.quantityOrdered) AS total_sold
        FROM products p
        JOIN orderdetails od ON p.productCode = od.productCode
        GROUP BY p.productCode, p.productName
        ORDER BY total_sold DESC
        LIMIT 10
    """,

    "Show me monthly sales trends": """
        SELECT
            strftime('%Y-%m', o.orderDate) AS month,
            SUM(od.quantityOrdered * od.priceEach) AS monthly_revenue
        FROM orders o
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """,

    "Which sales representatives have the most customers": """
        SELECT e.firstName || ' ' || e.lastName AS sales_rep, COUNT(*) AS customer_count
        FROM employees e
        JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
        GROUP BY e.employeeNumber, sales_rep
        ORDER BY customer_count DESC
    """,

    "What is the distribution of orders by status": """
        SELECT status, COUNT(*) AS order_count
        FROM orders
        GROUP BY status
        ORDER BY order_count DESC
    """,

    # Chart/Visualization Requests (4 questions)
    "Show me a bar chart of products by price": """
        SELECT productName, buyPrice
        FROM products
        ORDER BY buyPrice DESC
        LIMIT 15
    """,

    "Create a pie chart of customers by country": """
        SELECT country, COUNT(*) AS customer_count
        FROM customers
        GROUP BY country
        ORDER BY customer_count DESC
        LIMIT 10
    """,

    "Generate a line chart of orders over time": """
        SELECT
            strftime('%Y-%m', orderDate) AS month,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY month
        ORDER BY month ASC
    """,

    "Create a bar graph of top 10 customers by total purchases": """
        SELECT c.customerName, SUM(od.quantityOrdered * od.priceEach) AS total_purchases
        FROM customers c
        JOIN orders o ON c.customerNumber = o.customerNumber
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY c.customerNumber, c.customerName
        ORDER BY total_purchases DESC
        LIMIT 10
    """,

    # Professional Reports (3 questions)
    "Generate a professional report on customer data": """
        SELECT * FROM customers LIMIT 100
    """,

    "Create a detailed report with executive summary on sales": """
        SELECT
            strftime('%Y-%m', o.orderDate) AS month,
            SUM(od.quantityOrdered * od.priceEach) AS revenue,
            COUNT(DISTINCT o.orderNumber) AS order_count,
            COUNT(DISTINCT o.customerNumber) AS customer_count
        FROM orders o
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY month
        ORDER BY month DESC
    """,

    "Generate a comprehensive analysis report on products": """
        SELECT * FROM products
    """,

    # Complex Queries (5 questions)
    "Which products have never been ordered": """
        SELECT p.productCode, p.productName
        FROM products p
        LEFT JOIN orderdetails od ON p.productCode = od.productCode
        WHERE od.productCode IS NULL
    """,

    "Show me customers who placed more than 5 orders": """
        SELECT c.customerName, COUNT(o.orderNumber) AS order_count
        FROM customers c
        JOIN orders o ON c.customerNumber = o.customerNumber
        GROUP BY c.customerNumber, c.customerName
        HAVING COUNT(o.orderNumber) > 5
        ORDER BY order_count DESC
    """,

    "What is the revenue trend for the last 6 months": """
        SELECT
            strftime('%Y-%m', o.orderDate) AS month,
            SUM(od.quantityOrdered * od.priceEach) AS revenue
        FROM orders o
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        WHERE o.orderDate >= date('now', '-6 months')
        GROUP BY month
        ORDER BY month ASC
    """,

    "Find the most profitable product lines": """
        SELECT
            p.productLine,
            SUM(od.quantityOrdered * (od.priceEach - p.buyPrice)) AS profit
        FROM products p
        JOIN orderdetails od ON p.productCode = od.productCode
        GROUP BY p.productLine
        ORDER BY profit DESC
    """,

    "Which employees manage the most valuable customers": """
        SELECT
            e.firstName || ' ' || e.lastName AS employee_name,
            SUM(od.quantityOrdered * od.priceEach) AS managed_customer_value
        FROM employees e
        JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
        JOIN orders o ON c.customerNumber = o.customerNumber
        JOIN orderdetails od ON o.orderNumber = od.orderNumber
        GROUP BY e.employeeNumber, employee_name
        ORDER BY managed_customer_value DESC
        LIMIT 10
    """
}


def get_template_sql(question: str) -> str | None:
    """
    Get hardcoded SQL template for a suggested question.

    Args:
        question: User's question text

    Returns:
        SQL query string if template exists, None otherwise
    """
    # Normalize question for matching
    normalized = question.strip().rstrip('?.!')
    return SUGGESTED_QUESTION_TEMPLATES.get(normalized)


def has_template(question: str) -> bool:
    """Check if a template exists for this question."""
    return get_template_sql(question) is not None
