#!/usr/bin/env python
"""Run only core music21 tests (no external dependencies) for PyCharm Test Coverage"""

from music21.test.testSingleCoreAll import main

if __name__ == '__main__':
    # Run only core tests, skip external tests that need additional software
    # testGroup options:
    # - 'core': Basic functionality tests
    # - 'complete': All tests except external
    # - 'external': Tests requiring external software (Lilypond, etc.)
    
    print("Running core music21 tests (no external dependencies)...")
    main(testGroup=('test',), show=False)