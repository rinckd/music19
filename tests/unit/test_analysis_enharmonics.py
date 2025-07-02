# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.enharmonics import *


class Test(unittest.TestCase):


    def testGetAlterationScore(self):
        pList = [pitch.Pitch('C'), pitch.Pitch('D'), pitch.Pitch('E')]
        es = EnharmonicSimplifier(pList)
        poss = [pitch.Pitch('C'), pitch.Pitch('D'), pitch.Pitch('E')]
        testAltScore = es.getAlterationScore(poss)

        self.assertEqual(len(pList), 3)
        self.assertIsInstance(testAltScore, int)

    def testGetMixSharpFlatsScore(self):
        pList = [pitch.Pitch('C'), pitch.Pitch('D'), pitch.Pitch('E')]
        es = EnharmonicSimplifier(pList)
        poss = [pitch.Pitch('C'), pitch.Pitch('D'), pitch.Pitch('E')]
        testMixScore = es.getMixSharpFlatsScore(poss)

        self.assertEqual(len(pList), 3)
        self.assertIsInstance(testMixScore, int)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
