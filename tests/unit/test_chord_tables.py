# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.chord.tables import *


class Test(unittest.TestCase):

    def testDummy(self):
        self.assertEqual(True, True)

    def testTnIndexToChordInfo(self):
        for key, value in tnIndexToChordInfo.items():
            self.assertEqual(len(key), 3)
            if value:
                # if we have keys, make sure that name is one of them
                self.assertTrue('name' in value)

    def testForteNumberWithInversionToTnIndex(self):
        partition = {}
        for key, value in forteNumberWithInversionToTnIndex.items():
            self.assertEqual(len(key), 3)
            # the third value of the key should be -1, 1, or 0
            self.assertTrue(key[2] in [-1, 0, 1])
            if key[0] not in partition:
                partition[key[0]] = []
                partition[key[0]].append(value)  # append unique ids
            else:
                partition[key[0]].append(value)  # append unique ids

        for key, value in partition.items():
            # the length of the list should be the max value stored
            self.assertEqual(max(value), len(value))

    def testCardinalityToChordMembers(self):
        for key, value in cardinalityToChordMembers.items():
            maxVal = maximumIndexNumberWithoutInversionEquivalence[key]
            # make sure the max value is the length of all keys for each size
            self.assertEqual(maxVal, len(value.keys()))

    def testForte(self):
        set_info = maximumIndexNumberWithInversionEquivalence.items()
        for setSize, setCount in set_info:  # look at TnI structures
            if setSize == 0:
                continue
            for i in range(1, setCount + 1):
                self.assertEqual(len(FORTE[setSize][1]), 4)
            # must subtract one b/c all groups contain a zero set to pad
            # index values
            self.assertEqual(len(FORTE[setSize]) - 1, setCount)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
