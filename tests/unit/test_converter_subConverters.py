# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.converter.subConverters import *


class Test(unittest.TestCase):

    def testSimpleTextShow(self):
        from music21 import note
        n = note.Note()
        s = stream.Stream()
        s.append(n)
        unused_x = s.show('textLine')


    def testWriteMXL(self):
        from music21 import converter
        from music21.musicxml import testPrimitive

        s = converter.parseData(testPrimitive.multiDigitEnding)
        mxlPath = s.write('mxl')
        self.assertTrue(str(mxlPath).endswith('.mxl'), f'{mxlPath} does not end with .mxl')

        # Just the filepath ending in .mxl is sufficient to write .mxl
        s.write(fp=mxlPath)
        # Verify that it actually wrote bytes
        with self.assertRaises(UnicodeDecodeError):
            with open(mxlPath, 'r', encoding='utf-8') as f:
                f.read(20)

        # Also test ConverterMusicXML object directly
        conv = ConverterMusicXML()
        mxlPath2 = conv.write(obj=s, fmt='mxl')
        with self.assertRaises(UnicodeDecodeError):
            with open(mxlPath2, 'r', encoding='utf-8') as f:
                f.read(20)

        os.remove(mxlPath)
        os.remove(mxlPath2)

    def testWriteMusicXMLMakeNotation(self):
        from music21 import converter
        from music21 import note
        from music21.musicxml.xmlObjects import MusicXMLExportException

        m1 = stream.Measure(note.Note(quarterLength=5.0))
        m2 = stream.Measure()
        p = stream.Part([m1, m2])
        s = stream.Score(p)

        self.assertEqual(len(m1.notes), 1)
        self.assertEqual(len(m2.notes), 0)

        out1 = s.write()  # makeNotation=True is assumed
        # 4/4 will be assumed; quarter note will be moved to measure 2
        round_trip_back = converter.parse(out1)
        self.assertEqual(
            len(round_trip_back.parts.first().getElementsByClass(stream.Measure)[0].notes), 1)
        self.assertEqual(
            len(round_trip_back.parts.first().getElementsByClass(stream.Measure)[1].notes), 1)

        with self.assertRaises(MusicXMLExportException):
            # must splitAtDurations()!
            s.write(makeNotation=False)

        s = s.splitAtDurations(recurse=True)[0]
        out2 = s.write(makeNotation=False)
        round_trip_back = converter.parse(out2)
        # 4/4 will not be assumed; quarter note will still be split out from 5.0QL,
        # but it will remain in measure 1
        # and there will be no rests in measure 2
        self.assertEqual(
            len(round_trip_back.parts.first().getElementsByClass(stream.Measure)[0].notes), 2)
        self.assertEqual(
            len(round_trip_back.parts.first().getElementsByClass(stream.Measure)[1].notes), 0)

        # makeNotation = False cannot be used on non-scores
        with self.assertRaises(MusicXMLExportException):
            p.write(makeNotation=False)

        for out in (out1, out2):
            os.remove(out)

    def testBrailleKeywords(self):
        from music21 import converter

        # Braille functionality has been removed


class TestExternal(unittest.TestCase):
    show = True

    def testXMLShow(self):
        from music21 import corpus
        c = corpus.parse('bwv66.6')
        if self.show:
            c.show()  # musicxml

    # def testWriteLilypond(self):
    #     # Removed - Lilypond support removed
    #     from music21 import note
    #     n = note.Note()
    #     n.duration.type = 'whole'
    #     s = stream.Stream()
    #     s.append(n)
    #     if self.show:
    #         s.show('lily.png')
    #         print(s.write('lily.png'))

    def testMultiPageXMlShow1(self):
        '''
        tests whether show() works for music that is 10-99 pages long
        '''
        # OMR functionality has been removed

    # def testMultiPageXMlShow2(self):
    #     '''
    #      tests whether show() works for music that is 100-999 pages long.
    #      Currently, takes way too long to run.
    #      '''
    #     from music21 import stream, note
    #     biggerStream = stream.Stream()
    #     note1 = note.Note('C4')
    #     note1.duration.type = 'whole'
    #     biggerStream.repeatAppend(note1, 10000)
    #     biggerStream.show('musicxml.png')
    #     biggerStream.show()
    #     print(biggerStream.write('musicxml.png'))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
