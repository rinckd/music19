# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.figuredBass.realizer import *


class Test(unittest.TestCase):
    def testMultipleFiguresInLyric(self):
        from music21 import converter

        s = converter.parse('tinynotation: 4/4 C4 F4 G4_64 G4 C1', makeNotation=False)
        third_note = s[note.Note][2]
        self.assertEqual(third_note.lyric, '64')
        unused_fb = figuredBassFromStream(s)
        self.assertEqual(third_note.editorial.notationString, '6, 4')

        third_note.lyric = '#6#42'
        unused_fb = figuredBassFromStream(s)
        self.assertEqual(third_note.editorial.notationString, '#6, #4, 2')

        third_note.lyric = '#64#2'
        unused_fb = figuredBassFromStream(s)
        self.assertEqual(third_note.editorial.notationString, '#6, 4, #2')

        # original case
        third_note.lyric = '6\n4'
        unused_fb = figuredBassFromStream(s)
        self.assertEqual(third_note.editorial.notationString, '6, 4')

        # single accidental
        for single_symbol in '+#bn':
            with self.subTest(single_symbol=single_symbol):
                third_note.lyric = single_symbol
                unused_fb = figuredBassFromStream(s)
                self.assertEqual(third_note.editorial.notationString, single_symbol)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
