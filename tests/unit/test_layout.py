# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.layout import *


class Test(unittest.TestCase):

    def testBasic(self):
        from music21 import note
        from music21.musicxml import m21ToXml
        s = stream.Stream()

        for i in range(1, 11):
            m = stream.Measure()
            m.number = i
            n = note.Note()
            m.append(n)
            s.append(m)

        sl = SystemLayout()
        # sl.isNew = True  # this should not be on first system
        # as this causes all subsequent margins to be distorted
        sl.leftMargin = 300
        sl.rightMargin = 300
        s.getElementsByClass(stream.Measure)[0].insert(0, sl)

        sl = SystemLayout()
        sl.isNew = True
        sl.leftMargin = 200
        sl.rightMargin = 200
        sl.distance = 40
        s.getElementsByClass(stream.Measure)[2].insert(0, sl)

        sl = SystemLayout()
        sl.isNew = True
        sl.leftMargin = 220
        s.getElementsByClass(stream.Measure)[4].insert(0, sl)

        sl = SystemLayout()
        sl.isNew = True
        sl.leftMargin = 60
        sl.rightMargin = 300
        sl.distance = 200
        s.getElementsByClass(stream.Measure)[6].insert(0, sl)

        sl = SystemLayout()
        sl.isNew = True
        sl.leftMargin = 0
        sl.rightMargin = 0
        s.getElementsByClass(stream.Measure)[8].insert(0, sl)

        # systemLayoutList = s[music21.layout.SystemLayout]
        # self.assertEqual(len(systemLayoutList), 4)

        # s.show()
        unused_raw = m21ToXml.GeneralObjectExporter().parse(s)

    def x_testGetPageMeasureNumbers(self):
        from music21 import corpus
        c = corpus.parse('luca/gloria').parts[0]
        # c.show('text')
        retStr = ''
        for x in c.flatten():
            if 'PageLayout' in x.classes:
                retStr += str(x.pageNumber) + ': ' + str(x.measureNumber) + ', '
#        print(retStr)
        self.assertEqual(retStr, '1: 1, 2: 23, 3: 50, 4: 80, 5: 103, ')

    def testGetStaffLayoutFromStaff(self):
        '''
        we have had problems with attributes disappearing.
        '''
        from music21 import corpus
        from music21 import layout
        lt = corpus.parse('demos/layoutTest.xml')
        ls = layout.divideByPages(lt, fastMeasures=True)

        hiddenStaff = ls.pages[0].systems[3].staves[1]
        self.assertTrue(repr(hiddenStaff).endswith('Staff 11: p.1, sys.4, st.2>'),
                        repr(hiddenStaff))
        self.assertIsNotNone(hiddenStaff.staffLayout)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
