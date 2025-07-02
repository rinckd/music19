# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.tree.fromStream import *


class Test(unittest.TestCase):

    def testFastPopulate(self):
        '''
        tests that the isSorted speed up trick ends up producing identical results.
        '''
        from music21 import corpus
        sf = corpus.parse('bwv66.6').flatten()
        sfTree = sf.asTree()
        # print(sfTree)

        sf.isSorted = False
        sf._cache = {}
        sfTreeSlow = sf.asTree()
        self.assertEqual(len(sf), len(sfTreeSlow))
        self.assertEqual(len(sf), len(sfTree))
        for fastI, slowI in zip(sfTree, sfTreeSlow):
            self.assertIs(fastI, slowI)

    def testAutoSortExample(self):
        from music21.tree import makeExampleScore
        sc = makeExampleScore()
        sc.sort()
        scTree = asTree(sc)
        self.assertEqual(scTree.endTime, 8.0)
        # print(repr(scTree))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
