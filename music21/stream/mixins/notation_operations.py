# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/notation_operations.py
# Purpose:      Notation operations mixin for Stream objects
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Notation operations mixin for Stream objects.

This module contains the NotationOperationsMixin class that provides
notation-related functionality for Stream objects. Methods were extracted
from stream/base.py to improve code organization.
"""
from __future__ import annotations

import typing as t

from music21 import note
from music21 import pitch
from music21 import key
from music21 import meter
from music21 import exceptions21
from music21.stream import makeNotation

if t.TYPE_CHECKING:
    from music21.common.types import StreamType

# Exception shortcuts
StreamException = exceptions21.StreamException


class NotationOperationsMixin:
    """
    Mixin providing notation-related operations for Stream objects.
    
    This mixin contains methods for:
    - Rest creation and management (makeRests)
    - Tie handling (makeTies, stripTies, extendTies)
    - Beam creation (makeBeams)
    - Comprehensive notation creation (makeNotation)
    - Notation validation (isWellFormedNotation)
    
    Extracted from stream/base.py to improve code organization.
    Methods total: ~167 lines from original base.py
    
    Most methods delegate to the music21.stream.makeNotation module
    for actual implementation, providing a clean API surface.
    """
    
    def makeRests(
        self,
        refStreamOrTimeRange=None,
        fillGaps=False,
        timeRangeFromBarDuration=False,
        inPlace=False,
        hideRests=False,
    ):
        '''
        Calls :py:func:`~music21.stream.makeNotation.makeRests`.

        * Changed in v7, inPlace=False by default.
        '''
        return makeNotation.makeRests(
            self,
            refStreamOrTimeRange=refStreamOrTimeRange,
            fillGaps=fillGaps,
            timeRangeFromBarDuration=timeRangeFromBarDuration,
            inPlace=inPlace,
            hideRests=hideRests,
        )

    def makeTies(self,
                 meterStream=None,
                 inPlace=False,
                 displayTiedAccidentals=False,
                 classFilterList=(note.GeneralNote,)):
        '''
        Calls :py:func:`~music21.stream.makeNotation.makeTies`.

        * Changed in v7, inPlace=False by default.
        '''
        return makeNotation.makeTies(
            self,
            meterStream=meterStream,
            inPlace=inPlace,
            displayTiedAccidentals=displayTiedAccidentals,
            classFilterList=classFilterList,
        )

    def makeBeams(self, *, inPlace=False, setStemDirections=True, failOnNoTimeSignature=False):
        '''
        Return a new Measure, or modify the Measure in place, with beams applied to all
        notes.

        See :py:func:`~music21.meter.makeBeams` for more information.

        * Changed in v7, inPlace=False by default.
        '''
        return makeNotation.makeBeams(
            self,
            inPlace=inPlace,
            setStemDirections=setStemDirections,
            failOnNoTimeSignature=failOnNoTimeSignature,
        )

    def makeNotation(self: 'StreamType',
                     *,
                     meterStream=None,
                     refStreamOrTimeRange=None,
                     inPlace=False,
                     bestClef=False,
                     pitchPast: list[pitch.Pitch]|None = None,
                     pitchPastMeasure: list[pitch.Pitch]|None = None,
                     useKeySignature: bool|key.KeySignature = True,
                     alteredPitches: list[pitch.Pitch]|None = None,
                     cautionaryPitchClass: bool = True,
                     cautionaryAll: bool = False,
                     overrideStatus: bool = False,
                     cautionaryNotImmediateRepeat: bool = True,
                     tiePitchSet: set[str]|None = None
                     ):
        '''
        This method calls a sequence of Stream methods on this Stream to prepare
        notation, including creating voices for overlapped regions, Measures
        if necessary, creating ties, beams, accidentals, and tuplet brackets.

        If `inPlace` is True, this is done in-place.
        if `inPlace` is False, this returns a modified deep copy.

        The following additional parameters are documented on
        :meth:`~music21.stream.base.makeAccidentals`::

            pitchPast
            pitchPastMeasure
            useKeySignature
            alteredPitches
            cautionaryPitchClass
            cautionaryAll
            overrideStatus
            cautionaryNotImmediateRepeat
            tiePitchSet

        >>> s = stream.Stream()
        >>> n = note.Note('g')
        >>> n.quarterLength = 1.5
        >>> s.repeatAppend(n, 10)
        >>> sMeasures = s.makeNotation()
        >>> len(sMeasures.getElementsByClass(stream.Measure))
        4
        >>> sMeasures.getElementsByClass(stream.Measure).last().rightBarline.type
        'final'

        * Changed in v7: `inPlace=True` returns `None`.
        '''
        # determine what is the object to work on first
        returnStream: 'StreamType|Stream[t.Any]'
        if inPlace:
            returnStream = self
        else:
            returnStream = self.coreCopyAsDerivation('makeNotation')

        # retrieve necessary spanners; insert only if making a copy
        returnStream.coreGatherMissingSpanners(
            insert=not inPlace,
            # definitely do NOT put a constrainingSpannerBundle constraint
        )
        # only use inPlace arg on first usage
        if not returnStream.hasMeasures():
            # only try to make voices if no Measures are defined
            returnStream.makeVoices(inPlace=True, fillGaps=True)
            # if this is not inPlace, it will return a newStream; if
            # inPlace, this returns None
            # use inPlace=True, as already established above
            returnStream.makeMeasures(
                meterStream=meterStream,
                refStreamOrTimeRange=refStreamOrTimeRange,
                inPlace=True,
                bestClef=bestClef)

            if not returnStream.hasMeasures():
                raise StreamException(
                    f'no measures found in stream with {len(self)} elements')

        # for now, calling makeAccidentals once per measures
        # pitches from last measure are passed
        # this needs to be called before makeTies
        # note that this functionality is also placed in Part
        if not returnStream.streamStatus.accidentals:
            makeNotation.makeAccidentalsInMeasureStream(
                returnStream,
                pitchPast=pitchPast,
                pitchPastMeasure=pitchPastMeasure,
                useKeySignature=useKeySignature,
                alteredPitches=alteredPitches,
                cautionaryPitchClass=cautionaryPitchClass,
                cautionaryAll=cautionaryAll,
                overrideStatus=overrideStatus,
                cautionaryNotImmediateRepeat=cautionaryNotImmediateRepeat,
                tiePitchSet=tiePitchSet)

        makeNotation.makeTies(returnStream, meterStream=meterStream, inPlace=True)

        for m in returnStream._stream_factory.get_elements_by_class(returnStream, 'Measure'):
            makeNotation.splitElementsToCompleteTuplets(m, recurse=True, addTies=True)
            makeNotation.consolidateCompletedTuplets(m, recurse=True, onlyIfTied=True)

        if not returnStream.streamStatus.beams:
            try:
                makeNotation.makeBeams(returnStream, inPlace=True)
            except meter.MeterException as me:
                import warnings  # lazy import - used only for meter exception warnings
                warnings.warn(str(me))

        # note: this needs to be after makeBeams, as placing this before
        # makeBeams was causing the duration's tuplet to lose its type setting
        # check for tuplet brackets one measure at a time
        # this means that they will never extend beyond one measure
        for m in returnStream._stream_factory.get_elements_by_class(returnStream, 'Measure'):
            if not m.streamStatus.tuplets:
                makeNotation.makeTupletBrackets(m, inPlace=True)

        if not inPlace:
            return returnStream

    def stripTies(self, 
                  inPlace=False, 
                  matchByPitch=True, 
                  retainContainers=False):
        '''
        Calls :py:func:`~music21.stream.makeNotation.stripTies`.

        * Changed in v7, inPlace=False by default.
        '''
        return makeNotation.stripTies(
            self,
            inPlace=inPlace,
            matchByPitch=matchByPitch,
            retainContainers=retainContainers,
        )

    def extendTies(self, ignoreRests=False, pitchAttr='nameWithOctave'):
        '''
        Calls :py:func:`~music21.stream.makeNotation.extendTies`.
        '''
        return makeNotation.extendTies(
            self,
            ignoreRests=ignoreRests,
            pitchAttr=pitchAttr,
        )

    def isWellFormedNotation(self) -> bool:
        '''
        Return True if, given the context of this Stream or Stream subclass,
        contains what appears to be well-formed notation.

        This method provides a way to test the output of various procedures that
        manipulate musical data.
        '''
        return makeNotation.isWellFormedNotation(self)