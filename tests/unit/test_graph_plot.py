# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph.plot import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testPitchSpaceDurationCount(self):
        a = corpus.parse('bach/bwv57.8')
        b = ScatterWeightedPitchSpaceQuarterLength(a.parts[0].flatten(), doneAction=None,
                                                   title='Bach (soprano voice)')
        b.run()

    def testPitchSpace(self):
        a = corpus.parse('bach')
        b = HistogramPitchSpace(a.parts[0].flatten(), doneAction=None, title='Bach (soprano voice)')
        b.run()

    def testPitchClass(self):
        a = corpus.parse('bach/bwv57.8')
        b = HistogramPitchClass(a.parts[0].flatten(),
                                doneAction=None,
                                title='Bach (soprano voice)')
        b.run()

    def testQuarterLength(self):
        a = corpus.parse('bach/bwv57.8')
        b = HistogramQuarterLength(a.parts[0].flatten(),
                                   doneAction=None,
                                   title='Bach (soprano voice)')
        b.run()

    def testPitchDuration(self):
        a = corpus.parse('schoenberg/opus19', 2)
        b = ScatterPitchSpaceDynamicSymbol(a.parts[0].flatten(),
                                           doneAction=None,
                                           title='Schoenberg (piano)')
        b.run()

        b = ScatterWeightedPitchSpaceDynamicSymbol(a.parts[0].flatten(),
                                                   doneAction=None,
                                                   title='Schoenberg (piano)')
        b.run()

    def testWindowed(self, doneAction=None):
        a = corpus.parse('bach/bwv66.6')
        fn = 'bach/bwv66.6'
        windowStep = 20  # set high to be fast

#         b = WindowedAmbitus(a.parts, title='Bach Ambitus',
#             minWindow=1, maxWindow=8, windowStep=3,
#             doneAction=doneAction)
#         b.run()

        b = WindowedKey(a.flatten(), title=fn,
                        minWindow=1, windowStep=windowStep,
                        doneAction=doneAction, dpi=300)
        b.run()
        self.assertEqual(b.graphLegend.data,
            [
                ['Major',
                    [('C#', '#f0727a'), ('D', '#ffd752'), ('E', '#eeff9a'),
                     ('F#', '#b9f0ff'), ('A', '#bb9aff'), ('B', '#ffb5ff')
                     ]
                 ],
                ['Minor',
                    [('c#', '#8c0e16'), ('', '#ffffff'), ('', '#ffffff'),
                     ('f#', '#558caa'), ('', '#ffffff'), ('b', '#9b519b')
                     ]
                 ]
            ]
        )

    def testFeatures(self):
        streamList = ['bach/bwv66.6', 'schoenberg/opus19/movement2', 'corelli/opus3no1/1grave']
        feList = ['ql1', 'ql2', 'ql3']

        p = Features(streamList, featureExtractors=feList, doneAction=None)
        p.run()

    def testChordsA(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        b = Histogram(stream.Stream(), doneAction=None)
        c = chord.Chord(['b', 'c', 'd'])
        b.axisX = axis.PitchSpaceAxis(b, 'x')  # pylint: disable=attribute-defined-outside-init
        self.assertEqual(b.extractChordDataOneAxis(b.axisX, c, {}), [71, 60, 62])

        s = stream.Stream()
        s.append(chord.Chord(['b', 'c#', 'd']))
        s.append(note.Note('c3'))
        s.append(note.Note('c5'))
        b = HistogramPitchSpace(s, doneAction=None)
        b.run()

        # b.write()
        self.assertEqual(b.data, [(1, 1, {}), (2, 1, {}), (3, 1, {}), (4, 1, {}), (5, 1, {})])

        s = stream.Stream()
        s.append(sc.getChord('e3', 'a3'))
        s.append(note.Note('c3'))
        s.append(note.Note('c3'))
        b = HistogramPitchClass(s, doneAction=None)
        b.run()

        # b.write()
        self.assertEqual(b.data, [(1, 2, {}), (2, 1, {}), (3, 1, {}), (4, 1, {}), (5, 1, {})])

        s = stream.Stream()
        s.append(sc.getChord('e3', 'a3', quarterLength=2))
        s.append(note.Note('c3', quarterLength=0.5))
        b = HistogramQuarterLength(s, doneAction=None)
        b.run()

        # b.write()
        self.assertEqual(b.data, [(1, 1, {}), (2, 1, {})])

        # test scatter plots

        b = Scatter(stream.Stream(), doneAction=None)
        b.axisX = axis.PitchSpaceAxis(b, 'x')  # pylint: disable=attribute-defined-outside-init
        b.axisY = axis.QuarterLengthAxis(b, 'y')  # pylint: disable=attribute-defined-outside-init
        b.axisY.useLogScale = False
        c = chord.Chord(['b', 'c', 'd'], quarterLength=0.5)

        self.assertEqual(b.extractChordDataMultiAxis(c, {}),
                         [[71, 60, 62], [0.5, 0.5, 0.5]])

        b.matchPitchCountForChords = False
        self.assertEqual(b.extractChordDataMultiAxis(c, {}), [[71, 60, 62], [0.5]])
        # matching the number of pitches for each data point may be needed

    def testChordsA2(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        s.append(sc.getChord('b3', 'c5', quarterLength=1.5))
        s.append(note.Note('c3', quarterLength=2))
        b = ScatterPitchSpaceQuarterLength(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()

        match = [(0.5, 52.0, {}), (0.5, 53.0, {}), (0.5, 55.0, {}), (0.5, 57.0, {}),
                 (1.5, 59.0, {}), (1.5, 60.0, {}),
                 (1.5, 62.0, {}), (1.5, 64.0, {}),
                 (1.5, 65.0, {}), (1.5, 67.0, {}),
                 (1.5, 69.0, {}), (1.5, 71.0, {}), (1.5, 72.0, {}),
                 (2.0, 48.0, {})]
        self.assertEqual(b.data, match)
        # b.write()

    def testChordsA3(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        s.append(sc.getChord('b3', 'c5', quarterLength=1.5))
        s.append(note.Note('c3', quarterLength=2))
        b = ScatterPitchClassQuarterLength(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()

        match = [(0.5, 4, {}), (0.5, 5, {}), (0.5, 7, {}), (0.5, 9, {}),
                 (1.5, 11, {}), (1.5, 0, {}), (1.5, 2, {}), (1.5, 4, {}), (1.5, 5, {}),
                 (1.5, 7, {}), (1.5, 9, {}), (1.5, 11, {}), (1.5, 0, {}),
                 (2.0, 0, {})]
        self.assertEqual(b.data, match)
        # b.write()

    def testChordsA4(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        s.append(note.Note('c3', quarterLength=2))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(note.Note('d3', quarterLength=2))
        self.assertEqual([e.offset for e in s], [0.0, 0.5, 2.5, 4.0])

        # s.show()
        b = ScatterPitchClassOffset(s, doneAction=None)
        b.run()

        match = [(0.0, 4, {}), (0.0, 5, {}), (0.0, 7, {}), (0.0, 9, {}),
                 (0.5, 0, {}),
                 (2.5, 11, {}), (2.5, 0, {}), (2.5, 2, {}), (2.5, 4, {}),
                 (4.0, 2, {})]
        self.assertEqual(b.data, match)
        # b.write()

    def testChordsA5(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(dynamics.Dynamic('f'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(dynamics.Dynamic('p'))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        # s.append(note.Note('d3', quarterLength=2))

        # s.show()
        b = ScatterPitchSpaceDynamicSymbol(s, doneAction=None)
        b.run()

        self.assertEqual(b.data, [(52, 8, {}), (53, 8, {}), (55, 8, {}),
                                  (57, 8, {}), (59, 8, {}), (59, 5, {}),
                                  (60, 8, {}), (60, 5, {}), (62, 8, {}),
                                  (62, 5, {}), (64, 8, {}), (64, 5, {})])
        # b.write()

    def testChordsB(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(note.Note('c3'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))

        b = HorizontalBarPitchClassOffset(s, doneAction=None)
        b.run()

        match = [['C', [(0.0, 0.9375, {}), (1.5, 1.4375, {})], {}],
                 ['', [], {}],
                 ['D', [(1.5, 1.4375, {})], {}],
                 ['', [], {}],
                 ['E', [(1.0, 0.4375, {}), (1.5, 1.4375, {})], {}],
                 ['F', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['G', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['A', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['B', [(1.5, 1.4375, {})], {}]]
        self.assertEqual(b.data, match)
        # b.write()

        s = stream.Stream()
        s.append(note.Note('c3'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))

        b = HorizontalBarPitchSpaceOffset(s, doneAction=None)
        b.run()
        match = [['C3', [(0.0, 0.9375, {})], {}],
                 ['', [], {}],
                 ['', [], {}],
                 ['', [], {}],
                 ['E', [(1.0, 0.4375, {})], {}],
                 ['F', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['G', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['A', [(1.0, 0.4375, {})], {}],
                 ['', [], {}],
                 ['B', [(1.5, 1.4375, {})], {}],
                 ['C4', [(1.5, 1.4375, {})], {}],
                 ['', [], {}],
                 ['D', [(1.5, 1.4375, {})], {}],
                 ['', [], {}],
                 ['E', [(1.5, 1.4375, {})], {}]]

        self.assertEqual(b.data, match)
        # b.write()

        s = stream.Stream()
        s.append(note.Note('c3'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(note.Note('c5', quarterLength=3))

        b = ScatterWeightedPitchSpaceQuarterLength(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()

        self.assertEqual(b.data[0:7], [(0.5, 52.0, 1, {}), (0.5, 53.0, 1, {}), (0.5, 55.0, 1, {}),
                                       (0.5, 57.0, 1, {}), (1.0, 48.0, 1, {}), (1.5, 59.0, 1, {}),
                                       (1.5, 60.0, 1, {})])
        # b.write()

        s = stream.Stream()
        s.append(note.Note('c3'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        # s.append(note.Note('c3', quarterLength=2))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(note.Note('c5', quarterLength=3))

        b = ScatterWeightedPitchClassQuarterLength(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()

        self.assertEqual(b.data[0:8], [(0.5, 4, 1, {}), (0.5, 5, 1, {}), (0.5, 7, 1, {}),
                                       (0.5, 9, 1, {}),
                                       (1.0, 0, 1, {}),
                                       (1.5, 0, 1, {}), (1.5, 2, 1, {}), (1.5, 4, 1, {})])
        # b.write()

    def testChordsB2(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(dynamics.Dynamic('f'))
        # s.append(note.Note('c3'))
        c = sc.getChord('e3', 'a3', quarterLength=0.5)
        self.assertEqual(repr(c), '<music21.chord.Chord E3 F3 G3 A3>')
        self.assertEqual([n.pitch.ps for n in c], [52.0, 53.0, 55.0, 57.0])
        s.append(c)
        # s.append(note.Note('c3', quarterLength=2))
        s.append(dynamics.Dynamic('mf'))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(dynamics.Dynamic('pp'))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(note.Note('c5', quarterLength=3))

        b = ScatterWeightedPitchSpaceDynamicSymbol(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()
        match = [(52.0, 8, 1, {}), (53.0, 8, 1, {}), (55.0, 8, 1, {}), (57.0, 8, 1, {}),
                 (59.0, 7, 1, {}), (59.0, 8, 1, {}), (60.0, 7, 1, {}), (60.0, 8, 1, {}),
                 (62.0, 7, 1, {}), (62.0, 8, 1, {}), (64.0, 7, 1, {}), (64.0, 8, 1, {}),
                 (65.0, 4, 2, {}), (65.0, 7, 1, {}),
                 (67.0, 4, 2, {}), (67.0, 7, 1, {}),
                 (69.0, 4, 2, {}), (69.0, 7, 1, {}), (71.0, 4, 2, {}), (71.0, 7, 1, {}),
                 (72.0, 4, 3, {}), (72.0, 7, 1, {}), (74.0, 4, 2, {}), (74.0, 7, 1, {}),
                 (76.0, 4, 2, {}), (76.0, 7, 1, {}), (77.0, 4, 2, {}), (77.0, 7, 1, {}),
                 (79.0, 4, 2, {}), (79.0, 7, 1, {})]

        self.maxDiff = 2048
        # TODO: Is this right? why are the old dynamics still active?
        self.assertEqual(b.data, match)
        # b.write()

    def testChordsB3(self):
        from music21 import scale
        sc = scale.MajorScale('c4')

        s = stream.Stream()
        s.append(dynamics.Dynamic('f'))
        s.append(note.Note('c3'))
        s.append(sc.getChord('e3', 'a3', quarterLength=0.5))
        s.append(dynamics.Dynamic('mf'))
        s.append(sc.getChord('b3', 'e4', quarterLength=1.5))
        s.append(dynamics.Dynamic('pp'))
        s.append(sc.getChord('f4', 'g5', quarterLength=3))
        s.append(note.Note('c5', quarterLength=3))

        b = Plot3DBarsPitchSpaceQuarterLength(s, doneAction=None)
        b.axisX.useLogScale = False
        b.run()

        self.assertEqual(b.data[0], (0.5, 52.0, 1, {}))
        # b.write()

    def testDolanA(self):
        a = corpus.parse('bach/bwv57.8')
        b = Dolan(a, title='Bach', doneAction=None)
        b.run()

        # b.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
