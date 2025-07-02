# -*- coding: utf-8 -*-
# Migrated from embedded tests
import pathlib
import unittest

from music21.common.pathTools import *


class Test(unittest.TestCase):
    def testGetSourcePath(self):
        fp = getSourceFilePath()
        self.assertIsInstance(fp, pathlib.Path)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
