#!/usr/bin/env python
"""Run all music19 tests using pytest for better PyCharm integration"""

import pytest
import sys
import os

if __name__ == '__main__':
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))

    # Run pytest with coverage on the entire music19 package
    # This discovers all test files automatically
    pytest.main([
        'music19/test/',
        'music19/*/test_*.py',
        '--cov=music19',
        '--cov-report=html',
        '--cov-report=term',
        '-v'
    ])
