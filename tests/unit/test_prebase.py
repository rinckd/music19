# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.prebase import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def test_reprInternal(self):
        from music21.base import Music21Object
        b = Music21Object()
        b.id = 'hello'
        r = repr(b)
        self.assertEqual(r, '<music21.base.Music21Object id=hello>')


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
