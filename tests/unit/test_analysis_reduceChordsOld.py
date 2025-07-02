# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.reduceChordsOld import *


class Test(unittest.TestCase):

    def testSimpleMeasure(self):
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
        # c = corpus.parse('beethoven/opus18no1', 2).measures(1, 19)


        c = corpus.parse('PMFC_06_Giovanni-05_Donna').measures(1, 30)
        # c = corpus.parse('PMFC_06_Giovanni-05_Donna').measures(90, 118)
        # c = corpus.parse('PMFC_06_Piero_1').measures(1, 10)
        # c = corpus.parse('PMFC_06-Jacopo').measures(1, 30)

        # c = corpus.parse('PMFC_12_13').measures(1, 40)

        # fix clef
        fixClef = True
        if fixClef:
            startClefs = c.parts[1].getElementsByClass(stream.Measure
                                                       ).first().getElementsByClass(clef.Clef)
            if startClefs:
                clef1 = startClefs[0]
                c.parts[1].getElementsByClass(stream.Measure).first().remove(clef1)
            c.parts[1].getElementsByClass(stream.Measure).first().insert(0, clef.Treble8vbClef())


        cr = ChordReducer()
        # cr.printDebug = True
        p = cr.multiPartReduction(c, maxChords=3)
        # p = cr.multiPartReduction(c, closedPosition=True)
        from music21 import key
        from music21 import roman
        cm = key.Key('G')
        for thisChord in p[chord.Chord]:
            thisChord.lyric = roman.romanNumeralFromChord(thisChord,
                                                          cm,
                                                          preferSecondaryDominants=True).figure


        c.insert(0, p)
        if self.show:
            c.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
