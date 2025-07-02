# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.common.parallel import *


class Test(unittest.TestCase):
    # pylint: disable=redefined-outer-name
    def x_figure_out_segfault_testMultiprocess(self):
        files = ['bach/bwv66.6', 'schoenberg/opus19', 'AcaciaReel']
        # for importing into testSingleCoreAll we need the full path to the modules
        from music21.common.parallel import _countN, _countUnpacked
        output = runParallel(files, _countN)
        self.assertEqual(output, [165, 50, 131])
        runParallel(files, _countN,
                    updateFunction=self._customUpdate1)
        runParallel(files, _countN,
                    updateFunction=self._customUpdate2,
                    updateSendsIterable=True)
        passed = runParallel(list(enumerate(files)), _countUnpacked,
                             unpackIterable=True)
        self.assertEqual(len(passed), 3)
        self.assertNotIn(False, passed)

    # testing functions
    def _customUpdate1(self, i, total, output):
        self.assertEqual(total, 3)
        self.assertLess(i, 3)
        self.assertIn(output, [165, 50, 131])

    def _customUpdate2(self, i, unused_total, unused_output, fn):
        self.assertIn(fn, ['bach/bwv66.6', 'schoenberg/opus19', 'AcaciaReel'])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
