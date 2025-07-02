# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.graph.utilities import *


class Test(unittest.TestCase):
    def testColors(self):
        self.assertEqual(getColor([0.5, 0.5, 0.5]), '#808080')
        self.assertEqual(getColor(0.5), '#808080')
        self.assertEqual(getColor(255), '#ffffff')
        self.assertEqual(getColor('Steel Blue'), '#4682b4')


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
