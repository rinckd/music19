# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.tablature import *


class Test(unittest.TestCase):

    def testFretNoteString(self):
        f = FretNote(4, 1, 2)

        stringAndFretInfo = [f.string, f.fret]

        self.assertEqual(stringAndFretInfo, [4, 1])

    def testStupidFretNote(self):
        self.assertEqual(FretNote().string, None)

    def testFretNoteWeirdRepr(self):
        from music21 import tablature
        weirdFretNote = tablature.FretNote(6, 133)

        expectedRepr = '<music21.tablature.FretNote 6th string, 133rd fret>'

        self.assertEqual(repr(weirdFretNote), expectedRepr)

    def testFretBoardLowestFirst(self):
        fretNote1 = FretNote(1, 2, 2)
        fretNote2 = FretNote(2, 1, 1)

        myFretBoard = FretBoard(6, fretNotes=[fretNote1, fretNote2])

        stringList = []

        for thisNote in myFretBoard.fretNotesLowestFirst():
            stringList.append(thisNote.string)

        self.assertEqual(stringList, [2, 1])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
