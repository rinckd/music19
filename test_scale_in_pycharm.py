#!/usr/bin/env python
"""Run scale module tests in PyCharm using music19's test runner"""

import music19

def run_all_scale_tests():
    """Run all tests for the scale module"""
    print("Running all scale module tests...")
    music19.mainTest(music19.scale)

def run_scale_tests_verbose():
    """Run scale tests with verbose output"""
    print("Running scale tests with verbose output...")
    music19.mainTest(music19.scale, 'verbose')

def run_scale_tests_no_doctest():
    """Run scale tests without doctests (faster for debugging)"""
    print("Running scale tests without doctests...")
    music19.mainTest(music19.scale, 'noDocTest')

def run_scale_doctests_only():
    """Run only scale doctests"""
    print("Running only scale doctests...")
    music19.mainTest(music19.scale, 'onlyDocTest')

def run_specific_scale_test():
    """Run a specific scale test class"""
    print("Running specific scale test class...")
    music19.mainTest(music19.scale.Test)

if __name__ == '__main__':
    # Default: run all tests
    # You can modify this to call different test functions
    run_all_scale_tests()
    
    # Uncomment any of these for different test modes:
    # run_scale_tests_verbose()
    # run_scale_tests_no_doctest()
    # run_scale_doctests_only()
    # run_specific_scale_test()