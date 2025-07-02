# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph.findPlot import *


class Test(unittest.TestCase):
    def testGetPlotsToMakeA(self):
        post = getPlotsToMake('ambitus')
        self.assertEqual(post, [plot.WindowedAmbitus])
        post = getPlotsToMake('key')
        self.assertEqual(post, [plot.WindowedKey])

        # no args get pitch space piano roll
        post = getPlotsToMake()
        self.assertEqual(post, [plot.HorizontalBarPitchSpaceOffset])

        # one arg gives a histogram of that parameters
        post = getPlotsToMake('duration')
        self.assertEqual(post, [plot.HistogramQuarterLength])
        post = getPlotsToMake('quarterLength')
        self.assertEqual(post, [plot.HistogramQuarterLength])
        post = getPlotsToMake('ps')
        self.assertEqual(post, [plot.HistogramPitchSpace])
        post = getPlotsToMake('pitch')
        self.assertEqual(post, [plot.HistogramPitchSpace])
        post = getPlotsToMake('pitchspace')
        self.assertEqual(post, [plot.HistogramPitchSpace])
        post = getPlotsToMake('pitchClass')
        self.assertEqual(post, [plot.HistogramPitchClass])

        post = getPlotsToMake('scatter', 'pitch', 'ql')
        self.assertEqual(post, [plot.ScatterPitchSpaceQuarterLength])

        post = getPlotsToMake('scatter', 'pc', 'offset')
        self.assertEqual(post, [plot.ScatterPitchClassOffset])

    def testGetPlotsToMakeB(self):
        post = getPlotsToMake('dolan')
        self.assertEqual(post, [plot.Dolan])
        post = getPlotsToMake('instruments')
        self.assertEqual(post, [plot.Dolan])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
