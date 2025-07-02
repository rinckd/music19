# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.stream.iterator import *


class Test(unittest.TestCase):
    def testSimpleClone(self):
        from music21 import stream
        s = stream.Stream()
        r = note.Rest()
        n = note.Note()
        s.append([r, n])
        all_s = list(s.iter())
        self.assertEqual(len(all_s), 2)
        self.assertIs(all_s[0], r)
        self.assertIs(all_s[1], n)
        s_notes = list(s.iter().notes)
        self.assertEqual(len(s_notes), 1)
        self.assertIs(s_notes[0], n)

    def testAddingFiltersMidIteration(self):
        from music21 import stream
        s = stream.Stream()
        r = note.Rest()
        n = note.Note()
        s.append([r, n])
        sIter = s.iter()
        r0 = next(sIter)
        self.assertIs(r0, r)

        # adding a filter gives a new StreamIterator that restarts at 0
        sIter2 = sIter.notesAndRests  # this filter does nothing here.
        obj0 = next(sIter2)
        self.assertIs(obj0, r)

        # the original StreamIterator should be at its original spot, so this should
        # move to the next element
        n0 = next(sIter)
        self.assertIs(n0, n)

    def testRecursiveActiveSites(self):
        from music21 import converter
        s = converter.parse('tinyNotation: 4/4 c1 c4 d=id2 e f')
        rec = s.recurse()
        n = rec.getElementById('id2')
        self.assertEqual(n.activeSite.number, 2)

    def testCurrentHierarchyOffsetReset(self):
        from music21 import stream
        p = stream.Part()
        m = stream.Measure()
        m.append(note.Note('D'))
        m.append(note.Note('E'))
        p.insert(0, note.Note('C'))
        p.append(m)
        pRecurse = p.recurse(includeSelf=True)
        allOffsets = []
        for _ in pRecurse:
            allOffsets.append(pRecurse.currentHierarchyOffset())
        self.assertListEqual(allOffsets, [0.0, 0.0, 1.0, 1.0, 2.0])
        currentOffset = pRecurse.currentHierarchyOffset()
        self.assertIsNone(currentOffset)

    def testAddingFiltersMidRecursiveIteration(self):
        from music21 import stream
        # noinspection PyUnresolvedReferences
        from music21.stream.iterator import RecursiveIterator as ImportedRecursiveIterator
        m = stream.Measure()
        r = note.Rest()
        n = note.Note()
        m.append([r, n])
        p = stream.Part()
        p.append(m)

        sc = stream.Score()
        sc.append(p)

        sIter = sc.recurse()
        p0 = next(sIter)
        self.assertIs(p0, p)

        child = sIter.childRecursiveIterator
        self.assertIsInstance(child, ImportedRecursiveIterator)




_DOC_ORDER = [StreamIterator, RecursiveIterator, OffsetIterator]


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
