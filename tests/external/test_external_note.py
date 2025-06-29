# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         tests/external/test_external_note.py
# Purpose:      External tests for music21.note
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
External tests for music21.note module.

These are tests that open windows and rely on external software.
Extracted from embedded TestExternal classes.
"""
from __future__ import annotations

import unittest

from music21 import note
from music21 import stream


class TestExternalNote(unittest.TestCase):
    """
    External tests for music21.note module.
    These are tests that open windows and rely on external software.
    """
    show = False  # Set to True for manual testing with external software

    def testSingle(self):
        """
        Need to test direct note creation w/o stream
        """
        a = note.Note('D-3')
        a.quarterLength = 2.25
        if self.show:
            a.show()

    def testBasic(self):
        """Test basic note display functionality."""
        a = stream.Stream()

        for pitchName, qLen in [('d-3', 2.5), ('c#6', 3.25), ('a--5', 0.5),
                                ('f', 1.75), ('g3', 1.5), ('d##4', 1.25),
                                ('d-3', 2.5), ('c#6', 3.25), ('a--5', 0.5),
                                ('f#2', 1.75), ('g-3', (4 / 3)), ('d#6', (2 / 3))
                                ]:
            b = note.Note()
            b.quarterLength = qLen
            b.name = pitchName
            # Pylint going crazy here
            b.style.color = '#FF00FF'  # pylint: disable=attribute-defined-outside-init
            a.append(b)

        if self.show:
            a.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(TestExternalNote)