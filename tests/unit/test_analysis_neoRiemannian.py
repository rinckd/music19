# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.analysis.neoRiemannian import *


class Test(unittest.TestCase):

    def testNeoRiemannianTransformations(self):
        c2 = chord.Chord('C4 E-4 G4')
        c2_L = L(c2)
        c2_P = P(c2)
        self.assertEqual(str(c2_L), '<music21.chord.Chord C4 E-4 A-4>')
        self.assertIsInstance(c2_L, chord.Chord)
        self.assertEqual(str(c2_P), '<music21.chord.Chord C4 E4 G4>')

        c5 = chord.Chord('C4 E4 G4 C5 C5 G5')
        copyC5 = copy.deepcopy(c5)
        for i in range(4):
            c5 = L(c5)
        self.assertEqual(copyC5.pitches, c5.pitches)

        c5 = chord.Chord('C4 E4 G4 C5 E5 G5')
        copyC5 = copy.deepcopy(c5)
        for i in range(4):
            c5 = P(c5)
        self.assertEqual(copyC5.pitches, c5.pitches)

        c5 = chord.Chord('C4 E4 G4 C5 C5 G5')
        copyC5 = copy.deepcopy(c5)
        for i in range(4):
            c5 = R(c5)
        self.assertEqual(copyC5.pitches, c5.pitches)

    def testNeoRiemannianCombinations(self):
        c5 = chord.Chord('C4 E4 G4')
        c5_T = LRP_combinations(c5, 'LP')
        self.assertEqual(str(c5_T), '<music21.chord.Chord B3 E4 G#4>')

        c6 = chord.Chord('C4 E4 G4 C5 E5')
        c6_T = LRP_combinations(c6, 'RLP')
        self.assertEqual(str(c6_T), '<music21.chord.Chord C4 F4 A-4 C5 F5>')

        c7 = chord.Chord('C4 E4 G4 C5 E5')
        c7_T = LRP_combinations(c7, 'LP', leftOrdered=True)
        self.assertEqual(str(c7_T), '<music21.chord.Chord C4 E-4 A-4 C5 E-5>')

        c8 = chord.Chord('C-4 E-4 G-4')
        c8_T = LRP_combinations(c8, 'LP')
        self.assertEqual(str(c8_T), '<music21.chord.Chord B-3 E-4 G4>')

        d_sharp_min_misspelled = chord.Chord('B- D# F#')
        d_sharp_min_transformed = LRP_combinations(d_sharp_min_misspelled, 'LP',
                                                   raiseException=False)
        self.assertIs(d_sharp_min_misspelled, d_sharp_min_transformed)
        with self.assertRaises(LRPException):
            LRP_combinations(d_sharp_min_misspelled, 'LP', raiseException=True)

        f_min_misspelled = chord.Chord('B# F G#')
        with self.assertRaises(LRPException):
            LRP_combinations(f_min_misspelled, 'LP', raiseException=True)

        e_sharp_min = chord.Chord('B# E# G#')
        e_sharp_min_transformed = LRP_combinations(e_sharp_min, 'LP', raiseException=True)
        self.assertEqual(chord.Chord('C# E G#').pitches, e_sharp_min_transformed.pitches)



    def testSnN(self):

        c10 = chord.Chord('C5 E5 G5')
        c11 = chord.Chord('A4 C5 E5')

        slideUp = S(c10)
        self.assertEqual([x.name for x in slideUp.pitches], ['C#', 'E', 'G#'])

        slideDown = S(c11)
        self.assertEqual([x.name for x in slideDown.pitches], ['A-', 'C', 'E-'])

        N1 = N(c10)
        self.assertEqual([x.name for x in N1.pitches], ['C', 'F', 'A-'])

        N2 = N(c11)
        self.assertEqual([x.name for x in N2.pitches], ['G#', 'B', 'E'])

    def testInstantiatingChordPCNumbers(self):

        c_sharp_maj_named_transformed = L(chord.Chord('C# E# G#'))
        c_sharp_maj_pitch_classes_transformed = L(chord.Chord([1, 5, 8]))
        self.assertEqual(c_sharp_maj_named_transformed.pitches,
                         c_sharp_maj_pitch_classes_transformed.pitches)
        self.assertEqual(c_sharp_maj_pitch_classes_transformed.pitches,
                         chord.Chord('B# E# G#').pitches)

        b_maj_named = chord.Chord('B D# F#')
        b_maj_named_transformed = LRP_combinations(b_maj_named, 'LP',
                                                   simplifyEnharmonics=False)
        b_maj_pitch_classes = chord.Chord([11, 3, 6])
        b_maj_pitch_classes_transformed = LRP_combinations(b_maj_pitch_classes, 'LP',
                                                           simplifyEnharmonics=False)
        self.assertTrue(b_maj_pitch_classes.pitches[0].spellingIsInferred)
        for p in b_maj_pitch_classes_transformed.pitches:
            self.assertFalse(p.spellingIsInferred)

        self.assertEqual(b_maj_named_transformed.pitches,
                         b_maj_pitch_classes_transformed.pitches)
        self.assertEqual(b_maj_pitch_classes_transformed.pitches,
                         chord.Chord('A# D# F##').pitches)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
