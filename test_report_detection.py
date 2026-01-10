"""Test report detection logic."""

def detect_report_request(text: str) -> bool:
    """Detect if user is requesting a report."""
    text_lower = text.lower()
    report_keywords = [
        'report', 'generate report', 'create report',
        'detailed report', 'summary report', 'analysis report'
    ]
    return any(keyword in text_lower for keyword in report_keywords)


# Test cases
test_queries = [
    "Create a detailed report with executive summary on sales",
    "Create a customer analysis report",
    "Generate a report on products",
    "Show me sales data",  # Should NOT trigger
    "What are the top customers",  # Should NOT trigger
]

print("Testing Report Detection:")
print("=" * 60)

for query in test_queries:
    is_report = detect_report_request(query)
    status = "✅ REPORT" if is_report else "❌ NOT REPORT"
    print(f"{status}: {query}")

print("\n" + "=" * 60)
