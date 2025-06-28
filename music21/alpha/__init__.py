# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         alpha/__init__.py
# Purpose:      music21 modules not fully ready for prime-time
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
  Alpha Module - Experimental/Incomplete Features

  The alpha folder contains experimental, incomplete, or specialized features that aren't ready for the main music21 system.

  Purpose (from the documentation):

  - Experimental features not fully developed or ready for prime time
  - Useful for some things but not core functionality
  - May require obscure external libraries not in the standard music21 feature set
  - Prevents the main system from feeling bloated with half-finished features

  What's inside:

  alpha/analysis/ - Advanced Analysis Tools:

  1. aligner.py - Stream alignment algorithms
    - Aligns two musical streams/scores
    - Uses change operations (insertion, deletion, substitution)
    - Useful for comparing different versions of the same piece
  2. search.py - Musical pattern searching
    - Tools for finding scale patterns in music
    - Functions like findConsecutiveScale() to locate scale passages
  3. hasher.py - Music hashing algorithms
    - Creates fingerprints/hashes of musical content
    - Used by the aligner for comparison
  4. fixer.py - Score correction tools
    - Attempts to fix problems in musical scores
  5. ornamentRecognizer.py - Ornament detection
    - Identifies musical ornaments (trills, turns, etc.)
  6. testFiles.py - Test data for alpha features

  Future of Alpha Features:

  - Some may "graduate" to main music21
  - Some may be moved to music21-demos repository
  - Some may stay in alpha indefinitely
  - Some may be removed entirely
'''
from __future__ import annotations

__all__ = [
    # dirs
    'analysis',

    # files
]

from music21.alpha import analysis


