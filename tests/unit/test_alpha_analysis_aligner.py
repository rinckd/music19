# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.alpha.analysis.aligner import *


class Test(unittest.TestCase):
    def testSimpleStreamOneNote(self):
        '''
        two streams of the same note should have 1.0 similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('C4')

        target.append(note1)
        source.append(note2)

        sa = StreamAligner(target, source)
        sa.align()

        self.assertEqual(sa.similarityScore, 1.0)

    def testSimpleStreamOneNoteDifferent(self):
        '''
        two streams of two different notes should have 0.0 similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('C#4')
        note2.quarterLength = 4

        target.append(note1)
        source.append(note2)

        sa = StreamAligner(target, source)
        sa.align()

        self.assertEqual(sa.similarityScore, 0.0)

    def testSameSimpleStream(self):
        '''
        two streams of the same notes should have 1.0 percentage similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('D4')
        note3 = note.Note('E4')
        note4 = note.Note('F4')

        target.append([note1, note2, note3, note4])
        source.append([note1, note2, note3, note4])

        sa = StreamAligner(target, source)
        sa.align()

        self.assertEqual(sa.similarityScore, 1.0)

    def testSameSimpleStream2(self):
        '''
        two streams of the 2/3 same notes should have 2/3 similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('D#4')
        note3 = note.Note('D-4')
        note4 = note.Note('C4')

        target.append([note1, note2, note4])
        source.append([note1, note3, note4])

        sa = StreamAligner(target, source)
        sa.align()

        self.assertEqual(sa.similarityScore, 2 / 3)

    def testSameOneOffStream(self):
        '''
        two streams with just 1 note different should have 0.75 percentage similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('D4')
        note3 = note.Note('E4')
        note4 = note.Note('F4')
        note5 = note.Note('G4')

        target.append([note1, note2, note3, note4])
        source.append([note1, note2, note3, note5])

        sa = StreamAligner(target, source)
        sa.align()

        self.assertEqual(sa.similarityScore, 0.75)

    def testOneOffDeletionStream(self):
        '''
        two streams, both the same, but one has an extra note should
        have 0.75 percentage similarity
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        note1 = note.Note('C4')
        note2 = note.Note('D4')
        note3 = note.Note('E4')
        note4 = note.Note('F4')

        target.append([note1, note2, note3, note4])
        source.append([note1, note2, note3])

        sa = StreamAligner(target, source)
        sa.align()
        sa.showChanges()

        self.assertEqual(sa.similarityScore, 0.75)

    def testChordSimilarityStream(self):
        '''
        two streams, one with explicit chord
        '''
        from music21 import stream
        from music21 import chord

        target = stream.Stream()
        source = stream.Stream()

        cMajor = chord.Chord(['E3', 'C4', 'G4'])
        target.append(cMajor)
        source.append(cMajor)

        sa = StreamAligner(target, source)
        sa.align()
        self.assertEqual(sa.similarityScore, 1.)

    def testShowInsertion(self):
        '''
        Given two streams:

        MIDI is `C C C B`
        OMR is `C C C`

        Therefore, there needs to be an insertion to get from OMR to MIDI
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        noteC1 = note.Note('C4')
        noteC2 = note.Note('C4')
        noteC3 = note.Note('C4')
        noteC4 = note.Note('C4')
        noteC5 = note.Note('C4')
        noteC6 = note.Note('C4')
        noteB = note.Note('B3')

        target.append([noteC1, noteC2, noteC3, noteB])
        source.append([noteC4, noteC5, noteC6])

        sa = StreamAligner(target, source)
        sa.align()
        sa.showChanges()

        n0 = target.getElementById(sa.changes[3][0].id)
        self.assertIsNotNone(n0)
        n0 = cast(note.Note, n0)
        self.assertEqual(n0.style.color, 'green')
        self.assertEqual(n0.lyric, '3')

        n1 = source.getElementById(sa.changes[3][1].id)
        self.assertIsNotNone(n1)
        n1 = cast(note.Note, n1)
        self.assertEqual(n1.style.color, 'green')
        self.assertEqual(n1.lyric, '3')

    def testShowDeletion(self):
        '''
        Given two streams:

        MIDI is `C C C`

        OMR is `C C C B`

        Therefore, there needs to be a deletion to get from OMR to MIDI.
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        noteC1 = note.Note('C4')
        noteC2 = note.Note('C4')
        noteC3 = note.Note('C4')
        noteC4 = note.Note('C4')
        noteC5 = note.Note('C4')
        noteC6 = note.Note('C4')
        noteB = note.Note('B3')

        target.append([noteC1, noteC2, noteC3])
        source.append([noteC4, noteC5, noteC6, noteB])

        sa = StreamAligner(target, source)
        sa.align()
        sa.showChanges()

        n0 = target.getElementById(sa.changes[3][0].id)
        self.assertIsNotNone(n0)
        n0 = cast(note.Note, n0)
        self.assertEqual(n0.style.color, 'red')
        self.assertEqual(n0.lyric, '3')

        n1 = source.getElementById(sa.changes[3][1].id)
        self.assertIsNotNone(n1)
        n1 = cast(note.Note, n1)
        self.assertEqual(n1.style.color, 'red')
        self.assertEqual(n1.lyric, '3')

    def testShowSubstitution(self):
        '''
        two streams:
        MIDI is `C C C`
        OMR is `C C B`

        Therefore, there needs to be a substitution to get from OMR to MIDI
        '''
        from music21 import stream
        from music21 import note

        target = stream.Stream()
        source = stream.Stream()

        noteC1 = note.Note('C4')
        noteC2 = note.Note('C4')
        noteC3 = note.Note('C4')
        noteC4 = note.Note('C4')
        noteC5 = note.Note('C4')
        noteB = note.Note('B3')

        target.append([noteC1, noteC2, noteC3])
        source.append([noteC4, noteC5, noteB])

        sa = StreamAligner(target, source)
        sa.align()
        sa.showChanges()


        n0 = target.getElementById(sa.changes[2][0].id)
        self.assertIsNotNone(n0)
        n0 = cast(note.Note, n0)
        self.assertEqual(n0.style.color, 'purple')
        self.assertEqual(n0.lyric, '2')

        n1 = source.getElementById(sa.changes[2][1].id)
        self.assertIsNotNone(n1)
        n1 = cast(note.Note, n1)
        self.assertEqual(n1.style.color, 'purple')
        self.assertEqual(n1.lyric, '2')


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
