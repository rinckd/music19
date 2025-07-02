# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph.axis import *


class Test(unittest.TestCase):

    def testCountingAxisFormat(self):
        def countingAxisFormatter(n, formatDict):
            if n.pitch.accidental is not None:
                formatDict['color'] = 'red'
            return n.pitch.diatonicNoteNum

        from music21.graph.plot import Histogram
        from music21 import converter
        s = converter.parse('tinynotation: 4/4 C4 D E F C D# E F#')
        hist = Histogram(s)
        hist.doneAction = None
        hist.axisX = Axis(hist, 'x')
        hist.axisX.extractOneElement = countingAxisFormatter
        hist.run()
        self.assertEqual(hist.data,
                         [(1, 2, {}), (2, 2, {'color': 'red'}),
                          (3, 2, {}), (4, 2, {'color': 'red'})])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
