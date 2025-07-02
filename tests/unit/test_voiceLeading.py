# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.voiceLeading import *


class Test(unittest.TestCase):

    def testInstantiateEmptyObject(self):
        '''
        test instantiating an empty VoiceLeadingQuartet
        '''
        VoiceLeadingQuartet()

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def test_unifiedTest(self):
        c4 = note.Note('C4')
        d4 = note.Note('D4')
        e4 = note.Note('E4')
        # f4 = note.Note('F4')
        g4 = note.Note('G4')
        a4 = note.Note('A4')
        # b4 = note.Note('B4')
        c5 = note.Note('C5')
        # d5 = note.Note('D5')

        a = VoiceLeadingQuartet(c4, d4, g4, a4)
        assert a.similarMotion() is True
        assert a.parallelMotion() is True
        assert a.antiParallelMotion() is False
        assert a.obliqueMotion() is False
        assert a.parallelInterval(interval.Interval('P5')) is True
        assert a.parallelInterval(interval.Interval('M3')) is False

        b = VoiceLeadingQuartet(c4, c4, g4, g4)
        assert b.noMotion() is True
        assert b.parallelMotion() is False
        assert b.antiParallelMotion() is False
        assert b.obliqueMotion() is False

        c = VoiceLeadingQuartet(c4, g4, c5, g4)
        assert c.antiParallelMotion() is True
        assert c.hiddenInterval(interval.Interval('P5')) is False

        d = VoiceLeadingQuartet(c4, d4, e4, a4)
        assert d.hiddenInterval(interval.Interval('P5')) is True
        assert d.hiddenInterval(interval.Interval('A4')) is False
        assert d.hiddenInterval(interval.Interval('AA4')) is False


class TestExternal(unittest.TestCase):
    pass


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
