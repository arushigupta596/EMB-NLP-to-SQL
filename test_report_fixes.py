"""Test script to verify report fixes."""
import re

def test_sql_query_removal():
    """Test that SQL query prefix is removed from summary."""
    test_cases = [
        "SQLQuery: This is a summary about customers.",
        "SQL query: This is a summary about products.",
        "SQL Query: This is a summary about orders.",
        "This is a normal summary without SQL prefix."
    ]

    print("Testing SQL Query Removal:")
    print("-" * 50)

    for test in test_cases:
        # Apply the cleaning logic
        cleaned = test.replace('Executive Summary:', '').strip()
        cleaned = re.sub(r'^SQLQuery:\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^SQL\s*[Qq]uery:\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        print(f"Original: {test}")
        print(f"Cleaned:  {cleaned}")
        print()

def test_insights_numbering():
    """Test that insights numbering works correctly."""
    test_insights = """1. First insight: This is the first key finding about the data.
It continues on multiple lines here.

2. Second insight: This is the second important discovery.
With more details here.

3. Third insight: This is the third analysis point.

4. Fourth insight: This is the final key takeaway."""

    print("Testing Insights Numbering:")
    print("-" * 50)

    if re.search(r'^\d+\.', test_insights.strip(), re.MULTILINE):
        # Split by numbered pattern to get all insights
        insights_list = []
        lines = test_insights.split('\n')
        current_insight = ""
        current_number = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a number
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                # Save previous insight if exists
                if current_number is not None and current_insight:
                    insights_list.append((current_number, current_insight.strip()))

                # Start new insight
                current_number = int(match.group(1))
                current_insight = match.group(2)
            else:
                # Continuation of current insight
                if current_number is not None:
                    current_insight += " " + line

        # Add last insight
        if current_number is not None and current_insight:
            insights_list.append((current_number, current_insight.strip()))

        # Display all insights
        print(f"Found {len(insights_list)} insights:")
        print()
        for num, insight in insights_list:
            print(f"**{num}.** {insight}")
            print()

if __name__ == "__main__":
    test_sql_query_removal()
    print("\n" + "="*50 + "\n")
    test_insights_numbering()
