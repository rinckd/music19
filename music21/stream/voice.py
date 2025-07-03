# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/voice.py
# Purpose:      Voice class extracted from stream/base.py
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#               Josiah Wolf Oberholtzer
#               Evan Lynch
#
# Copyright:    Copyright © 2008-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
Voice class for music21 streams.

Extracted from stream/base.py as part of Phase 2 dependency reduction.
'''
from __future__ import annotations

import typing as t

from music21.stream.enums import RecursionType

# PHASE 2 NOTE: This creates a circular import (voice.py -> base.py -> voice.py)
# This will be resolved in Phase 3 through dependency injection/factory patterns
# For now, we accept this circular import to maintain functionality
from music21.stream.base import Stream


class Voice(Stream):
    '''
    A Stream subclass for declaring that all the music in the
    stream belongs to a certain "voice" for analysis or display
    purposes.

    Note that both Finale's Layers and Voices as concepts are
    considered Voices here.

    Voices have a sort order of 1 greater than time signatures
    '''
    recursionType = RecursionType.ELEMENTS_FIRST
    classSortOrder = 5

    # define order for presenting names in documentation; use strings
    _DOC_ORDER = ['Voice']