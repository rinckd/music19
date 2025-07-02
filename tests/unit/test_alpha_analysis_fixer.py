# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.alpha.analysis.fixer import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def measuresEqual(self, m1, m2):
        '''
        Returns a tuple of (bool, reason) where the first element is
        whether the measures are equal and the second (`reason`) is a string
        explaining why they are unequal.

        Reason is an empty string if the measures are equal.
        '''
        if len(m1) != len(m2):
            msg = 'not equal length'
            return False, msg
        for i in range(len(m1)):
            if len(m1[i].expressions) != len(m2[i].expressions):
                msg = f'Expressions {i} unequal ({m1[i].expressions} != {m2[i].expressions})'
                return False, msg
            if m1[i] != m2[i]:
                msg = f'Elements {i} are unequal ({m1[i]} != {m2[i]})'
                return False, msg
        return True, ''

    def checkFixerHelper(self, testCase, testFixer):
        '''
        testCase is a dictionary with the following keys

        returnDict = {
            'name': string,
            'midi': measure stream,
            'omr': measure stream,
            'expected': fixed measure stream,
        }

        testFixer is an OMRMidiFixer
        '''
        omr = testCase['omr']
        midi = testCase['midi']
        expectedOmr = testCase['expected']
        testingName = testCase['name']

        # set up aligner
        sa = aligner.StreamAligner(sourceStream=omr, targetStream=midi)
        sa.align()
        omrCopy = deepcopy(omr)
        assertionCheck = 'Expect no changes from creating and aligning aligner.'
        self.assertTrue(self.measuresEqual(omrCopy, sa.sourceStream)[0], assertionCheck)

        # set up fixer
        fixer = testFixer(sa.changes, sa.targetStream, sa.sourceStream)
        assertionCheck = 'Expect no changes from creating fixer.'
        self.assertTrue(self.measuresEqual(omrCopy, sa.sourceStream)[0], assertionCheck)

        # test fixing not in place
        notInPlaceResult = fixer.fix(inPlace=False)

        assertionCheck = '. Expect no changes to aligner source stream, but unequal because '
        isEqual, reason = self.measuresEqual(omrCopy, sa.sourceStream)
        self.assertTrue(isEqual, testingName + assertionCheck + reason)

        assertionCheck = '. Expect no changes to fixer omr stream, but unequal because '
        isEqual, reason = self.measuresEqual(omrCopy, fixer.omrStream)
        self.assertTrue(isEqual, testingName + assertionCheck + reason)

        assertionCheck = '. Appropriate changes in new fixer, but unequal because '
        isEqual, reason = self.measuresEqual(notInPlaceResult.omrStream, expectedOmr)
        self.assertTrue(isEqual, testingName + assertionCheck + reason)

        # test fixing in place
        fixerInPlaceResult = fixer.fix(inPlace=True)
        self.assertIsNone(fixerInPlaceResult, testingName)

        assertionCheck = ". Expect changes in fixer's omr stream, but unequal because "
        isEqual, reason = self.measuresEqual(expectedOmr, fixer.omrStream)
        self.assertTrue(isEqual, testingName + assertionCheck + reason)

        assertionCheck = '. Expect changes in original omr stream, but unequal because '
        isEqual, reason = self.measuresEqual(expectedOmr, omr)
        self.assertTrue(isEqual, testingName + assertionCheck + reason)

    def testGetNotesWithinDuration(self):
        n1 = note.Note('C')
        n1.duration = duration.Duration('quarter')
        m1 = stream.Stream()
        m1.append(n1)

        result = getNotesWithinDuration(n1, duration.Duration('quarter'))
        self.assertIsInstance(result, stream.Stream)
        self.assertListEqual([n1], list(result.notes), 'starting note occupies full duration')

        result = getNotesWithinDuration(n1, duration.Duration('half'))
        self.assertListEqual([n1], list(result.notes), 'starting note occupies partial duration')

        result = getNotesWithinDuration(n1, duration.Duration('eighth'))
        self.assertListEqual([], list(result.notes), 'starting note too long')

        m2 = stream.Measure()
        n2 = note.Note('D')
        n2.duration = duration.Duration('eighth')
        n3 = note.Note('E')
        n3.duration = duration.Duration('eighth')
        m2.append([n1, n2, n3])

        result = getNotesWithinDuration(n1, duration.Duration('quarter'))
        self.assertListEqual([n1], list(result.notes), 'starting note occupies full duration')

        result = getNotesWithinDuration(n1, duration.Duration('half'))
        self.assertListEqual([n1, n2, n3], list(result.notes), 'all notes fill up full duration')

        result = getNotesWithinDuration(n1, duration.Duration('whole'))
        self.assertListEqual([n1, n2, n3], list(result.notes), 'all notes fill up partial duration')

        result = getNotesWithinDuration(n1, duration.Duration(1.5))
        self.assertListEqual([n1, n2], list(result.notes), 'some notes fill up full duration')

        result = getNotesWithinDuration(n1, duration.Duration(1.75))
        self.assertListEqual([n1, n2], list(result.notes), 'some notes fill up partial duration')

        # set active site from m2 to m1 (which runs out of notes to fill up)
        result = getNotesWithinDuration(n1, duration.Duration('half'), referenceStream=m1)
        self.assertListEqual([n1], list(result.notes), 'partial fill up from reference stream m1')

        m3 = stream.Measure()
        m3.id = 'm3'
        r1 = note.Rest()
        r1.duration = duration.Duration('quarter')
        m3.append([n1, r1])  # n1 active site now with m2
        result = getNotesWithinDuration(n1, duration.Duration('half'))
        msg = 'note and rest fill up full duration'
        self.assertListEqual([n1, r1], list(result.notesAndRests), msg)

        # set active site from m3 to m2
        result = getNotesWithinDuration(n1, duration.Duration('half'), referenceStream=m2)
        self.assertListEqual([n1, n2, n3], list(result.notes), 'fill up from reference stream m2')

    def testTrillFixer(self):
        def createDoubleTrillMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            noteDuration = duration.Duration('quarter')

            # GAGA Trill
            trill1NoteDuration = duration.Duration(.25)
            n0 = note.Note('G')
            n0.duration = noteDuration
            n1 = note.Note('G')
            n1.duration = trill1NoteDuration
            n2 = note.Note('A')
            n2.duration = trill1NoteDuration
            trill1 = [n1, n2, deepcopy(n1), deepcopy(n2)]  # G A G A

            # C B C B Trill
            trill2NoteDuration = duration.Duration(.0625)
            n3 = note.Note('B3')  # omr
            n3.duration = noteDuration
            n4 = note.Note('B3')
            n4.duration = trill2NoteDuration
            n5 = note.Note('C')
            n5.duration = trill2NoteDuration
            trill2 = [n5, n4, deepcopy(n5), deepcopy(n4),
                      deepcopy(n5), deepcopy(n4), deepcopy(n5), deepcopy(n4)]

            midiMeasure = stream.Measure()
            midiMeasure.append(trill1)
            midiMeasure.append(trill2)

            omrMeasure = stream.Measure()
            omrMeasure.append([n0, n3])

            expectedFixedOmrMeasure = stream.Measure()
            n0WithTrill = deepcopy(n0)
            n0Trill = expressions.Trill()
            n0Trill.size = interval.Interval('m-2')
            n0Trill.quarterLength = trill1NoteDuration.quarterLength
            n0WithTrill.expressions.append(n0Trill)
            n1WithTrill = deepcopy(n3)
            n1Trill = expressions.Trill()
            n1Trill.size = interval.Interval('M2')
            n1Trill.quarterLength = trill2NoteDuration.quarterLength
            n1WithTrill.expressions.append(n0Trill)
            expectedFixedOmrMeasure.append([n0WithTrill, n1WithTrill])

            returnDict = {
                'name': 'Double Trill Measure',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': expectedFixedOmrMeasure,
            }
            return returnDict

        def createWrongTrillMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            noteDuration = duration.Duration('quarter')

            n0 = note.Note('C')  # omr
            n0.duration = noteDuration
            n1 = note.Note('C')
            n1.duration = duration.Duration(.25)
            n2 = note.Note('A')
            n2.duration = duration.Duration(.25)

            nonTrill = [n1, n2, deepcopy(n1), deepcopy(n2)]

            midiMeasure = stream.Measure()
            midiMeasure.append(nonTrill)
            omrMeasure = stream.Measure()
            omrMeasure.append(n0)

            returnDict = {
                'name': 'Non-Trill Measure Wrong Oscillate Interval',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': deepcopy(omrMeasure),
            }
            return returnDict

        def createNonTrillMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            noteDuration = duration.Duration('quarter')

            n0 = note.Note('A')  # omr
            n0.duration = noteDuration
            n1 = note.Note('C')
            n1.duration = duration.Duration(.25)
            n2 = note.Note('D')
            n2.duration = duration.Duration(.25)

            nonTrill = [n1, n2, deepcopy(n1), deepcopy(n2)]

            midiMeasure = stream.Measure()
            midiMeasure.append(nonTrill)
            omrMeasure = stream.Measure()
            omrMeasure.append(n0)

            returnDict = {
                'name': 'Non-Trill Measure Wrong Notes',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': deepcopy(omrMeasure),
            }

            return returnDict

        def createNachschlagTrillMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            noteDuration = duration.Duration('quarter')
            trillDuration = duration.Duration(.125)

            n0 = note.Note('E')
            n0.duration = noteDuration

            tn1 = note.Note('E')
            tn1.duration = trillDuration
            tn2 = note.Note('F')
            tn2.duration = trillDuration
            tn3 = note.Note('D')
            tn3.duration = trillDuration
            firstHalfTrill = [tn1, tn2, deepcopy(tn1), deepcopy(tn2)]
            secondHalfTrill = [deepcopy(tn1), deepcopy(tn2), deepcopy(tn1), tn3]
            expandedTrill = firstHalfTrill + secondHalfTrill

            midiMeasure = stream.Measure()
            midiMeasure.append(expandedTrill)
            omrMeasure = stream.Measure()
            omrMeasure.append(n0)

            nachschlagTrill = expressions.Trill()
            nachschlagTrill.nachschlag = True
            nachschlagTrill.quarterLength = trillDuration.quarterLength
            expectedFixedOmrMeasure = stream.Measure()
            noteWithTrill = deepcopy(n0)
            noteWithTrill.expressions.append(deepcopy(nachschlagTrill))
            expectedFixedOmrMeasure.append(noteWithTrill)

            returnDict = {
                'name': 'Nachschlag Trill',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': expectedFixedOmrMeasure,
            }

            return returnDict

        def createMeasureWithTrillAlready():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            noteDuration = duration.Duration('quarter')
            trillDuration = duration.Duration(.125)

            noteWithTrill = note.Note('F')
            noteWithTrill.duration = noteDuration
            trill = expressions.Trill()
            trill.quarterLength = trillDuration.quarterLength
            noteWithTrill.expressions.append(trill)

            tn1 = note.Note('F')
            tn1.duration = trillDuration
            tn2 = note.Note('G')
            tn2.duration = trillDuration
            expandedTrill = [tn1, tn2, deepcopy(tn1), deepcopy(tn2)]

            midiMeasure = stream.Measure()
            midiMeasure.append(expandedTrill)
            omrMeasure = stream.Measure()
            omrMeasure.append(noteWithTrill)

            returnDict = {
                'name': 'OMR with Trill Notation',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': deepcopy(omrMeasure),
            }
            return returnDict

        testConditions = [
            createDoubleTrillMeasure(),
            createWrongTrillMeasure(),
            createNonTrillMeasure(),
            createNachschlagTrillMeasure(),
            createMeasureWithTrillAlready(),
        ]

        for testCase in testConditions:
            self.checkFixerHelper(testCase, TrillFixer)

    def testTurnFixer(self):
        def createSingleTurnMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            omrMeasure = stream.Measure()
            omrNote = note.Note('F')
            omrNote.duration = duration.Duration('whole')
            omrMeasure.append(omrNote)

            expectedFixedOmrMeasure = stream.Stream()
            expectedOmrNote = deepcopy(omrNote)
            expectedOmrNote.expressions.append(expressions.Turn())
            expectedFixedOmrMeasure.append(expectedOmrNote)

            midiMeasure = stream.Measure()
            turn = [note.Note('G'), note.Note('F'), note.Note('E'), note.Note('F')]
            midiMeasure.append(turn)

            returnDict = {
                'name': 'Single Turn Measure',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': expectedFixedOmrMeasure,
            }
            return returnDict

        def createDoubleInvertedTurnMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            omrMeasure = stream.Measure()
            omrNote1 = note.Note('B-')
            middleNote = note.Note('G')
            omrNote2 = note.Note('B-')  # enharmonic to trill
            omrMeasure.append([omrNote1, middleNote, omrNote2])


            expectedFixedOmrMeasure = stream.Stream()
            expectOmrNote1 = deepcopy(omrNote1)
            expectOmrNote1.expressions.append(expressions.InvertedTurn())
            expectOmrNote2 = deepcopy(omrNote2)
            expectOmrNote2.expressions.append(expressions.InvertedTurn())
            expectedFixedOmrMeasure.append([expectOmrNote1, deepcopy(middleNote), expectOmrNote2])

            midiMeasure = stream.Measure()
            turn1 = [note.Note('A'), note.Note('B-'), note.Note('C5'), note.Note('B-')]
            turn2 = [note.Note('G#'), note.Note('A#'), note.Note('B'), note.Note('A#')]
            for n in turn1:
                n.duration = duration.Duration(.25)
            for n in turn2:
                n.duration = duration.Duration(.25)
            midiMeasure.append([*turn1, deepcopy(middleNote), *turn2])

            returnDict = {
                'name': 'Inverted turns with accidentals separated By non-ornament Note',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': expectedFixedOmrMeasure,
            }
            return returnDict

        def createNonTurnMeasure():
            '''
            Returns a dictionary with the following keys

            returnDict = {
                'name': string,
                'midi': measure stream,
                'omr': measure stream,
                'expected': measure stream,
            }
            '''
            omrMeasure = stream.Measure()
            omrNote = note.Note('A')
            omrNote.duration = duration.Duration('whole')
            omrMeasure.append(omrNote)

            midiMeasure = stream.Measure()
            turn = [note.Note('B'), note.Note('A'), note.Note('G'), note.Note('F')]
            midiMeasure.append(turn)

            returnDict = {
                'name': 'Non-Turn Measure',
                'midi': midiMeasure,
                'omr': omrMeasure,
                'expected': deepcopy(omrMeasure),
            }
            return returnDict

        testConditions = [createSingleTurnMeasure(),
                          createDoubleInvertedTurnMeasure(),
                          createNonTurnMeasure()]

        for testCase in testConditions:
            self.checkFixerHelper(testCase, TurnFixer)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
