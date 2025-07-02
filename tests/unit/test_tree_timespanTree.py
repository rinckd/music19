# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.tree.timespanTree import *


class Test(unittest.TestCase):

    def testGetVerticalityAtWithKey(self):
        from music21 import stream
        from music21 import key
        from music21 import note
        s = stream.Stream()
        s.insert(0, key.Key('C'))
        s.insert(0, note.Note('F#4'))
        scoreTree = s.asTimespans()
        v = scoreTree.getVerticalityAt(0.0)
        ps = v.pitchSet
        self.assertEqual(len(ps), 1)

    def testTimespanTree(self):
        for attempt in range(100):
            starts = list(range(20))
            stops = list(range(20))
            random.shuffle(starts)
            random.shuffle(stops)
            tss = []
            for start, stop in zip(starts, stops):
                if start <= stop:
                    tss.append(spans.Timespan(start, stop))
                else:
                    tss.append(spans.Timespan(stop, start))
            tsTree = TimespanTree()

            for i, timespan in enumerate(tss):
                tsTree.insert(timespan)
                currentTimespansInList = list(sorted(tss[:i + 1],
                                                     key=lambda x: (x.offset, x.endTime)))
                currentTimespansInTree = list(tsTree)
                currentPosition = min(x.offset for x in currentTimespansInList)
                currentEndTime = max(x.endTime for x in currentTimespansInList)

                self.assertEqual(currentTimespansInTree,
                                 currentTimespansInList,
                                 (attempt, currentTimespansInTree, currentTimespansInList))
                self.assertEqual(tsTree.rootNode.endTimeLow,
                                 min(x.endTime for x in currentTimespansInList))
                self.assertEqual(tsTree.rootNode.endTimeHigh,
                                 max(x.endTime for x in currentTimespansInList))
                self.assertEqual(tsTree.lowestPosition(), currentPosition)
                self.assertEqual(tsTree.endTime, currentEndTime)
                for inList, inTree in zip(currentTimespansInList, currentTimespansInTree):
                    self.assertEqual(inList, inTree)

            random.shuffle(tss)
            while tss:
                timespan = tss.pop()
                currentTimespansInList = sorted(tss,
                                                key=lambda x: (x.offset, x.endTime))
                tsTree.removeTimespan(timespan)
                currentTimespansInTree = list(tsTree)
                self.assertEqual(currentTimespansInTree,
                                 currentTimespansInList,
                                 (attempt, currentTimespansInTree, currentTimespansInList))
                if tsTree.rootNode is not None:
                    currentPosition = min(x.offset for x in currentTimespansInList)
                    currentEndTime = max(x.endTime for x in currentTimespansInList)
                    self.assertEqual(tsTree.rootNode.endTimeLow,
                                     min(x.endTime for x in currentTimespansInList))
                    self.assertEqual(tsTree.rootNode.endTimeHigh,
                                     max(x.endTime for x in currentTimespansInList))
                    self.assertEqual(tsTree.lowestPosition(), currentPosition)
                    self.assertEqual(tsTree.endTime, currentEndTime)
                    for inList, inTree in zip(currentTimespansInList, currentTimespansInTree):
                        self.assertEqual(inList, inTree)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
