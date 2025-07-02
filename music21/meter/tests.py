# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         meter.tests.py
# Purpose:      Tests of meter
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
from __future__ import annotations

import copy
import random
from music21 import common
from music21 import duration
from music21 import note
from music21 import stream
from music21.meter.base import TimeSignature
from music21.meter.core import MeterSequence, MeterTerminal
