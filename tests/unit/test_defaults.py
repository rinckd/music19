# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.defaults import *


class Test(unittest.TestCase):
    '''
    Unit tests
    '''
    def testTest(self):
        self.assertEqual(1, 1)


# ----------------------------------------------------------------||||||||||||--


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
