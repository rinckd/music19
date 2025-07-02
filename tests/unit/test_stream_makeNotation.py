# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.stream.makeNotation import *


class Test(unittest.TestCase):
    '''
    Note: most Stream tests are found in stream/tests.py
    '''
    allaBreveBeamTest = "tinyNotation: 2/2 c8 d e f   trip{a b c' a b c'}  f' e' d' G  a b c' d'"

    def testNotesToVoices(self):
        from music21 import stream
        s = stream.Stream()
        n1 = note.Note()
        s.repeatAppend(n1, 4)
        self.assertEqual(len(s), 4)

        moveNotesToVoices(s)
        # now have one component
        self.assertEqual(len(s), 1)
        self.assertEqual(s[0].classes[0], 'Voice')  # default is a Voice
        self.assertEqual(len(s[0]), 4)
        self.assertEqual(str(list(s.voices[0].notesAndRests)),
                         '[<music21.note.Note C>, <music21.note.Note C>, '
                         + '<music21.note.Note C>, <music21.note.Note C>]')

    def testSetStemDirectionOneGroup(self):
        from music21 import converter
        p = converter.parse(self.allaBreveBeamTest)
        p.makeBeams(inPlace=True, setStemDirections=False)
        a, b, c, d = iterateBeamGroups(p)

        def testDirections(group, expected):
            self.assertEqual(len(group), len(expected))
            for groupNote, expectedStemDirection in zip(group, expected):
                self.assertEqual(groupNote.stemDirection, expectedStemDirection)

        testDirections(a, ['unspecified'] * 4)
        setStemDirectionOneGroup(a, setNewStems=False)
        testDirections(a, ['unspecified'] * 4)
        setStemDirectionOneGroup(a)
        testDirections(a, ['up'] * 4)
        for n in a:
            n.stemDirection = 'down'
        setStemDirectionOneGroup(a)
        testDirections(a, ['down'] * 4)
        setStemDirectionOneGroup(a, overrideConsistentStemDirections=True)
        testDirections(a, ['up'] * 4)

        setStemDirectionOneGroup(b)
        testDirections(b, ['down'] * 6)

        # this one is all high but has one very low G
        setStemDirectionOneGroup(c)
        testDirections(c, ['up'] * 4)

        dStems = ['down', 'noStem', 'double', 'up']
        for i, n in enumerate(d):
            n.stemDirection = dStems[i]
        setStemDirectionOneGroup(d)
        testDirections(d, ['down', 'noStem', 'double', 'down'])

    def testSetStemDirectionForBeamGroups(self):
        from music21 import converter
        p = converter.parse(self.allaBreveBeamTest)
        p.makeBeams(inPlace=True, setStemDirections=False)
        d = list(iterateBeamGroups(p))[-1]
        dStems = ['down', 'noStem', 'double', 'up']
        for i, n in enumerate(d):
            n.stemDirection = dStems[i]

        setStemDirectionForBeamGroups(p)
        self.assertEqual([n.stemDirection for n in p.flatten().notes],
                         ['up'] * 4 + ['down'] * 6 + ['up'] * 4
                         + ['down', 'noStem', 'double', 'down']
                         )

    def testSetStemDirectionConsistency(self):
        '''
        Stems that would all be up, starting from scratch,
        but because of overrideConsistentStemDirections=False,
        we only change the first group with an "unspecified" direction
        '''
        from music21 import converter
        p = converter.parse('tinyNotation: 2/4 b8 f8 a8 b8')
        p.makeBeams(inPlace=True)
        self.assertEqual(
            [n.stemDirection for n in p.flatten().notes],
            ['up', 'up', 'up', 'up']
        )

        # make manual changes
        dStems = ['down', 'unspecified', 'down', 'down']
        for n, stemDir in zip(p.flatten().notes, dStems):
            n.stemDirection = stemDir

        setStemDirectionForBeamGroups(p, setNewStems=True, overrideConsistentStemDirections=False)
        self.assertEqual(
            [n.stemDirection for n in p.flatten().notes],
            ['up', 'up', 'down', 'down']
        )

    def testMakeBeamsWithStemDirection(self):
        from music21 import converter
        p = converter.parse(self.allaBreveBeamTest)
        dStems = ['down', 'noStem', 'double', 'up']
        for i, n in enumerate(p.flatten().notes[-4:]):
            n.stemDirection = dStems[i]
        p.makeBeams(inPlace=True)
        self.assertEqual([n.stemDirection for n in p.flatten().notes],
                         ['up'] * 4 + ['down'] * 6 + ['up'] * 4
                         + ['down', 'noStem', 'double', 'down']
                         )

    def testMakeBeamsOnEmptyChord(self):
        from music21 import converter
        p = converter.parse('tinyNotation: 4/4')
        c1 = chord.Chord('d f')
        c1.quarterLength = 0.5
        c2 = chord.Chord('d f')
        c2.quarterLength = 0.5
        p.measure(1).insert(0, c1)
        p.measure(1).insert(0.5, c2)
        p.flatten().notes[0].notes = []
        p.flatten().notes[1].notes = []
        p.makeNotation(inPlace=True)
        self.assertEqual(
            [n.stemDirection for n in p.flatten().notes],
            ['unspecified', 'unspecified'],
        )

    def testMakeBeamsFromTimeSignatureInContext(self):
        from music21 import converter
        from music21 import stream

        p = converter.parse('tinyNotation: 2/4 r2 d8 d8 d8 d8')
        m2 = p[stream.Measure].last()
        self.assertIsNone(m2.timeSignature)
        m2_n0 = m2.notes.first()
        self.assertEqual(len(m2_n0.beams.beamsList), 0)
        m2.makeBeams(inPlace=True)
        self.assertEqual(len(m2_n0.beams.beamsList), 1)

        # Failure if no TimeSignature in context
        m1 = p[stream.Measure].first()
        m1.timeSignature = None
        msg = 'cannot process beams in a Measure without a time signature'
        with self.assertRaisesRegex(stream.StreamException, msg):
            m2.makeBeams(inPlace=True, failOnNoTimeSignature=True)

    def testStreamExceptions(self):
        from music21 import converter
        from music21 import stream
        p = converter.parse(self.allaBreveBeamTest)
        with self.assertRaises(stream.StreamException) as cm:
            p.makeMeasures(meterStream=duration.Duration())
        self.assertEqual(str(cm.exception),
            'meterStream is neither a Stream nor a TimeSignature!')

    def testMakeTiesChangingTimeSignatures(self):
        '''
        From a real-world failure.  Should not be
        making ties in an example that starts with a short TS
        but moves to a longer one and all is valid.
        '''
        from music21 import stream
        p = stream.Part()
        m1 = stream.Measure(number=1)
        m1.insert(0, meter.TimeSignature('3/4'))
        m1.insert(0, note.Note('C4', quarterLength=3.0))
        m2 = stream.Measure(number=2)
        m2.insert(0, meter.TimeSignature('6/1'))
        m2.insert(0, note.Note('D4', quarterLength=24.0))
        m3 = stream.Measure(number=3)
        m3.insert(0, note.Note('E4', quarterLength=24.0))
        p.append([m1, m2, m3])
        pp = p.makeTies()
        self.assertEqual(len(pp[stream.Measure]), 3)
        self.assertEqual(pp[stream.Measure].first().notes.first().duration.quarterLength, 3.0)
        self.assertEqual(pp[stream.Measure][1].notes.first().duration.quarterLength, 24.0)
        self.assertEqual(len(pp[stream.Measure][2].notes), 1)
        self.assertEqual(pp[stream.Measure][2].notes.first().duration.quarterLength, 24.0)

    def testSaveAccidentalDisplayStatus(self):
        from music21 import interval
        from music21 import stream
        m = stream.Measure([key.Key('C'), note.Note('C2'), note.Note('D2')])
        m.notes[0].pitch.accidental = 0
        m.notes[0].pitch.accidental.displayStatus = True
        m.notes[1].pitch.accidental = 0
        m.notes[1].pitch.accidental.displayStatus = False
        classList = (note.Note, chord.Chord, key.KeySignature)
        with saveAccidentalDisplayStatus(m):
            m.transpose(interval.Interval('m2'), inPlace=True, classFilterList=classList)
            self.assertEqual(m.notes[0].nameWithOctave, 'D-2')
            self.assertIsNone(m.notes[0].pitch.accidental.displayStatus)
            self.assertEqual(m.notes[1].nameWithOctave, 'E-2')
            self.assertIsNone(m.notes[1].pitch.accidental.displayStatus)

        # After exiting the with statement, accidental displayStatus will have been restored
        self.assertEqual(m.notes[0].nameWithOctave, 'D-2')
        self.assertIs(m.notes[0].pitch.accidental.displayStatus, True)
        self.assertEqual(m.notes[1].nameWithOctave, 'E-2')
        self.assertIs(m.notes[1].pitch.accidental.displayStatus, False)

    def testMakeNotationRecursive(self):
        from music21 import stream, tie

        def getScore():
            sc = stream.Score(id='mainScore')
            p0 = stream.Part(id='part0')

            m01 = stream.Measure(number=1)
            m01.append(meter.TimeSignature('4/4'))
            d1 = note.Note('D', type='half', dots=1)
            c1 = note.Note('C', type='quarter')
            c1.tie = tie.Tie('start')
            m01.append([d1, c1])
            m02 = stream.Measure(number=2)
            c2 = note.Note('C', type='quarter')
            c2.tie = tie.Tie('stop')
            c3 = note.Note('D', type='half')
            m02.append([c2, c3])
            p0.append([m01, m02])

            sc.insert(0, p0)
            return sc

        s = getScore()
        s.stripTies(inPlace=True)
        ss = s.makeTies()
        self.assertEqual(ss.flatten().notes[1].tie, tie.Tie('start'))
        self.assertEqual(ss.flatten().notes[2].tie, tie.Tie('stop'))
        self.assertIsNone(s.flatten().notes[1].tie)

        s.makeTies(inPlace=True)
        self.assertEqual(s.flatten().notes[1].tie, tie.Tie('start'))
        self.assertEqual(s.flatten().notes[2].tie, tie.Tie('stop'))

        op = stream.Opus()
        s1 = getScore()
        s1.id = 'score1'
        s2 = getScore()
        s2.id = 'score2'
        op.insert(0, s1)
        op.append(s2)
        op.stripTies(inPlace=True)
        opp = op.makeTies()
        self.assertEqual(opp.scores.first()[note.Note][1].tie, tie.Tie('start'))
        self.assertIsNone(op.scores.first()[note.Note][1].tie)
        op.makeTies(inPlace=True)
        self.assertEqual(op.scores[1][note.Note][2].tie, tie.Tie('stop'))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
