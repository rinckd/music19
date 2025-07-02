# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.transposition import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testConstructTranspositionChecker(self):
        p = [pitch.Pitch('D#')]
        tc = TranspositionChecker(p)

        self.assertEqual(tc.pitches, p)
        numberOfPitchesInTc = len(tc.pitches)
        self.assertEqual(numberOfPitchesInTc, len(p))

    def testTranspositions(self):
        p = [pitch.Pitch('D#')]
        tc = TranspositionChecker(p)
        allTranspositions = tc.getTranspositions()

        self.assertEqual(len(allTranspositions), 12)
        self.assertIsInstance(allTranspositions[0][0], pitch.Pitch)
        self.assertEqual(allTranspositions[0][0].midi, p[0].midi)
        self.assertEqual(allTranspositions[1][0].midi, p[0].midi + 1)

        p = [pitch.Pitch('D#'), pitch.Pitch('F')]
        tc = TranspositionChecker(p)
        allTranspositions = tc.getTranspositions()

        self.assertEqual(len(allTranspositions), 12)
        self.assertIsInstance(allTranspositions[0][0], pitch.Pitch)
        self.assertEqual(allTranspositions[0][0].midi, p[0].midi)
        self.assertEqual(allTranspositions[0][1].midi, p[1].midi)

    def testNormalOrders(self):
        pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        tc = TranspositionChecker(pList)
        normalOrders = tc.listNormalOrders()

        self.assertEqual(len(normalOrders), 12)
        self.assertLess(normalOrders[0][0], 13)

    def testDistinctNormalOrders(self):
        pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        tc = TranspositionChecker(pList)
        allDistinctNormalOrders = tc.listDistinctNormalOrders()

        lengthDistinctNormalOrders = tc.numDistinctTranspositions()

        self.assertEqual(len(allDistinctNormalOrders), 4)
        self.assertEqual(lengthDistinctNormalOrders, 4)
        self.assertIsInstance(allDistinctNormalOrders, list)
        self.assertEqual(allDistinctNormalOrders[0], [0, 4, 8])

    def testNormalOrderChords(self):
        pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        tc = TranspositionChecker(pList)

        allNormalOrderChords = tc.getChordsOfDistinctTranspositions()

        self.assertEqual(len(allNormalOrderChords), 4)
        # self.assertEqual(lengthDistinctNormalOrders, 4)
        self.assertIsInstance(allNormalOrderChords[0], chord.Chord)
        self.assertIsInstance(allNormalOrderChords[0].pitches[0], pitch.Pitch)
        # self.assertEqual(allDistinctNormalOrders[0], [0,4,8])

    def testNormalOrdersPitches(self):
        pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        tc = TranspositionChecker(pList)

        allNormalOrderPitchTuples = tc.getPitchesOfDistinctTranspositions()

        self.assertEqual(len(allNormalOrderPitchTuples), 4)
        # self.assertEqual(lengthDistinctNormalOrders, 4)
        self.assertIsInstance(allNormalOrderPitchTuples[0], tuple)
        self.assertIsInstance(allNormalOrderPitchTuples[0][0], pitch.Pitch)
        # self.assertEqual(allDistinctNormalOrders[0], [0,4,8])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
