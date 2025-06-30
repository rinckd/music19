#!/usr/bin/env python
"""Run all music19 tests for PyCharm Test Coverage"""

from music19.test.testSingleCoreAll import main

if __name__ == '__main__':
    # Run all tests using music19's official test runner
    # Skip external tests that require additional software (like Lilypond)
    # This is equivalent to: python -m music19.test.testSingleCoreAll
    main(testGroup=('test',), show=False)
