"""Test answer text cleaning."""
import re

def clean_answer(answer: str) -> str:
    """Clean answer text to remove SQL query portions."""
    if not answer:
        return answer

    # Remove "Question:" prefix
    answer = re.sub(r'^Question:\s*.+?\n', '', answer, flags=re.IGNORECASE)

    # Remove "SQLQuery:" lines
    answer = re.sub(r'SQLQuery:\s*.+?(?:\n|$)', '', answer, flags=re.IGNORECASE | re.MULTILINE)

    # Remove "SQLResult:" lines
    answer = re.sub(r'SQLResult:\s*.+?(?:\n|$)', '', answer, flags=re.IGNORECASE | re.MULTILINE)

    # Remove "Answer:" prefix if present
    answer = re.sub(r'^Answer:\s*', '', answer, flags=re.IGNORECASE)

    # Clean up multiple newlines
    answer = re.sub(r'\n{3,}', '\n\n', answer)
    answer = answer.strip()

    return answer


# Test cases
test_answers = [
    {
        'name': 'Answer with SQLQuery',
        'input': 'Question: Create a detailed report with executive summary on sales SQLQuery: SELECT e.lastname, e.firstname FROM employees',
        'expected_contains': 'Create a detailed report',
        'expected_not_contains': 'SQLQuery'
    },
    {
        'name': 'Clean answer',
        'input': 'The report has been generated successfully.',
        'expected_contains': 'The report has been generated',
        'expected_not_contains': 'SQLQuery'
    },
    {
        'name': 'Answer with Question and Answer prefix',
        'input': 'Question: Show me customers\nSQLQuery: SELECT * FROM customers\nAnswer: Here are the customers.',
        'expected_contains': 'Here are the customers',
        'expected_not_contains': 'Question:'
    },
    {
        'name': 'Answer with SQL inline',
        'input': 'Answer: Based on the query, there are 15 employees.',
        'expected_contains': 'Based on the query',
        'expected_not_contains': 'Answer:'
    },
]

print("Testing Answer Cleaning:")
print("=" * 70)

for test in test_answers:
    print(f"\nTest: {test['name']}")
    print(f"  Input:  {test['input'][:80]}...")
    cleaned = clean_answer(test['input'])
    print(f"  Output: {cleaned}")

    contains_check = test['expected_contains'] in cleaned
    not_contains_check = test['expected_not_contains'] not in cleaned

    print(f"  ✓ Contains '{test['expected_contains']}': {contains_check}")
    print(f"  ✓ Does NOT contain '{test['expected_not_contains']}': {not_contains_check}")
    print(f"  Result: {'PASS ✅' if (contains_check and not_contains_check) else 'FAIL ❌'}")

print("\n" + "=" * 70)
print("Testing complete!")
