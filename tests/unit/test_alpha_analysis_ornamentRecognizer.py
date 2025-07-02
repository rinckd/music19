# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.alpha.analysis.ornamentRecognizer import *

class _TestCondition:
    def __init__(
        self, name, busyNotes, isOrnament,
        simpleNotes=None, ornamentSize=None, isNachschlag=False, isInverted=False
    ):
        self.name = name
        self.busyNotes = busyNotes
        self.isOrnament = isOrnament
        self.simpleNotes = simpleNotes
        self.ornamentSize = ornamentSize
        self.isNachschlag = isNachschlag
        self.isInverted = isInverted

class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testRecognizeTurn(self):
        # set up experiment
        testConditions = []

        n1 = note.Note('F#')
        n1Enharmonic = note.Note('G-')
        noteInTurnNotBase = note.Note('G')
        noteNotInTurn = note.Note('A')

        evenTurn = [note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('F#')]
        for n in evenTurn:
            n.duration.quarterLength = n1.duration.quarterLength / len(evenTurn)

        delayedTurn = [note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('F#')]
        delayedTurn[0].duration.quarterLength = 2 * n1.duration.quarterLength / len(delayedTurn)
        for i in range(1, len(delayedTurn)):
            smallerDuration = n1.duration.quarterLength / (2 * len(delayedTurn))
            delayedTurn[i].duration.quarterLength = smallerDuration

        rubatoTurn = [note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('F#')]
        # durations all different, add up to 1
        rubatoTurn[0].duration.quarterLength = .25
        rubatoTurn[1].duration.quarterLength = .15
        rubatoTurn[2].duration.quarterLength = .2
        rubatoTurn[3].duration.quarterLength = .4

        invertedTurn = [note.Note('E'), note.Note('F#'), note.Note('G'), note.Note('F#')]
        for n in invertedTurn:
            n.duration.quarterLength = n1.duration.quarterLength / len(invertedTurn)

        testConditions.append(
            _TestCondition(
                name='even turn no simple note',
                busyNotes=evenTurn,
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='even turn with simple note',
                busyNotes=evenTurn,
                simpleNotes=[n1],
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='even turn with enharmonic simple note',
                busyNotes=evenTurn,
                simpleNotes=[n1Enharmonic],
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='even turn with wrong simple note still in turn',
                busyNotes=evenTurn,
                simpleNotes=[noteInTurnNotBase],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='even turn with wrong simple note not in turn',
                busyNotes=evenTurn,
                simpleNotes=[noteNotInTurn],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='rubato turn with all notes different length',
                busyNotes=rubatoTurn,
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='delayed turn',
                busyNotes=delayedTurn,
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='inverted turn',
                busyNotes=invertedTurn,
                isInverted=True,
                isOrnament=True)
        )
        testConditions.append(
            _TestCondition(
                name='one wrong note',
                busyNotes=[note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('D')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='non-adjacent note jump',
                busyNotes=[note.Note('E'), note.Note('G'), note.Note('A'), note.Note('G')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='trill is not a turn',
                busyNotes=[note.Note('G'), note.Note('F#'), note.Note('G'), note.Note('F#')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='too many notes for turn',
                busyNotes=[note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('F#'),
                           note.Note('E')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='too few notes for turn',
                busyNotes=[note.Note('G'), note.Note('F#'), note.Note('E')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='total turn notes length longer than simple note',
                busyNotes=[note.Note('G'), note.Note('F#'), note.Note('E'), note.Note('F#')],
                simpleNotes=[n1],
                isOrnament=False)
        )

        # run test
        for cond in testConditions:
            turnRecognizer = TurnRecognizer()
            if cond.simpleNotes:
                turn = turnRecognizer.recognize(cond.busyNotes, simpleNotes=cond.simpleNotes)
            else:
                turn = turnRecognizer.recognize(cond.busyNotes)

            if cond.isOrnament:
                if cond.isInverted:
                    self.assertIsInstance(turn, expressions.InvertedTurn, cond.name)
                else:
                    self.assertIsInstance(turn, expressions.Turn, cond.name)
            else:
                self.assertFalse(turn, cond.name)

    def testRecognizeTrill(self):
        # set up the experiment
        testConditions = []

        n1Duration = duration.Duration('quarter')
        t1NumNotes = 4
        t1UpInterval = interval.Interval('M2')
        t1DownInterval = interval.Interval('M-2')
        n1Lower = note.Note('G')
        n1Lower.duration = n1Duration
        n1Upper = note.Note('A')
        n1Upper.duration = n1Duration
        t1 = expressions.Trill()
        t1NoteDuration = calculateTrillNoteDuration(t1NumNotes, n1Duration)
        t1.quarterLength = t1NoteDuration
        t1Notes = t1.realize(n1Lower)[0]  # GAGA
        t1NotesWithRest = deepcopy(t1Notes)  # GA_A
        r1 = note.Rest()
        r1.duration = duration.Duration(t1NoteDuration)
        t1NotesWithRest[2] = r1
        testConditions.append(
            _TestCondition(
                name='even whole step trill up without simple note',
                busyNotes=t1Notes,
                isOrnament=True,
                ornamentSize=t1UpInterval)
        )
        testConditions.append(
            _TestCondition(
                name='even whole step trill up from simple note',
                busyNotes=t1Notes,
                simpleNotes=[n1Lower],
                isOrnament=True,
                ornamentSize=t1UpInterval)
        )
        testConditions.append(
            _TestCondition(
                name='even whole step trill up to simple note',
                busyNotes=t1Notes,
                simpleNotes=[n1Upper],
                isOrnament=True,
                ornamentSize=t1DownInterval)
        )
        testConditions.append(
            _TestCondition(
                name='valid trill up to enharmonic simple note',
                busyNotes=t1Notes,
                simpleNotes=[note.Note('G##')],  # A
                isOrnament=True,
                ornamentSize=t1DownInterval)
        )
        testConditions.append(
            _TestCondition(
                name='valid trill but not with simple note',
                busyNotes=t1Notes,
                simpleNotes=[note.Note('E')],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='invalid trill has rest inside',
                busyNotes=t1NotesWithRest,
                isOrnament=False)
        )

        n2Duration = duration.Duration('half')
        t2NumNotes = 5
        t2UpInterval = interval.Interval('m2')
        t2DownInterval = interval.Interval('m-2')
        n2Lower = note.Note('G#')
        n2Lower.duration = n2Duration
        n2Upper = note.Note('A')
        n2Upper.duration = n2Duration
        t2NoteDuration = duration.Duration(calculateTrillNoteDuration(t2NumNotes, n2Duration))
        t2n1 = note.Note('A')  # trill2note1
        t2n1.duration = t2NoteDuration
        t2n2 = note.Note('G#')
        t2n2.duration = t2NoteDuration
        t2Notes = stream.Stream()  # A G# A G# A
        t2Notes.append([t2n1, t2n2, deepcopy(t2n1), deepcopy(t2n2), deepcopy(t2n1)])
        testConditions.append(
            _TestCondition(
                name='odd half step trill down without simple note',
                busyNotes=t2Notes,
                isOrnament=True,
                ornamentSize=t2DownInterval)
        )
        testConditions.append(
            _TestCondition(
                name='odd half step trill down to simple note',
                busyNotes=t2Notes,
                simpleNotes=[n2Lower],
                isOrnament=True,
                ornamentSize=t2UpInterval)
        )
        testConditions.append(
            _TestCondition(
                name='odd trill down from simple note',
                busyNotes=t2Notes,
                simpleNotes=[n2Upper],
                isOrnament=True,
                ornamentSize=t2DownInterval)
        )

        n3Duration = duration.Duration('quarter')
        t3NumNotes = 8
        t3UpInterval = interval.Interval('m2')
        t3DownInterval = interval.Interval('m-2')
        n3 = note.Note('B')
        n3.duration = n3Duration
        t3NoteDuration = duration.Duration(calculateTrillNoteDuration(t3NumNotes, n3Duration))
        t3n1 = note.Note('C5')
        t3n1.duration = t3NoteDuration
        t3n2 = note.Note('B')
        t3n2.duration = t3NoteDuration
        nachschlagN1 = note.Note('D5')
        nachschlagN1.duration = t3NoteDuration
        nachschlagN2 = note.Note('E5')
        nachschlagN2.duration = t3NoteDuration
        nachschlagN3 = note.Note('F5')
        nachschlagN3.duration = t3NoteDuration
        t3Notes = stream.Stream()  # C B C B C D E F
        t3Notes.append(
            [t3n1, t3n2, deepcopy(t3n1), deepcopy(t3n2), deepcopy(t3n1),
            nachschlagN1, nachschlagN2, nachschlagN3]
        )

        testConditions.append(
            _TestCondition(
                name='Nachschlag trill when not checking for nachschlag',
                busyNotes=t3Notes,
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='Nachschlag trill when checking for nachschlag',
                busyNotes=t3Notes,
                isNachschlag=True,
                isOrnament=True,
                ornamentSize=t3DownInterval)
        )
        testConditions.append(
            _TestCondition(
                name='Nachschlag trill when checking for nachschlag up to simple note',
                busyNotes=t3Notes,
                simpleNotes=[n3],
                isNachschlag=True,
                isOrnament=True,
                ornamentSize=t3UpInterval)
        )

        t4Duration = duration.Duration('eighth')
        t4n1 = note.Note('A')
        t4n1.duration = t4Duration
        t4n2 = note.Note('G')
        t4n2.duration = t4Duration
        testConditions.append(
            _TestCondition(
                name='One note not a trill',
                busyNotes=[t4n1],
                isOrnament=False)
        )
        testConditions.append(
            _TestCondition(
                name='Two notes not a trill',
                busyNotes=[t4n1, t4n2],
                isOrnament=False)
        )

        t5NoteDuration = duration.Duration('eighth')
        t5n1 = note.Note('A')  # trill2note1
        t5n1.duration = t5NoteDuration
        t5n2 = note.Note('C')
        t5n2.duration = t5NoteDuration
        t5Notes = stream.Stream()  # A C A C
        t5Notes.append([t5n1, t5n2, deepcopy(t5n1), deepcopy(t5n2)])
        testConditions.append(
            _TestCondition(
                name='Too big of oscillating interval to be trill',
                busyNotes=t5Notes,
                isOrnament=False)
        )

        t6NoteDuration = duration.Duration('eighth')
        t6n1 = note.Note('F')  # trill2note1
        t6n1.duration = t6NoteDuration
        t6n2 = note.Note('E')
        t6n2.duration = t6NoteDuration
        t6n3 = note.Note('G')
        t6n3.duration = t2NoteDuration
        t5Notes = stream.Stream()  # F E F G
        t5Notes.append([t6n1, t6n2, deepcopy(t6n1), t6n3])
        testConditions.append(
            _TestCondition(
                name='Right interval but not oscillating between same notes',
                busyNotes=t5Notes,
                isOrnament=False)
        )

        # run test
        for cond in testConditions:
            trillRecognizer = TrillRecognizer()
            if cond.isNachschlag:
                trillRecognizer.checkNachschlag = True

            if cond.simpleNotes:
                trill = trillRecognizer.recognize(cond.busyNotes, simpleNotes=cond.simpleNotes)
            else:
                trill = trillRecognizer.recognize(cond.busyNotes)

            if cond.isOrnament:
                self.assertIsInstance(trill, expressions.Trill, cond.name)
                # ensure trill is correct
                self.assertEqual(trill.nachschlag, cond.isNachschlag, cond.name)
                if cond.ornamentSize:
                    if cond.simpleNotes:
                        if cond.simpleNotes[0].pitch.midi == cond.busyNotes[1].pitch.midi:
                            size = trill.getSize(cond.busyNotes[1])
                        else:
                            size = trill.getSize(cond.busyNotes[0])
                    else:
                        size = trill.getSize(cond.busyNotes[0])
                    self.assertEqual(size, cond.ornamentSize, cond.name)
            else:
                self.assertFalse(trill, cond.name)


def calculateTrillNoteDuration(numTrillNotes, totalDuration):
    return totalDuration.quarterLength / numTrillNotes


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
