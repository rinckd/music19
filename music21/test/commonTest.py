# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         test/commonTest.py
# Purpose:      Compatibility import for relocated commonTest
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Compatibility import for commonTest that has been moved to tests/framework/.

This file provides backward compatibility for:
from music21.test.commonTest import testCopyAll
"""
import sys
from pathlib import Path

# Add the new tests location to Python path
project_root = Path(__file__).parent.parent.parent
tests_path = project_root / 'tests'
if str(tests_path) not in sys.path:
    sys.path.insert(0, str(tests_path))

# Import everything from the new location
from tests.framework.commonTest import *  # noqa