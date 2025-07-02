# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.alpha.analysis.search import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testFindConsecutiveScaleA(self):
        sc = scale.MajorScale('a4')

        # fixed collection
        part = stream.Stream()
        for pn in ['a4', 'b4', 'c#4', 'd4', 'e4', 'f#4', 'g#4', 'a4']:
            n = note.Note(pn)
            part.append(n)

        # todo: presently this is still permitting gaps
        post = findConsecutiveScale(part, sc, degreesRequired=4)
        self.assertEqual(len(post), 1)  # one group
        self.assertEqual(len(post[0]['stream']), 8)  # has all 8 elements

        part = stream.Stream()
        for pn in ['a4', 'b4', 'c#4', 'd4', 'e4', 'f#4', 'g#4', 'a4']:
            n = note.Note(pn)
            part.append(n)

        # todo: presently this is still permitting gaps
        post = findConsecutiveScale(part, sc, degreesRequired=4,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 1)  # one group
        self.assertEqual(len(post[0]['stream']), 6)  # has last 6 elements

        part = stream.Stream()
        for pn in ['a4', 'b4', 'c#5', 'd5', 'e5', 'a4', 'b4', 'c#5', 'd5', 'e5']:
            n = note.Note(pn)
            part.append(n)

        post = findConsecutiveScale(part, sc, degreesRequired=4,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 2)  # two groups
        self.assertEqual(len(post[0]['stream']), 5)  # has last 6 elements
        self.assertEqual(len(post[1]['stream']), 5)  # has last 6 elements

        # with octave shifts
        part = stream.Stream()
        for pn in ['a4', 'b8', 'c#3', 'd3', 'e4', 'a4', 'b9', 'c#2', 'd4', 'e12']:
            n = note.Note(pn)
            part.append(n)

        # todo: presently this is still permitting gaps
        post = findConsecutiveScale(part, sc, degreesRequired=4, comparisonAttribute='name')
        self.assertEqual(len(post), 2)  # two groups
        self.assertEqual(len(post[0]['stream']), 5)  # has last 6 elements
        self.assertEqual(len(post[1]['stream']), 5)  # has last 6 elements

        # three segments
        part = stream.Stream()
        for pn in ['a4', 'b4', 'c#5', 'd-3', 'a4', 'b4', 'c#5', 'd-3', 'a4', 'b4', 'c#5', 'd-3']:
            n = note.Note(pn)
            part.append(n)

        # todo: presently this is still permitting gaps
        post = findConsecutiveScale(part, sc, degreesRequired=4,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 0)  # no match
        # set to search for groups of 3
        post = findConsecutiveScale(part, sc, degreesRequired=3,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 3)  # no match

        self.assertEqual(len(post[0]['stream']), 3)  # each has 3
        self.assertEqual(len(post[1]['stream']), 3)
        self.assertEqual(len(post[2]['stream']), 3)

        # changes in direction
        part = stream.Stream()
        stub = ['c#5', 'd3', 'e4', 'f#4', 'g#4']
        stubReversed = ['c#5', 'd3', 'e4', 'f#4', 'g#4']
        stubReversed.reverse()

        for pn in (stub + stubReversed + stub + stubReversed + stubReversed):
            n = note.Note(pn)
            part.append(n)

        # pitch space is not consecutive
        post = findConsecutiveScale(part, sc, degreesRequired=5,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 0)  # five segments found

        # pitch names are consecutive
        post = findConsecutiveScale(part, sc, degreesRequired=5, comparisonAttribute='name')
        self.assertEqual(len(post), 5)  # five segments found

        self.assertEqual(len(post[0]['stream']), 5)  # each has 5
        self.assertEqual(post[0]['stream'][0].pitch.nameWithOctave, 'C#5')  # each has 5
        self.assertEqual(len(post[1]['stream']), 5)
        self.assertEqual(post[1]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5
        self.assertEqual(len(post[2]['stream']), 5)
        self.assertEqual(post[2]['stream'][0].pitch.nameWithOctave, 'C#5')  # each has 5
        self.assertEqual(len(post[3]['stream']), 5)
        self.assertEqual(post[3]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5
        self.assertEqual(len(post[4]['stream']), 5)
        self.assertEqual(post[4]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5

        # changes in direction with intermingled notes
        part = stream.Stream()
        stub = ['c#5', 'd3', 'e4', 'f#4', 'g#4']
        stubReversed = ['c#5', 'd3', 'e4', 'f#4', 'g#4']
        stubReversed.reverse()

        for pn in (stub
                   + stubReversed
                   + ['g2', 'e#7']
                   + stub
                   + ['a-2']
                   + stubReversed
                   + ['a', 'b']
                   + stubReversed):
            n = note.Note(pn)
            part.append(n)

        # pitch space is not consecutive
        post = findConsecutiveScale(part, sc, degreesRequired=5,
                                    comparisonAttribute='nameWithOctave')
        self.assertEqual(len(post), 0)  # five segments found

        # pitch names are consecutive
        post = findConsecutiveScale(part, sc, degreesRequired=5, comparisonAttribute='name')
        self.assertEqual(len(post), 5)  # five segments found

        self.assertEqual(len(post[0]['stream']), 5)  # each has 5
        self.assertEqual(post[0]['stream'][0].pitch.nameWithOctave, 'C#5')  # each has 5
        self.assertEqual(len(post[1]['stream']), 5)
        self.assertEqual(post[1]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5
        self.assertEqual(len(post[2]['stream']), 5)
        self.assertEqual(post[2]['stream'][0].pitch.nameWithOctave, 'C#5')  # each has 5
        self.assertEqual(len(post[3]['stream']), 5)
        self.assertEqual(post[3]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5
        self.assertEqual(len(post[4]['stream']), 5)
        self.assertEqual(post[4]['stream'][0].pitch.nameWithOctave, 'G#4')  # each has 5

    def xtestFindConsecutiveScaleB(self):
        from music21 import corpus

        scGMajor = scale.MajorScale('g4')
        scAMajor = scale.MajorScale('a4')
        scDMajor = scale.MajorScale('d4')

        s = corpus.parse('mozart/k80/movement1').measures(1, 28)
        for sc in [scGMajor, scDMajor, scAMajor]:
            for part in s.parts:  # just first part
                # must provide flat version
                post = findConsecutiveScale(part.flatten(), sc, degreesRequired=5,
                                            comparisonAttribute='name')
                for g, group in enumerate(post):
                    for n in group:
                        n.addLyric(f'{sc.getTonic().name}{g + 1}')

        # s.show()

        # ex = stream.Score()
        # for sub in post:
        #     m = stream.Measure()
        #     for e in sub:
        #         m.append(e)
        #     ex.append(m)
        # ex.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
