# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.key import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testBasic(self):
        a = KeySignature()
        self.assertEqual(a.sharps, 0)

    def testSetTonic(self):
        from music21 import chord
        k = Key()

        # Set tonic attribute from single pitch
        b = pitch.Pitch('B')
        k.tonic = b
        self.assertIs(k.tonic, b)

        # Initialize with tonic from chord - no longer allowed.
        # Call root explicitly
        b_flat_maj = chord.Chord('Bb4 D5 F5').root()
        k = Key(tonic=b_flat_maj)
        self.assertEqual(k.tonic.name, 'B-')

    def testTonalAmbiguityA(self):
        from music21 import corpus
        from music21 import stream
        # s = corpus.parse('bwv64.2')
        # k = s.analyze('KrumhanslSchmuckler')
        # k.tonalCertainty(method='correlationCoefficient')

        s = corpus.parse('bwv66.6')
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        s = corpus.parse('schoenberg/opus19', 6)
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        sc1 = scale.MajorScale('g')
        sc2 = scale.MajorScale('d')
        sc3 = scale.MajorScale('a')
        sc5 = scale.MajorScale('f#')

        s = stream.Stream()
        for p in sc1.pitches:
            s.append(note.Note(p))
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        s = stream.Stream()
        for p in sc1.pitches + sc2.pitches + sc2.pitches + sc3.pitches:
            s.append(note.Note(p))
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        s = stream.Stream()
        for p in sc1.pitches + sc5.pitches:
            s.append(note.Note(p))
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        s = stream.Stream()
        for p in ('c', 'g', 'c', 'c', 'e'):
            s.append(note.Note(p))
        k = s.analyze('KrumhanslSchmuckler')
        ta = k.tonalCertainty(method='correlationCoefficient')
        self.assertTrue(2 > ta > 0.1)

        # s = corpus.parse('bwv66.2')
        # k = s.analyze('KrumhanslSchmuckler')
        # k.tonalCertainty(method='correlationCoefficient')
        # s = corpus.parse('bwv48.3')

    def testAsKey(self):
        ks = KeySignature(2)

        k = ks.asKey(mode=None, tonic=None)
        self.assertEqual(k.mode, 'major')
        self.assertEqual(k.tonicPitchNameWithCase, 'D')

        k = ks.asKey(tonic='E')
        self.assertEqual(k.mode, 'dorian')
        self.assertEqual(k.tonicPitchNameWithCase, 'E')

        expected = 'ignoring provided tonic: E'
        with self.assertWarnsRegex(KeyWarning, expected) as cm:
            # warn user we ignored their tonic
            k = ks.asKey(mode='minor', tonic='E')
        self.assertEqual(k.mode, 'minor')
        self.assertEqual(k.tonicPitchNameWithCase, 'b')

        expected = 'Could not solve for mode from sharps=2, tonic=A-'
        with self.assertRaisesRegex(KeyException, expected) as cm:
            k = ks.asKey(mode=None, tonic='A-')
        # test exception chained from KeyError
        self.assertIsInstance(cm.exception.__cause__, KeyError)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
