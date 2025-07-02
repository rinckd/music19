# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.reduction import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testExtractionA(self):
        from music21 import analysis
        from music21 import corpus
        s = corpus.parse('bwv66.6')
        # s.show()
        s.parts[0].flatten().notes[3].addLyric('test')
        s.parts[0].flatten().notes[4].addLyric('::/o:6/tb:here')
        s.parts[3].flatten().notes[2].addLyric('::/o:5/tb:fromBass')

        s.parts[1].flatten().notes[7].addLyric('::/o:4/nf:no/g:Ursatz/ta:3 3 200')

        sr = analysis.reduction.ScoreReduction()
        sr.score = s

        post = sr.reduce()
        # post.show()
        # post.parts[0].show('t')
        self.assertEqual(len(post.parts[0].flatten().notes), 3)
        # post.parts[0].show('t')

        three_measures = post.parts.first()[stream.Measure][:3]
        new_stream = stream.Stream()
        for m in three_measures:
            new_stream.append(m)
        flat_stream = new_stream.flatten()
        match = [(repr(e), e.offset, e.duration.quarterLength) for e in flat_stream.notesAndRests]
        self.maxDiff = None
        self.assertEqual(match,
                         [('<music21.note.Rest quarter>', 0.0, 1.0),
                          ('<music21.note.Note F#>', 1.0, 1.0),
                          ('<music21.note.Rest quarter>', 2.0, 1.0),
                          ('<music21.note.Note C#>', 3.0, 1.0),
                          ('<music21.note.Rest quarter>', 4.0, 1.0),
                          ('<music21.note.Note G#>', 5.0, 1.0)])

        # test that lyric is found
        self.assertEqual(post.parts[0].flatten().notes[0].lyric, 'fromBass')


    def testExtractionB(self):
        from music21 import analysis
        from music21 import corpus
        s = corpus.parse('bwv66.6')

        s.parts[0].flatten().notes[4].addLyric('::/o:6/v:1/tb:s/g:Ursatz')
        s.parts[3].flatten().notes[2].addLyric('::/o:5/v:2/tb:b')
        s.parts[2].flatten().notes[3].addLyric('::/o:4/v:2/tb:t')
        s.parts[1].flatten().notes[2].addLyric('::/o:4/v:2/tb:a')

        sr = analysis.reduction.ScoreReduction()
        extract = s.measures(0, 10)
        # extract.show()
        sr.score = extract
        # sr.score = s
        post = sr.reduce()
        # post.show()
        self.assertEqual(len(post.parts), 5)
        match = post.parts[0].flatten().notes
        self.assertEqual(len(match), 3)
        # post.show()

    # def testExtractionC(self):
    #     from music21 import analysis
    #     from music21 import corpus
    #     # http://solomonsmusic.net/schenker.htm
    #     # shows extracting an Ursatz line
    #
    #     # BACH pre;ide !, WTC
    #
    #     src = corpus.parse('bwv846')
    #     import warnings
    #     with warnings.catch_warnings():  # catch deprecation warning
    #         warnings.simplefilter('ignore', category=exceptions21.Music21DeprecationWarning)
    #         chords = src.flatten().makeChords(minimumWindowSize=4,  # make chords is gone
    #                                     makeRests=False)
    #     for c in chords.flatten().notes:
    #         c.quarterLength = 4
    #     for m in chords.getElementsByClass(stream.Measure):
    #         m.clef = clef.bestClef(m, recurse=True)
    #
    #     chords.measure(1).notes[0].addLyric('::/p:e/o:5/nf:no/ta:3/g:Ursatz')
    #     chords.measure(1).notes[0].addLyric('::/p:c/o:4/nf:no/tb:I')
    #
    #     chords.measure(24).notes[0].addLyric('::/p:d/o:5/nf:no/ta:2')
    #     chords.measure(24).notes[0].addLyric('::/p:g/o:3/nf:no/tb:V')
    #
    #     chords.measure(30).notes[0].addLyric('::/p:f/o:4/tb:7')
    #
    #     chords.measure(34).notes[0].addLyric('::/p:c/o:5/nf:no/v:1/ta:1')
    #     chords.measure(34).notes[0].addLyric('::/p:g/o:4/nf:no/v:2')
    #     chords.measure(34).notes[0].addLyric('::/p:c/o:4/nf:no/v:1/tb:I')
    #
    #     sr = analysis.reduction.ScoreReduction()
    #     sr.chordReduction = chords
    #     # sr.score = src
    #     unused_post = sr.reduce()
    #     # unused_post.show()


    def testExtractionD(self):
        # this shows a score, extracting a single pitch
        from music21 import analysis
        from music21 import corpus

        src = corpus.parse('schoenberg/opus19', 6)
        for n in src.flatten().notes:
            if isinstance(n, note.Note):
                if n.pitch.name == 'F#':
                    n.addLyric('::/p:f#/o:4')
        #                 if n.pitch.name == 'C':
        #                     n.addLyric('::/p:c/o:4/g:C')
            elif isinstance(n, chord.Chord):
                if 'F#' in [p.name for p in n.pitches]:
                    n.addLyric('::/p:f#/o:4')
        #                 if 'C' in [p.name for p in n.pitches]:
        #                     n.addLyric('::/p:c/o:4/g:C')

        sr = analysis.reduction.ScoreReduction()
        sr.score = src
        unused_post = sr.reduce()
        # post.show()

    def testExtractionD2(self):
        # this shows a score, extracting a single pitch
        from music21 import analysis
        from music21 import corpus

        src = corpus.parse('schoenberg/opus19', 6)
        for n in src.flatten().notes:
            if isinstance(n, note.Note):
                if n.pitch.name == 'F#':
                    n.addLyric('::/p:f#/o:4/g:F#')
                if n.pitch.name == 'C':
                    n.addLyric('::/p:c/o:4/g:C')
            elif isinstance(n, chord.Chord):
                if 'F#' in [p.name for p in n.pitches]:
                    n.addLyric('::/p:f#/o:4/g:F#')
                if 'C' in [p.name for p in n.pitches]:
                    n.addLyric('::/p:c/o:4/g:C')

        sr = analysis.reduction.ScoreReduction()
        sr.score = src
        unused_post = sr.reduce()
        # post.show()

    def testExtractionE(self):
        from music21 import analysis
        from music21 import corpus

        src = corpus.parse('corelli/opus3no1/1grave')

        # chords = src.chordify()

        sr = analysis.reduction.ScoreReduction()
        # sr.chordReduction = chords
        sr.score = src
        unused_post = sr.reduce()
        # post.show()

    def testPartReductionA(self):
        from music21 import analysis
        from music21 import corpus

        s = corpus.parse('bwv66.6')

        partGroups = [
            {
                'name': 'High Voices',
                'color': '#ff0088',
                'match': ['soprano', 'alto']
            },
            {
                'name': 'Low Voices',
                'color': '#8800ff',
                'match': ['tenor', 'bass']
            },
        ]
        pr = analysis.reduction.PartReduction(s, partGroups=partGroups)
        pr.process()
        for sub in pr._partGroups:
            self.assertEqual(len(sub['match']), 2)


    def _matchWeightedData(self, match, target):
        '''
        Utility function to compare known data but not compare floating point weights.
        '''
        for partId, b in enumerate(target):
            a = match[partId]
            self.assertEqual(a[0], b[0])
            for i, dataMatch in enumerate(a[1]):  # second item has data
                dataTarget = b[1][i]
                # start
                self.assertAlmostEqual(dataMatch[0], dataTarget[0])
                # span
                self.assertAlmostEqual(dataMatch[1], dataTarget[1])
                # weight
                self.assertAlmostEqual(
                    dataMatch[2],
                    dataTarget[2],
                    msg=(f'for partId {partId}, entry {i}: '
                         + f'should be {dataMatch[2]} <-> was {dataTarget[2]}')
                )

    def testPartReductionB(self, show=False):
        '''
        Artificially create test cases.
        '''
        from music21 import analysis
        from music21 import dynamics
        from music21 import graph
        durDynPairsA = [(1, 'mf'), (3, 'f'), (2, 'p'), (4, 'ff'), (2, 'mf')]
        durDynPairsB = [(1, 'mf'), (3, 'f'), (2, 'p'), (4, 'ff'), (2, 'mf')]

        s = stream.Score()
        pCount = 0
        for pairs in [durDynPairsA, durDynPairsB]:
            p = stream.Part()
            p.id = pCount
            pos = 0
            for ql, dyn in pairs:
                p.insert(pos, note.Note(quarterLength=ql))
                p.insert(pos, dynamics.Dynamic(dyn))
                pos += ql
            # p.makeMeasures(inPlace=True)
            s.insert(0, p)
            pCount += 1

        if show is True:
            s.show()

        pr = analysis.reduction.PartReduction(s, normalize=False)
        pr.process()
        match = pr.getGraphHorizontalBarWeightedData()
        target = [(0, [[0.0, 1.0, 0.07857142857142858, '#666666'],
                       [1.0, 3.0, 0.09999999999999999, '#666666'],
                       [4.0, 2.0, 0.05, '#666666'],
                       [6.0, 4.0, 0.12142857142857143, '#666666'],
                       [10.0, 2.0, 0.07857142857142858, '#666666']]),
                  (1, [[0.0, 1.0, 0.07857142857142858, '#666666'],
                       [1.0, 3.0, 0.09999999999999999, '#666666'],
                       [4.0, 2.0, 0.05, '#666666'],
                       [6.0, 4.0, 0.12142857142857143, '#666666'],
                       [10.0, 2.0, 0.07857142857142858, '#666666']])]

        self._matchWeightedData(match, target)

        if show is True:
            p = graph.plot.Dolan(s, title='Dynamics', doneAction=None)
            p.run()


    def testPartReductionC(self):
        '''
        Artificially create test cases.
        '''
        from music21 import analysis
        from music21 import dynamics

        s = stream.Score()
        p1 = stream.Part()
        p1.id = 0
        p2 = stream.Part()
        p2.id = 1
        for ql in [1, 2, 1, 4]:
            p1.append(note.Note(quarterLength=ql))
            p2.append(note.Note(quarterLength=ql))
        for pos, dyn in [(0, 'p'), (2, 'fff'), (6, 'ppp')]:
            p1.insert(pos, dynamics.Dynamic(dyn))
        for pos, dyn in [(0, 'p'), (1, 'fff'), (2, 'ppp')]:
            p2.insert(pos, dynamics.Dynamic(dyn))
        s.insert(0, p1)
        s.insert(0, p2)
        # s.show()
        pr = analysis.reduction.PartReduction(s, normalize=False)
        pr.process()
        match = pr.getGraphHorizontalBarWeightedData()

        target = [(0, [[0.0, 2.0, 0.05, '#666666'],
                       [2.0, 4.0, 0.1285714285714286, '#666666'],
                       [6.0, 2.0, 0.0214285714286, '#666666']]),
                  (1, [[0.0, 1.0, 0.05, '#666666'],
                       [1.0, 1.0, 0.1285714285714286, '#666666'],
                       [2.0, 6.0, 0.0214285714286, '#666666']])]

        self._matchWeightedData(match, target)


    def testPartReductionD(self):
        '''
        Artificially create test cases. Here, uses rests.
        '''
        from music21 import analysis
        from music21 import dynamics

        s = stream.Score()
        p1 = stream.Part()
        p1.id = 0
        p2 = stream.Part()
        p2.id = 1
        for ql in [None, 2, False, 2, False, 2]:
            if ql:
                p1.append(note.Note(quarterLength=ql))
                p2.append(note.Note(quarterLength=ql))
            else:
                p1.append(note.Rest(quarterLength=2))
                p2.append(note.Rest(quarterLength=2))
        for pos, dyn in [(0, 'p'), (2, 'fff'), (6, 'ppp')]:
            p1.insert(pos, dynamics.Dynamic(dyn))
        for pos, dyn in [(0, 'mf'), (2, 'f'), (6, 'mf')]:
            p2.insert(pos, dynamics.Dynamic(dyn))
        s.insert(0, p1)
        s.insert(0, p2)
        # s.show()

        pr = analysis.reduction.PartReduction(s)
        pr.process()
        match = pr.getGraphHorizontalBarWeightedData()
        # print(match)
        target = [(0, [[2.0, 2.0, 1.0, '#666666'],
                       [6.0, 2.0, 1 / 6, '#666666'],
                       [10.0, 2.0, 1 / 6, '#666666']]),
                  (1, [[2.0, 2.0, 7 / 9, '#666666'],
                       [6.0, 2.0, 0.6111111111111112, '#666666'],
                       [10.0, 2.0, 0.6111111111111112, '#666666']])]
        self._matchWeightedData(match, target)
        # p = graph.PlotDolan(s, title='Dynamics')
        # p.process()


    def testPartReductionE(self):
        '''
        Artificially create test cases.
        '''
        from music21 import analysis
        from music21 import dynamics
        s = stream.Score()
        p1 = stream.Part()
        p1.id = 0
        p2 = stream.Part()
        p2.id = 1
        for ql in [2, 2, False, 2, False, 2]:
            if ql:
                p1.append(note.Note(quarterLength=ql))
                p2.append(note.Note(quarterLength=ql))
            else:
                p1.append(note.Rest(quarterLength=2))
                p2.append(note.Rest(quarterLength=2))
        for pos, dyn in [(0, 'p'), (2, 'fff'), (6, 'ppp')]:
            p1.insert(pos, dynamics.Dynamic(dyn))
        for pos, dyn in [(0, 'mf'), (2, 'f'), (6, 'mf')]:
            p2.insert(pos, dynamics.Dynamic(dyn))
        p1.makeMeasures(inPlace=True)
        p2.makeMeasures(inPlace=True)
        s.insert(0, p1)
        s.insert(0, p2)
        # s.show()
        pr = analysis.reduction.PartReduction(s, fillByMeasure=True,
                    segmentByTarget=False, normalize=False)
        pr.process()
        target = pr.getGraphHorizontalBarWeightedData()
        match = [(0, [[0.0, 4.0, 0.178571428571, '#666666'],
                      [4.0, 4.0, 0.0214285714286, '#666666'],
                      [8.0, 4.0, 0.0214285714286, '#666666']]),
                 (1, [[0.0, 4.0, 0.178571428571, '#666666'],
                      [4.0, 4.0, 0.07857142857142858, '#666666'],
                      [8.0, 4.0, 0.07857142857142858, '#666666']])]

        self._matchWeightedData(match, target)

        pr = analysis.reduction.PartReduction(s, fillByMeasure=False,
                    segmentByTarget=True, normalize=False)
        pr.process()
        target = pr.getGraphHorizontalBarWeightedData()
        match = [(0, [[0.0, 2.0, 0.05, '#666666'],
                      [2.0, 2.0, 0.1285714285714286, '#666666'],
                      [6.0, 2.0, 0.0214285714286, '#666666'],
                      [10.0, 2.0, 0.0214285714286, '#666666']]),
                 (1, [[0.0, 2.0, 0.07857142857142858, '#666666'],
                      [2.0, 2.0, 0.1, '#666666'],
                      [6.0, 2.0, 0.07857142857142858, '#666666'],
                      [10.0, 2.0, 0.07857142857142858, '#666666']])]
        # from pprint import pprint as print
        # print(target)
        self._matchWeightedData(match, target)


        pr = analysis.reduction.PartReduction(s, fillByMeasure=False,
                    segmentByTarget=False)
        pr.process()
        target = pr.getGraphHorizontalBarWeightedData()
        # print(target)
        match = [(0, [[0.0, 4.0, 1.0, '#666666'],
                      [6.0, 2.0, 0.12, '#666666'],
                      [10.0, 2.0, 0.12, '#666666']]),
                 (1, [[0.0, 4.0, 1.0, '#666666'],
                      [6.0, 2.0, 0.44, '#666666'],
                      [10.0, 2.0, 0.44, '#666666']])]
        self._matchWeightedData(match, target)


        pr = analysis.reduction.PartReduction(s, fillByMeasure=True,
                    segmentByTarget=True)
        pr.process()
        target = pr.getGraphHorizontalBarWeightedData()
        match = [(0, [[0.0, 2.0, 0.3888888888888, '#666666'],
                      [2.0, 2.0, 1.0, '#666666'],
                      [6.0, 2.0, 0.166666666667, '#666666'],
                      [8.0, 4.0, 0.166666666667, '#666666']]),
                 (1, [[0.0, 2.0, 0.6111111111111112, '#666666'],
                      [2.0, 2.0, 0.7777777777777776, '#666666'],
                      [6.0, 2.0, 0.611111111111111, '#666666'],
                      [8.0, 4.0, 0.611111111111111, '#666666']])]
        self._matchWeightedData(match, target)
        # p = graph.PlotDolan(s, title='Dynamics', fillByMeasure=False,
        #                     segmentByTarget=True, normalizeByPart=False)
        # p.process()

    def xtestPartReductionSchoenberg(self):
        from music21 import corpus
        sc = corpus.parse('schoenberg/opus19', 2)
        pr = PartReduction(
            sc,
            fillByMeasure=False,
            segmentByTarget=True,
            normalizeByPart=False
        )
        pr.process()
        unused_target = pr.getGraphHorizontalBarWeightedData()


class TestExternal(unittest.TestCase):
    show = True

    def testPartReductionB(self):
        test = Test()
        test.testPartReductionB(show=self.show)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
