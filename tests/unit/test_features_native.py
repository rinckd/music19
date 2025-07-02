# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.features.native import *


class Test(unittest.TestCase):

    def testIncorrectlySpelledTriadPrevalence(self):
        from music21 import stream
        from music21 import features
        from music21 import chord

        s = stream.Stream()
        s.append(chord.Chord(['c', 'e', 'g']))
        s.append(chord.Chord(['c', 'e', 'a']))
        s.append(chord.Chord(['c', 'd#', 'g']))
        s.append(chord.Chord(['c', 'd#', 'a--']))

        fe = features.native.IncorrectlySpelledTriadPrevalence(s)
        self.assertEqual(str(fe.extract().vector[0]), '0.5')

    def testLandiniCadence(self):
        from music21 import converter
        from music21 import features

        s = converter.parse('tinynotation: 3/4 f#4 f# e g2')
        fe = features.native.LandiniCadence(s)
        self.assertEqual(fe.extract().vector[0], 1)

        s = converter.parse('tinynotation: 3/4 f#4 f# f# g2')
        fe = features.native.LandiniCadence(s)
        self.assertEqual(fe.extract().vector[0], 0)

        s = converter.parse('tinynotation: 3/4 f#4 e a g2')
        fe = features.native.LandiniCadence(s)
        self.assertEqual(fe.extract().vector[0], 0)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
