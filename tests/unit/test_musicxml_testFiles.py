# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.musicxml.testFiles import *


class Test(unittest.TestCase):

    def testBasic(self):
        from music21 import converter
        for testMaterial in ALL[:1]:
            unused = converter.parse(testMaterial)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
