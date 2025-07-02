# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.text import *


class Test(unittest.TestCase):

    def testBasic(self):
        from music21 import converter
        from music21 import corpus

        a = converter.parse(corpus.getWork('haydn/opus1no1/movement4.xml'))
        post = assembleLyrics(a)
        self.assertEqual(post, '')  # no lyrics!

        a = converter.parse(corpus.getWork('luca/gloria'))
        post = assembleLyrics(a)
        self.assertTrue(post.startswith('Et in terra pax hominibus bone voluntatis'))


    def testAssembleLyricsA(self):
        from music21 import stream
        from music21 import note
        s = stream.Stream()
        for syl in ['hel-', '-lo', 'a-', '-gain']:
            n = note.Note()
            n.lyric = syl
            s.append(n)
        post = assembleLyrics(s)
        self.assertEqual(post, 'hello again')

        s = stream.Stream()
        for syl in ['a-', '-ris-', '-to-', '-cats', 'are', 'great']:
            n = note.Note()
            n.lyric = syl
            s.append(n)
        post = assembleLyrics(s)
        # noinspection SpellCheckingInspection
        self.assertEqual(post, 'aristocats are great')

        s = stream.Stream()
        for syl in ['长', '亭', '外', '古', '道', '边']:
            n = note.Note()
            n.lyric = syl
            s.append(n)
        post = assembleLyrics(s, wordSeparator='')
        # custom word separator
        self.assertEqual(post, '长亭外古道边')

    # noinspection SpellCheckingInspection
    def testLanguageDetector(self):
        ld = LanguageDetector()
        diffFrIt = ld.trigrams['fr'] - ld.trigrams['it']
        self.assertTrue(0.50 < diffFrIt < 0.55)
        self.assertTrue(0.67 < ld.trigrams['fr'] - ld.trigrams['de'] < 0.70)
        self.assertTrue(0.99 < ld.trigrams['fr'] - ld.trigrams['cn'] < 1.0)

        self.assertEqual('en',
                         ld.mostLikelyLanguage('hello friends, this is a test of the '
                                               + 'ability of language detector to '
                                               + 'tell what language I am writing in.'))
        self.assertEqual('it', ld.mostLikelyLanguage(
            'ciao amici! cosé trovo in quale lingua ho scritto questo passaggio. Spero che '
            + 'troverà che é stata scritta in italiano'))

        # TODO: Replace
        # messiahGovernment = corpus.parse('handel/hwv56/movement1-13.md')
        # forUntoUs = assembleLyrics(messiahGovernment)
        # self.assertTrue(forUntoUs.startswith('For unto us a child is born'))
        # forUntoUs = forUntoUs.replace('_', '')
        # self.assertEqual('en', ld.mostLikelyLanguage(forUntoUs))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
