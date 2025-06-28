#!/usr/bin/env python
"""Run all music21 tests for PyCharm Test Coverage"""

from music21.test.testSingleCoreAll import main

if __name__ == '__main__':
    # Run all tests using music21's official test runner
    # Skip external tests that require additional software (like Lilypond)
    # This is equivalent to: python -m music21.test.testSingleCoreAll
    main(testGroup=('test',), show=False)
