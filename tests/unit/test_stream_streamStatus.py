# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.stream.streamStatus import *


class Test(unittest.TestCase):
    '''
    Note: most Stream tests are found in stream.tests
    '''

    def testHaveBeamsBeenMadeAfterDeepcopy(self):
        import copy
        from music21 import stream
        from music21 import note
        m = stream.Measure()
        c = note.Note('C4', type='quarter')
        m.append(c)
        d1 = note.Note('D4', type='eighth')
        d2 = note.Note('D4', type='eighth')
        m.append([d1, d2])
        e3 = note.Note('E4', type='eighth')
        e4 = note.Note('E4', type='eighth')
        m.append([e3, e4])
        d1.beams.append('start')
        d2.beams.append('stop')
        self.assertTrue(m.streamStatus.haveBeamsBeenMade())
        mm = copy.deepcopy(m)
        self.assertTrue(mm.streamStatus.haveBeamsBeenMade())
        mm.streamStatus.beams = False
        mmm = copy.deepcopy(mm)
        self.assertFalse(mmm.streamStatus.beams)
        # m.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
