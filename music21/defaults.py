# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         defaults.py
# Purpose:      Storage for user environment settings and defaults
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-2010 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Simple storage for data defaults used throughout music21.
'''
from __future__ import annotations

import typing as t
from music21 import _version

# note: this module should not import any higher level modules
StepName = t.Literal['C', 'D', 'E', 'F', 'G', 'A', 'B']  # restating so as not to import.

# TODO: defaults should check the environment object to see
#     if there are any preferences set for values used here

# ------------------------------------------------------------------------------
title = 'Music21 Fragment'
author = 'Music21'
software = 'music21 v.' + _version.__version__  # used in xml encoding source software
musicxmlVersion = '4.0'

meterNumerator = 4
meterDenominator = 'quarter'
meterDenominatorBeatType = 4  # musicxml representation

limitOffsetDenominator = 65535  # > CD track level precision.
# allows for tuples up to n:x within m:y within l:z within k:w where x,y,z <=100 and w<=44
# not allowing more can be construed as a feature.

pitchStep: StepName = 'C'
pitchOctave = 4

partGroup = 'Part Group'
partGroupAbbreviation = 'PG'

durationType = 'quarter'

instrumentName: str = ''
partName: str = ''

keyFifths = 0
keyMode = 'major'

clefSign = 'G'
clefLine = 2

# define a default notehead for notes that know they are unpitched
noteheadUnpitched = 'square'
'''
Divisions are a MusicXML concept that music21 does not share
It basically represents the lowest time unit that all other notes
are integer multiples of.  Useful for compatibility with MIDI, but
ultimately restricting since it must be less than 16384, so thus
cannot accurately reflect a piece which uses 64th notes, triplets,
quintuplets, septuplets, 11-tuplets, and 13-tuplets in the same piece
I have chosen a useful base that allows for perfect representation of
128th notes, triplets within triplets, quintuplets, and septuplets
within the piece.  Other tuplets (11, etc.) will be close enough for
most perceptual uses (11:1 will be off by 4 parts per thousand) but
will cause measures to be incompletely filled, etc.  If this gets to
be a problem, music21 could be modified to keep track of "rounding errors"
and make sure that for instance half the notes of an 11:1 are 916 divisions
long and the other half are 917.  But this has not been done yet.
'''
divisionsPerQuarter = 32 * 3 * 3 * 5 * 7  # 10080

# ticks per quarter is used for midi - left separate for flexibility in the future.
ticksPerQuarter = divisionsPerQuarter
# how many ticks to pad as a rest at the beginning of a MIDI file.
# also used to pad the end, one quarter note.
ticksAtStart = ticksPerQuarter

# quantizationQuarterLengthDivisors
# what to snap MIDI quantization to.  (4, 3) indicates sixteenth notes and triplets.

quantizationQuarterLengthDivisors = (4, 3)

# scaling -- the size of notes in musicxml -- 40 tenths = a 5-line staff
# so how many millimeters = a staff?
scalingMillimeters = 7
scalingTenths = 40

jupyterImageDpi = 200  # retina quality (can go higher soon?)

# multi-measure rests
multiMeasureRestUseSymbols = True
multiMeasureRestMaxSymbols = 11

# id numbers above this number will be considered memory locations
# and rewritten on thaw, etc.
minIdNumberToConsiderMemoryLocation = 100_000_001

# abc files without any version information parse as this version
abcVersionDefault = (1, 3, 0)

# ----------------------------------------------------------------||||||||||||--
