# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.features.jSymbolic import *


class Test(unittest.TestCase):

    def testAverageMelodicIntervalFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p5', 'p5', 'p4', 'p4', 'p4']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.AverageMelodicIntervalFeature(s)
        f = fe.extract()
        # average of 3 p5 and 3 p4 is the tritone
        self.assertEqual(f.vector, [6.0])

    def testMostCommonMelodicIntervalFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p5', 'p5', 'p4', 'p4', 'p4', 'p4']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MostCommonMelodicIntervalFeature(s)
        f = fe.extract()
        # average of 3 p5 and 3 p4 is the tritone
        self.assertEqual(f.vector, [5])

    def testDistanceBetweenMostCommonMelodicIntervalsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p5', 'p5', 'p4', 'p4', 'p4', 'p4', 'm2', 'm3']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.DistanceBetweenMostCommonMelodicIntervalsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [2])

    def testMostCommonMelodicIntervalPrevalenceFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p5', 'p4', 'p4', 'p4', 'p4', 'm2', 'm3']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MostCommonMelodicIntervalPrevalenceFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.5])

    def testRelativeStrengthOfMostCommonIntervalsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p5', 'p5', 'p4', 'p4', 'p4', 'p4', 'm2', 'm3']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.RelativeStrengthOfMostCommonIntervalsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.75])

    def testNumberOfCommonMelodicIntervalsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p5', 'p4', 'p4', 'p4', 'p4', 'p4', 'p4', 'p4', 'p4', 'p4', 'p4', 'm2', 'm3']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.NumberOfCommonMelodicIntervalsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [1])

    def testAmountOfArpeggiationFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'M2', 'M3', 'p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.AmountOfArpeggiationFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.5])

    def testRepeatedNotesFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['p1', 'p1', 'p1', 'M2', 'M3', 'p5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.RepeatedNotesFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.5])

    def testChromaticMotionFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'M3', 'p5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.ChromaticMotionFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.5])

    def testStepwiseMotionFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'M3', 'p5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.StepwiseMotionFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [2 / 3])

    def testMelodicThirdsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'M3', 'p5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MelodicThirdsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [1 / 6])

    def testMelodicFifthsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'p5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MelodicFifthsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [2 / 6])

    def testMelodicTritonesFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'd5']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MelodicTritonesFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [1 / 6])

    def testMelodicOctavesFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))

        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))

        fe = features.jSymbolic.MelodicOctavesFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [1 / 6])

    def testDirectionOfMotionFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        # all up
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.DirectionOfMotionFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [1.0])

        # half down, half up
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', '-m2', '-M2', '-p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.DirectionOfMotionFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.5])

        # downward only
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['-m2', '-m2', '-m2', '-M2', '-p5', '-p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.DirectionOfMotionFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0.0])

    def testDurationOfMelodicArcsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        # all up
        # in jSymbolic implementation, all up means there
        # is no melodic arc and thus the average duration
        # of melodic arc is set to 0.
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.DurationOfMelodicArcsFeature(s)
        f = fe.extract()
        self.assertEqual(f.vector, [0])

        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', '-p8', 'M2', 'p5', '-p8', 'p8', '-p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.DurationOfMelodicArcsFeature(s)
        f = fe.extract()
        self.assertAlmostEqual(f.vector[0], 8 / 5)

    def testSizeOfMelodicArcsFeature(self):
        from music21 import stream
        from music21 import pitch
        from music21 import note
        from music21 import features
        # all up
        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', 'm2', 'M2', 'p5', 'p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.SizeOfMelodicArcsFeature(s)
        unused_f = fe.extract()
        # self.assertEqual(f.vector, [5])

        s = stream.Stream()
        p = pitch.Pitch('c2')
        s.append(note.Note(copy.deepcopy(p)))
        for i in ['m2', 'm2', '-p8', 'M2', 'p5', '-p8', 'p8', '-p8']:
            p = p.transpose(i)
            s.append(note.Note(copy.deepcopy(p)))
        fe = features.jSymbolic.SizeOfMelodicArcsFeature(s)
        unused_f = fe.extract()
        # self.assertAlmostEqual(f.vector[0], 1 + 2/3)

    def testNoteDensityFeatureA(self):
        from music21 import stream
        from music21 import note
        from music21 import tempo
        from music21 import features
        s = stream.Stream()
        s.insert(0, tempo.MetronomeMark(number=60))
        s.insert(0, note.Note(quarterLength=8))
        s.insert(1, note.Note(quarterLength=7))
        s.insert(2, note.Note(quarterLength=6))
        s.insert(3, note.Note(quarterLength=5))
        s.insert(4, note.Note(quarterLength=4))
        s.insert(5, note.Note(quarterLength=3))
        s.insert(6, note.Note(quarterLength=2))
        s.insert(7, note.Note(quarterLength=1))

        fe = features.jSymbolic.NoteDensityFeature(s)
        f = fe.extract()
        # 8 notes in the span of 8 seconds
        self.assertAlmostEqual(f.vector[0], 1.0)

        s = stream.Stream()
        s.insert(0, tempo.MetronomeMark(number=240))
        s.insert(0, note.Note(quarterLength=8))
        s.insert(1, note.Note(quarterLength=7))
        s.insert(2, note.Note(quarterLength=6))
        s.insert(3, note.Note(quarterLength=5))
        s.insert(4, note.Note(quarterLength=4))
        s.insert(5, note.Note(quarterLength=3))
        s.insert(6, note.Note(quarterLength=2))
        s.insert(7, note.Note(quarterLength=1))

        # 8 notes in the span of 2 seconds
        fe = features.jSymbolic.NoteDensityFeature(s)
        f = fe.extract()
        self.assertAlmostEqual(f.vector[0], 4.0)

    def testFeatureCount(self):
        from music21 import features
        fs = features.jSymbolic.extractorsById
        feTotal = 0
        feImplemented = 0
        for k in fs:
            for i in range(len(fs[k])):
                if fs[k][i] is not None:
                    feTotal += 1
                    if fs[k][i] in features.jSymbolic.featureExtractors:
                        feImplemented += 1
        environLocal.printDebug(['fe total:', feTotal, 'fe implemented',
                                 feImplemented, 'percent', feImplemented / feTotal])

    def testBeatHistogram(self):
        from music21 import corpus
        from music21 import tempo
        sch = corpus.parse('schoenberg/opus19', 2)
        for p in sch.parts:
            p.insert(0, tempo.MetronomeMark('Langsam', 70))
        fe = StrongestRhythmicPulseFeature(sch)
        f = fe.extract()
        self.assertEqual(140.0, f.vector[0])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
