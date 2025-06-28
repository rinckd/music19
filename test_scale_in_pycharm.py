#!/usr/bin/env python
"""Run scale module tests in PyCharm using music21's test runner"""

import music21

def run_all_scale_tests():
    """Run all tests for the scale module"""
    print("Running all scale module tests...")
    music21.mainTest(music21.scale)

def run_scale_tests_verbose():
    """Run scale tests with verbose output"""
    print("Running scale tests with verbose output...")
    music21.mainTest(music21.scale, 'verbose')

def run_scale_tests_no_doctest():
    """Run scale tests without doctests (faster for debugging)"""
    print("Running scale tests without doctests...")
    music21.mainTest(music21.scale, 'noDocTest')

def run_scale_doctests_only():
    """Run only scale doctests"""
    print("Running only scale doctests...")
    music21.mainTest(music21.scale, 'onlyDocTest')

def run_specific_scale_test():
    """Run a specific scale test class"""
    print("Running specific scale test class...")
    music21.mainTest(music21.scale.Test)

if __name__ == '__main__':
    # Default: run all tests
    # You can modify this to call different test functions
    run_all_scale_tests()
    
    # Uncomment any of these for different test modes:
    # run_scale_tests_verbose()
    # run_scale_tests_no_doctest()
    # run_scale_doctests_only()
    # run_specific_scale_test()