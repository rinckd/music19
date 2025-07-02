# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.sieve import *


class Test(unittest.TestCase):

    def testDummy(self):
        self.assertEqual(True, True)

    def pitchOut(self, listIn):
        out = '['
        for p in listIn:
            out += str(p) + ', '
        out = out[0:len(out) - 2]
        out += ']'
        return out

    def testIntersection(self):
        a = Residual(3)
        testArgs = [(3, 6, 2, 5), (4, 6, 1, 3), (5, 4, 3, 2), ]
        for m1, m2, n1, n2 in testArgs:
            a = Residual(m1, n1)
            b = Residual(m2, n2)
            i = a & b           # do intersection

    def testSieveParse(self):
        testArgs = ['-5 | 4 & 4sub3 & 6 | 4 & 4',
                    '2 or 4 and 4 & 6 or 4 & 4',
                    3,
                    # '3 and 4 or not 3, 1 and 4, 1 or not 3 and 4, 2 or not 3, 2 and 4, 3',
                    (2, 4, 6, 8),
                    (1, 6, 11, 16, 17),
                    ]
        for arg in testArgs:
            # environLocal.printDebug(['testSieveParse', arg])
            testObj = Sieve(arg)
            dummy = testObj(0, list(range(30)))

    def testSievePitch(self):
        unused_testObj = PitchSieve('-5 | 4 & 4sub3 & 6', 'b3', 'f#4')
        testObj = PitchSieve('-5 | 4 & 4sub3 & 6')
        dummy = testObj.pitchLower, testObj.pitchUpper
        dummy = testObj()

    def testTimePoint(self):
        args = [(3, 6, 12),
                (0, 6, 12, 15, 18, 24, 30, 36, 42),
                (4, 6, 13),
                (2, 3, 4, 5, 8, 9, 10, 11, 14, 17, 19, 20, 23, 24, 26, 29, 31),
                #  (3, 23, 33, 47, 63, 70, 71, 93, 95, 119, 123, 143, 153, 167),
                (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24),
                (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                (-8, -6, -4, -2, 0, 2, 1),
                ]
        for src in args:
            obj = CompressionSegment(src)
            sObj = Sieve(str(obj))
            dummy = sObj()

    def testSieve(self):
        z = list(range(100))
        usrStr = '3@2 & 4@1 | 2@0 & 3@1 | 3@3 | -4@2'
        a = Sieve(usrStr, z)
        self.assertEqual(str(a), '3@2&4@1|2@0&3@1|3@0|-4@2')

        usrStr = '-(3@2 & -4@1 & -(12@3 | 12@8) | (-2@0 & 3@1 | (3@3)))'
        a = Sieve(usrStr, z)
        self.assertEqual(str(a), '-{3@2&-4@1&-{12@3|12@8}|{-2@0&3@1|{3@0}}}')

        # 'example from Flint, on Psapha'
        usrStr = ('[(8@0 | 8@1 | 8@7) & (5@1 | 5@3)] |   [(8@0 | 8@1 | 8@2) & 5@0] | '
                  '[8@3 & (5@0 | 5@1 | 5@2 | 5@3 | 5@4)] | '
                  '[8@4 & (5@0 | 5@1 | 5@2 | 5@3 | 5@4)] | '
                  '[(8@5 | 8@6) & (5@2 | 5@3 | 5@4)] | (8@1 & 5@2) | (8@6 & 5@1)')
        a = Sieve(usrStr, z)
        self.assertEqual(str(a),
                         '{{8@0|8@1|8@7}&{5@1|5@3}}|{{8@0|8@1|8@2}&5@0}|'
                         '{8@3&{5@0|5@1|5@2|5@3|5@4}}|{8@4&{5@0|5@1|5@2|5@3|5@4}}|'
                         '{{8@5|8@6}&{5@2|5@3|5@4}}|{8@1&5@2}|{8@6&5@1}')

        # 'major scale from FM, p197'
        usrStr = '(-3@2 & 4) | (-3@1 & 4@1) | (3@2 & 4@2) | (-3 & 4@3)'
        a = Sieve(usrStr, z)
        self.assertEqual(str(a), '{-3@2&4@0}|{-3@1&4@1}|{3@2&4@2}|{-3@0&4@3}')

        # 'nomos alpha sieve'
        usrStr = ('(-(13@3 | 13@5 | 13@7 | 13@9) & 11@2) | (-(11@4 | 11@8) & 13@9) | '
                  '(13@0 | 13@1 | 13@6)')
        a = Sieve(usrStr, z)
        self.assertEqual(str(a),
                         '{-{13@3|13@5|13@7|13@9}&11@2}|{-{11@4|11@8}&13@9}|{13@0|13@1|13@6}')

    def testPitchSieveA(self):
        from music21 import sieve

        s1 = sieve.PitchSieve('3@0|7@0', 'c2', 'c6')
        self.assertEqual(self.pitchOut(s1()),
                         '[C2, E-2, F#2, G2, A2, C3, D3, E-3, F#3, A3, C4, E-4, '
                         'E4, F#4, A4, B4, C5, E-5, F#5, A5, C6]')

        s1 = sieve.PitchSieve('3@0|7@0', 'c2', 'c6', eld=2)
        self.assertEqual(self.pitchOut(s1()),
                         '[C2, D2, F#2, C3, E3, F#3, C4, F#4, C5, F#5, G#5, C6]')

    def testPitchSieveB(self):
        from music21 import sieve

        # mircotonal elds
        s1 = sieve.PitchSieve('1@0', 'c2', 'c6', eld=0.5)
        self.assertEqual(self.pitchOut(s1()),
                         '[C2, C~2, C#2, C#~2, D2, D~2, E-2, E`2, E2, E~2, F2, F~2, F#2, '
                         'F#~2, G2, G~2, G#2, G#~2, A2, A~2, B-2, B`2, B2, B~2, C3, C~3, C#3, '
                         'C#~3, D3, D~3, E-3, E`3, E3, E~3, F3, F~3, F#3, F#~3, G3, G~3, G#3, '
                         'G#~3, A3, A~3, B-3, B`3, B3, B~3, C4, C~4, C#4, C#~4, D4, D~4, E-4, '
                         'E`4, E4, E~4, F4, F~4, F#4, F#~4, G4, G~4, G#4, G#~4, A4, A~4, B-4, '
                         'B`4, B4, B~4, C5, C~5, C#5, C#~5, D5, D~5, E-5, E`5, E5, E~5, F5, F~5, '
                         'F#5, F#~5, G5, G~5, G#5, G#~5, A5, A~5, B-5, B`5, B5, B~5, C6]')

        s1 = sieve.PitchSieve('3@0', 'c2', 'c6', eld=0.5)
        self.assertEqual(self.pitchOut(s1()),
                         '[C2, C#~2, E-2, E~2, F#2, G~2, A2, B`2, C3, C#~3, E-3, E~3, F#3, G~3, '
                         'A3, B`3, C4, C#~4, E-4, E~4, F#4, G~4, A4, B`4, C5, C#~5, E-5, E~5, F#5, '
                         'G~5, A5, B`5, C6]')

# sieve that breaks LCM
# >>> t = sieve.Sieve((3, 99, 123123, 2433, 2050))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
