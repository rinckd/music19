# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.windowed import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testBasic(self):
        from music21 import corpus
        from music21.analysis import discrete
        # get a procedure

        s = corpus.parse('bach/bwv324')

        for pClass in [discrete.KrumhanslSchmuckler, discrete.Ambitus]:
            p = pClass()

            # get windowing object, provide a stream for analysis as well as
            # the processor
            wa = WindowedAnalysis(s.flatten(), p)
            # do smallest and larges
            for i in list(range(1, 4)) + [None]:
                unused_x, unused_y, unused_z = wa.process(i, i)

    def testWindowing(self):
        '''
        Test that windows are doing what they are supposed to do
        '''
        p = TestMockProcessor()

        from music21 import note
        s1 = stream.Stream()
        s1.append(note.Note('C'))
        s1.append(note.Note('C'))

        s2 = stream.Stream()
        s2.append(note.Note('C'))
        s2.append(note.Note('D'))
        s2.append(note.Note('E'))
        s2.append(note.Note('F'))
        s2.append(note.Note('G'))
        s2.append(note.Note('A'))
        s2.append(note.Note('B'))
        s2.append(note.Note('C'))

        wa1 = WindowedAnalysis(s1, p)
        wa2 = WindowedAnalysis(s2, p)

        # windows partitioned at quarter length
        self.assertEqual(len(wa1._windowedStream), 2)
        self.assertEqual(len(wa2._windowedStream), 8)

        # window size of 1 gets 2 solutions
        a, unused_b, unused_c = wa1.process(1, 1, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 2)
        self.assertEqual(a[0][0], 1)
        self.assertEqual(a[0][1], 1)

        # window size of 2 gets 1 solution
        a, unused_b, unused_c = wa1.process(2, 2, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 1)
        # two items in this window
        self.assertEqual(a[0][0], 2)

        # window size of 1 gets 8 solutions
        a, unused_b, unused_c = wa2.process(1, 1, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 8)
        self.assertEqual(a[0][0], 1)
        self.assertEqual(a[0][1], 1)

        # window size of 2 gets 7 solutions
        a, unused_b, unused_c = wa2.process(2, 2, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 7)

        # window size of 7 gets 2 solutions
        a, unused_b, unused_c = wa2.process(7, 7, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 2)

        # window size of 8 gets 1 solutions
        a, unused_b, unused_c = wa2.process(8, 8, 1, includeTotalWindow=False)
        self.assertEqual(len(a[0]), 1)


    def testVariableWindowing(self):
        from music21.analysis import discrete
        from music21 import corpus
        from music21 import graph

        p = discrete.KrumhanslSchmuckler()
        s = corpus.parse('bach/bwv66.6')

        unused_wa = WindowedAnalysis(s.flatten(), p)

        plot = graph.plot.WindowedKey(s.flatten(), doneAction=None,
                                      windowStep=4, windowType='overlap')
        plot.run()
        # plot.write()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
