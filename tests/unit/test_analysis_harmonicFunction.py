# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.harmonicFunction import *


class Test(unittest.TestCase):
    def testAllFunctionLabelsInEnum(self):
        '''
        Test that all the entries in the functionFigureTuples
        (both major and minor) are represented in the HarmonicFunction enum.

        Also tests one fake (invalid) function label.
        '''
        # All and only valid
        for thisHarmonicFunction in functionFigureTuplesMajor:
            HarmonicFunction(thisHarmonicFunction)
        for thisHarmonicFunction in functionFigureTuplesMinor:
            HarmonicFunction(thisHarmonicFunction)

        # Invalid
        fakeExample = 'TPG'
        self.assertRaises(ValueError, HarmonicFunction, fakeExample)

    def testFunctionToRoman(self):
        self.assertEqual(functionToRoman(HarmonicFunction.TONIC_MAJOR).figure, 'I')

    def testSimplified(self):
        rn = roman.RomanNumeral('III', 'f')

        fn1 = romanToFunction(rn)
        self.assertIs(fn1, HarmonicFunction.TONIC_MINOR_PARALLELKLANG_MAJOR)
        self.assertEqual(str(fn1), 'tP')

        fn2 = romanToFunction(rn, onlyHauptHarmonicFunction=True)
        self.assertIs(fn2, HarmonicFunction.TONIC_MINOR)
        self.assertEqual(str(fn2), 't')

    def testIgnoresInversion(self):
        self.assertEqual(romanToFunction(roman.RomanNumeral('i6')), 't')


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
