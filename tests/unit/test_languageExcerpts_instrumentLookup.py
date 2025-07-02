# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.languageExcerpts.instrumentLookup import *


class Test(unittest.TestCase):

    def testAllToClassNamePopulated(self):
        '''
        Test that the allToClassName dict includes all the keys from the constituent dicts.

        Note: No length test due to duplicate entries
        (i.e. allToClassName is smaller than the sum of its parts).
        '''
        for eachDict in [abbreviationToClassName,
                         englishToClassName,
                         frenchToClassName,
                         germanToClassName,
                         italianToClassName,
                         russianToClassName,
                         spanishToClassName]:

            for key in eachDict:
                self.assertIn(key, allToClassName)

    def testAllToClassNameExamples(self):
        '''
        Test an example from each constituent dict that makes up allToClassName.
        '''

        for testString, langDict in [('a sax', abbreviationToClassName),
                                     ('accordion', englishToClassName),
                                     ('accord\xe9on', frenchToClassName),
                                     ('aeolophon', germanToClassName),
                                     ('a becco', italianToClassName),
                                     ("al't", russianToClassName),
                                     ('acorde\xf3n', spanishToClassName)
                                     ]:
            self.assertEqual(allToClassName[testString], langDict[testString])

    def testAllClassNames(self):
        '''
        Test that all class names are real.
        '''
        from music21 import instrument as instr
        for v in allToClassName.values():
            with self.subTest(name=v):
                getattr(instr, v)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
