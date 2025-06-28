#!/usr/bin/env python
"""Verify we're using the local music21, not a pip-installed version"""

import sys
import os

# Add the current directory to Python path (if not already there)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and check
import music21

print(f"Python executable: {sys.executable}")
print(f"music21 location: {music21.__file__}")
print(f"music21 version: {music21.__version__}")
print(f"Is local repo: {current_dir in music21.__file__}")

# You can also check if editable install exists
try:
    import importlib.metadata
    dist = importlib.metadata.distribution('music21')
    print(f"\nInstalled via pip: {dist.version}")
    print(f"Installation location: {dist.locate_file('')}")
except importlib.metadata.PackageNotFoundError:
    print("\nNo pip-installed music21 found (good - using local only)")