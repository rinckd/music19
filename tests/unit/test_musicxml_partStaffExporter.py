# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.musicxml.partStaffExporter import *


class Test(unittest.TestCase):

    def getXml(self, obj):
        from music21.musicxml.m21ToXml import GeneralObjectExporter

        gex = GeneralObjectExporter()
        bytesOut = gex.parse(obj)
        bytesOutUnicode = bytesOut.decode('utf-8')
        return bytesOutUnicode

    def getET(self, obj):
        from music21.musicxml.m21ToXml import ScoreExporter

        SX = ScoreExporter(obj)
        mxScore = SX.parse()
        helpers.indent(mxScore)
        return mxScore

    def testJoinPartStaffsA(self):
        '''
        Measure 1, staff 2 contains mid-measure treble clef in LH
        '''
        from music21 import corpus
        sch = corpus.parse('schoenberg/opus19', 2)
        root = self.getET(sch)
        # helpers.dump(root)

        m1 = root.find('part/measure')
        clefs = m1.findall('attributes/clef')
        self.assertEqual(len(clefs), 3)
        self.assertEqual(clefs[0].get('number'), '1')
        self.assertEqual(clefs[1].get('number'), '2')
        self.assertEqual(clefs[2].get('number'), '2')
        self.assertEqual(clefs[2].find('sign').text, 'G')

    def testJoinPartStaffsB(self):
        '''
        Gapful first PartStaff, ensure <backup> in second PartStaff correct
        '''
        from music21 import layout
        from music21 import note
        s = stream.Score()
        ps1 = stream.PartStaff()
        ps1.insert(0, note.Note())
        # Gap
        ps1.insert(3, note.Note())
        ps2 = stream.PartStaff()
        ps2.insert(0, note.Note())
        s.append(ps1)
        s.append(ps2)
        s.insert(0, layout.StaffGroup([ps1, ps2]))
        root = self.getET(s)
        notes = root.findall('.//note')

        # since there are no voices in either PartStaff, the voice number of each note
        # should be the same as the staff number.
        for mxNote in notes:
            self.assertEqual(mxNote.find('voice').text, mxNote.find('staff').text)

        forward = root.find('.//forward')
        backup = root.find('.//backup')
        amountToBackup = (
            int(notes[0].find('duration').text)
            + int(forward.find('duration').text)
            + int(notes[1].find('duration').text)
        )
        self.assertEqual(int(backup.find('duration').text), amountToBackup)

    def testJoinPartStaffsC(self):
        '''
        First PartStaff longer than second
        '''
        from music21 import layout
        from music21 import note
        s = stream.Score()
        ps1 = stream.PartStaff()
        ps1.repeatAppend(note.Note(), 8)
        ps1.makeNotation(inPlace=True)  # makeNotation to freeze notation
        s.insert(0, ps1)
        ps2 = stream.PartStaff()
        ps2.repeatAppend(note.Note(), 4)
        ps2.makeNotation(inPlace=True)  # makeNotation to freeze notation
        s.insert(0, ps2)
        s.insert(0, layout.StaffGroup([ps1, ps2]))
        root = self.getET(s)
        measures = root.findall('.//measure')
        notes = root.findall('.//note')
        self.assertEqual(len(measures), 2)
        self.assertEqual(len(notes), 12)

    def testJoinPartStaffsD(self):
        '''
        Same example as testJoinPartStaffsC but switch the hands:
        second PartStaff longer than first
        '''
        from music21 import layout
        from music21 import note
        s = stream.Score()
        ps1 = stream.PartStaff()
        ps1.repeatAppend(note.Note(), 8)
        ps1.makeNotation(inPlace=True)  # makeNotation to freeze notation
        ps2 = stream.PartStaff()
        ps2.repeatAppend(note.Note(), 4)
        ps2.makeNotation(inPlace=True)  # makeNotation to freeze notation
        s.insert(0, ps2)
        s.insert(0, ps1)
        s.insert(0, layout.StaffGroup([ps2, ps1]))
        root = self.getET(s)
        measures = root.findall('.//measure')
        notes = root.findall('.//note')
        # from music21.musicxml.helpers import dump
        # dump(root)
        self.assertEqual(len(measures), 2)
        self.assertEqual(len(notes), 12)

    def testJoinPartStaffsD2(self):
        '''
        Add measures and voices and check for unique voice numbers across the StaffGroup.
        '''
        from music21 import layout
        from music21 import note
        s = stream.Score()
        ps1 = stream.PartStaff()
        m1 = stream.Measure()
        ps1.insert(0, m1)
        v1 = stream.Voice()
        v2 = stream.Voice()
        m1.insert(0, v1)
        m1.insert(0, v2)
        v1.repeatAppend(note.Note('C4'), 4)
        v2.repeatAppend(note.Note('E4'), 4)
        ps1.makeNotation(inPlace=True)  # makeNotation to freeze notation

        ps2 = stream.PartStaff()
        m2 = stream.Measure()
        ps2.insert(0, m2)
        v3 = stream.Voice()
        v4 = stream.Voice()
        m2.insert(0, v3)
        m2.insert(0, v4)
        v3.repeatAppend(note.Note('C3'), 4)
        v4.repeatAppend(note.Note('G3'), 4)
        ps2.makeNotation(inPlace=True)  # makeNotation to freeze notation

        s.insert(0, ps2)
        s.insert(0, ps1)
        s.insert(0, layout.StaffGroup([ps1, ps2]))
        root = self.getET(s)
        measures = root.findall('.//measure')
        notes = root.findall('.//note')
        # from music21.musicxml.helpers import dump
        # dump(root)
        self.assertEqual(len(measures), 1)
        self.assertEqual(len(notes), 16)

        # check those voice and staff numbers
        for mxNote in notes:
            mxPitch = mxNote.find('pitch')
            if mxPitch.find('step').text == 'C' and mxPitch.find('octave').text == '4':
                self.assertEqual(mxNote.find('voice').text, '1')
                self.assertEqual(mxNote.find('staff').text, '1')
            elif mxPitch.find('step').text == 'E' and mxPitch.find('octave').text == '4':
                self.assertEqual(mxNote.find('voice').text, '2')
                self.assertEqual(mxNote.find('staff').text, '1')
            elif mxPitch.find('step').text == 'C' and mxPitch.find('octave').text == '3':
                self.assertEqual(mxNote.find('voice').text, '3')
                self.assertEqual(mxNote.find('staff').text, '2')
            elif mxPitch.find('step').text == 'G' and mxPitch.find('octave').text == '3':
                self.assertEqual(mxNote.find('voice').text, '4')
                self.assertEqual(mxNote.find('staff').text, '2')

    def testJoinPartStaffsE(self):
        '''
        Measure numbers existing only in certain PartStaffs: don't collapse together
        '''
        from music21 import corpus
        from music21 import layout
        sch = corpus.parse('schoenberg/opus19', 2)

        s = stream.Score()
        ps1 = stream.PartStaff()
        ps2 = stream.PartStaff()
        s.append(ps1)
        s.append(ps2)
        s.insert(0, layout.StaffGroup([ps1, ps2]))
        m1 = sch.parts[0].measure(1)  # RH
        m2 = sch.parts[1].measure(2)  # LH
        m3 = sch.parts[0].measure(3)  # RH
        ps1.append(m1)
        ps1.append(m3)
        ps2.insert(m1.offset, m2)
        root = self.getET(s)
        m1tag, m2tag, m3tag = root.findall('part/measure')
        self.assertEqual({staff.text for staff in m1tag.findall('note/staff')}, {'1'})
        self.assertEqual({staff.text for staff in m2tag.findall('note/staff')}, {'2'})
        self.assertEqual({staff.text for staff in m3tag.findall('note/staff')}, {'1'})

    def testJoinPartStaffsF(self):
        '''
        Flattening the score will leave StaffGroup spanners with parts no longer in the stream.
        '''
        from music21 import corpus
        from music21 import musicxml
        sch = corpus.parse('schoenberg/opus19', 2)

        # NB: Using ScoreExporter directly is an advanced use case:
        # does not run makeNotation(), so here GeneralObjectExporter is used first
        gex = musicxml.m21ToXml.GeneralObjectExporter()
        with self.assertWarnsRegex(Warning, 'not well-formed'):
            # No part layer. Measure directly under Score.
            obj = gex.fromGeneralObject(sch.flatten())
        SX = musicxml.m21ToXml.ScoreExporter(obj)
        SX.scorePreliminaries()
        SX.parseFlatScore()
        # Previously, an exception was raised by getRootForPartStaff()
        SX.joinPartStaffs()

    def testJoinPartStaffsG(self):
        '''
        A derived score should still have joinable groups.
        '''
        from music21 import corpus
        from music21 import musicxml
        s = corpus.parse('demos/two-parts')

        m1 = s.measure(1)
        self.assertIn('Score', m1.classes)
        SX = musicxml.m21ToXml.ScoreExporter(m1)
        SX.scorePreliminaries()
        SX.parsePartlikeScore()
        self.assertEqual(len(SX.joinableGroups()), 1)

    def testJoinPartStaffsH(self):
        '''
        Overlapping PartStaffs cannot be guaranteed to export correctly,
        so they fall back to the old export paradigm (no joinable groups).
        '''
        from music21 import musicxml

        ps1 = stream.PartStaff(stream.Measure())
        ps2 = stream.PartStaff(stream.Measure())
        ps3 = stream.PartStaff(stream.Measure())
        sg1 = StaffGroup([ps1, ps2])
        sg2 = StaffGroup([ps1, ps3])
        s = stream.Score([ps1, ps2, ps3, sg1, sg2])

        SX = musicxml.m21ToXml.ScoreExporter(s)
        SX.scorePreliminaries()
        with self.assertWarns(MusicXMLWarning):
            SX.parsePartlikeScore()
            self.assertEqual(SX.joinableGroups(), [])

    def testJoinPartStaffsAgain(self):
        '''
        Regression test for side effects on the stream passed to ScoreExporter
        preventing it from being written out again.
        '''
        from music21 import corpus
        from music21.musicxml.m21ToXml import ScoreExporter
        b = corpus.parse('cpebach')
        SX = ScoreExporter(b)
        SX.parse()
        SX.parse()

    def testMeterChanges(self):
        from music21 import layout
        from music21 import meter
        from music21 import note

        ps1 = stream.PartStaff()
        ps2 = stream.PartStaff()
        sg = layout.StaffGroup([ps1, ps2])
        s = stream.Score([ps1, ps2, sg])
        for ps in ps1, ps2:
            ps.insert(0, meter.TimeSignature('3/1'))
            ps.repeatAppend(note.Note(type='whole'), 6)
            ps.makeNotation(inPlace=True)  # makes measures
            ps[stream.Measure][1].insert(meter.TimeSignature('4/1'))

        root = self.getET(s)
        # Just two <attributes> tags, a 3/1 in measure 1 and a 4/1 in measure 2
        self.assertEqual(len(root.findall('part/measure/attributes/time')), 2)

        # Edge cases -- no expectation of correctness, just don't crash
        ps1[stream.Measure].last().number = 0  # was measure 2
        root = self.getET(s)
        self.assertEqual(len(root.findall('part/measure/attributes/time')), 3)

    def testBackupAmount(self):
        '''
        Regression test for chord members causing too-large backup amounts.
        '''
        from music21 import chord
        from music21 import defaults
        from music21 import layout

        ps1 = stream.PartStaff(chord.Chord('C E G'))
        ps2 = stream.PartStaff(chord.Chord('D F A'))
        sg = layout.StaffGroup([ps1, ps2])
        s = stream.Score([sg, ps1, ps2])

        root = self.getET(s)
        self.assertEqual(
            root.findall('part/measure/backup/duration')[0].text,
            str(defaults.divisionsPerQuarter)
        )

    def testForwardRepeatMarks(self):
        '''
        Regression test for losing forward repeat marks.
        '''
        from music21 import bar
        from music21 import layout
        from music21 import note

        measureRH = stream.Measure(
            [bar.Repeat(direction='start'), note.Note(type='whole')])
        measureRH.storeAtEnd(bar.Repeat(direction='end'))
        measureLH = stream.Measure(
            [bar.Repeat(direction='start'), note.Note(type='whole')])
        measureLH.storeAtEnd(bar.Repeat(direction='end'))

        ps1 = stream.PartStaff(measureRH)
        ps2 = stream.PartStaff(measureLH)
        sg = layout.StaffGroup([ps1, ps2])
        s = stream.Score([sg, ps1, ps2])

        root = self.getET(s)
        self.assertEqual(
            [r.get('direction') for r in root.findall('.//repeat')],
            ['forward', 'backward']
        )


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
