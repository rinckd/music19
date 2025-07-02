# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.bar import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testSortOrder(self):
        from music21 import stream
        from music21 import clef
        from music21 import note
        from music21 import metadata
        m = stream.Measure()
        b = Repeat()
        m.leftBarline = b
        c = clef.BassClef()
        m.append(c)
        n = note.Note()
        m.append(n)

        # check sort order
        self.assertEqual(m[0], b)
        self.assertEqual(m[1], c)
        self.assertEqual(m[2], n)

        # if we add metadata, it sorts ahead of bar
        md = metadata.Metadata()
        m.insert(0, md)

        self.assertEqual(m[0], md)
        self.assertEqual(m[1], b)

    def testFreezeThaw(self):
        from music21 import converter
        from music21 import stream
        # pylint: disable=redefined-outer-name
        from music21.bar import Barline  # avoid not same class error

        b = Barline()
        self.assertNotIn('StyleMixin', b.classes)
        s = stream.Stream([b])
        data = converter.freezeStr(s, fmt='pickle')
        s2 = converter.thawStr(data)
        thawedBarline = s2[0]
        # Previously, raised AttributeError
        self.assertEqual(thawedBarline.hasStyleInformation, False)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
