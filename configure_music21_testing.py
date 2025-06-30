#!/usr/bin/env python
"""Configure music19 environment for testing without external dependencies"""

from music19 import environment

def setup_testing_environment():
    """Configure music19 to skip tests requiring external software"""
    
    # Get the user environment
    us = environment.UserSettings()
    
    # Disable external software dependencies for testing
    # This tells music19 not to look for these programs
    us['lilypondPath'] = None
    us['musescoreDirectPNGPath'] = None
    us['graphicsPath'] = None
    
    print("Music19 environment configured for testing without external dependencies")
    print("External software tests will be skipped")

if __name__ == '__main__':
    setup_testing_environment()