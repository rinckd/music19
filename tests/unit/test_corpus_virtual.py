# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.corpus.virtual import *


class Test(unittest.TestCase):

    def testBasic(self):
        '''
        Test instantiating all objects defined in the virtual corpus module
        '''
        a = BachBWV1007Prelude()
        self.assertNotEqual(a.getUrlByExt(['.xml']), [])
        self.assertNotEqual(a.getUrlByExt(['.krn']), [])
        BachBWV772()
        BachBWV773()
        ColtraneGiantSteps()
        SchubertD576()
        SchubertD5762()
        SchubertD5763()
        SchubertD5764()
        PachelbelCanonD()


class TestExternal(unittest.TestCase):
    # interpreter loading
    pass


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
