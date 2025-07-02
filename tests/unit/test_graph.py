# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testAll(self):
        from music21 import corpus
        a = corpus.parse('bach/bwv57.8')
        plotStream(a.flatten(), doneAction=None)

    def testPlotChordsC(self):
        from music21 import dynamics
        from music21 import note
        from music21 import stream
        from music21 import scale

        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(dynamics.Dynamic('f'))
        s.append(note.Note('c4'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(dynamics.Dynamic('mf'))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(dynamics.Dynamic('pp'))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(note.Note('c5', quarterLength=3))

        for plotType, xValue, yValue in [
            ('histogram', 'pitch', None),
            ('histogram', 'pitchclass', None),
            ('histogram', 'quarterlength', None),
            ('scatter', 'pitch', 'quarterlength'),
            ('scatter', 'pitchspace', 'offset'),
            ('scatter', 'pitch', 'offset'),
            ('scatter', 'dynamics', None),
            ('bar', 'pitch', None),
            ('bar', 'pc', None),
            ('weighted', 'pc', 'duration'),
            ('weighted', 'dynamics', None),
        ]:
            s.plot(plotType, xValue=xValue, yValue=yValue, doneAction=None)

    def testHorizontalInstrumentationB(self):
        from music21 import corpus
        from music21 import dynamics
        from music21 import stream
        s = corpus.parse('bwv66.6')
        dyn = ['p', 'mf', 'f', 'ff', 'mp', 'fff', 'ppp']
        i = 0
        for p in s.parts:
            for m in p.getElementsByClass(stream.Measure):
                m.insert(0, dynamics.Dynamic(dyn[i % len(dyn)]))
                i += 1
        s.plot('dolan', fillByMeasure=True, segmentByTarget=True, doneAction=None)


class TestExternal(unittest.TestCase):
    show = True

    def testAll(self):
        from music21 import corpus
        from music21 import dynamics
        a = corpus.parse('bach/bwv57.8')
        a.parts[0].insert(0, dynamics.Dynamic('mf'))
        a.parts[0].insert(10, dynamics.Dynamic('f'))
        if self.show:
            plotStream(a, 'all', doneAction=None)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
