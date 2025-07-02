# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.corpus.testCorpus import *


class Test(unittest.TestCase):

    def testGetPaths(self):
        for known in [
            'schumann_clara/opus17/movement3.xml',
            'schoenberg/opus19/movement2.mxl',
            'palestrina/agnus_02.krn',
        ]:
            a = corpus.getWork(known)
            # make sure it is not an empty list
            self.assertTrue(a)
            workSlashes = re.sub(r'\\', '/', str(a))
            self.assertTrue(workSlashes.lower().endswith(known.lower()), (workSlashes, known))

    def testBachKeys(self):
        from music21 import key
        keyObjs = []
        for filePath in corpus.getComposer('bach')[23:28]:  # get 5 in the middle
            s = corpus.parse(filePath)
            # get keys from first part
            keyObj = s.parts[0][key.KeySignature].first()
            keyObjs.append(keyObj)
            # environLocal.printDebug([keyObj])
        self.assertEqual(len(keyObjs), 5)


    def testSearch05(self):
        searchResults = corpus.search('bach')
        self.assertGreater(len(searchResults), 120)

    def testSearch06(self):
        searchResults = corpus.search('haydn', field='composer')
        self.assertEqual(len(searchResults), 0)
        searchResults = corpus.search('haydn|bach', field='composer')
        self.assertGreaterEqual(len(searchResults), 16)

    def testSearch07(self):
        searchResults = corpus.search('canon')
        self.assertGreaterEqual(len(searchResults), 1)

    def testSearch10(self):
        from music21 import key
        ks = key.KeySignature(3)
        searchResults = corpus.search(ks, field='keySignature')
        self.assertEqual(len(searchResults) >= 32, True, len(searchResults))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
