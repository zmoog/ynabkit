#!/usr/bin/env python
"""Simple test runner for ynabkit tests."""

import sys
sys.path.insert(0, '.')

from tests.test_ynab import (
    test_version,
    test_describe_date_filtering,
    test_payees_add,
    test_payees_add_no_patterns,
    test_payees_lint,
    test_payees_lint_case_insensitive,
    test_payees_lint_empty_file,
)

# List of all tests
tests = [
    ('test_version', test_version),
    ('test_describe_date_filtering', test_describe_date_filtering),
    ('test_payees_add', test_payees_add),
    ('test_payees_add_no_patterns', test_payees_add_no_patterns),
    ('test_payees_lint', test_payees_lint),
    ('test_payees_lint_case_insensitive', test_payees_lint_case_insensitive),
    ('test_payees_lint_empty_file', test_payees_lint_empty_file),
]

def main():
    """Run all tests and report results."""
    passed = 0
    failed = 0
    errors = []

    print("Running tests...\n")

    for name, test_func in tests:
        try:
            test_func()
            print(f'✓ {name}')
            passed += 1
        except AssertionError as e:
            print(f'✗ {name}: {e}')
            failed += 1
            errors.append((name, str(e)))
        except Exception as e:
            print(f'✗ {name}: {e}')
            failed += 1
            errors.append((name, str(e)))

    # Summary
    print(f'\n{"="*60}')
    print(f'Test Results: {passed} passed, {failed} failed')
    print(f'{"="*60}')

    if errors:
        print('\nFailed tests:')
        for name, error in errors:
            print(f'  - {name}: {error}')

    return 1 if failed > 0 else 0

if __name__ == '__main__':
    sys.exit(main())
