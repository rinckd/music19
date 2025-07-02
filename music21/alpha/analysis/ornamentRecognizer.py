# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         alpha/analysis/ornamentRecognizer.py
# Purpose:      Identifies expanded ornaments
#
# Authors:      Janelle Sands
#
# Copyright:    Copyright © 2016 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

from copy import deepcopy
from music21.common.numberTools import opFrac
from music21.common.types import OffsetQL
from music21 import duration
from music21 import expressions
from music21 import interval
from music21 import note
from music21 import stream

class OrnamentRecognizer:
    '''
    An object to identify if a stream of notes is an expanded ornament.
    Busy notes refer to the expanded ornament notes.
    Simple note(s) refer to the base note of ornament which is often shown
    with the ornament marking on it.
    '''
    def calculateOrnamentNoteQl(
        self,
        busyNotes,
        simpleNotes=None
    ):
        '''
        Finds the quarter length value for each ornament note
        assuming busy notes all are an expanded ornament.

        Expanded ornament total duration is time of all busy notes combined or
        duration of the first note in simpleNotes when provided.
        '''
        numOrnamentNotes = len(busyNotes)
        totalDurationQuarterLength = self.calculateOrnamentTotalQl(busyNotes, simpleNotes)
        return opFrac(totalDurationQuarterLength / numOrnamentNotes)

    def calculateOrnamentTotalQl(
        self,
        busyNotes: list[note.GeneralNote],
        simpleNotes: list[note.GeneralNote]|None = None
    ) -> OffsetQL:
        '''
        Returns total length of trill assuming busy notes are all an expanded trill.
        This is either the time of all busy notes combined or
        duration of the first note in simpleNotes when provided.
        '''
        if simpleNotes:
            return simpleNotes[0].duration.quarterLength
        trillQl: OffsetQL = 0.0
        for n in busyNotes:
            trillQl += float(n.duration.quarterLength)
        return opFrac(trillQl)

class TrillRecognizer(OrnamentRecognizer):
    '''
    An object to identify if a stream of ("busy") notes is an expanded trill.

    By default, does not consider Nachschlag trills, but setting checkNachschlag will consider.

    When optional stream of simpleNotes are provided, considers if busyNotes are
    an expansion of a trill which would be denoted on the first note in simpleNotes.
    '''
    def __init__(self, checkNachschlag=False):
        self.checkNachschlag = checkNachschlag
        self.acceptableInterval = 3
        self.minimumLengthForNachschlag = 5

    def recognize(self, busyNotes, simpleNotes=None) -> bool|expressions.Trill:
        '''
        Tries to identify the busy notes as a trill.

        When simple notes is provided, tries to identify busy notes
        as the trill shortened by simple notes.
        Currently only supports one simple note in simple notes.

        Only when checkNachschlag is true, allows last few notes to break trill rules.

        Trill interval size is interval between busy notes.

        Returns: False if not possible or the Trill Expression
        '''
        # Enough notes to trill
        if len(busyNotes) <= 2:
            return False

        # Oscillation pitches
        n1 = busyNotes[0]
        n2 = busyNotes[1]

        if not n1.isNote or not n2.isNote:
            return False

        if abs(n1.pitch.midi - n2.pitch.midi) > self.acceptableInterval:
            return False

        twoNoteOscillation = True
        i = 0
        for i in range(len(busyNotes)):
            noteConsidering = busyNotes[i]
            if not noteConsidering.isNote:
                return False
            if i % 2 == 0 and noteConsidering.pitch != n1.pitch:
                twoNoteOscillation = False
                break
            elif i % 2 != 0 and noteConsidering.pitch != n2.pitch:
                twoNoteOscillation = False
                break

        isNachschlag = False
        if twoNoteOscillation:
            pass
        elif not self.checkNachschlag:
            return False
        else:
            lengthOk = len(busyNotes) >= self.minimumLengthForNachschlag
            notTooMuchNachschlag = i >= len(busyNotes) / 2
            if lengthOk and notTooMuchNachschlag:
                isNachschlag = True
            else:
                return False

        if not simpleNotes:
            # set up trill (goes up) or inverted trill (goes down)
            if n1.pitch.midi <= n2.pitch.midi:
                trill = expressions.Trill()
            else:
                trill = expressions.InvertedTrill()
            trill.quarterLength = self.calculateOrnamentNoteQl(busyNotes, simpleNotes)
            if isNachschlag:
                trill.nachschlag = True

            if n2.pitch.accidental is not None:
                trill.accidental = n2.pitch.accidental
            trill.resolveOrnamentalPitches(n1)
            return trill

        # currently ignore other notes in simpleNotes
        simpleNote = simpleNotes[0]

        # enharmonic invariant checker
        if simpleNote.pitch.midi not in (n1.pitch.midi, n2.pitch.midi):
            return False

        endNote = n2
        startNote = n1
        if simpleNote.pitch.midi == n2.pitch.midi:
            endNote = n1
            startNote = n2

        # set up trill (goes up) or inverted trill (goes down)
        if startNote.pitch.midi <= endNote.pitch.midi:
            trill = expressions.Trill()
        else:
            trill = expressions.InvertedTrill()
        trill.quarterLength = self.calculateOrnamentNoteQl(busyNotes, simpleNotes)
        if isNachschlag:
            trill.nachschlag = True

        if endNote.pitch.accidental is not None:
            trill.accidental = endNote.pitch.accidental
        trill.resolveOrnamentalPitches(startNote)
        return trill

class TurnRecognizer(OrnamentRecognizer):
    def __init__(self, ):
        self.acceptableInterval = 3
        self.minimumLengthForNachschlag = 6
        self.acceptableIntervals = [
            interval.Interval('M2'), interval.Interval('M-2'),
            interval.Interval('m2'), interval.Interval('m-2'),
            interval.Interval('A2'), interval.Interval('A-2'),
        ]

    def isAcceptableInterval(self, intervalToCheck: interval.Interval) -> bool:
        '''
        Returns whether that interval can occur in a turn
        '''
        return intervalToCheck in self.acceptableIntervals

    def recognize(
        self,
        busyNotes,
        simpleNotes=None,
    ) -> bool|expressions.Turn|expressions.InvertedTurn:
        '''
        Tries to identify the busy notes as a turn or inverted turn.

        When simple notes is provided, tries to identify busy notes
        as the turn shortened by simple notes.
        Currently only supports one simple note in simple notes.

        Turns and inverted turns have four notes separated by m2, M2, A2.

        Turns:
        start above base note
        go down to base note,
        go down again,
        and go back up to base note

        Inverted Turns:
        start below base note
        go up to base note,
        go up again,
        and go back down to base note

        When going up or down, must go to the adjacent note name,
        so A goes down to G, G#, G flat, G##, etc

        Returns: False if not possible or the Turn/Inverted Turn Expression
        '''
        # number of notes/ duration of notes ok
        if len(busyNotes) != 4:
            return False

        if simpleNotes:
            eps = 0.1
            totalBusyNotesDuration = 0
            for n in busyNotes:
                totalBusyNotesDuration += n.duration.quarterLength
            if abs(simpleNotes[0].duration.quarterLength - totalBusyNotesDuration) > eps:
                return False

        # pitches ok
        if busyNotes[1].pitch.midi != busyNotes[3].pitch.midi:
            return False
        if simpleNotes and simpleNotes[0].pitch.midi != busyNotes[1].pitch.midi:
            return False

        # intervals ok
        firstInterval = interval.Interval(noteStart=busyNotes[0], noteEnd=busyNotes[1])
        if not self.isAcceptableInterval(firstInterval):
            return False
        secondInterval = interval.Interval(noteStart=busyNotes[1], noteEnd=busyNotes[2])
        if not self.isAcceptableInterval(secondInterval):
            return False
        thirdInterval = interval.Interval(noteStart=busyNotes[2], noteEnd=busyNotes[3])
        if not self.isAcceptableInterval(thirdInterval):
            return False

        # goes in same direction
        if firstInterval.direction != secondInterval.direction:
            return False
        # and then in opposite direction
        if secondInterval.direction == thirdInterval.direction:
            return False

        # decide direction of turn to return
        if firstInterval.direction == interval.Interval('M-2').direction:  # down
            turn = expressions.Turn()
        else:
            turn = expressions.InvertedTurn()
        turn.quarterLength = self.calculateOrnamentNoteQl(busyNotes, simpleNotes)
        return turn

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
