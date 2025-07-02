# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.metrical import *


class Test(unittest.TestCase):
    pass


class TestExternal(unittest.TestCase):
    show = True

    def testSingle(self):
        '''
        Need to test direct meter creation w/o stream
        '''
        from music21 import note
        from music21 import meter
        s = stream.Stream()
        ts = meter.TimeSignature('4/4')

        s.append(ts)
        n = note.Note()
        n.quarterLength = 1
        s.repeatAppend(n, 4)

        n = note.Note()
        n.quarterLength = 0.5
        s.repeatAppend(n, 8)

        s = s.makeMeasures()
        s = labelBeatDepth(s)

        if self.show:
            s.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
