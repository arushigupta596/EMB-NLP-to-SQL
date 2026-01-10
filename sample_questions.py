"""Sample questions for different data domains."""
from typing import List, Dict

# Sample questions categorized by type
SAMPLE_QUESTIONS = {
    "Basic Queries": [
        "Show me all customers",
        "How many orders do we have?",
        "What are the top 5 products by price?",
        "List all employees",
        "Show me the office locations"
    ],
    "Aggregation Queries": [
        "What is the total revenue from all orders?",
        "How many customers are in each country?",
        "What is the average order value?",
        "Count products by product line",
        "What is the total payment received?"
    ],
    "Analysis Queries": [
        "Which customers have spent the most?",
        "What are the top selling products?",
        "Show me monthly sales trends",
        "Which sales representatives have the most customers?",
        "What is the distribution of orders by status?"
    ],
    "Chart/Visualization Requests": [
        "Show me a bar chart of products by price",
        "Create a pie chart of customers by country",
        "Generate a line chart of orders over time",
        "Show me a scatter plot of quantity vs price",
        "Create a bar graph of top 10 customers by total purchases"
    ],

    "Professional Reports": [
        "Generate a professional report on customer data",
        "Create a detailed report with executive summary on sales",
        "Generate a comprehensive analysis report on products"
],
    "Complex Queries": [
        "Which products have never been ordered?",
        "Show me customers who placed more than 5 orders",
        "What is the revenue trend for the last 6 months?",
        "Find the most profitable product lines",
        "Which employees manage the most valuable customers?"
    ]
}


def get_all_sample_questions() -> Dict[str, List[str]]:
    """Get all sample questions organized by category.

    Returns:
        Dictionary mapping categories to lists of sample questions
    """
    return SAMPLE_QUESTIONS


def get_sample_questions_flat() -> List[str]:
    """Get all sample questions as a flat list.

    Returns:
        List of all sample questions
    """
    questions = []
    for category_questions in SAMPLE_QUESTIONS.values():
        questions.extend(category_questions)
    return questions


def get_questions_by_category(category: str) -> List[str]:
    """Get sample questions for a specific category.

    Args:
        category: Question category

    Returns:
        List of questions in the category
    """
    return SAMPLE_QUESTIONS.get(category, [])


def get_categories() -> List[str]:
    """Get list of question categories.

    Returns:
        List of category names
    """
    return list(SAMPLE_QUESTIONS.keys())


# Domain-specific question templates
DOMAIN_TEMPLATES = {
    "sales": {
        "total": "What is the total {metric} for {period}?",
        "top": "Show me the top {n} {entity} by {metric}",
        "trend": "What is the {metric} trend over {period}?",
        "comparison": "Compare {metric} between {entity1} and {entity2}",
    },
    "customer": {
        "segmentation": "How many customers are in {segment}?",
        "behavior": "Which customers have {behavior}?",
        "value": "Show me customers with {metric} greater than {value}",
    },
    "product": {
        "performance": "What are the best performing products by {metric}?",
        "inventory": "Show me products with {condition}",
        "category": "List all products in {category}",
    }
}


def generate_question_from_template(
    domain: str,
    template_type: str,
    **kwargs
) -> str:
    """Generate a question from a template.

    Args:
        domain: Domain name (sales, customer, product)
        template_type: Type of template
        **kwargs: Template variables

    Returns:
        Generated question string
    """
    if domain not in DOMAIN_TEMPLATES:
        raise ValueError(f"Unknown domain: {domain}")

    if template_type not in DOMAIN_TEMPLATES[domain]:
        raise ValueError(f"Unknown template type: {template_type}")

    template = DOMAIN_TEMPLATES[domain][template_type]
    return template.format(**kwargs)
