# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         stream/tests.py
# Purpose:      Tests for streams
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

import copy
import os
import random
import music21
from music21.note import GeneralNote

from music21.stream.base import StreamException
from music21.stream.base import Stream
from music21.stream.base import Voice
from music21.stream.base import Measure
from music21.stream.base import Score
from music21.stream.base import Part
from music21.stream.base import Opus

from music21 import bar
from music21 import beam
from music21 import chord
from music21 import clef
from music21 import common
from music21 import converter
from music21 import corpus
from music21 import defaults
from music21 import duration
from music21 import dynamics
from music21 import environment
from music21 import expressions
from music21 import instrument
from music21 import interval
from music21 import layout
from music21 import key
from music21 import metadata
from music21 import meter
from music21 import note
from music21 import pitch
from music21 import sites
from music21 import spanner
from music21 import tempo
from music21 import text
from music21 import tie
from music21 import variant

from music21.base import Music21Exception, _SplitTuple

from music21.musicxml import m21ToXml

from music21.midi import translate as midiTranslate

environLocal = environment.Environment('stream.tests')

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    music21.mainTest(Test, 'verbose')
