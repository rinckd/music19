# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.common.numberTools import *


class Test(unittest.TestCase):
    '''
    Tests not requiring file output.
    '''

    def setUp(self):
        pass

    def testToRoman(self):
        for src, dst in [(1, 'I'), (3, 'III'), (5, 'V')]:
            self.assertEqual(dst, toRoman(src))

    def testOrdinalsToNumbers(self):
        self.assertEqual(ordinalsToNumbers['unison'], 1)
        self.assertEqual(ordinalsToNumbers['Unison'], 1)
        self.assertEqual(ordinalsToNumbers['first'], 1)
        self.assertEqual(ordinalsToNumbers['First'], 1)
        self.assertEqual(ordinalsToNumbers['1st'], 1)
        self.assertEqual(ordinalsToNumbers['octave'], 8)
        self.assertEqual(ordinalsToNumbers['Octave'], 8)
        self.assertEqual(ordinalsToNumbers['eighth'], 8)
        self.assertEqual(ordinalsToNumbers['Eighth'], 8)
        self.assertEqual(ordinalsToNumbers['8th'], 8)

    def testWeightedSelection(self):
        # test equal selection
        for j in range(10):
            x = 0
            for i in range(1000):
                # equal chance of -1, 1
                x += weightedSelection([-1, 1], [1, 1])
            # environLocal.printDebug(['weightedSelection([-1, 1], [1, 1])', x])
            self.assertTrue(-250 < x < 250)

        # test a strongly weighed boundary
        for j in range(10):
            x = 0
            for i in range(1000):
                # 10000 more chance of 0 than 1.
                x += weightedSelection([0, 1], [10000, 1])
            # environLocal.printDebug(['weightedSelection([0, 1], [10000, 1])', x])
            self.assertTrue(0 <= x < 20)

        for j in range(10):
            x = 0
            for i in range(1000):
                # 10,000 times more likely 1 than 0.
                x += weightedSelection([0, 1], [1, 10000])
            # environLocal.printDebug(['weightedSelection([0, 1], [1, 10000])', x])
            self.assertTrue(900 <= x <= 1000)

        for unused_j in range(10):
            x = 0
            for i in range(1000):
                # no chance of anything but 0.
                x += weightedSelection([0, 1], [1, 0])
            # environLocal.printDebug(['weightedSelection([0, 1], [1, 0])', x])
            self.assertEqual(x, 0)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
