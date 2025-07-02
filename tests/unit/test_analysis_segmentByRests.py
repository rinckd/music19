# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.segmentByRests import *


class Test(unittest.TestCase):

    def testGetSegmentsList(self):
        ex = converter.parse('tinyNotation: E4 r F G A r g c r c')
        segments = Segmenter.getSegmentsList(ex)

        self.assertIsInstance(segments[0], list)
        self.assertEqual(segments[1][0].name, 'F')

    def testGetIntervalList(self):
        ex = converter.parse('tinyNotation: E4 r F G A r g c r c')
        intervalList = Segmenter.getIntervalList(ex)

        self.assertEqual(intervalList[0].name, 'M2')
        self.assertIsInstance(intervalList, list)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
