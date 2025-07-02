# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.dynamics import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testBasic(self):
        noDyn = Dynamic()
        assert noDyn.longName is None

        pp = Dynamic('pp')
        self.assertEqual(pp.value, 'pp')
        self.assertEqual(pp.longName, 'pianissimo')
        self.assertEqual(pp.englishName, 'very soft')

    def testCorpusDynamicsWedge(self):
        from music21 import corpus
        from music21 import dynamics

        a = corpus.parse('opus41no1/movement2')  # has dynamics!
        b = a.parts[0].flatten().getElementsByClass(dynamics.Dynamic)
        self.assertEqual(len(b), 35)

        b = a.parts[0].flatten().getElementsByClass(dynamics.DynamicWedge)
        self.assertEqual(len(b), 2)

    def testMusicxmlOutput(self):
        # test direct rendering of musicxml
        from music21.musicxml import m21ToXml
        d = Dynamic('p')
        xmlOut = m21ToXml.GeneralObjectExporter().parse(d).decode('utf-8')
        match = '<p />'
        self.assertNotEqual(xmlOut.find(match), -1, xmlOut)

    def testDynamicsPositionA(self):
        from music21 import stream
        from music21 import note
        s = stream.Stream()
        selections = ['pp', 'f', 'mf', 'fff']
        # positions = [-20, 0, 20]
        for i in range(10):
            d = Dynamic(selections[i % len(selections)])
            s.append(d)
            s.append(note.Note('c1'))
        # s.show()

    def testDynamicsPositionB(self):
        import random
        from music21 import stream
        from music21 import note
        from music21 import layout
        s = stream.Stream()
        for i in range(6):
            m = stream.Measure(number=i + 1)
            m.append(layout.SystemLayout(isNew=True))
            m.append(note.Rest(type='whole'))
            s.append(m)
        stream_iterator = s.getElementsByClass(stream.Measure)
        for m in stream_iterator:
            offsets = [x * 0.25 for x in range(16)]
            random.shuffle(offsets)
            offsets = offsets[:4]
            for o in offsets:
                d = Dynamic('mf')
                d.style.absoluteY = 20
                m.insert(o, d)
        # s.show()


class TestExternal(unittest.TestCase):
    show = True

    def testSingle(self):
        a = Dynamic('ffff')
        if self.show:
            a.show()

    def testBasic(self):
        '''
        present each dynamic in a single measure
        '''
        from music21 import stream
        a = stream.Stream()
        o = 0
        for dynStr in shortNames:
            b = Dynamic(dynStr)
            a.insert(o, b)
            o += 4  # increment
        if self.show:
            a.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
