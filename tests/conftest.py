# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         tests/conftest.py
# Purpose:      PyCharm/pytest configuration for music21 tests
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
PyCharm/pytest configuration for music21 tests.

This file configures test discovery and setup for running music21 tests
in PyCharm, Rider, or with pytest.
"""
import sys
import os
from pathlib import Path

# Add music21 to Python path if not already there
music21_root = Path(__file__).parent.parent
if str(music21_root) not in sys.path:
    sys.path.insert(0, str(music21_root))

import pytest

# Import music21 to ensure proper initialization
import music21

@pytest.fixture(scope="session", autouse=True)
def setup_music21_environment():
    """
    Setup music21 environment for testing.
    This fixture runs once per test session.
    """
    # Ensure music21 is properly initialized
    # Add any global test setup here
    pass

@pytest.fixture
def clean_environment():
    """
    Provide a clean music21 environment for each test.
    """
    # Add any per-test setup/cleanup here
    yield
    # Cleanup after test if needed

# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "external: mark test as external/integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )

# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location."""
    for item in items:
        # Mark external tests
        if "external" in str(item.fspath):
            item.add_marker(pytest.mark.external)
        
        # Mark integration tests  
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.external)
            item.add_marker(pytest.mark.slow)