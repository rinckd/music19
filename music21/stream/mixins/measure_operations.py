# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/measure_operations.py
# Purpose:      Measure operations mixin for Stream objects
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Measure operations mixin for Stream objects.

This module contains the MeasureOperationsMixin class that provides
measure-related functionality for Stream objects. Methods were extracted
from stream/base.py to improve code organization.
"""
from __future__ import annotations

import types
import typing as t
from collections import OrderedDict

from music21 import bar
from music21 import common
from music21 import exceptions21
from music21.common.enums import GatherSpanners
from music21.common.types import OffsetQL
from music21.stream import iterator
from music21.stream import makeNotation

if t.TYPE_CHECKING:
    from music21.common.types import StreamType, M21ObjType
    from music21.stream.base import Stream
    from music21.stream.measure import Measure

# Exception shortcuts
StreamException = exceptions21.StreamException


class MeasureOperationsMixin:
    """
    Mixin providing measure-related operations for Stream objects.
    
    This mixin contains methods for:
    - Measure access and retrieval (measures, measure)
    - Measure numbering and mapping (measureOffsetMap, _fixMeasureNumbers) 
    - Measure creation (makeMeasures)
    - Barline management (_getFinalBarline, _setFinalBarline)
    - Beat and measure calculations (beatAndMeasureFromOffset)
    - Measure detection (hasMeasures)
    
    Extracted from stream/base.py to improve code organization.
    Methods total: ~2,187 lines from original base.py
    
    These operations are fundamental to measure-based music analysis and
    manipulation, providing ways to access, create, and modify measures
    within musical scores.
    """
    
    # We'll start with the simpler methods and build up to the complex ones
    
    def _getMeasureOffset(self) -> float:
        '''
        Get the offset of this stream in its measure container.
        '''
        if self.activeSite is not None:
            return self.activeSite.elementOffset(self)
        return 0.0
    
    def hasMeasures(self) -> bool:
        '''
        Return True if this Stream contains Measure objects, False otherwise.
        
        This method is cached for performance.
        '''
        if 'hasMeasures' not in self._cache or self._cache['hasMeasures'] is None:
            hasMeasures = False
            for obj in self._elements:
                if 'Measure' in obj.classes:
                    hasMeasures = True
                    break
            self._cache['hasMeasures'] = hasMeasures
        return self._cache['hasMeasures']
    
    def makeMeasures(self,
                     meterStream=None,
                     refStreamOrTimeRange=None,
                     searchContext=False,
                     innerBarline=None,
                     finalBarline='final',
                     bestClef=False,
                     inPlace=False):
        '''
        Return a new stream (or modify this stream if inPlace=True) with 
        measures created from the notes and rests in this stream.
        
        This method delegates to :meth:`music21.stream.makeNotation.makeMeasures`.
        '''
        return makeNotation.makeMeasures(
            self,
            meterStream=meterStream,
            refStreamOrTimeRange=refStreamOrTimeRange,
            searchContext=searchContext,
            innerBarline=innerBarline,
            finalBarline=finalBarline,
            bestClef=bestClef,
            inPlace=inPlace,
        )
    
    def _getMeasureNumberListByStartEnd(
        self,
        numberStart: int|str,
        numberEnd: int|str,
        *,
        indicesNotNumbers: bool
    ) -> list['Measure']:
        '''
        Private method to extract a list of Measure objects based on start and end numbers.
        
        Supports measure suffixes and both indices vs. numbers mode.
        '''
        def hasMeasureNumberInformation(measureIterator: iterator.StreamIterator['Measure']) -> bool:
            '''
            Many people create streams where every number is zero.
            This will check for that as quickly as possible.
            '''
            for m in measureIterator:
                try:
                    mNumber = int(m.number)
                except ValueError:  # pragma: no cover
                    # should never happen.
                    raise StreamException(f'found problematic measure for numbering: {m}')
                if mNumber != 0:
                    return True
            return False

        mStreamIter: iterator.StreamIterator['Measure'] = self._stream_factory.get_elements_by_class(self, 'Measure')

        # FIND THE CORRECT ORIGINAL MEASURE OBJECTS
        # for indicesNotNumbers, this is simple
        if indicesNotNumbers:
            if not isinstance(numberStart, int) or not isinstance(numberEnd, (int, types.NoneType)):
                raise ValueError(
                    'numberStart and numberEnd must be integers with indicesNotNumbers=True'
                )
            # noinspection PyTypeChecker
            return t.cast(list['Measure'], list(mStreamIter[numberStart:numberEnd]))

        hasUniqueMeasureNumbers = hasMeasureNumberInformation(mStreamIter)

        # unused
        # originalNumberStart = numberStart
        # originalNumberEnd = numberEnd
        startSuffix = None
        endSuffix = None
        if isinstance(numberStart, str):
            numberStart, startSuffixTemp = common.getNumFromStr(numberStart)
            if startSuffixTemp:
                startSuffix = startSuffixTemp
            numberStart = int(numberStart)

        if isinstance(numberEnd, str):
            numberEnd, endSuffixTemp = common.getNumFromStr(numberEnd)
            if endSuffixTemp:
                endSuffix = endSuffixTemp
            numberEnd = int(numberEnd)

        matches: list['Measure']
        if numberEnd is not None:
            matchingMeasureNumbers = set(range(numberStart, numberEnd + 1))

            if hasUniqueMeasureNumbers:
                matches = [m for m in mStreamIter if m.number in matchingMeasureNumbers]
            else:
                matches = [m for i, m in enumerate(mStreamIter)
                                if i + 1 in matchingMeasureNumbers]
        else:
            if hasUniqueMeasureNumbers:
                matches = [m for m in mStreamIter if m.number >= numberStart]
            else:
                matches = [m for i, m in enumerate(mStreamIter)
                                    if i + 1 >= numberStart]

        if startSuffix is not None:
            oldMatches = matches
            matches = []
            for m in oldMatches:
                if m.number != numberStart:
                    matches.append(m)
                elif not m.numberSuffix:
                    matches.append(m)
                elif m.numberSuffix >= startSuffix:
                    matches.append(m)

        if endSuffix is not None:
            oldMatches = matches
            matches = []
            for m in oldMatches:
                if m.number != numberEnd:
                    matches.append(m)
                elif not m.numberSuffix:
                    matches.append(m)
                elif m.numberSuffix <= endSuffix:
                    matches.append(m)
        return matches

    def measures(
        self,
        numberStart,
        numberEnd,
        *,
        collect=('Clef', 'TimeSignature', 'Instrument', 'KeySignature'),
        gatherSpanners=GatherSpanners.ALL,
        indicesNotNumbers=False
    ) -> 'Stream[Measure]':
        '''
        Get a region of Measures based on a start and end Measure number
        where the boundary numbers are both included.

        That is, a request for measures 4 through 10 will return 7 Measures, numbers 4 through 10.

        Additionally, any number of associated classes can be gathered from the context
        and put into the measure.  By default, we collect the Clef, TimeSignature, KeySignature,
        and Instrument so that there is enough context to perform.  (See getContextByClass()
        and .previous() for definitions of the context)

        While all elements in the source are the original elements in the extracted region,
        new Measure objects are created and returned.

        >>> bachIn = corpus.parse('bach/bwv66.6')
        >>> bachExcerpt = bachIn.parts[0].measures(1, 3)
        >>> len(bachExcerpt.getElementsByClass(stream.Measure))
        3

        Because bwv66.6 has a pickup measure, and we requested to start at measure 1,
        this is NOT true:

        >>> firstExcerptMeasure = bachExcerpt.getElementsByClass(stream.Measure).first()
        >>> firstBachMeasure = bachIn.parts[0].getElementsByClass(stream.Measure).first()
        >>> firstExcerptMeasure is firstBachMeasure
        False
        >>> firstBachMeasure.number
        0
        >>> firstExcerptMeasure.number
        1

        To get all measures from the beginning, go ahead and always request measure 0 to x,
        there will be no error if there is not a pickup measure.

        >>> bachExcerpt = bachIn.parts[0].measures(0, 3)
        >>> excerptNote = bachExcerpt.getElementsByClass(stream.Measure).first().notes.first()
        >>> originalNote = bachIn.parts[0].recurse().notes[0]
        >>> excerptNote is originalNote
        True

        if `indicesNotNumbers` is True, then it ignores defined measureNumbers and
        uses 0-indexed measure objects and half-open range.  For instance, if you have a piece
        that goes "m1, m2, m3, m4, ..." (like a standard piece without pickups, then
        `.measures(1, 3, indicesNotNumbers=True)` would return measures 2 and 3, because
        it is interpreted as the slice from object with index 1, which is measure 2 (m1 has
        an index of 0) up to but NOT including the object with index 3, which is measure 4.
        IndicesNotNumbers is like a Python-slice.

        >>> bachExcerpt2 = bachIn.parts[0].measures(0, 2, indicesNotNumbers=True)
        >>> for m in bachExcerpt2.getElementsByClass(stream.Measure):
        ...     print(m)
        ...     print(m.number)
        <music21.stream.Measure 0 offset=0.0>
        0
        <music21.stream.Measure 1 offset=1.0>
        1

        If `numberEnd=None` then it is interpreted as the last measure of the stream:

        >>> bachExcerpt3 = bachIn.parts[0].measures(7, None)
        >>> for m in bachExcerpt3.getElementsByClass(stream.Measure):
        ...     print(m)
        <music21.stream.Measure 7 offset=0.0>
        <music21.stream.Measure 8 offset=4.0>
        <music21.stream.Measure 9 offset=8.0>

        Note that the offsets in the new stream are shifted so that the first measure
        in the excerpt begins at 0.0

        The measure elements are the same objects as the original:

        >>> lastExcerptMeasure = bachExcerpt3.getElementsByClass(stream.Measure).last()
        >>> lastOriginalMeasure = bachIn.parts[0].getElementsByClass(stream.Measure).last()
        >>> lastExcerptMeasure is lastOriginalMeasure
        True

        At the beginning of the Stream returned, before the measures will be some additional
        objects so that the context is properly preserved:

        >>> for thing in bachExcerpt3:
        ...     print(thing)
        P1: Soprano: Instrument 1
        <music21.clef.TrebleClef>
        f# minor
        <music21.meter.TimeSignature 4/4>
        <music21.stream.Measure 7 offset=0.0>
        <music21.stream.Measure 8 offset=4.0>
        <music21.stream.Measure 9 offset=8.0>

        Collecting gets the most recent element in the context of the stream:

        >>> bachIn.parts[0].insert(10, key.Key('D-'))
        >>> bachExcerpt4 = bachIn.parts[0].measures(7, None)
        >>> for thing in bachExcerpt4:
        ...     print(thing)
        P1: Soprano: Instrument 1
        <music21.clef.TrebleClef>
        D- major
        ...

        What is collected is determined by the "collect" iterable.  To collect nothing
        send an empty list:

        >>> bachExcerpt5 = bachIn.parts[0].measures(8, None, collect=[])
        >>> for thing in bachExcerpt5:
        ...     print(thing)
        <music21.stream.Measure 8 offset=0.0>
        <music21.stream.Measure 9 offset=4.0>

        If a stream has measure suffixes, then Streams having that suffix or no suffix
        are returned.

        >>> p = stream.Part()
        >>> mSuffix3 = stream.Measure(number=3)
        >>> mSuffix4 = stream.Measure(number=4)
        >>> mSuffix4a = stream.Measure(number=4)
        >>> mSuffix4a.numberSuffix = 'a'
        >>> mSuffix4b = stream.Measure(number=4)
        >>> mSuffix4b.numberSuffix = 'b'
        >>> mSuffix5 = stream.Measure(number=5)
        >>> mSuffix5a = stream.Measure(number=5)
        >>> mSuffix5a.numberSuffix = 'a'
        >>> mSuffix6 = stream.Measure(number=6)
        >>> p.append([mSuffix3, mSuffix4, mSuffix4a, mSuffix4b, mSuffix5, mSuffix5a, mSuffix6])
        >>> suffixExcerpt = p.measures('4b', 6)
        >>> suffixExcerpt.show('text')
        {0.0} <music21.stream.Measure 4 offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 4b offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 5 offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 5a offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 6 offset=0.0>
        <BLANKLINE>
        >>> suffixExcerpt2 = p.measures(3, '4a')
        >>> suffixExcerpt2.show('text')
        {0.0} <music21.stream.Measure 3 offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 4 offset=0.0>
        <BLANKLINE>
        {0.0} <music21.stream.Measure 4a offset=0.0>
        <BLANKLINE>

        GatherSpanners can change the output:

        >>> from music21.common.enums import GatherSpanners
        >>> beachIn = corpus.parse('beach')
        >>> beachExcerpt = beachIn.measures(3, 4, gatherSpanners=GatherSpanners.ALL)
        >>> len(beachExcerpt.spannerBundle)
        8
        >>> len(beachIn.spannerBundle)
        94

        * Changed in v7: does not create measures automatically.
        * Changed in v7: If `gatherSpanners` is True or GatherSpanners.ALL (default),
          then just the spanners pertaining to the requested measure region
          are provided, rather than the entire bundle from the source.

        OMIT_FROM_DOCS

        Ensure that layout.StaffGroup objects are present:

        >>> for sp in beachExcerpt.spannerBundle.getByClass('StaffGroup'):
        ...    print(sp)
        <music21.layout.StaffGroup <music21.stream.PartStaff P5-Staff1><... P5-Staff2>>
        <music21.layout.StaffGroup <music21.stream.Part Soprano I><...Alto II>>

        This is in OMIT
        '''
        startMeasure: 'Measure|None'

        returnObj = t.cast('Stream[Measure]', self.cloneEmpty(derivationMethod='measures'))
        srcObj = self

        matches = self._getMeasureNumberListByStartEnd(
            numberStart,
            numberEnd,
            indicesNotNumbers=indicesNotNumbers
        )

        startOffset: OffsetQL
        if not matches:
            startMeasure = None
            startOffset = 0.0  # does not matter; could be any number
        else:
            startMeasure = matches[0]
            startOffset = startMeasure.getOffsetBySite(srcObj)

        for className in collect:
            # first, see if it is in this Measure
            if (startMeasure is None
                    or startMeasure.recurse().getElementsByClass(className).getElementsByOffset(0)):
                continue

            # placing missing objects in outer container, not Measure
            found = startMeasure.getContextByClass(className)
            if found is not None:
                if startMeasure is not None:
                    found.priority = startMeasure.priority - 1
                    # TODO: This should not change global priority on found, but
                    #   instead priority, like offset, should be a per-site attribute
                returnObj.coreInsert(0, found)

        for m in matches:
            mOffset = m.getOffsetBySite(srcObj) - startOffset
            returnObj.coreInsert(mOffset, m)

        # used coreInsert
        returnObj.coreElementsChanged()

        if gatherSpanners:  # True, GatherSpanners.ALL, or GatherSpanners.COMPLETE_ONLY
            requireAllPresent = (gatherSpanners is GatherSpanners.COMPLETE_ONLY)
            returnObj.coreGatherMissingSpanners(
                requireAllPresent=requireAllPresent,
                constrainingSpannerBundle=self.spannerBundle,
            )

        # environLocal.printDebug(['len(returnObj.flatten())', len(returnObj.flatten())])
        return returnObj

    def _getFinalBarline(self):
        '''
        Private method to get the final barline from measures in the stream.
        '''
        # if we have part-like streams, process each part
        if self.hasPartLikeStreams():
            post = []
            for p in self.getElementsByClass('Stream'):
                post.append(p._getFinalBarline())
            return post  # a list of barlines
        # core routines for a single Stream
        else:
            if self.hasMeasures():
                return self._stream_factory.get_elements_by_class(self, 'Measure').last().rightBarline
            elif hasattr(self, 'rightBarline'):
                return self.rightBarline
            else:
                return None

    def _setFinalBarline(self, value):
        '''
        Private method to set the final barline on measures in the stream.
        '''
        # if we have part-like streams, process each part
        if self.hasPartLikeStreams():
            if not common.isListLike(value):
                value = [value]
            for i, p in enumerate(self.getElementsByClass('Stream')):
                # set final barline w/ mod iteration of value list
                bl = value[i % len(value)]
                # environLocal.printDebug(['enumerating measures', i, p, 'setting barline', bl])
                p._setFinalBarline(bl)
            return

        # core routines for a single Stream
        if self.hasMeasures():
            self._stream_factory.get_elements_by_class(self, 'Measure').last().rightBarline = value
        elif hasattr(self, 'rightBarline'):
            self.rightBarline = value  # pylint: disable=attribute-defined-outside-init
        # do nothing for other streams

    @property
    def finalBarline(self):
        '''
        Get or set the final barline of this Stream's Measures,
        if and only if there are Measures defined as elements in this Stream.
        This method will not create Measures if none exist.

        >>> p = stream.Part()
        >>> m1 = stream.Measure()
        >>> m1.rightBarline = bar.Barline('double')
        >>> p.append(m1)
        >>> p.finalBarline
        <music21.bar.Barline type=double>
        >>> m2 = stream.Measure()
        >>> m2.rightBarline = bar.Barline('final')
        >>> p.append(m2)
        >>> p.finalBarline
        <music21.bar.Barline type=final>
        '''
        return self._getFinalBarline()

    @finalBarline.setter
    def finalBarline(self, value):
        self._setFinalBarline(value)

    def measure(self,
                measureNumber,
                *,
                collect=('Clef', 'TimeSignature', 'Instrument', 'KeySignature'),
                indicesNotNumbers=False) -> 'Measure|None':
        '''
        Given a measure number, return a single
        :class:`~music21.stream.Measure` object if the Measure number exists, otherwise return None.

        This method is distinguished from :meth:`~music21.stream.Stream.measures`
        in that this method returns a single Measure object, not a Stream containing
        one or more Measure objects.

        >>> a = corpus.parse('bach/bwv324.xml')
        >>> a.parts[0].measure(3)
        <music21.stream.Measure 3 offset=8.0>

        See :meth:`~music21.stream.Stream.measures` for an explanation of collect and
        indicesNotNumbers

        To get the last measure of a piece, use -1 as a measureNumber -- this will turn
        on indicesNotNumbers if it is off:

        >>> a.parts[0].measure(-1)
        <music21.stream.Measure 9 offset=38.0>

        Getting a non-existent measure will return None:

        >>> print(a.parts[0].measure(99))
        None

        OMIT_FROM_DOCS

        >>> sf = a.parts[0].flatten()
        >>> sf.measure(2) is None
        True
        '''
        if not isinstance(measureNumber, str) and measureNumber < 0:
            indicesNotNumbers = True

        startMeasureNumber = measureNumber
        endMeasureNumber = measureNumber
        if indicesNotNumbers:
            endMeasureNumber += 1
            if startMeasureNumber == -1:
                endMeasureNumber = None

        matchingMeasures = self._getMeasureNumberListByStartEnd(
            startMeasureNumber,
            endMeasureNumber,
            indicesNotNumbers=indicesNotNumbers
        )
        if matchingMeasures:
            m = matchingMeasures[0]
            self.coreSelfActiveSite(m)  # not needed?
            return m
        return None

    def measureOffsetMap(
        self,
        classFilterList: list[t.Type]|list[str]|tuple[t.Type]|tuple[str] = ('Measure',)
    ) -> OrderedDict[float|t.Any, list['Measure']]:
        '''
        If this Stream contains Measures, returns an OrderedDict
        whose keys are the offsets of the start of each measure
        and whose values are a list of references
        to the :class:`~music21.stream.Measure` objects that start
        at that offset.

        Even in normal music there may be more than
        one Measure starting at each offset because each
        :class:`~music21.stream.Part` might define its own Measure.
        However, you are unlikely to encounter such things unless you
        run Score.flatten(retainContainers=True).

        The offsets are always measured relative to the
        calling Stream (self).

        You can specify a `classFilterList` argument as a list of classes
        to find instead of Measures.  But the default will of course
        find Measure objects.

        Example 1: This Bach chorale is in 4/4 without a pickup, so
        as expected, measures are found every 4 offsets, until the
        weird recitation in m. 7 which in our edition lasts 10 beats
        and thus causes a gap in measureOffsetMap from 24.0 to 34.0.

        .. image:: images/streamMeasureOffsetMapBWV324.*
            :width: 572

        >>> chorale = corpus.parse('bach/bwv324.xml')
        >>> alto = chorale.parts['#alto']
        >>> altoMeasures = alto.measureOffsetMap()
        >>> altoMeasures
        OrderedDict([(0.0, [<music21.stream.Measure 1 offset=0.0>]),
                     (4.0, [<music21.stream.Measure 2 offset=4.0>]),
                     (8.0, [<music21.stream.Measure 3 offset=8.0>]),
                     ...
                     (38.0, [<music21.stream.Measure 9 offset=38.0>])])
        >>> list(altoMeasures.keys())
        [0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 34.0, 38.0]

        altoMeasures is a dictionary of the measures
        that are found in the alto part, so we can get
        the measure beginning on offset 4.0 (measure 2)
        and display it (though it's the only measure
        found at offset 4.0, there might be others as
        in example 2, so we need to call altoMeasures[4.0][0]
        to get this measure.):

        >>> altoMeasures[4.0]
        [<music21.stream.Measure 2 offset=4.0>]
        >>> altoMeasures[4.0][0].show('text')
        {0.0} <music21.note.Note D>
        {1.0} <music21.note.Note D#>
        {2.0} <music21.note.Note E>
        {3.0} <music21.note.Note F#>

        Example 2: How to get all the measures from all parts (not the
        most efficient way, but it works!):

        >>> mom = chorale.measureOffsetMap()
        >>> mom
        OrderedDict([(0.0, [<music21.stream.Measure 1 offset=0.0>,
                            <music21.stream.Measure 1 offset=0.0>,
                            <music21.stream.Measure 1 offset=0.0>,
                            <music21.stream.Measure 1 offset=0.0>]),
                      (4.0, [<music21.stream.Measure 2 offset=4.0>,
                             ...])])
        >>> for measure_obj in mom[8.0]:
        ...     print(measure_obj, measure_obj.getContextByClass(stream.Part).id)
        <music21.stream.Measure 3 offset=8.0> Soprano
        <music21.stream.Measure 3 offset=8.0> Alto
        <music21.stream.Measure 3 offset=8.0> Tenor
        <music21.stream.Measure 3 offset=8.0> Bass

        Changed in v9: classFilterList must be a list or tuple of strings or Music21Objects

        OMIT_FROM_DOCS

        see important examples in testMeasureOffsetMap() and
        testMeasureOffsetMapPostTie()
        '''
        # environLocal.printDebug(['calling measure offsetMap()'])

        # environLocal.printDebug([classFilterList])
        offsetMap: dict[float|t.Any, list['Measure']] = {}
        # first, try to get measures
        # this works best of this is a Part or Score
        measure_class = self._stream_factory.get_class('Measure')
        if measure_class in classFilterList or 'Measure' in classFilterList:
            for m in self._stream_factory.get_elements_by_class(self, 'Measure'):
                offset = self.elementOffset(m)
                if offset not in offsetMap:
                    offsetMap[offset] = []
                # there may be more than one measure at the same offset
                offsetMap[offset].append(m)

        # try other classes
        for className in classFilterList:
            if className in (measure_class, 'Measure'):  # do not redo
                continue
            for e in self.getElementsByClass(className):
                # environLocal.printDebug(['calling measure offsetMap(); e:', e])
                # NOTE: if this is done on Notes, this can take an extremely
                # long time to process
                # 'reverse' here is a reverse sort, where the oldest objects
                # are returned first
                maybe_m = e.getContextByClass(measure_class)  # , sortByCreationTime='reverse')
                if maybe_m is None:  # pragma: no cover
                    # hard to think of a time this would happen, but better safe.
                    continue
                m = maybe_m
                # assuming that the offset returns the proper offset context
                # this is, the current offset may not be the stream that
                # contains this Measure; its current activeSite
                offset = m.offset
                if offset not in offsetMap:
                    offsetMap[offset] = []
                if m not in offsetMap[offset]:
                    offsetMap[offset].append(m)

        orderedOffsetMap = OrderedDict(sorted(offsetMap.items(), key=lambda o: o[0]))
        return orderedOffsetMap

    def beatAndMeasureFromOffset(self, searchOffset, fixZeros=True):
        '''
        Returns a two-element tuple of the beat and the Measure object (or the first one
        if there are several at the same offset; unlikely but possible) for a given
        offset from the start of this Stream (that contains measures).

        Recursively searches for measures.  Note that this method assumes that all parts
        have measures of consistent length.  If that's not the case, this
        method can be called on the relevant part.

        This algorithm should work even for weird time signatures such as 2+3+2/8.

        >>> bach = corpus.parse('bach/bwv1.6')
        >>> bach.parts[0].measure(2).getContextByClass(meter.TimeSignature)
        <music21.meter.TimeSignature 4/4>
        >>> returnTuples = []
        >>> for offset in [0.0, 1.0, 2.0, 5.0, 5.5]:
        ...     returnTuples.append(bach.beatAndMeasureFromOffset(offset))
        >>> returnTuples
        [(4.0, <music21.stream.Measure 0 offset=0.0>),
         (1.0, <music21.stream.Measure 1 offset=1.0>),
         (2.0, <music21.stream.Measure 1 offset=1.0>),
         (1.0, <music21.stream.Measure 2 offset=5.0>),
         (1.5, <music21.stream.Measure 2 offset=5.0>)]

        To get just the measureNumber and beat, use a transformation like this:
        >>> [(beat, measureObj.number) for beat, measureObj in returnTuples]
        [(4.0, 0), (1.0, 1), (2.0, 1), (1.0, 2), (1.5, 2)]

        Adapted from contributed code by Dmitri Tymoczko.  With thanks to DT.
        '''
        from music21 import meter

        myStream = self
        if not myStream.hasMeasures():
            if myStream.hasPartLikeStreams():
                foundPart = False
                for subStream in myStream:
                    if not subStream.isStream:
                        continue
                    if subStream.hasMeasures():
                        foundPart = True
                        myStream = subStream
                        break
                if not foundPart:
                    raise StreamException('beatAndMeasureFromOffset: could not find any parts!')
                    # was return False
            else:
                if not myStream.hasMeasures():
                    raise StreamException('beatAndMeasureFromOffset: could not find any measures!')
                    # return False
        # Now we get the measure containing our offset.
        # In most cases this second part of the code does the job.
        myMeas = myStream.getElementAtOrBefore(searchOffset, classList=['Measure'])
        if myMeas is None:
            raise StreamException('beatAndMeasureFromOffset: no measure at that offset.')
        ts1 = myMeas.timeSignature
        if ts1 is None:
            ts1 = myMeas.getContextByClass(meter.TimeSignature)

        if ts1 is None:
            raise StreamException(
                'beatAndMeasureFromOffset: could not find a time signature for that place.')
        try:
            myBeat = ts1.getBeatProportion(searchOffset - myMeas.offset)
        except:
            raise StreamException(
                'beatAndMeasureFromOffset: offset is beyond the end of the piece')
        foundMeasureNumber = myMeas.number
        # deal with second half of partial measures

        # Now we deal with the problem case, where we have the second half of a partial measure.
        # These are
        # treated as unnumbered measures (or measures with suffix 'X') by notation programs,
        # even though they are
        # logically part of the previous measure.
        # The variable padBeats will represent extra beats we add to the front
        # of our partial measure
        numSuffix = myMeas.numberSuffix
        if numSuffix == '':
            numSuffix = None

        if numSuffix is not None or (fixZeros and foundMeasureNumber == 0):
            prevMeas = myStream.getElementBeforeOffset(myMeas.offset, classList=['Measure'])
            if prevMeas:
                ts2 = prevMeas.getContextByClass(meter.TimeSignature)
                if not ts2:
                    raise StreamException(
                        'beatAndMeasureFromOffset: partial measure found, '
                        + 'but could not find a time signature for the preceding measure')
                # foundMeasureNumber = prevMeas.number

                # need this for chorales 197 and 280, where we
                # have a full-length measure followed by a pickup in
                # a new time signature
                if prevMeas.highestTime == ts2.barDuration.quarterLength:
                    padBeats = ts2.beatCount
                else:
                    padBeats = ts2.getBeatProportion(prevMeas.highestTime) - 1
                return (myBeat + padBeats, prevMeas)
            else:
                # partial measure at start of piece
                padBeats = ts1.getBeatProportion(
                    ts1.barDuration.quarterLength - myMeas.duration.quarterLength) - 1
                return (myBeat + padBeats, myMeas)
        else:
            return (myBeat, myMeas)

    def _fixMeasureNumbers(self, deletedMeasures, insertedMeasures):
        # noinspection PyShadowingNames
        '''
        Corrects the measures numbers of a string of measures given a list of measure numbers
        that have been deleted and a
        list of tuples (highest measure number below insertion, number of inserted measures).

        >>> s = converter.parse('tinynotation: 4/4 d4 e4 f4 g4   a2 b-4 a4    g4 a8 g8 f4 e4  g1')
        >>> s[-1].offset = 20.0
        >>> s.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note A>
            {2.0} <music21.note.Note B->
            {3.0} <music21.note.Note A>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {1.5} <music21.note.Note G>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note E>
        {20.0} <music21.stream.Measure 4 offset=20.0>
            {0.0} <music21.note.Note G>
            {4.0} <music21.bar.Barline type=final>
        >>> s.remove(s.measure(2))
        >>> s.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            ...
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note G>
            ...
        {20.0} <music21.stream.Measure 4 offset=20.0>
            {0.0} <music21.note.Note G>
            {4.0} <music21.bar.Barline type=final>
        >>> deletedMeasures = [2]
        >>> m1 = stream.Measure()
        >>> m1.repeatAppend(note.Note('e'),4)
        >>> s.insert(12.0, m1)
        >>> m2 = stream.Measure()
        >>> m2.repeatAppend(note.Note('f'),4)
        >>> s.insert(16.0, m2)
        >>> s.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            ...
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note G>
            ...
        {12.0} <music21.stream.Measure 0 offset=12.0>
            {0.0} <music21.note.Note E>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note E>
            {3.0} <music21.note.Note E>
        {16.0} <music21.stream.Measure 0 offset=16.0>
            {0.0} <music21.note.Note F>
            {1.0} <music21.note.Note F>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note F>
        {20.0} <music21.stream.Measure 4 offset=20.0>
            {0.0} <music21.note.Note G>
            {4.0} <music21.bar.Barline type=final>
        >>> insertedMeasures = [(3, [m1, m2])]

        >>> s._fixMeasureNumbers(deletedMeasures, insertedMeasures)
        >>> s.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            ...
        {8.0} <music21.stream.Measure 2 offset=8.0>
            {0.0} <music21.note.Note G>
            ...
        {12.0} <music21.stream.Measure 3 offset=12.0>
            {0.0} <music21.note.Note E>
            ...
        {16.0} <music21.stream.Measure 4 offset=16.0>
            {0.0} <music21.note.Note F>
            ...
        {20.0} <music21.stream.Measure 5 offset=20.0>
            {0.0} <music21.note.Note G>
            {4.0} <music21.bar.Barline type=final>
        >>> fixedNumbers = []
        >>> for m in s.getElementsByClass(stream.Measure):
        ...    fixedNumbers.append( m.number )
        >>> fixedNumbers
        [1, 2, 3, 4, 5]

        '''
        deletedMeasures.extend(insertedMeasures)
        allMeasures = deletedMeasures

        if not allMeasures:
            return

        def measureNumberSortRoutine(numOrNumTuple):
            if isinstance(numOrNumTuple, tuple):
                return measureNumberSortRoutine(numOrNumTuple[0])
            elif numOrNumTuple is None:
                return -9999
            else:
                return numOrNumTuple

        allMeasures.sort(key=measureNumberSortRoutine)

        oldMeasures = self._stream_factory.get_elements_by_class(self, 'Measure').stream()
        newMeasures = []

        cumulativeNumberShift = 0
        oldCorrections = {}
        newCorrections = {}
        # the inserted measures must be treated differently than the original measures.
        # an inserted measure should not shift itself,
        # but it should shift measures with the same number.
        # However, inserted measures should still be shifted by every other correction.

        # First collect dictionaries of shift boundaries and the amount of the shift.
        # at the same time, five un-numbered measures numbers that make sense.
        for measureNumber in allMeasures:
            if isinstance(measureNumber, tuple):  # tuple implies insertion
                measurePrior, extendedMeasures = measureNumber
                if not extendedMeasures:  # No measures were added, therefore no shift.
                    continue
                cumulativeNumberShift += len(extendedMeasures)
                nextMeasure = measurePrior + 1
                for m in extendedMeasures:
                    oldMeasures.remove(m)
                    newMeasures.append(m)
                    m.number = nextMeasure
                    nextMeasure += 1
                oldCorrections[measurePrior + 1] = cumulativeNumberShift
                newCorrections[nextMeasure] = cumulativeNumberShift
            else:  # integer implies deletion
                cumulativeNumberShift -= 1
                oldCorrections[measureNumber + 1] = cumulativeNumberShift
                newCorrections[measureNumber + 1] = cumulativeNumberShift

        # Second, make corrections based on the dictionaries. The key is the measure number
        # above which measures should be shifted by the value up to the next key. It is easiest
        # to do this in reverse order so there is no overlapping.
        previousBoundary = None
        for k in sorted(oldCorrections, key=lambda x: -1 * x):
            shift = oldCorrections[k]
            for m in oldMeasures:
                if previousBoundary is None or m.number < previousBoundary:
                    if m.number >= k:
                        m.number = m.number + shift
            previousBoundary = k

        previousBoundary = None
        for k in sorted(newCorrections, key=lambda x: -1 * x):
            shift = newCorrections[k]
            for m in newMeasures:
                if previousBoundary is None or m.number < previousBoundary:
                    if m.number >= k:
                        m.number = m.number + shift
            previousBoundary = k