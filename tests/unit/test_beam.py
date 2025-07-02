# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.beam import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
