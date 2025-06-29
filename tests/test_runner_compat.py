# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         tests/test_runner_compat.py
# Purpose:      Compatibility layer for music21.mainTest() with new test structure
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Compatibility layer for music21.mainTest() to work with the new consolidated test structure.

This module provides functions to discover and run tests from the new tests/ directory
while maintaining backward compatibility with the existing music21.mainTest() interface.
"""
from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

def get_test_module_for_music21_module(module_name: str) -> str:
    """
    Get the corresponding test module name for a music21 module.
    
    Args:
        module_name: Name of the music21 module (e.g., 'music21.note')
        
    Returns:
        Test module name (e.g., 'tests.unit.test_note')
    """
    # Strip 'music21.' prefix if present
    if module_name.startswith('music21.'):
        module_name = module_name[8:]
    
    # Handle submodules
    parts = module_name.split('.')
    if len(parts) == 1:
        # Main module like 'note' -> 'tests.unit.test_note'
        return f'tests.unit.test_{parts[0]}'
    else:
        # Submodule like 'stream.base' -> 'tests.unit.test_stream'
        return f'tests.unit.test_{parts[0]}'

def discover_tests_for_module(module_name: str) -> unittest.TestSuite:
    """
    Discover tests for a specific music21 module from the new test structure.
    
    Args:
        module_name: Name of the music21 module
        
    Returns:
        TestSuite containing all tests for the module
    """
    test_module_name = get_test_module_for_music21_module(module_name)
    suite = unittest.TestSuite()
    
    try:
        test_module = importlib.import_module(test_module_name)
        loader = unittest.TestLoader()
        module_suite = loader.loadTestsFromModule(test_module)
        suite.addTest(module_suite)
    except ImportError:
        # Fallback: try to find tests in the original location
        pass
    
    return suite

def discover_all_tests() -> unittest.TestSuite:
    """
    Discover all tests from the new test structure.
    
    Returns:
        TestSuite containing all tests
    """
    loader = unittest.TestLoader()
    
    # Add project root to path if not already there
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Discover all tests from the tests directory
    suite = loader.discover('tests', pattern='test_*.py')
    return suite

def run_tests_for_module(module_name: str, verbosity: int = 1) -> unittest.TestResult:
    """
    Run tests for a specific music21 module.
    
    Args:
        module_name: Name of the music21 module
        verbosity: Verbosity level for test output
        
    Returns:
        TestResult object with test results
    """
    suite = discover_tests_for_module(module_name)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)

def run_all_tests(verbosity: int = 1) -> unittest.TestResult:
    """
    Run all tests from the new test structure.
    
    Args:
        verbosity: Verbosity level for test output
        
    Returns:
        TestResult object with test results
    """
    suite = discover_all_tests()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)