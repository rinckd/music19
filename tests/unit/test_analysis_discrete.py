# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.discrete import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testKeyAnalysisKrumhansl(self):
        from music21 import converter

        p = KrumhanslSchmuckler()
        s1 = converter.parse('tinynotation: 4/4 c4 d e f g a b c   c#4 d# e# f#')
        s2 = converter.parse('tinynotation: 4/4 c#4 d# e# f#  f g a b- c d e f')
        s3 = converter.parse('tinynotation: 4/4 c4 d e f g a b c   c#4 d# e# f#  '
                             + 'c#4 d# e# f#  f g a b- c d e f')

        # self.assertEqual(p._getPitchClassDistribution(s1),
        #            [1.0, 0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        p.process(s1.flatten())
        likelyKeysMajor1, likelyKeysMinor1 = p._likelyKeys(s1.flatten())
        likelyKeysMajor1.sort()
        likelyKeysMinor1.sort()
        allResults1 = likelyKeysMajor1 + likelyKeysMinor1
        # post = []
        # _post = sorted([(y, x) for x, y in allResults1])

        p.process(s2.flatten())
        likelyKeysMajor2, likelyKeysMinor2 = p._likelyKeys(s2.flatten())
        likelyKeysMajor2.sort()
        likelyKeysMinor2.sort()
        allResults2 = likelyKeysMajor2 + likelyKeysMinor2
        # post = []
        # _post = sorted([(y, x) for x, y in allResults2])

        likelyKeysMajor3, likelyKeysMinor3 = p._likelyKeys(s3.flatten())
        likelyKeysMajor3.sort()
        likelyKeysMinor3.sort()
        # allResults3 = likelyKeysMajor3 + likelyKeysMinor3
        # _post = sorted([(y, x) for x, y in allResults3])

        avg = []
        for i in range(len(allResults1)):
            p, count1 = allResults1[i]
            p, count2 = allResults2[i]
            avg.append((p, (count1 + count2) / 2.0))
        # _post = sorted([(y, x) for x, y in avg])

    def testIntervalDiversity(self):
        from music21 import stream
        from music21 import corpus

        s = stream.Stream()
        s.append(note.Note('g#3'))
        s.append(note.Note('a3'))
        s.append(note.Note('g4'))

        mid = MelodicIntervalDiversity()
        midDict = mid.countMelodicIntervals(s)
        self.assertEqual(str(midDict['m7']), '[<music21.interval.Interval m7>, 1]')
        self.assertEqual(str(midDict['m2']), '[<music21.interval.Interval m2>, 1]')
        self.assertEqual(len(midDict), 2)

        s = stream.Stream()
        s.append(note.Note('c3'))
        s.append(note.Note('d3'))
        s.append(note.Note('c3'))
        s.append(note.Note('d3'))

        mid = MelodicIntervalDiversity()
        midDict = mid.countMelodicIntervals(s)
        self.assertEqual(len(midDict), 1)
        self.assertEqual(str(midDict['M2']), '[<music21.interval.Interval M2>, 3]')

        midDict = mid.countMelodicIntervals(s, ignoreDirection=False)
        self.assertEqual(len(midDict), 2)
        self.assertEqual(str(midDict['M-2']), '[<music21.interval.Interval M-2>, 1]')
        self.assertEqual(str(midDict['M2']), '[<music21.interval.Interval M2>, 2]')

        mid = MelodicIntervalDiversity()
        s = corpus.parse('corelli/opus3no1/1grave')
        # s.show()

        midDict = mid.countMelodicIntervals(s.parts[1])
        self.assertEqual(len(midDict), 9)
        self.assertEqual(str(midDict['P5']), '[<music21.interval.Interval P5>, 8]')
        self.assertEqual(str(midDict['P4']), '[<music21.interval.Interval P4>, 7]')
        self.assertEqual(str(midDict['m3']), '[<music21.interval.Interval m3>, 1]')
        self.assertEqual(str(midDict['M2']), '[<music21.interval.Interval M2>, 21]')

        midDict = mid.countMelodicIntervals(s)
        self.assertEqual(len(midDict), 10)
        self.assertEqual(str(sorted(list(midDict))),
                         "['M2', 'M3', 'M6', 'P15', 'P4', 'P5', 'P8', 'd5', 'm2', 'm3']")
        self.assertEqual(str(midDict['P15']), '[<music21.interval.Interval P15>, 1]')
        self.assertEqual(str(midDict['P5']), '[<music21.interval.Interval P5>, 16]')
        self.assertEqual(str(midDict['P4']), '[<music21.interval.Interval P4>, 29]')
        self.assertEqual(str(midDict['M3']), '[<music21.interval.Interval M3>, 16]')
        self.assertEqual(str(midDict['m3']), '[<music21.interval.Interval m3>, 12]')
        self.assertEqual(str(midDict['M2']), '[<music21.interval.Interval M2>, 79]')
        self.assertEqual(str(midDict['m2']), '[<music21.interval.Interval m2>, 43]')

    def testKeyAnalysisSpelling(self):
        from music21 import stream

        for p in ['A', 'B-', 'A-']:
            s = stream.Stream()
            s.append(note.Note(p))
            self.assertEqual(str(s.analyze('Krumhansl').tonic), p)

    def testKeyAnalysisDiverseWeights(self):
        from music21 import converter
        from music21.musicxml import testFiles
        # use a musicxml test file with independently confirmed results
        s = converter.parse(testFiles.edgefield82b)

        p = KrumhanslSchmuckler()
        k = p.getSolution(s)
        post = [k.tonic, k.mode, k.correlationCoefficient]
        self.assertEqual(str(post[0]), 'F#')
        self.assertEqual(str(post[1]), 'major')
        self.assertEqual(str(post[2])[0:7], '0.81063')

        p = AardenEssen()
        k = p.getSolution(s)
        post = [k.tonic, k.mode, k.correlationCoefficient]
        self.assertEqual(str(post[0]), 'F#')
        self.assertEqual(str(post[1]), 'minor')

        p = SimpleWeights()
        k = p.getSolution(s)
        post = [k.tonic, k.mode, k.correlationCoefficient]
        self.assertEqual(str(post[0]), 'F#')
        self.assertEqual(str(post[1]), 'minor')

        p = BellmanBudge()
        k = p.getSolution(s)
        post = [k.tonic, k.mode, k.correlationCoefficient]
        self.assertEqual(str(post[0]), 'F#')
        self.assertEqual(str(post[1]), 'minor')

        p = TemperleyKostkaPayne()
        k = p.getSolution(s)
        post = [k.tonic, k.mode, k.correlationCoefficient]
        self.assertEqual(str(post[0]), 'F#')
        self.assertEqual(str(post[1]), 'minor')

    def testKeyAnalysisLikelyKeys(self):
        from music21 import stream
        s = stream.Stream()
        s.repeatAppend(note.Note('c'), 6)
        s.repeatAppend(note.Note('g'), 4)
        s.repeatAppend(note.Note('a'), 2)

        k = s.analyze('KrumhanslSchmuckler')
        self.assertEqual(str(k), 'C major')
        self.assertEqual(' '.join(kp.tonicPitchNameWithCase for kp in k.alternateInterpretations),
                         'c G a F g e f E- A- B- d D A b b- c# f# C# E g# F# e- B')

        k = s.analyze('AardenEssen')
        self.assertEqual(str(k), 'F major')
        self.assertEqual(' '.join(kp.tonicPitchNameWithCase for kp in k.alternateInterpretations),
                         'C c g f a G d A- B- E- e b- D A f# C# b E c# e- F# B g#')

        # s.plot('grid', 'KrumhanslSchmuckler')
        # s.plot('windowed', 'aarden')

        # Create a tied correlation value for g minor and g# minor
        s2 = stream.Stream()
        s2.repeatAppend(note.Note('c'), 2)
        s2.repeatAppend(note.Note('c#'), 2)
        k = s2.analyze('key')
        # Ensure all pitch classes are present
        self.assertEqual(len(k.alternateInterpretations), 23)

    def testKeyAnalysisIgnoresUnpitched(self):
        from music21 import stream
        s = stream.Stream()
        s.append(note.Unpitched())
        s.append(percussion.PercussionChord([
            note.Unpitched(),
            note.Note('E-4'),
            note.Note('B-4'),
        ]))

        k = s.analyze('key')
        self.assertEqual(k.name, 'E- major')


# define presented order in documentation
_DOC_ORDER = [analyzeStream, DiscreteAnalysis, Ambitus, MelodicIntervalDiversity,
              KeyWeightKeyAnalysis, SimpleWeights, AardenEssen, BellmanBudge,
              KrumhanslSchmuckler, TemperleyKostkaPayne]


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
