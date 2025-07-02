# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.reduceChords import *


class Test(unittest.TestCase):

    def testSimpleMeasure(self):
        # from music21 import chord
        s = stream.Measure()
        c1 = chord.Chord('C4 E4 G4 C5')
        c1.quarterLength = 2.0
        c2 = chord.Chord('C4 E4 F4 B4')
        c3 = chord.Chord('C4 E4 G4 C5')
        for c in [c1, c2, c3]:
            s.append(c)


class TestExternal(unittest.TestCase):
    show = True

    def testTrecentoMadrigal(self):
        from music21 import corpus

        score = corpus.parse('PMFC_06_Giovanni-05_Donna').measures(1, 10)
        # score = corpus.parse('bach/bwv846').measures(1, 19)
        # score = corpus.parse('bach/bwv66.6')
        # score = corpus.parse('beethoven/opus18no1', 2).measures(1, 30)
        # score = corpus.parse('beethoven/opus18no1', 2).measures(1, 8)
        # score = corpus.parse('PMFC_06_Giovanni-05_Donna').measures(90, 118)
        # score = corpus.parse('PMFC_06_Piero_1').measures(1, 10)
        # score = corpus.parse('PMFC_06-Jacopo').measures(1, 30)
        # score = corpus.parse('PMFC_12_13').measures(1, 40)
        # score = corpus.parse('monteverdi/madrigal.4.16.xml').measures(1, 8)

        chordReducer = ChordReducer()
        reduction = chordReducer.run(
            score,
            allowableChords=(
                chord.Chord('F#4 A4 C5'),
            ),
            closedPosition=True,
            forbiddenChords=None,
            maximumNumberOfChords=3,
        )

        for part in reduction:
            score.insert(0, part)

        if self.show:
            score.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
