# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.correlate import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testActivityMatchPitchToDynamic(self):
        from music21 import corpus

        a = corpus.parse('schoenberg/opus19', 2)

        b = ActivityMatch(a.flatten())
        dataPairs = b.pitchToDynamic()
        # print(dataPairs)
        # previous pair count was 401
        self.assertEqual(len(dataPairs), 111)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
