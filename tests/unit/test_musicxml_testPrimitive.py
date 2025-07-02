# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.musicxml.testPrimitive import *


class Test(unittest.TestCase):

    def testBasic(self):
        # a basic test to make sure each parse
        from music21 import converter
        for i, testMaterial in enumerate(ALL):
            try:
                dummy = converter.parse(testMaterial)
            except Exception:
                print('Failure in test ', i)
                raise

    def testMidMeasureClef1(self):
        '''
        Tests if there are mid-measure clefs: single staff
        '''
        from music21 import stream
        from music21 import note
        from music21 import clef
        from music21 import musicxml
        from music21 import converter
        from music21 import meter

        orig_stream = stream.Stream()
        orig_stream.append(meter.TimeSignature('4/4'))
        orig_stream.append(clef.TrebleClef())
        orig_stream.repeatAppend(note.Note('C4'), 2)
        orig_stream.append(clef.BassClef())
        orig_stream.repeatAppend(note.Note('C4'), 2)
        orig_clefs = orig_stream.flatten().getElementsByClass(clef.Clef)

        xml = musicxml.m21ToXml.GeneralObjectExporter().parse(orig_stream)
        self.assertEqual(xml.count(b'<clef>'), 2)  # clefs got out
        self.assertEqual(xml.count(b'<measure'), 1)  # in one measure

        new_stream = converter.parse(xml)
        new_clefs = new_stream.flatten().getElementsByClass(clef.Clef)

        self.assertEqual(len(new_clefs), len(orig_clefs))
        self.assertEqual([c.offset for c in new_clefs], [c.offset for c in orig_clefs])
        self.assertEqual([c.classes for c in new_clefs], [c.classes for c in orig_clefs])

    def testMidMeasureClefs2(self):
        '''
        Tests if there are mid-measure clefs: multiple staves.
        '''
        from music21 import clef
        from music21 import converter
        from music21 import meter
        from music21 import musicxml
        from music21 import note
        from music21 import stream

        orig_stream = stream.Stream()
        orig_stream.append(stream.Part())
        orig_stream.append(stream.Part())
        orig_stream.append(meter.TimeSignature('3/4'))

        for item in [clef.TrebleClef(), note.Note('C4'), clef.BassClef(),
                     note.Note('C4'), note.Note('C4')]:
            orig_stream[0].append(item)

        for item in [clef.BassClef(), note.Note('C4'), note.Note('C4'),
                     clef.TrebleClef(), note.Note('C4')]:
            orig_stream[1].append(item)

        orig_clefs = [staff.flatten().getElementsByClass(clef.Clef).stream() for staff in
                      orig_stream.getElementsByClass(stream.Part)]

        xml = musicxml.m21ToXml.GeneralObjectExporter().parse(orig_stream)

        new_stream = converter.parse(xml.decode('utf-8'))
        new_clefs = [staff.flatten().getElementsByClass(clef.Clef).stream() for staff in
                     new_stream.getElementsByClass(stream.Part)]

        self.assertEqual([len(clefs) for clefs in new_clefs],
                         [len(clefs) for clefs in orig_clefs])
        self.assertEqual([c.offset for c in new_clefs],
                         [c.offset for c in orig_clefs])
        self.assertEqual([c.classes for c in new_clefs],
                         [c.classes for c in orig_clefs])

    def testMidMeasureClefs3(self):
        '''
        Test midmeasure clef changes outside voices
        '''
        from music21 import clef
        from music21 import note
        from music21 import musicxml
        from music21 import stream

        v1 = stream.Voice()
        v2 = stream.Voice()
        quarter = note.Note()
        v1.repeatAppend(quarter, 4)
        v2.repeatAppend(quarter, 4)
        m = stream.Measure([v1, v2])
        m.insert(1.0, clef.BassClef())
        p = stream.Part(m)
        p.makeNotation(inPlace=True)

        tree = musicxml.test_m21ToXml.Test().getET(p)
        self.assertEqual(len(tree.findall('.//clef')), 1)
        # One backup from the clef back to voice 1, then another back to voice 2
        self.assertEqual(len(tree.findall('.//backup')), 2)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
