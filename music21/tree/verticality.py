# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Name:         tree/verticality.py
# Purpose:      Object for dealing with vertical simultaneities in a
#               fast way w/o Chord's overhead
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2013-2016 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ----------------------------------------------------------------------------
'''
Object for dealing with vertical simultaneities in a fast way w/o Chord's overhead.
'''
from __future__ import annotations

from collections.abc import Iterable, Sequence
import copy
import itertools
import typing as t
from typing import overload
from music21 import chord
from music21 import common
from music21 import environment
from music21 import exceptions21
from music21 import note
from music21 import prebase
from music21 import tie
# from music21 import key
# from music21 import pitch
from music21.common.types import OffsetQL, OffsetQLIn
from music21.tree import spans

if t.TYPE_CHECKING:
    from music21.tree.trees import OffsetTree
    from music21.voiceLeading import VoiceLeadingQuartet

environLocal = environment.Environment('tree.verticality')

PitchedTimespanQuartet = tuple[
    tuple[spans.PitchedTimespan, spans.PitchedTimespan],
    tuple[spans.PitchedTimespan, spans.PitchedTimespan],
]

class VerticalityException(exceptions21.TreeException):
    pass

class Verticality(prebase.ProtoM21Object):
    r'''
    A collection of information about elements that are sounding at a given
    offset or just finished at that offset or are continuing from before, etc..

    Create a timespan-stream from a score:

    >>> score = corpus.parse('bwv66.6')
    >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
    ...        classList=(note.Note, chord.Chord))

    Find the verticality at offset 6.5, or beat 2.5 of measure 2 (there's a one
    beat pickup)

    >>> verticality = scoreTree.getVerticalityAt(6.5)
    >>> verticality
    <music21.tree.verticality.Verticality 6.5 {E3 D4 G#4 B4}>

    The representation of a verticality gives the pitches from lowest to
    highest (in sounding notes).

    A verticality knows its offset, but because elements might end at
    different times, it doesn't know its endTime

    >>> verticality.offset
    6.5
    >>> verticality.endTime
    Traceback (most recent call last):
    AttributeError: 'Verticality' object has no attribute 'endTime'

    However, we can find when the next verticality starts by looking at the nextVerticality

    >>> nv = verticality.nextVerticality
    >>> nv
    <music21.tree.verticality.Verticality 7.0 {A2 C#4 E4 A4}>
    >>> nv.offset
    7.0

    Or more simply:

    >>> verticality.nextStartOffset
    7.0

    (There is also a previousVerticality, but not a previousStartOffset)

    What we just demonstrated is actually very powerful: a Verticality keeps a
    record of exactly where it is in the timespanTree -- scores can be
    recreated with this information.

    Getting back to the task at hand, we can find all the PitchedTimespans (and
    from there the elements) that start at exactly 6.5.  There's one, it's a
    passing tone D in the tenor.  It lasts from offset 6.5 to offset 7.0,
    with respect to the beginning of the score, not to the beginning of the
    measure.  That is to say, it's an eighth note.

    >>> verticality.startTimespans
    (<PitchedTimespan (6.5 to 7.0) <music21.note.Note D>>,)

    And we can get all the PitchedTimespans that were already sounding at the
    moment (that is to say, the non-passing tones):

    >>> verticality.overlapTimespans
    (<PitchedTimespan (6.0 to 7.0) <music21.note.Note B>>,
     <PitchedTimespan (6.0 to 7.0) <music21.note.Note G#>>,
     <PitchedTimespan (6.0 to 7.0) <music21.note.Note E>>)

    And we can get all the things that stop right at this moment.  It's the E
    in the tenor preceding the passing tone D:

    >>> verticality.stopTimespans
    (<PitchedTimespan (6.0 to 6.5) <music21.note.Note E>>,)
    '''

    # CLASS VARIABLES #

    __slots__ = (
        'offsetTree',
        'timespanTree',
        'overlapTimespans',
        'startTimespans',
        'offset',
        'stopTimespans',
    )

    _DOC_ATTR: dict[str, str] = {
        'offsetTree': r'''
            Returns the tree initially set else None
            ''',
        'timespanTree': r'''
            Returns the tree initially set if it was a TimespanTree, else None
            ''',
        'overlapTimespans': r'''
            Gets timespans overlapping the start offset of a verticality.

            >>> score = corpus.parse('bwv66.6')
            >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
            ...            classList=(note.Note, chord.Chord))
            >>> verticality = scoreTree.getVerticalityAt(0.5)
            >>> verticality
            <music21.tree.verticality.Verticality 0.5 {G#3 B3 E4 B4}>
            >>> verticality.overlapTimespans
            (<PitchedTimespan (0.0 to 1.0) <music21.note.Note E>>,)
            ''',
        'startTimespans': r'''
            Gets the timespans starting at a verticality's start offset.

            >>> score = corpus.parse('bwv66.6')
            >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
            ...            classList=(note.Note, chord.Chord))
            >>> verticality = scoreTree.getVerticalityAt(1.0)
            >>> verticality
            <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>
            >>> for timespan in verticality.startTimespans:
            ...     timespan
            ...
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note A>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note F#>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note C#>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note F#>>
            ''',
        'offset': r'''
            Gets the start offset of a verticality.

            >>> score = corpus.parse('bwv66.6')
            >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
            ...            classList=(note.Note, chord.Chord))
            >>> verticality = scoreTree.getVerticalityAt(1.0)
            >>> verticality
            <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>
            >>> verticality.offset
            1.0
            ''',
        'stopTimespans': r'''
            Gets the timespans stopping at a verticality's start offset.

            >>> score = corpus.parse('bwv66.6')
            >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
            ...                classList=(note.Note, chord.Chord))
            >>> verticality = scoreTree.getVerticalityAt(1.0)
            >>> verticality
            <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>

            Note that none of the elements in the stopTimespans are listed in
            the repr for the Verticality

            >>> for timespan in verticality.stopTimespans:
            ...     timespan
            ...
            <PitchedTimespan (0.0 to 1.0) <music21.note.Note E>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note B>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note B>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note G#>>
            ''',
    }

    # INITIALIZER #

    def __init__(
        self,
        offset: OffsetQL = 0.0,
        overlapTimespans: tuple[spans.ElementTimespan, ...] = (),
        startTimespans: tuple[spans.ElementTimespan, ...] = (),
        stopTimespans: tuple[spans.ElementTimespan, ...] = (),
        timespanTree=None,
    ):
        from music21.tree.timespanTree import TimespanTree
        self.offsetTree: OffsetTree | None = timespanTree
        self.timespanTree: TimespanTree | None = None
        if isinstance(timespanTree, TimespanTree):
            self.timespanTree = timespanTree

        self.offset: OffsetQL = offset

        if not isinstance(startTimespans, tuple):
            raise VerticalityException(
                f'startTimespans must be a tuple of ElementTimespans, not {startTimespans!r}')
        if not isinstance(stopTimespans, tuple):
            raise VerticalityException(
                f'stopTimespans must be a tuple of ElementTimespans, not {stopTimespans!r}')
        if not isinstance(overlapTimespans, tuple):
            raise VerticalityException(
                f'overlapTimespans must be a tuple of ElementTimespans, not {overlapTimespans!r}')

        self.startTimespans: tuple[spans.ElementTimespan, ...] = startTimespans
        self.stopTimespans: tuple[spans.ElementTimespan, ...] = stopTimespans
        self.overlapTimespans: tuple[spans.ElementTimespan, ...] = overlapTimespans

    # SPECIAL METHODS #

    def _reprInternal(self):
        sortedPitches = sorted(self.pitchSet)
        enclosedNames = '{' + ' '.join(x.nameWithOctave for x in sortedPitches) + '}'
        return f'{self.offset} {enclosedNames}'

    # PUBLIC PROPERTIES #

    @property
    def bassTimespan(self):
        r'''
        Gets the bass timespan in this verticality.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> verticality
        <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>

        >>> verticality.bassTimespan
        <PitchedTimespan (1.0 to 2.0) <music21.note.Note F#>>
        '''
        overallLowestPitch = None
        lowestTimespan = None

        for ts in self.startAndOverlapTimespans:
            if not hasattr(ts, 'pitches'):
                continue

            tsPitches = ts.pitches
            if not tsPitches:
                continue

            lowestPitch = sorted(tsPitches)[0]
            if overallLowestPitch is None:
                overallLowestPitch = lowestPitch
                lowestTimespan = ts
            if lowestPitch <= overallLowestPitch:
                overallLowestPitch = lowestPitch
                lowestTimespan = ts

        return lowestTimespan

    @property
    def beatStrength(self):
        r'''
        Gets the beat strength of a verticality.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> verticality.beatStrength
        1.0

        Note that it will return None if there are no startTimespans at this point:

        >>> verticality = scoreTree.getVerticalityAt(1.25)
        >>> verticality
        <music21.tree.verticality.Verticality 1.25 {F#3 C#4 F#4 A4}>
        >>> verticality.startTimespans
        ()
        >>> verticality.beatStrength is None
        True
        '''
        try:
            thisTimespan = self.startTimespans[0]
        except IndexError:
            return None
        return thisTimespan.element.beatStrength

    def toChord(self):
        '''
        Creates a chord.Chord object of default length (1.0 or
        the duration of some note object) from the verticality.

        Does nothing about ties, etc. -- it's a very dumb chord, but useful
        for querying consonance, etc.  See makeElement() for the smart version.

        It may be a zero- or one-pitch chord.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans()
        >>> verticality = scoreTree.getVerticalityAt(4.0)
        >>> verticality.toChord()
        <music21.chord.Chord G#3 B3 E4 E5>
        '''
        c = chord.Chord(sorted(self.pitchSet))
        return c

    @property
    def measureNumber(self):
        r'''
        Gets the measure number of the verticality's starting elements.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(7.0)
        >>> verticality.measureNumber
        2
        '''
        return self.startTimespans[0].measureNumber

    @property
    def nextStartOffset(self) -> float|None:
        r'''
        Gets the next start-offset in the verticality's offset-tree.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> verticality.nextStartOffset
        2.0

        If a verticality has no tree attached, then it will return None
        '''
        tree = self.offsetTree
        if tree is None:
            return None
        offset = tree.getPositionAfter(self.offset)
        return offset

    @property
    def nextVerticality(self):
        r'''
        Gets the next verticality after a verticality.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> print(verticality)
        <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>

        >>> nextVerticality = verticality.nextVerticality
        >>> print(nextVerticality)
        <music21.tree.verticality.Verticality 2.0 {G#3 B3 E4 B4}>

        Verticality objects created by an offset-tree hold a reference back to
        that offset-tree. This means that they determine their next or previous
        verticality dynamically based on the state of the offset-tree only when
        asked. Because of this, it is safe to mutate the offset-tree by
        inserting or removing timespans while iterating over it.

        >>> scoreTree.removeTimespanList(nextVerticality.startTimespans)
        >>> verticality.nextVerticality
        <music21.tree.verticality.Verticality 3.0 {A3 E4 C#5}>
        '''
        tree = self.offsetTree
        if tree is None:
            return None
        offset = tree.getPositionAfter(self.offset)
        if offset is None:
            return None
        return tree.getVerticalityAt(offset)

    @property
    def pitchSet(self):
        r'''
        Gets the pitch set of all elements in a verticality.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> for pitch in sorted(verticality.pitchSet):
        ...     pitch
        ...
        <music21.pitch.Pitch F#3>
        <music21.pitch.Pitch C#4>
        <music21.pitch.Pitch F#4>
        <music21.pitch.Pitch A4>
        '''
        pitchNameSet = set()
        pitchSet = set()

        for timespan in self.startAndOverlapTimespans:
            if not hasattr(timespan, 'pitches'):
                continue
            for p in timespan.pitches:
                pName = p.nameWithOctave
                if pName in pitchNameSet:
                    continue

                pitchNameSet.add(pName)
                pitchSet.add(p)

        return pitchSet

    @property
    def pitchClassSet(self):
        # noinspection PyShadowingNames
        r'''
        Gets a set of all pitches in a verticality with distinct pitchClasses

        >>> n1 = note.Note('C4')
        >>> n2 = note.Note('B#5')
        >>> s = stream.Stream()
        >>> s.insert(4.0, n1)
        >>> s.insert(4.0, n2)
        >>> scoreTree = s.asTimespans()
        >>> verticality = scoreTree.getVerticalityAt(4.0)
        >>> pitchSet = verticality.pitchSet
        >>> list(sorted(pitchSet))
        [<music21.pitch.Pitch C4>, <music21.pitch.Pitch B#5>]

        PitchClassSet will return only one pitch.  Which of these
        is returned is arbitrary.

        >>> pitchClassSet = verticality.pitchClassSet
        >>> #_DOCS_SHOW list(sorted(pitchClassSet))
        >>> print('[<music21.pitch.Pitch B#5>]')  #_DOCS_HIDE
        [<music21.pitch.Pitch B#5>]
        '''
        outPitchSet = set()
        pitchClassSet = set()

        for currentPitch in self.pitchSet:
            pitchClass = currentPitch.pitchClass
            if pitchClass in pitchClassSet:
                continue

            pitchClassSet.add(pitchClass)
            outPitchSet.add(currentPitch)
        return outPitchSet

    @property
    def previousVerticality(self):
        r'''
        Gets the previous verticality before a verticality.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> print(verticality)
        <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>

        >>> previousVerticality = verticality.previousVerticality
        >>> print(previousVerticality)
        <music21.tree.verticality.Verticality 0.5 {G#3 B3 E4 B4}>

        Continue it:

        >>> v = scoreTree.getVerticalityAt(1.0)
        >>> while v is not None:
        ...     print(v)
        ...     v = v.previousVerticality
        <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>
        <music21.tree.verticality.Verticality 0.5 {G#3 B3 E4 B4}>
        <music21.tree.verticality.Verticality 0.0 {A3 E4 C#5}>

        Verticality objects created by an offset-tree hold a reference back to
        that offset-tree. This means that they determine their next or previous
        verticality dynamically based on the state of the offset-tree only when
        asked. Because of this, it is safe to mutate the offset-tree by
        inserting or removing timespans while iterating over it.

        >>> scoreTree.removeTimespanList(previousVerticality.startTimespans)
        >>> verticality.previousVerticality
        <music21.tree.verticality.Verticality 0.0 {A3 E4 C#5}>
        '''
        tree = self.offsetTree
        if tree is None:
            return None
        offset = tree.getPositionBefore(self.offset)
        if offset is None:
            return None
        return tree.getVerticalityAt(offset)

    @property
    def startAndOverlapTimespans(self):
        '''
        Return a tuple adding the start and overlap timespans into one.

        >>> n1 = note.Note('C4')
        >>> n2 = note.Note('D4')
        >>> s = stream.Stream()
        >>> s.insert(4.0, n1)
        >>> s.insert(4.5, n2)
        >>> scoreTree = s.asTimespans()
        >>> verticality = scoreTree.getVerticalityAt(4.5)
        >>> verticality.startTimespans
        (<PitchedTimespan (4.5 to 5.5) <music21.note.Note D>>,)

        >>> verticality.overlapTimespans
        (<PitchedTimespan (4.0 to 5.0) <music21.note.Note C>>,)

        >>> verticality.startAndOverlapTimespans
        (<PitchedTimespan (4.5 to 5.5) <music21.note.Note D>>,
         <PitchedTimespan (4.0 to 5.0) <music21.note.Note C>>)

        >>> verticality = scoreTree.getVerticalityAt(4.0)
        >>> verticality.startAndOverlapTimespans
        (<PitchedTimespan (4.0 to 5.0) <music21.note.Note C>>,)
        '''
        if self.overlapTimespans is None:
            return tuple(self.startTimespans)

        return tuple(self.startTimespans[:] + self.overlapTimespans[:])

    @property
    def timeToNextEvent(self) -> OffsetQL|None:
        '''
        Returns a float or Fraction of the quarterLength to the next
        event (usually the next Verticality, but also to the end of the piece).

        Returns None if there is no next event, such as when the verticality
        is divorced from its tree.
        '''
        nextOffset = self.nextStartOffset
        if nextOffset is None:
            if self.timespanTree is None:
                return None
            nextOffset = self.timespanTree.endTime
        return common.opFrac(nextOffset - self.offset)

    # makeElement

    def makeElement(
        self,
        quarterLength: OffsetQLIn|None = None,
        *,
        addTies=True,
        addPartIdAsGroup=False,
        removeRedundantPitches=True,
        gatherArticulations='single',
        gatherExpressions='single',
        copyPitches=True,
    ) -> note.Rest|chord.Chord:
        # noinspection PyDunderSlots, PyShadowingNames
        r'''
        Makes a Chord or Rest from this verticality and quarterLength.

        >>> score = tree.makeExampleScore()
        >>> scoreTree = tree.fromStream.asTimespans(score, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality = scoreTree.getVerticalityAt(4.0)
        >>> verticality
        <music21.tree.verticality.Verticality 4.0 {E#3 G3}>
        >>> verticality.startTimespans
        (<PitchedTimespan (4.0 to 5.0) <music21.note.Note G>>,
         <PitchedTimespan (4.0 to 6.0) <music21.note.Note E#>>)

        >>> el = verticality.makeElement(2.0)
        >>> el
        <music21.chord.Chord E#3 G3>
        >>> el.duration.quarterLength
        2.0
        >>> el.duration.type
        'half'

        If there is nothing there, then a Rest is created

        >>> verticality = scoreTree.getVerticalityAt(400.0)
        >>> verticality
        <music21.tree.verticality.Verticality 400.0 {}>
        >>> el = verticality.makeElement(1/3)
        >>> el
        <music21.note.Rest 1/3ql>
        >>> el.duration.fullName
        'Eighth Triplet (1/3 QL)'

        >>> n1 = note.Note('C4')
        >>> n2 = note.Note('C4')
        >>> s = stream.Score()
        >>> s.insert(0, n1)
        >>> s.insert(0.5, n2)
        >>> scoreTree = s.asTimespans()
        >>> verticality = scoreTree.getVerticalityAt(0.5)
        >>> c = verticality.makeElement(0.5)
        >>> c
        <music21.chord.Chord C4>

        >>> c = verticality.makeElement(0.5, removeRedundantPitches=False)
        >>> c
        <music21.chord.Chord C4 C4>

        Generally the pitches of the new element are not connected to the original pitch:

        >>> c[0].pitch.name = 'E'
        >>> c[1].pitch.name = 'F'
        >>> (n1.name, n2.name)
        ('C', 'C')

        But if `copyPitches` is False then the original pitch will be used:

        >>> n1.name = 'D'
        >>> n2.name = 'E'
        >>> c = verticality.makeElement(0.5, removeRedundantPitches=False, copyPitches=False)
        >>> c
        <music21.chord.Chord D4 E4>

        >>> c[0].pitch.name = 'F'
        >>> c[1].pitch.name = 'G'
        >>> (n1.name, n2.name)
        ('F', 'G')

        gatherArticulations and gatherExpressions can be True, False, or (default) 'single'.

        * If False, no articulations (or expressions) are transferred to the chord.
        * If True, all articulations are transferred to the chord.
        * If 'single', then no more than one articulation of each class
          (chosen from the lowest note) will be added.
          This way, the chord does not get 4 fermatas, etc.

        >>> n1 = note.Note('C4')
        >>> n2 = note.Note('D4')
        >>> s = stream.Stream()
        >>> s.insert(0, n1)
        >>> s.insert(0.5, n2)

        >>> class AllAttachArticulation(articulations.Articulation):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.tieAttach = 'all'

        >>> class OtherAllAttachArticulation(articulations.Articulation):
        ...     def __init__(self):
        ...         super().__init__()
        ...         self.tieAttach = 'all'

        >>> n1.articulations.append(articulations.Accent())
        >>> n1.articulations.append(AllAttachArticulation())
        >>> n1.expressions.append(expressions.Fermata())

        >>> n2.articulations.append(articulations.Staccato())
        >>> n2.articulations.append(AllAttachArticulation())
        >>> n2.articulations.append(OtherAllAttachArticulation())
        >>> n2.expressions.append(expressions.Fermata())

        >>> scoreTree = s.asTimespans()

        >>> verticality = scoreTree.getVerticalityAt(0.0)
        >>> c = verticality.makeElement(1.0)
        >>> c.expressions
        [<music21.expressions.Fermata>]
        >>> c.articulations
        [<music21.articulations.Accent>, <...AllAttachArticulation>]

        >>> verticality = scoreTree.getVerticalityAt(0.5)

        Here there will be no expressions, because there is no note ending
        at 0.75 and Fermatas attach to the last note:

        >>> c = verticality.makeElement(0.25)
        >>> c.expressions
        []

        >>> c = verticality.makeElement(0.5)
        >>> c.expressions
        [<music21.expressions.Fermata>]

        Only two articulations, since accent attaches to beginning
        and staccato attaches to last
        and we are beginning after the start of the first note (with an accent)
        and cutting right through the second note (with a staccato)

        >>> c.articulations
        [<...AllAttachArticulation>,
         <...OtherAllAttachArticulation>]

        >>> c = verticality.makeElement(0.5, gatherArticulations=True)
        >>> c.articulations
        [<...AllAttachArticulation>,
         <...AllAttachArticulation>,
         <...OtherAllAttachArticulation>]

        >>> c = verticality.makeElement(0.5, gatherArticulations=False)
        >>> c.articulations
        []

        >>> verticality = scoreTree.getVerticalityAt(1.0)
        >>> c = verticality.makeElement(0.5)
        >>> c.expressions
        [<music21.expressions.Fermata>]
        >>> c.articulations
        [<music21.articulations.Staccato>,
         <...AllAttachArticulation>,
         <...OtherAllAttachArticulation>]

        * New in v6.3: copyPitches option

        OMIT_FROM_DOCS

        Test that copyPitches works with expressions:

        >>> c = verticality.makeElement(0.5, copyPitches=False)
        >>> c
        <music21.chord.Chord D4>
        >>> c.pitches[0].accidental = pitch.Accidental('sharp')
        >>> n2
        <music21.note.Note D#>

        * Changed in v7.3: if quarterLength is not given, the duration
          to the next quarterLength is used.
        '''
        if quarterLength is None:
            event_duration = self.timeToNextEvent
            if event_duration is None:
                quarterLength = 1.0
            else:
                quarterLength = event_duration  # already opFrac
        else:
            quarterLength = common.opFrac(quarterLength)

        if not self.pitchSet:
            r = note.Rest()
            r.duration.quarterLength = quarterLength
            return r

        # easy stuff done, time to get to the hard stuff

        c = chord.Chord()
        c.duration.quarterLength = quarterLength
        dur = c.duration

        seenPitches = set()
        notesToAdd = {}

        startStopSet = {'start', 'stop'}
        pitchBust = 0  # used if removeRedundantPitches is False.

        # noinspection PyShadowingNames
        def newNote(ts: spans.PitchedTimespan, n: note.Note) -> note.Note:
            '''
            Make a copy of the note and clear some settings
            '''
            nNew = copy.deepcopy(n)
            nNew.duration = dur
            if not copyPitches:
                nNew.pitch = n.pitch

            if nNew.stemDirection != 'noStem':
                nNew.stemDirection = 'unspecified'
            if not addTies:
                return nNew

            offsetDifference = common.opFrac(self.offset - ts.offset)
            if t.TYPE_CHECKING:
                assert quarterLength is not None

            endTimeDifference = common.opFrac(ts.endTime - (self.offset + quarterLength))
            if t.TYPE_CHECKING:
                assert endTimeDifference is not None

            # noinspection PyTypeChecker
            if offsetDifference == 0 and endTimeDifference <= 0:
                addTie = None
            elif offsetDifference > 0:
                # noinspection PyTypeChecker
                if endTimeDifference > 0:
                    addTie = 'continue'
                else:
                    addTie = 'stop'
            elif endTimeDifference > 0:
                addTie = 'start'
            else:
                raise VerticalityException('What possibility was missed?',
                                           offsetDifference, endTimeDifference, ts, self)

            if nNew.tie is not None and {nNew.tie.type, addTie} == startStopSet:
                nNew.tie.type = 'continue'
            elif nNew.tie is not None and nNew.tie.type == 'continue':
                nNew.tie.placement = None
            elif addTie is None and nNew.tie is not None:
                nNew.tie.placement = None

            elif addTie:
                nNew.tie = tie.Tie(addTie)

            return nNew

        # noinspection PyShadowingNames
        def conditionalAdd(ts: spans.PitchedTimespan, n: note.Note) -> None:
            '''
            Add an element only if it is not already in the chord.

            If it has more tie information than the previously
            added note, then remove the previously added note and add it
            '''
            from music21 import stream

            nonlocal pitchBust  # love Py3!!!
            p = n.pitch
            pitchKey = p.nameWithOctave

            pitchGroup = None
            if addPartIdAsGroup:
                partContext = n.getContextByClass(stream.Part)
                if partContext is not None:
                    pidStr = str(partContext.id)
                    pitchGroup = pidStr.replace(' ', '_')  # spaces are not allowed as group names
                    n.pitch.groups.append(pitchGroup)
                    n.groups.append(pitchGroup)

            if pitchKey not in seenPitches:
                seenPitches.add(pitchKey)
                notesToAdd[pitchKey] = newNote(ts, n)
                return
            elif not removeRedundantPitches:
                notesToAdd[pitchKey + str(pitchBust)] = newNote(ts, n)
                pitchBust += 1
                return
            elif addPartIdAsGroup and pitchGroup is not None:
                notesToAdd[pitchKey].groups.append(pitchGroup)
                notesToAdd[pitchKey].pitch.groups.append(pitchGroup)

            if not addTies:
                return

            # else add derivation once multiple derivations are allowed.
            oldNoteTie = notesToAdd[pitchKey].tie
            if oldNoteTie is not None and oldNoteTie.type == 'continue':
                return  # previous note was as good or better

            possibleNewNote = newNote(ts, n)
            possibleNewNote.groups = notesToAdd[pitchKey].groups

            if possibleNewNote.tie is None:
                return  # do nothing

            if oldNoteTie is None:
                notesToAdd[pitchKey] = possibleNewNote  # a better note to add
            elif {oldNoteTie.type, possibleNewNote.tie.type} == startStopSet:
                other_t = notesToAdd[pitchKey].tie
                if other_t is not None:  # this test is not needed, except for mypy.
                    other_t.type = 'continue'
            elif possibleNewNote.tie.type == 'continue':
                notesToAdd[pitchKey] = possibleNewNote  # a better note to add
            elif possibleNewNote.tie.type == oldNoteTie.type:
                return
            else:
                raise VerticalityException('Did I miss one? ', possibleNewNote.tie, oldNoteTie)

        for timeSpan in self.startAndOverlapTimespans:
            if not isinstance(timeSpan, spans.PitchedTimespan):
                continue
            el = timeSpan.element
            if isinstance(el, chord.ChordBase):
                firstNoteElement: note.Note | None = None
                for subEl in el:
                    if isinstance(subEl, note.Note):
                        firstNoteElement = subEl
                        break

                if firstNoteElement is None:
                    continue

                if el.articulations or el.expressions:
                    # make a deepcopy of the first note element
                    # adding all articulations and expressions from the Chord to it.
                    originalPitch = firstNoteElement.pitch
                    firstNoteElement = copy.deepcopy(firstNoteElement)
                    firstNoteElement.articulations += el.articulations
                    firstNoteElement.expressions += el.expressions
                    if not copyPitches:
                        firstNoteElement.pitch = originalPitch
                conditionalAdd(timeSpan, firstNoteElement)

                if len(el) > 1:
                    for subEl in list(el)[1:]:
                        if isinstance(subEl, note.Note):
                            conditionalAdd(timeSpan, subEl)
            elif isinstance(el, note.Note):
                conditionalAdd(timeSpan, el)

        seenArticulations = set()
        seenExpressions = set()

        for n in sorted(notesToAdd.values(), key=lambda x: x.pitch.ps):
            c.add(n)
            if gatherArticulations:
                for art in n.articulations:
                    if art.tieAttach == 'first' and n.tie is not None and n.tie.type != 'start':
                        continue
                    if art.tieAttach == 'last' and n.tie is not None and n.tie.type != 'stop':
                        continue

                    if gatherArticulations == 'single' and type(art) in seenArticulations:
                        continue
                    c.articulations.append(art)
                    seenArticulations.add(type(art))
            if gatherExpressions:
                for exp in n.expressions:
                    if exp.tieAttach == 'first' and n.tie is not None and n.tie.type != 'start':
                        continue
                    if exp.tieAttach == 'last' and n.tie is not None and n.tie.type != 'stop':
                        continue

                    if gatherExpressions == 'single' and type(exp) in seenExpressions:
                        continue
                    c.expressions.append(exp)
                    seenExpressions.add(type(exp))

        return c

    # Analysis type things
    @overload
    def getAllVoiceLeadingQuartets(
        self,
        *,
        includeRests=True,
        includeOblique=True,
        includeNoMotion=False,
        returnObjects: t.Literal[False],
        partPairNumbers: list[tuple[int, int]] | None = None
    ) -> list[PitchedTimespanQuartet]:
        ...

    @overload
    def getAllVoiceLeadingQuartets(
        self,
        *,
        includeRests=True,
        includeOblique=True,
        includeNoMotion=False,
        returnObjects: t.Literal[True] = True,
        partPairNumbers: list[tuple[int, int]] | None = None
    ) -> list[VoiceLeadingQuartet]:
        ...

    def getAllVoiceLeadingQuartets(
        self,
        *,
        includeRests=True,
        includeOblique=True,
        includeNoMotion=False,
        returnObjects: bool = True,
        partPairNumbers: list[tuple[int, int]] | None = None
    ) -> list[VoiceLeadingQuartet] | list[PitchedTimespanQuartet]:
        # noinspection PyShadowingNames,PyCallingNonCallable
        '''
        >>> c = corpus.parse('luca/gloria').measures(1, 8)
        >>> tsCol = tree.fromStream.asTimespans(c, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality22 = tsCol.getVerticalityAt(22.0)

        >>> from pprint import pprint as pp
        >>> for vlq in verticality22.getAllVoiceLeadingQuartets():
        ...     pp(vlq)
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=G4, v1n2=C4, v2n1=E4, v2n2=F4>
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=G4, v1n2=C4, v2n1=A3, v2n2=A3>
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=E4, v1n2=F4, v2n1=A3, v2n2=A3>

        >>> for vlq in verticality22.getAllVoiceLeadingQuartets(includeRests=False):
        ...     pp(vlq)
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=E4, v1n2=F4, v2n1=A3, v2n2=A3>
        >>> for vlq in verticality22.getAllVoiceLeadingQuartets(includeOblique=False):
        ...     pp(vlq)
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=G4, v1n2=C4, v2n1=E4, v2n2=F4>
        >>> verticality22.getAllVoiceLeadingQuartets(includeOblique=False, includeRests=False)
        []

        Raw output, returns a 2-element tuple of 2-element tuples of PitchedTimespans

        >>> for vlqRaw in verticality22.getAllVoiceLeadingQuartets(returnObjects=False):
        ...     pp(vlqRaw)
        ((<PitchedTimespan (19.5 to 21.0) <music21.note.Note G>>,
          <PitchedTimespan (22.0 to 22.5) <music21.note.Note C>>),
         (<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
          <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>))
        ((<PitchedTimespan (19.5 to 21.0) <music21.note.Note G>>,
          <PitchedTimespan (22.0 to 22.5) <music21.note.Note C>>),
         (<PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>,
          <PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>))
        ((<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
          <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>),
         (<PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>,
          <PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>))

        >>> for vlq in verticality22.getAllVoiceLeadingQuartets(partPairNumbers=[(0, 1)]):
        ...     pp(vlq)
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=G4, v1n2=C4, v2n1=E4, v2n2=F4>

        >>> for vlq in verticality22.getAllVoiceLeadingQuartets(partPairNumbers=[(0, 2), (1, 2)]):
        ...     pp(vlq)
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=G4, v1n2=C4, v2n1=A3, v2n2=A3>
        <music21.voiceLeading.VoiceLeadingQuartet
            v1n1=E4, v1n2=F4, v2n1=A3, v2n2=A3>

        * Changed in v8: all parameters are keyword only.
        '''
        if not self.timespanTree:
            raise VerticalityException('Cannot iterate without .timespanTree defined')

        from music21.voiceLeading import VoiceLeadingQuartet
        pairedMotionList: list[
            tuple[spans.PitchedTimespan, spans.PitchedTimespan]
        ] = self.getPairedMotion(
            includeRests=includeRests,
            includeOblique=includeOblique
        )
        allPairedMotion = itertools.combinations(pairedMotionList, 2)
        filteredList: list[PitchedTimespanQuartet] = []
        filteredQuartet: list[VoiceLeadingQuartet] = []

        verticalityStreamParts = self.timespanTree.source.parts

        pairedMotion: PitchedTimespanQuartet
        for pairedMotion in allPairedMotion:
            if not hasattr(pairedMotion[0][0], 'pitches'):
                continue  # not a PitchedTimespan

            if includeNoMotion is False:
                if (pairedMotion[0][0].pitches == pairedMotion[0][1].pitches
                        and pairedMotion[1][0].pitches == pairedMotion[1][1].pitches):
                    continue

            if partPairNumbers is not None:
                isAppropriate = False
                for pp in partPairNumbers:
                    thisQuartetTopPart = pairedMotion[0][0].part
                    thisQuartetBottomPart = pairedMotion[1][0].part
                    if ((verticalityStreamParts[pp[0]] == thisQuartetTopPart
                            or verticalityStreamParts[pp[0]] == thisQuartetBottomPart)
                        and (verticalityStreamParts[pp[1]] == thisQuartetTopPart
                            or verticalityStreamParts[pp[1]] == thisQuartetBottomPart)):
                        isAppropriate = True
                        break
                if not isAppropriate:
                    continue

            if returnObjects is False:
                filteredList.append(pairedMotion)
            else:
                n11 = pairedMotion[0][0].element
                n12 = pairedMotion[0][1].element
                n21 = pairedMotion[1][0].element
                n22 = pairedMotion[1][1].element

                # fail on Chords for now.
                if (isinstance(n11, note.Note)
                        and isinstance(n12, note.Note)
                        and isinstance(n21, note.Note)
                        and isinstance(n22, note.Note)):
                    vlq = VoiceLeadingQuartet(n11, n12, n21, n22)
                    filteredQuartet.append(vlq)

        if returnObjects:
            return filteredQuartet
        return filteredList

    def getPairedMotion(
        self,
        *,
        includeRests: bool = True,
        includeOblique: bool = True
    ) -> list[tuple[spans.PitchedTimespan, spans.PitchedTimespan]]:
        '''
        Get a list of two-element tuples that are in the same part
        [TODO: or containing stream??]
        and which move at this verticality.

        >>> c = corpus.parse('luca/gloria').measures(1, 8)
        >>> tsCol = tree.fromStream.asTimespans(c, flatten=True,
        ...            classList=(note.Note, chord.Chord))
        >>> verticality22 = tsCol.getVerticalityAt(22.0)
        >>> for pm in verticality22.getPairedMotion():
        ...     print(pm)
        (<PitchedTimespan (19.5 to 21.0) <music21.note.Note G>>,
         <PitchedTimespan (22.0 to 22.5) <music21.note.Note C>>)
        (<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
         <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>)
        (<PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>,
         <PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>)

        Note that the second pair contains a one-beat rest at 21.0-22.0;
        so `includeRests=False` will
        get rid of that:

        >>> for pm in verticality22.getPairedMotion(includeRests=False):
        ...     print(pm)
        (<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
         <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>)
        (<PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>,
         <PitchedTimespan (21.5 to 22.5) <music21.note.Note A>>)

        Oblique here means a pair that does not move (it could be called noMotion,
        because there's no motion
        here in a two-note pair, but we still call it includeOblique so it's consistent with
        getAllVoiceLeadingQuartets).

        >>> for pm in verticality22.getPairedMotion(includeOblique=False):
        ...     print(pm)
        (<PitchedTimespan (19.5 to 21.0) <music21.note.Note G>>,
         <PitchedTimespan (22.0 to 22.5) <music21.note.Note C>>)
        (<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
         <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>)

        >>> for pm in verticality22.getPairedMotion(includeOblique=False, includeRests=False):
        ...     print(pm)
        (<PitchedTimespan (21.0 to 22.0) <music21.note.Note E>>,
         <PitchedTimespan (22.0 to 23.0) <music21.note.Note F>>)

        Changed in v9.3 -- arguments are keyword only
        '''
        if not self.timespanTree:
            return []

        stopTss = self.stopTimespans
        startTss = self.startTimespans
        overlapTss = self.overlapTimespans
        allPairedMotions: list[tuple[spans.PitchedTimespan, spans.PitchedTimespan]] = []

        for startingTs in startTss:
            if not isinstance(startingTs, spans.PitchedTimespan):
                continue
            previousTs = self.timespanTree.findPreviousPitchedTimespanInSameStreamByClass(
                startingTs)
            if previousTs is None or not isinstance(previousTs, spans.PitchedTimespan):
                continue  # first not in piece in this part

            if includeRests is False:
                if previousTs not in stopTss:
                    continue
            if includeOblique is False and startingTs.pitches == previousTs.pitches:
                continue
            tsTuple = (previousTs, startingTs)
            allPairedMotions.append(tsTuple)

        if includeOblique is True:
            for overlapTs in overlapTss:
                if not isinstance(overlapTs, spans.PitchedTimespan):
                    continue
                tsTuple = (overlapTs, overlapTs)
                allPairedMotions.append(tsTuple)

        return allPairedMotions

# -----------------------------------------------------------------------------

class VerticalitySequence(prebase.ProtoM21Object, Sequence[Verticality]):
    r'''
    A segment of verticalities.
    '''

    # INITIALIZER #

    def __init__(self, verticalities: Iterable[Verticality]):
        self._verticalities = tuple(verticalities)

    # SPECIAL METHODS #

    def __getitem__(self, item):
        return self._verticalities[item]

    def __len__(self):
        return len(self._verticalities)

    # noinspection PyProtectedMember
    def _reprInternal(self):
        internalRepr = ',\n\t'.join('(' + x._reprInternal() + ')' for x in self)
        out = f'[\n\t{internalRepr}\n\t]'
        return out

    # PUBLIC METHODS #

    def unwrap(self):
        from music21.tree.analysis import Horizontality

        unwrapped = {}
        for timespan in self[0].overlapTimespans:
            if timespan.part not in unwrapped:
                unwrapped[timespan.part] = []
            unwrapped[timespan.part].append(timespan)
        for timespan in self[0].startTimespans:
            if timespan.part not in unwrapped:
                unwrapped[timespan.part] = []
            unwrapped[timespan.part].append(timespan)
        for verticality in self[1:]:
            for timespan in verticality.startTimespans:
                if timespan.part not in unwrapped:
                    unwrapped[timespan.part] = []
                unwrapped[timespan.part].append(timespan)
        for part, timespans in unwrapped.items():
            horizontality = Horizontality(timespans=timespans)
            unwrapped[part] = horizontality
        return unwrapped

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

_DOC_ORDER = (Verticality, VerticalitySequence)

# -----------------------------------------------------------------------------
