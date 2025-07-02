# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.scale.scala import *


class Test(unittest.TestCase):

    def testScalaScaleA(self):
        msg = '''! slendro5_2.scl
!
A slendro type pentatonic which is based on intervals of 7, no. 2
 5
!
 7/6
 4/3
 3/2
 7/4
 2/1
'''
        ss = ScalaData(msg)
        ss.parse()
        self.assertEqual(ss.pitchCount, 5)
        self.assertEqual(ss.fileName, 'slendro5_2.scl')
        self.assertEqual(len(ss.pitchValues), 5)
        self.assertEqual([f'{x.cents:.9f}' for x in ss.pitchValues],
                         ['266.870905604', '498.044999135', '701.955000865',
                          '968.825906469', '1200.000000000'])

        self.assertEqual([f'{x:.9f}' for x in ss.getCentsAboveTonic()],
                         ['266.870905604', '498.044999135', '701.955000865',
                          '968.825906469', '1200.000000000'])
        # sent values between scale degrees
        self.assertEqual([f'{x:.9f}' for x in ss.getAdjacentCents()],
                         ['266.870905604', '231.174093531', '203.910001731',
                          '266.870905604', '231.174093531'])

        self.assertEqual([str(x) for x in ss.getIntervalSequence()],
                         ['<music21.interval.Interval m3 (-33c)>',
                          '<music21.interval.Interval M2 (+31c)>',
                          '<music21.interval.Interval M2 (+4c)>',
                          '<music21.interval.Interval m3 (-33c)>',
                          '<music21.interval.Interval M2 (+31c)>'])

    # noinspection SpellCheckingInspection
    def testScalaScaleB(self):
        msg = '''! fj-12tet.scl
!
Franck Jedrzejewski continued fractions approx. of 12-tet
 12
!
89/84
55/49
44/37
63/50
4/3
99/70
442/295
27/17
37/22
98/55
15/8
2/1
'''
        ss = ScalaData(msg)
        ss.parse()
        self.assertEqual(ss.pitchCount, 12)
        self.assertEqual(ss.fileName, 'fj-12tet.scl')
        self.assertEqual(ss.description,
                         'Franck Jedrzejewski continued fractions approx. of 12-tet')

        self.assertEqual([f'{x:.9f}' for x in ss.getCentsAboveTonic()], ['100.099209825',
                                                                         '199.979843291',
                                                                         '299.973903610',
                                                                         '400.108480470',
                                                                         '498.044999135',
                                                                         '600.088323762',
                                                                         '699.997698171',
                                                                         '800.909593096',
                                                                         '900.026096390',
                                                                        '1000.020156709',
                                                                        '1088.268714730',
                                                                        '1200.000000000'])

        self.assertEqual([f'{x:.9f}' for x in ss.getAdjacentCents()], ['100.099209825',
                                                                        '99.880633466',
                                                                        '99.994060319',
                                                                       '100.134576860',
                                                                        '97.936518664',
                                                                       '102.043324627',
                                                                        '99.909374409',
                                                                       '100.911894925',
                                                                        '99.116503294',
                                                                        '99.994060319',
                                                                        '88.248558022',
                                                                       '111.731285270'])

        self.assertEqual([str(x) for x in ss.getIntervalSequence()],
                         ['<music21.interval.Interval m2 (+0c)>',
                          '<music21.interval.Interval m2 (-0c)>',
                          '<music21.interval.Interval m2 (-0c)>',
                          '<music21.interval.Interval m2 (+0c)>',
                          '<music21.interval.Interval m2 (-2c)>',
                          '<music21.interval.Interval m2 (+2c)>',
                          '<music21.interval.Interval m2 (-0c)>',
                          '<music21.interval.Interval m2 (+1c)>',
                          '<music21.interval.Interval m2 (-1c)>',
                          '<music21.interval.Interval m2 (-0c)>',
                          '<music21.interval.Interval m2 (-12c)>',
                          '<music21.interval.Interval m2 (+12c)>'])


        # test loading a new scala object from adjacent sets
        ss2 = ScalaData()
        ss2.setAdjacentCents(ss.getAdjacentCents())

        self.assertEqual([f'{x:.9f}' for x in ss2.getCentsAboveTonic()],
                         [
                             '100.099209825',
                             '199.979843291',
                             '299.973903610',
                             '400.108480470',
                             '498.044999135',
                             '600.088323762',
                             '699.997698171',
                             '800.909593096',
                             '900.026096390',
                             '1000.020156709',
                             '1088.268714730',
                             '1200.000000000'])

    def testScalaFileA(self):
        # noinspection SpellCheckingInspection
        msg = '''! arist_chromenh.scl
!
Aristoxenos' Chromatic/Enharmonic, 3 + 9 + 18 parts
 7
!
 50.00000
 200.00000
 500.00000
 700.00000
 750.00000
 900.00000
 2/1
'''
        sf = ScalaFile()
        ss = sf.readstr(msg)
        self.assertEqual(ss.pitchCount, 7)

        # all but last will be the same
        # print(ss.getFileString())
        self.assertEqual(ss.getFileString()[:1], msg[:1])

        self.assertEqual([str(x) for x in ss.getIntervalSequence()],
                         ['<music21.interval.Interval P1 (+50c)>',
                          '<music21.interval.Interval m2 (+50c)>',
                          '<music21.interval.Interval m3>',
                          '<music21.interval.Interval M2>',
                          '<music21.interval.Interval P1 (+50c)>',
                          '<music21.interval.Interval m2 (+50c)>',
                          '<music21.interval.Interval m3>'])


class TestExternal(unittest.TestCase):
    pass


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
