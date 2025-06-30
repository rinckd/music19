# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         test/__init__.py
# Purpose:      Compatibility layer for relocated test framework
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Compatibility layer for test framework that has been moved to tests/.

ALL TESTS HAVE BEEN MOVED TO THE tests/ DIRECTORY:
- tests/unit/ - Unit tests
- tests/framework/ - Test framework and utilities  
- tests/external/ - External tests
- tests/performance/ - Performance tests
- tests/integration/ - Integration tests

This module provides backward compatibility for legacy imports.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

# Add the new tests location to Python path
project_root = Path(__file__).parent.parent.parent
tests_path = project_root / 'tests'
if str(tests_path) not in sys.path:
    sys.path.insert(0, str(tests_path))

# Note: Specific imports are handled by individual module files
# This avoids circular import issues with music21.__init__.py

# Test module imports for backward compatibility (lazy loading)
def __getattr__(name):
    """Lazy loading of test modules to avoid circular imports."""
    if name == 'base':
        from tests.unit import test_base as base
        return base
    elif name == 'chord':
        from tests.unit import test_chord as chord
        return chord
    elif name == 'clef':
        from tests.unit import test_clef as clef
        return clef
    elif name == 'expressions':
        from tests.unit import test_expressions as expressions
        return expressions
    elif name == 'interval':
        from tests.unit import test_interval as interval
        return interval
    elif name == 'metadata':
        from tests.unit import test_metadata as metadata
        return metadata
    elif name == 'note':
        from tests.unit import test_note as note
        return note
    elif name == 'pitch':
        from tests.unit import test_pitch as pitch
        return pitch
    elif name == 'testSingleCoreAll':
        from tests.framework import testSingleCoreAll
        return testSingleCoreAll
    elif name == 'coverageM21':
        from tests.framework import coverageM21
        return coverageM21
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

_DOC_IGNORE_MODULE_OR_PACKAGE = True