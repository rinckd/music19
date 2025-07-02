# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.sites import *


class Test(unittest.TestCase):
    def testSites(self):
        from music21 import note
        from music21 import stream
        from music21 import corpus
        from music21 import clef

        m = stream.Measure()
        m.number = 34
        n = note.Note()
        m.append(n)

        n2 = note.Note()
        n2.sites.add(m)

        c = clef.Clef()
        c.sites.add(n)

        self.assertEqual(n2.sites.getAttrByName('number'), 34)
        c.sites.setAttrByName('lyric', str(n2.sites.getAttrByName('number')))
        self.assertEqual(n.lyric, '34')
        c.sites.setAttrByName('lyric', n2.sites.getAttrByName('number'))
        # converted to a string now
        self.assertEqual(n.lyric, '34')

        violin1 = corpus.parse(
            'beethoven/opus18no1',
            3,
            fileExtensions=('xml',),
        ).getElementById('Violin I')
        lastNote = violin1.flatten().notes[-1]
        lastNoteClef = lastNote.getContextByClass(clef.Clef)
        self.assertIsInstance(lastNoteClef, clef.TrebleClef)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
