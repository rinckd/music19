# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.alpha.analysis.hasher import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def _approximatelyEqual(self, a, b, sig_fig=2):
        '''
        use to look at whether beat lengths are close, within a certain range
        probably can use for other things that are approx. equal
        '''
        return a == b or int(a * 10 ** sig_fig) == int(b * 10 ** sig_fig)

    def testBasicHash(self):
        '''
        test for hasher with basic settings: pitch, rounded duration, offset
        with notes, chord, and rest
        '''
        s1 = stream.Stream()
        note1 = note.Note('C4')
        note1.duration.type = 'half'
        note2 = note.Note('F#4')
        note3 = note.Note('B-2')
        cMinor = chord.Chord(['C4', 'G4', 'E-5'])
        cMinor.duration.type = 'half'
        r = note.Rest(quarterLength=1.5)
        s1.append(note1)
        s1.append(note2)
        s1.append(note3)
        s1.append(cMinor)
        s1.append(r)

        h = Hasher()

        hashes_plain_numbers = [(60, 2.0, 0.0), (66, 1.0, 2.0), (46, 1.0, 3.0), (60, 2.0, 4.0),
                                (67, 2.0, 4.0), (75, 2.0, 4.0), (0, 1.5, 6.0)]
        CNoteHash = collections.namedtuple('NoteHash', ['Pitch', 'Duration', 'Offset'])
        hashes_in_format = [CNoteHash(Pitch=x, Duration=y, Offset=z)
                            for (x, y, z) in hashes_plain_numbers]

        self.assertEqual(h.hashStream(s1), hashes_in_format)

    def testHashChordsAsChordsPrimeFormString(self):
        '''
        test to make sure that hashing works when trying to hash chord as chord
        '''
        s1 = stream.Stream()
        note1 = note.Note('C4')
        note1.duration.type = 'half'
        cMinor = chord.Chord(['C4', 'G4', 'E-5'])
        cMinor.duration.type = 'half'
        cMajor = chord.Chord(['C4', 'G4', 'E4'])
        cMajor.duration.type = 'whole'
        s1.append(note1)
        s1.append(cMinor)
        s1.append(cMajor)
        h = Hasher()
        h.hashChordsAsChords = True
        h.hashChordsAsNotes = False
        h.hashPrimeFormString = True
        CNoteHash = collections.namedtuple('NoteHash', ['Pitch', 'PrimeFormString',
                                                        'Duration', 'Offset'])
        hashes_plain_numbers = [(60, '<>', 2.0, 0.0), (1, '<037>', 2.0, 2.0),
                                (1, '<037>', 4.0, 4.0)]
        hashes_in_format = [CNoteHash(Pitch=x, PrimeFormString=y, Duration=z, Offset=a)
                            for (x, y, z, a) in hashes_plain_numbers]

        self.assertEqual(h.hashStream(s1), hashes_in_format)

    def testHashChordsAsChordsNormalOrder(self):
        s2 = stream.Stream()
        note1 = note.Note('C4')
        note1.duration.type = 'half'
        cMinor = chord.Chord(['C4', 'G4', 'E-5'])
        cMinor.duration.type = 'half'
        cMajor = chord.Chord(['C4', 'G4', 'E3'])
        cMajor.duration.type = 'whole'
        s2.append(note1)
        s2.append(cMinor)
        s2.append(cMajor)
        h = Hasher()
        h.hashChordsAsChords = True
        h.hashChordsAsNotes = False
        h.hashPrimeFormString = False
        h.hashNormalOrderString = True
        CNoteHash = collections.namedtuple('NoteHash', ['Pitch', 'NormalOrderString',
                                                        'Duration', 'Offset'])
        hashes_plain_numbers = [(60, '<>', 2.0, 0.0), (1, '<037>', 2.0, 2.0),
                                (1, '<047>', 4.0, 4.0)]
        hashes_in_format = [CNoteHash(Pitch=x, NormalOrderString=y, Duration=z, Offset=a)
                            for (x, y, z, a) in hashes_plain_numbers]
        self.assertEqual(h.hashStream(s2), hashes_in_format)

    def testHashUnroundedDuration(self):
        s3 = stream.Stream()
        note1 = note.Note('C4')
        note2 = note.Note('G4')
        cMinor = chord.Chord(['C4', 'G4'])
        note1.duration.quarterLength = 1.783
        note2.duration.quarterLength = 2 / 3
        cMinor.duration.type = 'half'
        s3.append(note1)
        s3.append(note2)
        s3.append(cMinor)
        h = Hasher()
        h.roundDurationAndOffset = False
        CNoteHash = collections.namedtuple('NoteHash', ['Pitch', 'Duration', 'Offset'])
        hashes_plain_numbers = [(60, 1.783, 0.0), (67, 2 / 3, 1.783), (60, 2.0, 1.783 + 2 / 3),
                                (67, 2.0, 1.783 + 2 / 3)]
        hashes_in_format = [CNoteHash(Pitch=x, Duration=z, Offset=a)
                            for (x, z, a) in hashes_plain_numbers]
        h3 = h.hashStream(s3)
        h3_floats = [h3[0][2], h3[1][2], h3[2][2], h3[3][2]]
        answers_floats = [hashes_in_format[0][2],
                          hashes_in_format[1][2],
                          hashes_in_format[2][2],
                          hashes_in_format[3][2]]
        assert all(self._approximatelyEqual(*values)
                   for values in zip(h3_floats, answers_floats))

    def testHashRoundedDuration(self):
        s3 = stream.Stream()
        note1 = note.Note('C4')
        note2 = note.Note('G4')
        cMinor = chord.Chord(['C4', 'G4'])
        note1.duration.quarterLength = 1.783
        note2.duration.quarterLength = 2 / 3
        cMinor.duration.type = 'half'
        s3.append(note1)
        s3.append(note2)
        s3.append(cMinor)
        h = Hasher()
        h.roundDurationAndOffset = True

        CNoteHash = collections.namedtuple('NoteHash', ['Pitch', 'Duration', 'Offset'])
        hashes_plain_numbers = [(60, 1.78125, 0.0), (67, 0.65625, 1.78125), (60, 2.0, 2.4375),
                                (67, 2.0, 2.4375)]
        hashes_in_format = [CNoteHash(Pitch=x, Duration=z, Offset=a)
                            for (x, z, a) in hashes_plain_numbers]
        h3 = h.hashStream(s3)
        self.assertEqual(h3, hashes_in_format)
        h.granularity = 8  # smallest length note is now 8th note
        new_hashes_in_format = [(60, 1.75, 0.0),
                                (67, 0.625, 1.75),
                                (60, 2.0, 2.5),
                                (67, 2.0, 2.5)]
        h4 = h.hashStream(s3)
        self.assertEqual(h4, new_hashes_in_format)

    def testReferences(self):
        s = stream.Stream()
        note1 = note.Note('C4')
        note2 = note.Note('G4')
        s.append([note1, note2])

        h = Hasher()
        h.includeReference = True
        hashes = h.hashStream(s)

        note1ref = hashes[0].reference
        note2ref = hashes[1].reference

        self.assertEqual(note1.id, note1ref.id)
        self.assertEqual(note2.id, note2ref.id)

    def testIntervals(self):
        s = stream.Stream()
        note1 = note.Note('E5')
        note2 = note.Note('D5')
        note3 = note.Note('A5')
        s.append([note1, note2, note3])
        h = Hasher()
        h.hashPitch = True
        h.hashDuration = False
        h.hashOffset = False
        h.hashIntervalFromLastNote = True
        unused_hashes = h.hashStream(s)


class TestExternal(unittest.TestCase):
    show = True

    # def testBasicHash(self):
    #     # from pprint import pprint as pp
    #     from music21 import corpus
    #     s1 = corpus.parse('schoenberg', 6).parts[0]
    #     h = Hasher()
    #     # h.hashPitch = True
    #     # h.hashDuration = True
    #     # h.hashOffset = True
    #     # h.hashMIDI = False
    #     # h.hashChords = False
    #     # h.hashChordsAsNotes = False
    #     # h.validTypes = [note.Note, note.Rest]
    #     # h.hashMIDI = False  # otherwise, hash string 'C-- instead of 58'
    #     # h.hashOctave = False
    #     # h.hashDuration = True
    #     # h.roundDurationAndOffset = False
    #     # h.roundOffset = False
    #     # h.hashChordsAsNotes = False
    #     # h.hashChordsAsChords = True
    #     # h.hashOctave = True
    #     # h.hashPrimeFormString = True
    #     h.hashIntervalFromLastNote = True
    #     # pp(h.hashStream(s1.recurse()))
    #     # hashes1 = h.hashStream(s1.recurse())
    #     s2 = corpus.parse('schoenberg', 2).parts[0]
    #     # hashes2 = h.hashStream(s2.recurse())
    #     s3 = corpus.parse('bwv66.6').parts[0]
    #     hashes3 = h.hashStream(s3)
    #     # s4 = corpus.parse('bwv66.6').parts[0].transpose('M2')
    #     # s4 = s5.parts[0].transpose('M2')
    #     s4.show()
    #     # pp(s4.recurse())

    #     hashes4 = h.hashStream(s4)
    #     print(hashes3)
    #     print('    ')
    #     print(hashes4)

    #     pp(difflib.SequenceMatcher(a=hashes1, b=hashes2).ratio())
    #     pp(difflib.SequenceMatcher(a=hashes1, b=hashes3).ratio())
    #     pp(difflib.SequenceMatcher(a=hashes2, b=hashes3).ratio())
    #     # pp(difflib.SequenceMatcher(a=hashes3, b=hashes4).ratio())

    # def testFolk(self):
    #     from music21 import corpus
    #     h = Hasher()

    #     s1 = corpus.parse('ryansMammoth/MyLoveIsInAmericaReel.abc').parts[0]
    #     s2 = corpus.parse('ryansMammoth/MyLoveIsFarAwayReel.abc').parts[0]

    #     s2.show()

    #     hashes1 = h.hashStream(s1)
    #     hashes2 = h.hashStream(s2)

    #     print(difflib.SequenceMatcher(a=hashes1, b=hashes2).ratio())

    #     h.hashPitch = False

    #     hashes1 = h.hashStream(s1)
    #     hashes2 = h.hashStream(s2)

    #     print(difflib.SequenceMatcher(a=hashes1, b=hashes2).ratio())

    def testBvSvS(self):
        from music21 import corpus
        h = Hasher()
        h.hashDuration = False
        h.hashOffset = False
        s1 = corpus.parse('schoenberg', 6).parts.first()
        s2 = corpus.parse('schoenberg', 2).parts.first()
        s3 = corpus.parse('bwv66.6').parts.first()
        hashes1 = h.hashStream(s1)
        hashes2 = h.hashStream(s2)
        hashes3 = h.hashStream(s3)

        if self.show:
            print(difflib.SequenceMatcher(a=hashes1, b=hashes2).ratio())
            print(difflib.SequenceMatcher(a=hashes1, b=hashes3).ratio())
            print(difflib.SequenceMatcher(a=hashes2, b=hashes3).ratio())
            s2.show()

        h.hashPitch = False
        h.hashDuration = True
        h.hashOffset = True

        hashes1 = h.hashStream(s1)
        hashes2 = h.hashStream(s2)
        hashes3 = h.hashStream(s3)

        if self.show:
            print(difflib.SequenceMatcher(a=hashes1, b=hashes2).ratio())
            print(difflib.SequenceMatcher(a=hashes1, b=hashes3).ratio())
            print(difflib.SequenceMatcher(a=hashes2, b=hashes3).ratio())

    def testInterval(self):
        from music21 import corpus
        h = Hasher()
        s3 = corpus.parse('bwv66.6').parts.first()
        s4 = corpus.parse('bwv66.6').parts.first().transpose('M2')

        hashes3 = h.hashStream(s3)
        hashes4 = h.hashStream(s4)

        if self.show:
            print(difflib.SequenceMatcher(a=hashes3, b=hashes4).ratio())

        h.hashIntervalFromLastNote = True
        h.hashPitch = False

        hashes3 = h.hashStream(s3)
        hashes4 = h.hashStream(s4)

        if self.show:
            print(difflib.SequenceMatcher(a=hashes3, b=hashes4).ratio())


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
