#!/usr/bin/env python
"""Configure music21 environment for testing without external dependencies"""

from music21 import environment

def setup_testing_environment():
    """Configure music21 to skip tests requiring external software"""
    
    # Get the user environment
    us = environment.UserSettings()
    
    # Disable external software dependencies for testing
    # This tells music21 not to look for these programs
    us['lilypondPath'] = None
    us['musescoreDirectPNGPath'] = None
    us['graphicsPath'] = None
    
    print("Music21 environment configured for testing without external dependencies")
    print("External software tests will be skipped")

if __name__ == '__main__':
    setup_testing_environment()