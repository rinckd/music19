# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         tree/timespanTree.py
# Purpose:      Subclasses of tree.trees.OffsetTree for manipulation
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2013-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
Tools for grouping elements, timespans, and especially
pitched elements into kinds of searchable tree organized by start and stop offsets
and other positions.
'''
from __future__ import annotations

from collections.abc import Generator, Iterable
import itertools
import random
import typing as t
import more_itertools

from music21 import common
from music21 import environment
from music21 import exceptions21

from music21.tree import spans
from music21.tree import trees

if t.TYPE_CHECKING:
    from music21.tree.verticality import Verticality, VerticalitySequence

environLocal = environment.Environment('tree.timespanTree')

# -----------------------------------------------------------------------------
class TimespanTreeException(exceptions21.TreeException):
    pass

# -----------------------------------------------------------------------------
class TimespanTree(trees.OffsetTree):
    r'''
    A TimespanTree is a data structure for efficiently slicing a score for pitches, or,
    like all :class:`~music21.tree.trees.OffsetTree` objects, for searching large scores
    quickly by time.

    While you can construct an TimespanTree by hand, inserting timespans one at
    a time, the common use-case is to construct the TimespanTree from an entire
    score at once:

    >>> bach = corpus.parse('bwv66.6')
    >>> scoreTree = tree.fromStream.asTimespans(bach, flatten=True,
    ...                                         classList=(note.Note, chord.Chord))

    From this representation, we can get what is happening at any given moment as a
    :class:`~music21.tree.verticality.Verticality` object.

    >>> print(scoreTree.getVerticalityAt(17.0))
    <music21.tree.verticality.Verticality 17.0 {F#3 C#4 A4}>

    The equivalent call from the stream itself is:

        `bach.asTrees(flatten=True, asTimespans=True, classList=(note.Note, chord.Chord))`

    All offsets are assumed to be relative to the score's source if flatten is True

    Example: How many moments in Bach are consonant and how many are dissonant:

    >>> totalConsonances = 0
    >>> totalDissonances = 0
    >>> for v in scoreTree.iterateVerticalities():
    ...     if v.toChord().isConsonant():
    ...        totalConsonances += 1
    ...     else:
    ...        totalDissonances += 1
    >>> (totalConsonances, totalDissonances)
    (34, 17)

    So 1/3 of the vertical moments in Bach are dissonant!  But is this an
    accurate perception? Let's sum up the total consonant duration vs.
    dissonant duration.

    Since verticality objects do not know their end times, we can iterate pairwise
    to figure out the length.  We add "padEnd=True" to include a dummy verticality
    at the end so that it includes the last object:

    >>> totalConsonanceDuration = 0
    >>> totalDissonanceDuration = 0
    >>> iterator = scoreTree.iterateVerticalitiesNwise(n=2, padEnd=True)
    >>> for verticality1, verticality2 in iterator:
    ...     offset1 = verticality1.offset
    ...     offset2 = verticality2.offset
    ...     quarterLength = offset2 - offset1
    ...     if verticality1.toChord().isConsonant():
    ...        totalConsonanceDuration += quarterLength
    ...     else:
    ...        totalDissonanceDuration += quarterLength
    >>> (totalConsonanceDuration, totalDissonanceDuration)
    (26.5, 9.5)

    Example: Remove neighbor tones from the Bach chorale.  (It's actually quite viscous
    in its pruning.)

    Here in Alto, measure 7, there's a neighbor tone E#.

    >>> bach.parts['#Alto'].measure(7).show('text')
    {0.0} <music21.note.Note F#>
    {0.5} <music21.note.Note E#>
    {1.0} <music21.note.Note F#>
    {1.5} <music21.note.Note F#>
    {2.0} <music21.note.Note C#>

    We'll get rid of it and a lot of other neighbor tones.

    >>> for verticalities in scoreTree.iterateVerticalitiesNwise(n=3):
    ...     horizontalities = scoreTree.unwrapVerticalities(verticalities)
    ...     for unused_part, horizontality in horizontalities.items():
    ...         if horizontality.hasNeighborTone:
    ...             merged = horizontality[0].new(
    ...                endTime=horizontality[2].endTime,
    ...             )  # merged is a new PitchedTimespan
    ...             scoreTree.removeTimespan(horizontality[0])
    ...             scoreTree.removeTimespan(horizontality[1])
    ...             scoreTree.removeTimespan(horizontality[2])
    ...             scoreTree.insert(merged)

    >>> #_DOCS_SHOW newBach = tree.toStream.partwise(scoreTree, templateStream=bach)
    >>> #_DOCS_SHOW newBach.parts['#Alto'].measure(7).show('text')
    {0.0} <music21.chord.Chord F#4>
    {1.5} <music21.chord.Chord F#3>
    {2.0} <music21.chord.Chord C#4>

    The second F# is an octave lower, so it wouldn't get merged even if
    adjacent notes were fused together (which they're not).

    ..  note::

        TimespanTree is an implementation of an extended AVL tree. AVL
        trees are a type of binary tree, like Red-Black trees. AVL trees are
        very efficient at insertion when the objects being inserted are already
        sorted - which is usually the case with data extracted from a score.
        TimespanTree is an extended AVL tree because each node in the
        tree keeps track of not just the start offsets of PitchedTimespans
        stored at that node, but also the earliest and latest stop offset of
        all PitchedTimespans stores at both that node and all nodes which are
        children of that node. This lets us quickly located PitchedTimespans
        which overlap offsets or which are contained within ranges of offsets.
        This also means that the contents of a TimespanTree are always
        sorted.

    OMIT_FROM_DOCS

    TODO: Doc examples for all functions, including privates.
    '''
    __slots__ = ()
    @staticmethod
    def _insertCorePayloadSortKey(x):
        return x.endTime
        # if hasattr(x, 'element'):
        #     return x.element.sortTuple()[2:]
        # elif isinstance(x, TimespanTree) and x.source is not None:
        #     environLocal.printDebug("Timespan tree added to Tree: nope.")
        #     return x.source.sortTuple()[2:]
        # else:
        #     return x.endTime  # PitchedTimespan with no Element!

    # PUBLIC METHODS #

    @staticmethod
    def elementEndTime(el, unused_node):
        '''
        Use so that both OffsetTrees, which have elements which do not have a .endTime, and
        TimespanTrees, which have element that have an .endTime but not a duration, can
        use most of the same code.
        '''
        return el.endTime

    def index(self, span):
        r'''
        Gets index of a TimeSpan in a TimespanTree.

        Since Timespans do not have .sites, there is only one offset to deal with

        >>> tsList = [(0, 2), (0, 9), (1, 1), (2, 3), (3, 4),
        ...           (4, 9), (5, 6), (5, 8), (6, 8), (7, 7)]
        >>> ts = [tree.spans.Timespan(x, y) for x, y in tsList]
        >>> tsTree = tree.timespanTree.TimespanTree()
        >>> tsTree.insert(ts)

        >>> for timespan in ts:
        ...     print("%r %s" % (timespan, tsTree.index(timespan)))
        ...
        <Timespan 0.0 2.0> 0
        <Timespan 0.0 9.0> 1
        <Timespan 1.0 1.0> 2
        <Timespan 2.0 3.0> 3
        <Timespan 3.0 4.0> 4
        <Timespan 4.0 9.0> 5
        <Timespan 5.0 6.0> 6
        <Timespan 5.0 8.0> 7
        <Timespan 6.0 8.0> 8
        <Timespan 7.0 7.0> 9

        >>> tsTree.index(tree.spans.Timespan(-100, 100))
        Traceback (most recent call last):
        ValueError: <Timespan -100.0 100.0> not in Tree at offset -100.0.
        '''
        offset = span.offset
        node = self.getNodeByPosition(offset)
        if node is None or span not in node.payload:
            raise ValueError(f'{span} not in Tree at offset {offset}.')
        index = node.payload.index(span) + node.payloadElementsStartIndex
        return index

    @property
    def offset(self):
        '''
        this is just for mimicking elements as streams.

        * Changed in v7: this was always meant to be a property, but was
          incorrectly a method earlier.
        '''
        return self.lowestPosition()

    def removeTimespanList(self, elements, offsets=None, runUpdate=True):
        '''
        this will eventually be different from above
        '''
        self.removeElements(elements, offsets, runUpdate)

    def removeTimespan(self, elements, offsets=None, runUpdate=True):
        '''
        this will eventually be different from above.
        '''
        self.removeElements(elements, offsets, runUpdate)

    def findNextPitchedTimespanInSameStreamByClass(
        self,
        pitchedTimespan: spans.PitchedTimespan,
        classList=None
    ) -> spans.PitchedTimespan | None:
        r'''
        Finds next element timespan in the same stream class as `PitchedTimespan`.

        Default classList is (stream.Part,)

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> timespan = scoreTree[0]
        >>> timespan
        <PitchedTimespan (0.0 to 0.5) <music21.note.Note C#>>

        >>> timespan.part
        <music21.stream.Part Soprano>

        >>> timespan = scoreTree.findNextPitchedTimespanInSameStreamByClass(timespan)
        >>> timespan
        <PitchedTimespan (0.5 to 1.0) <music21.note.Note B>>

        >>> timespan.part
        <music21.stream.Part Soprano>

        >>> timespan = scoreTree.findNextPitchedTimespanInSameStreamByClass(timespan)
        >>> timespan
        <PitchedTimespan (1.0 to 2.0) <music21.note.Note A>>

        >>> timespan.part
        <music21.stream.Part Soprano>
        '''
        from music21 import stream
        if classList is None:
            classList = (stream.Part,)
        if not isinstance(pitchedTimespan, spans.PitchedTimespan):
            message = f'PitchedTimespan {pitchedTimespan!r}, must be an PitchedTimespan'
            raise TimespanTreeException(message)
        verticality = self.getVerticalityAt(pitchedTimespan.offset)
        while verticality is not None:
            verticality = verticality.nextVerticality
            if verticality is None:
                return None
            for nextPitchedTimespan in verticality.startTimespans:
                if (nextPitchedTimespan.getParentageByClass(classList) is
                        pitchedTimespan.getParentageByClass(classList)):
                    return nextPitchedTimespan

    def findPreviousPitchedTimespanInSameStreamByClass(
        self,
        pitchedTimespan: spans.PitchedTimespan,
        classList=None
    ) -> spans.PitchedTimespan | None:
        r'''
        Finds next element timespan in the same Part/Measure, etc. (specify in classList) as
        the `pitchedTimespan`.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> timespan = scoreTree[-1]
        >>> timespan
        <PitchedTimespan (35.0 to 36.0) <music21.note.Note F#>>

        >>> timespan.part
        <music21.stream.Part Bass>

        >>> timespan = scoreTree.findPreviousPitchedTimespanInSameStreamByClass(timespan)
        >>> timespan
        <PitchedTimespan (34.0 to 35.0) <music21.note.Note B>>

        >>> timespan.part
        <music21.stream.Part Bass>

        >>> timespan = scoreTree.findPreviousPitchedTimespanInSameStreamByClass(timespan)
        >>> timespan
        <PitchedTimespan (33.0 to 34.0) <music21.note.Note D>>

        >>> timespan.part
        <music21.stream.Part Bass>
        '''
        from music21 import stream
        if classList is None:
            classList = (stream.Part,)
        if not isinstance(pitchedTimespan, spans.PitchedTimespan):
            message = f'PitchedTimespan {pitchedTimespan!r}, must be an PitchedTimespan'
            raise TimespanTreeException(message)
        verticality = self.getVerticalityAt(pitchedTimespan.offset)
        while verticality is not None:
            verticality = verticality.previousVerticality
            if verticality is None:
                return None
            for previousPitchedTimespan in verticality.startTimespans:
                if (previousPitchedTimespan.getParentageByClass(classList) is
                        pitchedTimespan.getParentageByClass(classList)):
                    return previousPitchedTimespan

    def getVerticalityAtOrBefore(self, offset):
        r'''
        Gets the :class:`~music21.tree.verticality.Verticality`
        in this TimeSpanTree which starts at `offset`.

        If the found Verticality has no start timespans, the function returns
        the next previous verticality with start timespans.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans()
        >>> scoreTree.getVerticalityAtOrBefore(0.125)
        <music21.tree.verticality.Verticality 0.0 {A3 E4 C#5}>

        >>> scoreTree.getVerticalityAtOrBefore(0.0)
        <music21.tree.verticality.Verticality 0.0 {A3 E4 C#5}>
        '''
        verticality = self.getVerticalityAt(offset)
        if not verticality.startTimespans:
            verticality = verticality.previousVerticality
        return verticality

    def iterateConsonanceBoundedVerticalities(self):
        # noinspection PyShadowingNames
        r'''
        Iterates consonant-bounded verticality subsequences in this
        offset-tree.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans()
        >>> for subsequence in scoreTree.iterateConsonanceBoundedVerticalities():
        ...     print('Subsequence:')
        ...     for verticality in subsequence:
        ...         verticalityChord = verticality.toChord()
        ...         print(f'\t[{verticality.measureNumber}] '
        ...               + f'{verticality}: {verticalityChord.isConsonant()}')
        ...
        Subsequence:
            [2] <music21.tree.verticality.Verticality 6.0 {E3 E4 G#4 B4}>: True
            [2] <music21.tree.verticality.Verticality 6.5 {E3 D4 G#4 B4}>: False
            [2] <music21.tree.verticality.Verticality 7.0 {A2 C#4 E4 A4}>: True
        Subsequence:
            [3] <music21.tree.verticality.Verticality 9.0 {F#3 C#4 F#4 A4}>: True
            [3] <music21.tree.verticality.Verticality 9.5 {B2 D4 G#4 B4}>: False
            [3] <music21.tree.verticality.Verticality 10.0 {C#3 C#4 E#4 G#4}>: True
        Subsequence:
            [3] <music21.tree.verticality.Verticality 10.0 {C#3 C#4 E#4 G#4}>: True
            [3] <music21.tree.verticality.Verticality 10.5 {C#3 B3 E#4 G#4}>: False
            [3] <music21.tree.verticality.Verticality 11.0 {F#2 A3 C#4 F#4}>: True
        Subsequence:
            [3] <music21.tree.verticality.Verticality 12.0 {F#3 C#4 F#4 A4}>: True
            [4] <music21.tree.verticality.Verticality 13.0 {G#3 B3 F#4 B4}>: False
            [4] <music21.tree.verticality.Verticality 13.5 {F#3 B3 F#4 B4}>: False
            [4] <music21.tree.verticality.Verticality 14.0 {G#3 B3 E4 B4}>: True
        Subsequence:
            [4] <music21.tree.verticality.Verticality 14.0 {G#3 B3 E4 B4}>: True
            [4] <music21.tree.verticality.Verticality 14.5 {A3 B3 E4 B4}>: False
            [4] <music21.tree.verticality.Verticality 15.0 {B3 D#4 F#4}>: True
        Subsequence:
            [4] <music21.tree.verticality.Verticality 15.0 {B3 D#4 F#4}>: True
            [4] <music21.tree.verticality.Verticality 15.5 {B2 A3 D#4 F#4}>: False
            [4] <music21.tree.verticality.Verticality 16.0 {C#3 G#3 C#4 E4}>: True
        Subsequence:
            [5] <music21.tree.verticality.Verticality 17.5 {F#3 D4 F#4 A4}>: True
            [5] <music21.tree.verticality.Verticality 18.0 {G#3 C#4 E4 B4}>: False
            [5] <music21.tree.verticality.Verticality 18.5 {G#3 B3 E4 B4}>: True
        Subsequence:
            [6] <music21.tree.verticality.Verticality 24.0 {F#3 C#4 F#4 A4}>: True
            [7] <music21.tree.verticality.Verticality 25.0 {B2 D4 F#4 G#4}>: False
            [7] <music21.tree.verticality.Verticality 25.5 {C#3 C#4 E#4 G#4}>: True
        Subsequence:
            [7] <music21.tree.verticality.Verticality 25.5 {C#3 C#4 E#4 G#4}>: True
            [7] <music21.tree.verticality.Verticality 26.0 {D3 C#4 F#4}>: False
            [7] <music21.tree.verticality.Verticality 26.5 {D3 F#3 B3 F#4}>: True
        Subsequence:
            [8] <music21.tree.verticality.Verticality 29.0 {A#2 F#3 C#4 F#4}>: True
            [8] <music21.tree.verticality.Verticality 29.5 {A#2 F#3 D4 F#4}>: False
            [8] <music21.tree.verticality.Verticality 30.0 {A#2 C#4 E4 F#4}>: False
            [8] <music21.tree.verticality.Verticality 31.0 {B2 C#4 E4 F#4}>: False
            [8] <music21.tree.verticality.Verticality 32.0 {C#3 B3 D4 F#4}>: False
            [8] <music21.tree.verticality.Verticality 32.5 {C#3 A#3 C#4 F#4}>: False
            [9] <music21.tree.verticality.Verticality 33.0 {D3 B3 F#4}>: True
        Subsequence:
            [9] <music21.tree.verticality.Verticality 33.0 {D3 B3 F#4}>: True
            [9] <music21.tree.verticality.Verticality 33.5 {D3 B3 C#4 F#4}>: False
            [9] <music21.tree.verticality.Verticality 34.0 {B2 B3 D4 F#4}>: True
        Subsequence:
            [9] <music21.tree.verticality.Verticality 34.0 {B2 B3 D4 F#4}>: True
            [9] <music21.tree.verticality.Verticality 34.5 {B2 B3 D4 E#4}>: False
            [9] <music21.tree.verticality.Verticality 35.0 {F#3 A#3 C#4 F#4}>: True
        '''
        iterator = self.iterateVerticalities()
        try:
            startingVerticality = next(iterator)
        except StopIteration:
            return

        while not startingVerticality.toChord().isConsonant():
            try:
                startingVerticality = next(iterator)
            except StopIteration:
                return

        verticalityBuffer = [startingVerticality]
        for verticality in iterator:
            verticalityBuffer.append(verticality)
            if verticality.toChord().isConsonant():
                if len(verticalityBuffer) > 2:
                    yield tuple(verticalityBuffer)
                verticalityBuffer = [verticality]

    def iterateVerticalities(
        self,
        reverse: bool = False,
    ) -> Generator[Verticality, None, None]:
        r'''
        Iterates all vertical moments in this TimespanTree, represented as
        :class:`~music21.tree.verticality.Verticality` objects.

        ..  note:: The TimespanTree can be mutated while its verticalities are
            iterated over. Each verticality holds a reference back to the
            TimespanTree and will ask for the start-offset after (or before) its
            own start offset in order to determine the next verticality to
            yield. If you mutate the tree by adding or deleting timespans, the
            next verticality will reflect those changes.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> iterator = scoreTree.iterateVerticalities()
        >>> for _ in range(10):
        ...     next(iterator)
        ...
        <music21.tree.verticality.Verticality 0.0 {A3 E4 C#5}>
        <music21.tree.verticality.Verticality 0.5 {G#3 B3 E4 B4}>
        <music21.tree.verticality.Verticality 1.0 {F#3 C#4 F#4 A4}>
        <music21.tree.verticality.Verticality 2.0 {G#3 B3 E4 B4}>
        <music21.tree.verticality.Verticality 3.0 {A3 E4 C#5}>
        <music21.tree.verticality.Verticality 4.0 {G#3 B3 E4 E5}>
        <music21.tree.verticality.Verticality 5.0 {A3 E4 C#5}>
        <music21.tree.verticality.Verticality 5.5 {C#3 E4 A4 C#5}>
        <music21.tree.verticality.Verticality 6.0 {E3 E4 G#4 B4}>
        <music21.tree.verticality.Verticality 6.5 {E3 D4 G#4 B4}>

        Verticalities can also be iterated in reverse:

        >>> iterator = scoreTree.iterateVerticalities(reverse=True)
        >>> for _ in range(10):
        ...     next(iterator)
        ...
        <music21.tree.verticality.Verticality 35.0 {F#3 A#3 C#4 F#4}>
        <music21.tree.verticality.Verticality 34.5 {B2 B3 D4 E#4}>
        <music21.tree.verticality.Verticality 34.0 {B2 B3 D4 F#4}>
        <music21.tree.verticality.Verticality 33.5 {D3 B3 C#4 F#4}>
        <music21.tree.verticality.Verticality 33.0 {D3 B3 F#4}>
        <music21.tree.verticality.Verticality 32.5 {C#3 A#3 C#4 F#4}>
        <music21.tree.verticality.Verticality 32.0 {C#3 B3 D4 F#4}>
        <music21.tree.verticality.Verticality 31.0 {B2 C#4 E4 F#4}>
        <music21.tree.verticality.Verticality 30.0 {A#2 C#4 E4 F#4}>
        <music21.tree.verticality.Verticality 29.5 {A#2 F#3 D4 F#4}>
        '''
        if reverse:
            offset = self.highestPosition()
            verticality = self.getVerticalityAt(offset)
            yield verticality
            verticality = verticality.previousVerticality
            while verticality is not None:
                yield verticality
                verticality = verticality.previousVerticality
        else:
            offset = self.lowestPosition()
            verticality = self.getVerticalityAt(offset)
            yield verticality
            verticality = verticality.nextVerticality
            while verticality is not None:
                yield verticality
                verticality = verticality.nextVerticality

    def iterateVerticalitiesNwise(
            self, n: int = 3, *, reverse: bool = False, padEnd: bool = False
    ) -> Generator[VerticalitySequence, None, None]:
        r'''
        Iterates :class:`~music21.tree.verticality.Verticality` objects in groups of length `n`.

        ..  note:: The TimespanTree can be mutated while its verticalities are
            iterated over. Each verticality holds a reference back to the
            TimespanTree and will ask for the start-offset after (or before) its
            own start offset in order to determine the next verticality to
            yield. If you mutate the tree by adding or deleting timespans, the
            next verticality will reflect those changes.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> iterator = scoreTree.iterateVerticalitiesNwise(n=2)
        >>> for _ in range(4):
        ...     print(next(iterator))
        ...
        <music21.tree.verticality.VerticalitySequence [
            (0.0 {A3 E4 C#5}),
            (0.5 {G#3 B3 E4 B4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (0.5 {G#3 B3 E4 B4}),
            (1.0 {F#3 C#4 F#4 A4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (1.0 {F#3 C#4 F#4 A4}),
            (2.0 {G#3 B3 E4 B4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (2.0 {G#3 B3 E4 B4}),
            (3.0 {A3 E4 C#5})
            ]>

        Grouped verticalities can also be iterated in reverse, but note that the
        groups within each iteration are still ordered from earliest to last.

        >>> iterator = scoreTree.iterateVerticalitiesNwise(n=2, reverse=True)
        >>> for _ in range(4):
        ...     print(next(iterator))
        ...
        <music21.tree.verticality.VerticalitySequence [
            (34.5 {B2 B3 D4 E#4}),
            (35.0 {F#3 A#3 C#4 F#4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (34.0 {B2 B3 D4 F#4}),
            (34.5 {B2 B3 D4 E#4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (33.5 {D3 B3 C#4 F#4}),
            (34.0 {B2 B3 D4 F#4})
            ]>
        <music21.tree.verticality.VerticalitySequence [
            (33.0 {D3 B3 F#4}),
            (33.5 {D3 B3 C#4 F#4})
            ]>

        When iterating with `n > 1` and `padEnd=True` will put sentinel
        Verticalities in the last VerticalitySequences that occur at the
        `endTime` of the tree, with no elements:

        >>> iterator = scoreTree.iterateVerticalitiesNwise(n=3, padEnd=True)
        >>> for v in iterator:
        ...     pass
        >>> v
        <music21.tree.verticality.VerticalitySequence [
            (35.0 {F#3 A#3 C#4 F#4}),
            (36.0 {}),
            (36.0 {})
            ]>

        * Changed in v8: added padEnd.  Streams with fewer than n elements
            also return an empty sentinel entry.
        '''
        from music21.tree.verticality import VerticalitySequence, Verticality

        n = int(n)
        if n <= 0:
            message = 'The number of verticalities in the group must be at '
            message += f'least one. Got {n}'
            raise TimespanTreeException(message)

        sentinelVerticality = Verticality(self.endTime, timespanTree=self)

        if padEnd:
            ending = [sentinelVerticality] * (n - 1)
        else:
            ending = []

        for verticalities in more_itertools.windowed(
            itertools.chain(self.iterateVerticalities(reverse=reverse), ending),
            n,
            sentinelVerticality
        ):
            if not reverse:
                yield VerticalitySequence(verticalities)
            else:
                yield VerticalitySequence(reversed(verticalities))

        # if reverse:
        #     for v in self.iterateVerticalities(reverse=True):
        #         verticalities = [v]
        #         while len(verticalities) < n:
        #             nextVerticality = verticalities[-1].nextVerticality
        #             if nextVerticality is None:
        #                 break
        #             verticalities.append(nextVerticality)
        #         if len(verticalities) == n:
        #             yield VerticalitySequence(verticalities)
        # else:
        #     for v in self.iterateVerticalities():
        #         verticalities = [v]
        #         while len(verticalities) < n:
        #             previousVerticality = verticalities[-1].previousVerticality
        #             if previousVerticality is None:
        #                 break
        #             verticalities.append(previousVerticality)
        #         if len(verticalities) == n:
        #             yield VerticalitySequence(reversed(verticalities))

    def splitAt(self, offsets):
        r'''
        Splits all timespans in this TimespanTree at `offsets`, operating in
        place.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans()
        >>> scoreTree.elementsStartingAt(0.1)
        ()

        >>> for timespan in scoreTree.elementsOverlappingOffset(0.1):
        ...     print("%r, %s" % (timespan, timespan.part.id))
        ...
        <PitchedTimespan (0.0 to 0.5) <music21.note.Note C#>>, Soprano
        <PitchedTimespan (0.0 to 0.5) <music21.note.Note A>>, Tenor
        <PitchedTimespan (0.0 to 0.5) <music21.note.Note A>>, Bass
        <PitchedTimespan (0.0 to 1.0) <music21.note.Note E>>, Alto

        Note that the Alto is last in both of these because currently the sorting
        is done according to the endTime -- potentially to be changed soon.

        >>> scoreTree.splitAt(0.1)
        >>> for timespan in scoreTree.elementsStartingAt(0.1):
        ...     print("%r, %s" % (timespan, timespan.part.id))
        ...
        <PitchedTimespan (0.1 to 0.5) <music21.note.Note C#>>, Soprano
        <PitchedTimespan (0.1 to 0.5) <music21.note.Note A>>, Tenor
        <PitchedTimespan (0.1 to 0.5) <music21.note.Note A>>, Bass
        <PitchedTimespan (0.1 to 1.0) <music21.note.Note E>>, Alto

        >>> scoreTree.elementsOverlappingOffset(0.1)
        ()
        '''
        if not isinstance(offsets, Iterable):
            offsets = [offsets]
        for offset in offsets:
            overlaps = self.elementsOverlappingOffset(offset)
            if not overlaps:
                continue
            for overlap in overlaps:
                self.removeTimespan(overlap)
                shards = overlap.splitAt(offset)
                self.insert(shards)

    def toPartwiseTimespanTrees(self):
        '''
        Returns a dictionary of TimespanTrees where each entry
        is indexed by a Part object (TODO: Don't use mutable objects as hash keys!)
        and each key is a TimeSpan tree containing only element timespans belonging
        to that part.

        Used by reduceChords.  May disappear at any time without a deprecation
        notice.
        '''
        partwiseTimespanTrees = {}
        for part in self.allParts():
            partwiseTimespanTrees[part] = TimespanTree()
        for timespan in self:
            partwiseTimespanTree = partwiseTimespanTrees[timespan.part]
            partwiseTimespanTree.insert(timespan)
        return partwiseTimespanTrees

    @staticmethod
    def unwrapVerticalities(verticalities):
        # noinspection PyShadowingNames
        r'''
        Unwraps a sequence of `Verticality` objects into a dictionary of
        `Part`:`Horizontality` key/value pairs.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> iterator = scoreTree.iterateVerticalitiesNwise()
        >>> verticalities = next(iterator)
        >>> unwrapped = scoreTree.unwrapVerticalities(verticalities)
        >>> for part in sorted(unwrapped, key=lambda x: x.partName):
        ...     print(part)
        ...     horizontality = unwrapped[part]
        ...     for timespan in horizontality:
        ...         print('\t%r' % timespan)
        ...
        <music21.stream.Part Alto>
            <PitchedTimespan (0.0 to 1.0) <music21.note.Note E>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note F#>>
        <music21.stream.Part Bass>
            <PitchedTimespan (0.0 to 0.5) <music21.note.Note A>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note G#>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note F#>>
        <music21.stream.Part Soprano>
            <PitchedTimespan (0.0 to 0.5) <music21.note.Note C#>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note B>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note A>>
        <music21.stream.Part Tenor>
            <PitchedTimespan (0.0 to 0.5) <music21.note.Note A>>
            <PitchedTimespan (0.5 to 1.0) <music21.note.Note B>>
            <PitchedTimespan (1.0 to 2.0) <music21.note.Note C#>>
        '''
        from music21.tree.verticality import VerticalitySequence
        sequence = VerticalitySequence(verticalities)
        unwrapped = sequence.unwrap()
        return unwrapped

    # PUBLIC PROPERTIES #

    def allParts(self):
        parts = set()
        for timespan in self:
            parts.add(timespan.part)
        parts = sorted(parts, key=lambda x: x.getInstrument().partId)
        return parts

    def maximumOverlap(self):
        '''
        The maximum number of timespans overlapping at any given moment in this
        timespan collection.

        >>> score = corpus.parse('bwv66.6')
        >>> scoreTree = score.asTimespans(classList=(note.Note,))
        >>> scoreTree.maximumOverlap()
        4

        Returns None if there is no verticality here.
        '''
        overlap = None
        for v in self.iterateVerticalities():
            degreeOfOverlap = len(v.startTimespans) + len(v.overlapTimespans)
            if overlap is None:
                overlap = degreeOfOverlap
            elif overlap < degreeOfOverlap:
                overlap = degreeOfOverlap
        return overlap

#     def minimumOverlap(self):
#         '''
#         The minimum number of timespans overlapping at any given moment in this
#         timespan collection.
#
#         In a tree created from a monophonic stream, the minimumOverlap will
#         probably be either zero or one.
#
#         >>> score = corpus.parse('bwv66.6')
#         >>> scoreTree = tree.fromStream.asTimespans(
#         ...     score, flatten=False, classList=(note.Note, chord.Chord))
#         >>> scoreTree[0].minimumOverlap()
#         1
#
#         Returns None if there is no verticality here.
#         '''
#         overlap = None
#         for v in self.iterateVerticalities():
#             degreeOfOverlap = len(v.startTimespans) + len(v.overlapTimespans)
#             if overlap is None:
#                 overlap = degreeOfOverlap
#             elif degreeOfOverlap < overlap:
#                 overlap = degreeOfOverlap
#         return overlap

    @property
    def element(self):
        '''
        defined so a TimespanTree can be used like an PitchedTimespan

        TODO: Look at subclassing or at least deriving from a common base.
        '''
        return common.unwrapWeakref(self._source)

    @element.setter
    def element(self, expr):
        self._source = common.wrapWeakref(expr)

# -----------------------------------------------------------------------------

# , runTest='testGetVerticalityAtWithKey')
