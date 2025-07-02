# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.serial import *


class Test(unittest.TestCase):

    def testMatrix(self):
        src = getHistoricalRowByName('SchoenbergOp37')
        self.assertEqual([p.name for p in src],
                         ['D', 'C#', 'A', 'B-', 'F', 'E-', 'E', 'C', 'G#', 'G', 'F#', 'B'])
        s37 = getHistoricalRowByName('SchoenbergOp37').matrix()
        r0 = s37[0]
        self.assertEqual([e.name for e in r0],
                         ['C', 'B', 'G', 'G#', 'E-', 'C#', 'D', 'B-', 'F#', 'F', 'E', 'A'])

    def testLabelingA(self):
        from music21 import corpus
        series = {'a': 1, 'g-': 2, 'g': 3, 'a-': 4,
                  'f': 5, 'e-': 6, 'e': 7, 'd': 8,
                  'c': 9, 'c#': 10, 'b-': 11, 'b': 12}
        s = corpus.parse('bwv66.6')
        for n in s.flatten().notes:
            for key in series:
                if n.pitch.pitchClass == pitch.Pitch(key).pitchClass:
                    n.addLyric(series[key])
        match = []
        for n in s.parts[0].flatten().notes:
            match.append(n.lyric)
        self.assertEqual(match, ['10', '12', '1', '12', '10', '7', '10', '12', '1', '10', '1',
                                 '12', '4', '2', '1', '12', '12', '2', '7', '1', '12', '10',
                                 '10', '1', '12', '10', '1', '4', '2', '4', '2', '2', '2',
                                 '2', '2', '5', '2'])
        # s.show()

    def testHistorical(self):
        nonRows = []
        for historicalRow in historicalDict:
            if getHistoricalRowByName(historicalRow).isTwelveToneRow() is False:
                nonRows.append(historicalRow)
        self.assertEqual(nonRows, [])

    def testExtractRowParts(self):
        '''
        Was a problem in slices
        '''
        aRow = getHistoricalRowByName('BergViolinConcerto')
        unused_aRow2 = aRow[0:3]

    def testPostTonalDocs(self):
        aRow = getHistoricalRowByName('BergViolinConcerto')
        # aMatrix = aRow.matrix()
        bStream = stream.Stream()
        for i in range(0, 12, 3):
            aRow2 = aRow[i:i + 3]
            c = chord.Chord(aRow2)
            c.addLyric(c.primeFormString)
            c.addLyric(c.forteClass)
            bStream.append(c)

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())


    # def testRows(self):
    #     from music21 import interval
    #
    #     self.assertEqual(len(vienneseRows), 71)
    #
    #     totalRows = 0
    #     cRows = 0
    #     for thisRow in vienneseRows:
    #         thisRow = thisRow()
    #         self.assertIsInstance(thisRow, TwelveToneRow)
    #
    #         if thisRow.composer == 'Berg':
    #             continue
    #         post = thisRow.title
    #
    #         totalRows += 1
    #         if thisRow[0].pitchClass == 0:
    #             cRows += 1
    #
    #          if interval.Interval(thisRow[0],
    #                               thisRow[6]).intervalClass == 6:
    #           # between element 1 and element 7 is there a TriTone?
    #           rowsWithTTRelations += 1


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
