# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.volume import *


class Test(unittest.TestCase):

    def testBasic(self):
        import gc
        from music21 import volume

        n1 = note.Note('G#4')
        v = volume.Volume(client=n1)
        self.assertEqual(v.client, n1)
        del n1
        gc.collect()
        # Now client is still there -- no longer weakref
        self.assertEqual(v.client, note.Note('G#4'))


    def testGetContextSearchA(self):
        from music21 import stream
        from music21 import volume

        s = stream.Stream()
        d1 = dynamics.Dynamic('mf')
        s.insert(0, d1)
        d2 = dynamics.Dynamic('f')
        s.insert(2, d2)

        n1 = note.Note('g')
        v1 = volume.Volume(client=n1)
        s.insert(4, n1)

        # can get dynamics from volume object
        self.assertEqual(v1.client.getContextByClass('Dynamic'), d2)
        self.assertEqual(v1.getDynamicContext(), d2)


    def testGetContextSearchB(self):
        from music21 import stream

        s = stream.Stream()
        d1 = dynamics.Dynamic('mf')
        s.insert(0, d1)
        d2 = dynamics.Dynamic('f')
        s.insert(2, d2)

        n1 = note.Note('g')
        s.insert(4, n1)

        # can get dynamics from volume object
        self.assertEqual(n1.volume.getDynamicContext(), d2)


    def testDeepCopyA(self):
        import copy
        from music21 import volume
        n1 = note.Note()

        v1 = volume.Volume()
        v1.velocity = 111
        v1.client = n1

        v1Copy = copy.deepcopy(v1)
        self.assertEqual(v1.velocity, 111)
        self.assertEqual(v1Copy.velocity, 111)

        self.assertEqual(v1.client, n1)
        self.assertEqual(v1Copy.client, n1)


    def testGetRealizedA(self):
        from music21 import volume

        v1 = volume.Volume(velocity=64)
        self.assertEqual(v1.getRealizedStr(), '0.5')

        d1 = dynamics.Dynamic('p')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.35')

        d1 = dynamics.Dynamic('ppp')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.15')


        d1 = dynamics.Dynamic('fff')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.91')


        # if vel is at max, can scale down with a dynamic
        v1 = volume.Volume(velocity=127)
        d1 = dynamics.Dynamic('fff')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '1.0')

        d1 = dynamics.Dynamic('ppp')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.3')
        d1 = dynamics.Dynamic('mp')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.9')
        d1 = dynamics.Dynamic('p')
        self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.7')


    def testGetRealizedB(self):
        v1 = Volume(velocity=64)
        self.assertEqual(v1.getRealizedStr(), '0.5')

        a1 = articulations.StrongAccent()
        self.assertEqual(v1.getRealizedStr(useArticulations=a1), '0.65')

        a2 = articulations.Accent()
        self.assertEqual(v1.getRealizedStr(useArticulations=a2), '0.6')

        # d1 = dynamics.Dynamic('ppp')
        # self.assertEqual(v1.getRealizedStr(useDynamicContext=d1), '0.1')





    def testRealizeVolumeA(self):
        from music21 import stream
        from music21 import volume

        s = stream.Stream()
        s.repeatAppend(note.Note('g3'), 16)

        # before insertion of dynamics
        match = [n.volume.cachedRealizedStr for n in s.notes]
        self.assertEqual(match, ['0.71'] * 16)

        for i, d in enumerate(['pp', 'p', 'mp', 'f', 'mf', 'ff', 'ppp', 'mf']):
            s.insert(i * 2, dynamics.Dynamic(d))

        # cached will be out of date in regard to new dynamics
        match = [n.volume.cachedRealizedStr for n in s.notes]
        self.assertEqual(match, ['0.71'] * 16)

        # calling realize will set all to new cached values
        volume.realizeVolume(s)
        match = [n.volume.cachedRealizedStr for n in s.notes]
        self.assertEqual(match, ['0.35', '0.35', '0.5', '0.5',
                                 '0.64', '0.64', '0.99', '0.99',
                                 '0.78', '0.78', '1.0', '1.0',
                                 '0.21', '0.21', '0.78', '0.78'])

        # we can get the same results without using realizeVolume, though
        # this uses slower context searches
        s = stream.Stream()
        s.repeatAppend(note.Note('g3'), 16)

        for i, d in enumerate(['pp', 'p', 'mp', 'f', 'mf', 'ff', 'ppp', 'mf']):
            s.insert(i * 2, dynamics.Dynamic(d))
        match = [n.volume.cachedRealizedStr for n in s.notes]
        self.assertEqual(match, ['0.35', '0.35',
                                 '0.5', '0.5',
                                 '0.64', '0.64',
                                 '0.99', '0.99',
                                 '0.78', '0.78',
                                 '1.0', '1.0',
                                 '0.21', '0.21',
                                 '0.78', '0.78'])

        # looking at raw velocity values
        match = [n.volume.velocity for n in s.notes]
        self.assertEqual(match, [None] * 16)

        # can set velocity with realized values
        volume.realizeVolume(s, setAbsoluteVelocity=True)
        match = [n.volume.velocity for n in s.notes]
        self.assertEqual(match, [45, 45, 63, 63, 81, 81, 126, 126, 99, 99,
                                 127, 127, 27, 27, 99, 99])

        # s.show('midi')

    def testRealizeVolumeB(self):
        from music21 import corpus
        from music21 import stream

        s = corpus.parse('bwv66.6')

        durUnit = s.highestTime // 8  # let floor
        dyns = ['pp', 'p', 'mp', 'f', 'mf', 'ff', 'f', 'mf']

        for i, p in enumerate(s.parts):
            for j, d in enumerate(dyns):
                oTarget = j * durUnit
                # placing dynamics in Measure requires extra handling
                m = p.getElementsByOffset(oTarget,
                                          mustBeginInSpan=False,
                                          ).getElementsByClass(stream.Measure).first()
                oInsert = oTarget - m.getOffsetBySite(p)
                m.insert(oInsert, dynamics.Dynamic(d))
            # shift 2 places each time
            dyns = dyns[2:] + dyns[:2]

        # s.show()
        # s.show('midi')

        # TODO: BUG -- one note too loud.
        match = [n.volume.cachedRealizedStr for n in s.parts[0].flatten().notes]
        self.assertEqual(match, ['0.35', '0.35', '0.35', '0.35', '0.35',
                                 '0.5', '0.5', '0.5', '0.5',
                                 '0.64', '0.64', '0.64', '0.64', '0.64',
                                 '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78',
                                 '1.0', '1.0', '1.0', '1.0',
                                 '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78', '0.78', '0.78', '0.78'])

        match = [n.volume.cachedRealizedStr for n in s.parts[1].flatten().notes]

        self.assertEqual(match, ['0.64', '0.64', '0.64', '0.64',
                                 '0.99', '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78', '0.78',
                                 '1.0', '1.0', '1.0', '1.0',
                                 '0.99', '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78',
                                 '0.35', '0.35', '0.35', '0.35', '0.35', '0.35',
                                 '0.5', '0.5', '0.5', '0.5', '0.5', '0.5', '0.5', '0.5', '0.5'])

        match = [n.volume.cachedRealizedStr for n in s.parts[3].flatten().notes]

        self.assertEqual(match, ['0.99', '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78', '0.78',
                                 '0.35', '0.35', '0.35', '0.35', '0.35',
                                 '0.5', '0.5', '0.5', '0.5', '0.5', '0.5', '0.5',
                                 '0.64', '0.64', '0.64', '0.64',
                                 '0.99', '0.99', '0.99', '0.99',
                                 '0.78', '0.78', '0.78', '0.78', '0.78',
                                 '1.0', '1.0', '1.0', '1.0', '1.0', '1.0'])


    def testRealizeVolumeC(self):
        from music21 import stream

        s = stream.Stream()
        s.repeatAppend(note.Note('g3'), 16)

        for i in range(0, 16, 3):
            s.notes[i].articulations.append(articulations.Accent())
        for i in range(0, 16, 4):
            s.notes[i].articulations.append(articulations.StrongAccent())

        match = [n.volume.cachedRealizedStr for n in s.notes]
        self.assertEqual(match, ['0.96', '0.71', '0.71', '0.81', '0.86', '0.71', '0.81',
                                 '0.71', '0.86', '0.81', '0.71', '0.71', '0.96', '0.71',
                                 '0.71', '0.81'])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
