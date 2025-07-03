# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/score.py
# Purpose:      Score and Opus classes extracted from stream/base.py
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#               Josiah Wolf Oberholtzer
#               Evan Lynch
#
# Copyright:    Copyright © 2008-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
Score and Opus classes for music21 streams.

Extracted from stream/base.py as part of Phase 2 dependency reduction.
'''
from __future__ import annotations

from collections import OrderedDict
import copy
import math
import os
import pathlib
import typing as t
from typing import overload

from music21 import clef
from music21 import common
from music21.common.enums import GatherSpanners
from music21.common.types import OffsetQL
from music21 import chord
from music21 import environment
from music21 import instrument
from music21 import key
from music21 import metadata
from music21 import note

from music21.stream.enums import RecursionType
from music21.stream import iterator
from music21.stream import makeNotation

# PHASE 2 NOTE: This creates a circular import (score.py -> base.py -> score.py)
# This will be resolved in Phase 3 through dependency injection/factory patterns
# For now, we accept this circular import to maintain functionality
from music21.stream.base import Stream

if t.TYPE_CHECKING:
    from music21.stream.part import Part
    from music21.stream.measure import Measure
    from music21.stream.voice import Voice
    from music21 import spanner

environLocal = environment.Environment('stream')


class Score(Stream):
    '''
    A Stream subclass for handling music with more than one Part.

    Almost totally optional (the largest containing Stream in a piece could be
    a generic Stream, or a Part, or a Staff).  And Scores can be
    embedded in other Scores (in fact, our original thought was to call
    this class a Fragment because of this possibility of continuous
    embedding; though it's probably better to embed a Score in an Opus),
    but we figure that many people will like calling the largest
    container a Score and that this will become a standard.
    '''
    recursionType = RecursionType.ELEMENTS_ONLY

    @property
    def parts(self) -> iterator.StreamIterator['Part']:
        '''
        Return all :class:`~music21.stream.Part` objects in a :class:`~music21.stream.Score`.

        It filters out all other things that might be in a Score object, such as Metadata
        returning just the Parts.

        >>> s = corpus.parse('bach/bwv66.6')
        >>> s.parts
        <music21.stream.iterator.StreamIterator for Score:bach/bwv66.6.mxl @:0>
        >>> len(s.parts)
        4
        '''
        # Use late import to avoid circular dependency
        from music21.stream.part import Part
        partIterator: iterator.StreamIterator['Part'] = self.getElementsByClass(Part)
        partIterator.overrideDerivation = 'parts'
        return partIterator

    def measures(self,
                 numberStart,
                 numberEnd,
                 collect=('Clef', 'TimeSignature', 'Instrument', 'KeySignature'),
                 gatherSpanners=GatherSpanners.ALL,
                 indicesNotNumbers=False):
        # noinspection PyShadowingNames
        '''
        This method overrides the :meth:`~music21.stream.Stream.measures`
        method on Stream. This creates a new Score stream that has the same measure
        range for all Parts.

        The `collect` argument is a list of classes that will be collected; see
        Stream.measures()

        >>> s = corpus.parse('bwv66.6')
        >>> post = s.measures(3, 5)  # range is inclusive, i.e., [3, 5]
        >>> len(post.parts)
        4
        >>> len(post.parts[0].getElementsByClass(stream.Measure))
        3
        >>> len(post.parts[1].getElementsByClass(stream.Measure))
        3
        '''
        post = self.__class__()
        # this calls on Music21Object, transfers groups, id if not id(self)
        post.mergeAttributes(self)
        # note that this will strip all objects that are not Parts
        for p in self.parts:
            # insert all at zero
            measuredPart = p.measures(numberStart,
                                      numberEnd,
                                      collect=collect,
                                      gatherSpanners=gatherSpanners,
                                      indicesNotNumbers=indicesNotNumbers)
            post.insert(0, measuredPart)
        # must manually add any spanners; do not need to add .flatten(),
        # as Stream.measures will handle lower level
        if gatherSpanners:
            spStream = self.spanners
            for sp in spStream:
                post.insert(0, sp)

        post.derivation.client = post
        post.derivation.origin = self
        post.derivation.method = 'measures'
        return post

    # this is Score.measure
    def measure(self,
                measureNumber,
                collect=(clef.Clef, 'TimeSignature', instrument.Instrument, key.KeySignature),
                gatherSpanners=GatherSpanners.ALL,
                indicesNotNumbers=False):
        '''
        Given a measure number (or measure index, if indicesNotNumbers is True)
        return another Score object which contains multiple parts but each of which has only a
        single :class:`~music21.stream.Measure` object if the
        Measure number exists, otherwise returns a score with parts that are empty.

        This method overrides the :meth:`~music21.stream.Stream.measure` method on Stream to
        allow for finding a single "measure slice" within parts:

        >>> bachIn = corpus.parse('bach/bwv324.xml')
        >>> excerpt = bachIn.measure(2)
        >>> excerpt
        <music21.stream.Score bach/bwv324.mxl>
        >>> len(excerpt.parts)
        4
        >>> excerpt.parts[0].show('text')
        {0.0} <music21.instrument.Instrument 'P1: Soprano: '>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.key.Key of e minor>
        {0.0} <music21.meter.TimeSignature 4/4>
        {0.0} <music21.stream.Measure 2 offset=0.0>
            {0.0} <music21.note.Note B>
            {1.0} <music21.note.Note B>
            {2.0} <music21.note.Note B>
            {3.0} <music21.note.Note B>

        Note that the parts created have all the meta-information outside the measure
        unless this information appears in the measure itself at the beginning:

        >>> bachIn.measure(1).parts[0].show('text')
        {0.0} <music21.instrument.Instrument 'P1: Soprano: '>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.key.Key of e minor>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.layout.SystemLayout>
            {0.0} <music21.note.Note B>
            {2.0} <music21.note.Note D>

        This way the original measure objects can be returned without being altered.

        The final measure slice of the piece can be obtained with index -1.  Example:
        quickly get the last chord of the piece, without needing to run .chordify()
        on the whole piece:

        >>> excerpt = bachIn.measure(-1)
        >>> excerptChords = excerpt.chordify()
        >>> excerptChords.show('text')
        {0.0} <music21.instrument.Instrument 'P1: Soprano: '>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.key.Key of e minor>
        {0.0} <music21.meter.TimeSignature 4/4>
        {0.0} <music21.stream.Measure 9 offset=0.0>
            {0.0} <music21.chord.Chord E2 G3 B3 E4>
            {4.0} <music21.bar.Barline type=final>

        >>> lastChord = excerptChords[chord.Chord].last()
        >>> lastChord
        <music21.chord.Chord E2 G3 B3 E4>

        Note that we still do a .getElementsByClass(chord.Chord) since many pieces end
        with nothing but a rest.
        '''
        # Use late import to avoid circular dependency
        from music21.stream.part import Part
        
        if measureNumber < 0:
            indicesNotNumbers = True

        startMeasureNumber = measureNumber
        endMeasureNumber = measureNumber
        if indicesNotNumbers:
            endMeasureNumber += 1
            if startMeasureNumber == -1:
                endMeasureNumber = None

        post = self.__class__()
        # this calls on Music21Object, transfers id, groups
        post.mergeAttributes(self)
        # note that this will strip all objects that are not Parts
        for p in self.getElementsByClass(Part):
            # insert all at zero
            mStream = p.measures(startMeasureNumber,
                                 endMeasureNumber,
                                 collect=collect,
                                 gatherSpanners=gatherSpanners,
                                 indicesNotNumbers=indicesNotNumbers)
            post.insert(0, mStream)

        if gatherSpanners:
            spStream = self.spanners
            for sp in spStream:
                post.insert(0, sp)

        post.derivation.client = post
        post.derivation.origin = self
        post.derivation.method = 'measure'

        return post

    def expandRepeats(self: 'Score', copySpanners: bool = True) -> 'Score':
        '''
        Expand all repeats, as well as all repeat indications
        given by text expressions such as D.C. al Segno.

        This method always returns a new Stream, with deepcopies
        of all contained elements at all level.

        Note that copySpanners is ignored here, as they are always copied.
        '''
        # Use late import to avoid circular dependency
        from music21.stream.part import Part
        
        post = self.cloneEmpty(derivationMethod='expandRepeats')
        # this calls on Music21Object, transfers id, groups
        post.mergeAttributes(self)

        # get all things in the score that are not Parts
        for e in self.iter().getElementsNotOfClass(Part):
            eNew = copy.deepcopy(e)  # assume that this is needed
            post.insert(self.elementOffset(e), eNew)

        for p in self.getElementsByClass(Part):
            # get spanners at highest level, not by Part
            post.insert(0, p.expandRepeats(copySpanners=False))

        # spannerBundle = spanner.SpannerBundle(list(post.flatten().spanners))
        spannerBundle = post.spannerBundle  # use property
        # iterate over complete semi flat (need containers); find
        # all new/old pairs
        for e in post.recurse(includeSelf=False):
            # update based on last id, new object
            if e.sites.hasSpannerSite():
                origin = e.derivation.origin
                if origin is not None and e.derivation.method == '__deepcopy__':
                    spannerBundle.replaceSpannedElement(origin, e)
        return post

    def measureOffsetMap(
        self,
        classFilterList: list[t.Type]|list[str]|tuple[t.Type]|tuple[str] = ('Measure',)
    ) -> OrderedDict[float|OffsetQL, list['Measure']]:
        '''
        This Score method overrides the
        :meth:`~music21.stream.Stream.measureOffsetMap` method of Stream.
        This creates a map based on all contained Parts in this Score.
        Measures found in multiple Parts with the same offset will be
        appended to the same list.

        If no parts are found in the score, then the normal
        :meth:`~music21.stream.Stream.measureOffsetMap` routine is called.

        This method is smart and does not assume that all Parts
        have measures with identical offsets.
        '''
        # Use late import to avoid circular dependency
        from music21.stream.measure import Measure
        
        parts = self.iter().parts
        if not parts:
            return Stream.measureOffsetMap(self, classFilterList)
        # else:
        offsetMap: dict[float|OffsetQL, list['Measure']] = {}
        for p in parts:
            mapPartial = p.measureOffsetMap(classFilterList)
            # environLocal.printDebug(['mapPartial', mapPartial])
            for k in mapPartial:
                if k not in offsetMap:
                    offsetMap[k] = []
                for m in mapPartial[k]:  # get measures from partial
                    if m not in offsetMap[k]:
                        offsetMap[k].append(m)
        orderedOffsetMap = OrderedDict(sorted(offsetMap.items(), key=lambda o: o[0]))
        return orderedOffsetMap

    @overload
    def sliceByGreatestDivisor(
        self: 'Score',
        *,
        addTies: bool = True,
        inPlace: t.Literal[True],
    ) -> None:
        pass

    @overload
    def sliceByGreatestDivisor(
        self: 'Score',
        *,
        addTies: bool = True,
        inPlace: t.Literal[False] = False,
    ) -> 'Score':
        pass

    def sliceByGreatestDivisor(
        self: 'Score',
        *,
        addTies: bool = True,
        inPlace: bool = False,
    ) -> 'Score|None':
        '''
        Slice all duration of all part by the minimum duration
        that can be summed to each concurrent duration.

        Overrides method defined on Stream.
        '''
        # Use late import to avoid circular dependency
        from music21.stream.part import Part
        from music21.stream.measure import Measure
        
        if not inPlace:  # make a copy
            returnObj = self.coreCopyAsDerivation('sliceByGreatestDivisor')
        else:

            returnObj = self

        # Find the greatest divisor for each measure at a time.
        # If there are no measures this will be zero.
        firstPart = returnObj.parts.first()
        if firstPart is None:
            raise TypeError('Cannot sliceByGreatestDivisor without parts')
        mStream = firstPart.getElementsByClass(Measure)
        mCount = len(mStream)
        if mCount == 0:
            mCount = 1  # treat as a single measure

        m_or_p: 'Measure|Part'
        for i in range(mCount):  # may be 1
            uniqueQuarterLengths = []
            p: 'Part'
            for p in returnObj.getElementsByClass(Part):
                if p.hasMeasures():
                    m_or_p = p.getElementsByClass(Measure)[i]
                else:
                    m_or_p = p  # treat the entire part as one measure

                # collect all unique quarter lengths
                for e in m_or_p.notesAndRests:
                    # environLocal.printDebug(['examining e', i, e, e.quarterLength])
                    if e.quarterLength not in uniqueQuarterLengths:
                        uniqueQuarterLengths.append(e.quarterLength)

            # after ql for all parts, find divisor
            divisor = common.approximateGCD(uniqueQuarterLengths)
            # environLocal.printDebug(['Score.sliceByGreatestDivisor:
            # got divisor from unique ql:', divisor, uniqueQuarterLengths])

            for p in returnObj.getElementsByClass(Part):
                # in place: already have a copy if nec
                # must do on measure at a time
                if p.hasMeasures():
                    m_or_p = p.getElementsByClass(Measure)[i]
                else:
                    m_or_p = p  # treat the entire part as one measure
                m_or_p.sliceByQuarterLengths(quarterLengthList=[divisor],
                                             target=None,
                                             addTies=addTies,
                                             inPlace=True)
        del mStream  # cleanup Streams
        returnObj.coreElementsChanged()
        if not inPlace:
            return returnObj

    def partsToVoices(self,
                      voiceAllocation: int|list[list|int] = 2,
                      permitOneVoicePerPart=False,
                      setStems=True):
        # noinspection PyShadowingNames
        '''
        Given a multi-part :class:`~music21.stream.Score`,
        return a new Score that combines parts into voices.

        The `voiceAllocation` parameter sets the maximum number
        of voices per Part.

        The `permitOneVoicePerPart` parameter, if True, will encode a
        single voice inside a single Part, rather than leaving it as
        a single Part alone, with no internal voices.

        >>> s = corpus.parse('bwv66.6')
        >>> len(s.flatten().notes)
        165
        >>> post = s.partsToVoices(voiceAllocation=4)
        >>> len(post.parts)
        1
        >>> len(post.parts.first().getElementsByClass(stream.Measure).first().voices)
        4
        >>> len(post.flatten().notes)
        165

        '''
        # Use late import to avoid circular dependency
        from music21.stream.part import Part
        from music21.stream.measure import Measure
        from music21.stream.voice import Voice
        from music21 import spanner

        sub: list['Part'] = []
        bundle = []
        if isinstance(voiceAllocation, int):
            voicesPerPart = voiceAllocation
            for pIndex, p in enumerate(self.parts):
                if pIndex % voicesPerPart == 0:
                    sub = []
                    sub.append(p)
                else:
                    sub.append(p)
                if pIndex % voicesPerPart == voicesPerPart - 1:
                    bundle.append(sub)
                    sub = []
            if sub:  # get last
                bundle.append(sub)
        # else, assume it is a list of groupings
        elif common.isIterable(voiceAllocation):
            voiceAllocation = t.cast(list[list|int], voiceAllocation)
            for group in voiceAllocation:
                sub = []
                # if a single entry
                if not isinstance(group, list):
                    # group is a single index
                    sub.append(self.parts[group])
                else:
                    for partId in group:
                        sub.append(self.parts[partId])
                bundle.append(sub)
        else:
            from music21.exceptions21 import StreamException
            raise StreamException(f'incorrect voiceAllocation format: {voiceAllocation}')

        # environLocal.printDebug(['partsToVoices() bundle:', bundle])

        s = self.cloneEmpty(derivationMethod='partsToVoices')
        s.metadata = self.metadata

        pActive: 'Part|None'
        for sub in bundle:  # each sub contains parts
            if len(sub) == 1 and not permitOneVoicePerPart:
                # probably need to create a new part and measure
                s.insert(0, sub[0])
                continue

            pActive = Part()
            # iterate through each part
            for pIndex, p in enumerate(sub):
                # only check for measures once per part
                if pActive.hasMeasures():
                    hasMeasures = True
                else:
                    hasMeasures = False

                for mIndex, m in enumerate(p.getElementsByClass(Measure)):
                    # environLocal.printDebug(['pIndex, p', pIndex, p,
                    #     'mIndex, m', mIndex, m, 'hasMeasures', hasMeasures])
                    # only create measures if non already exist
                    if not hasMeasures:
                        # environLocal.printDebug(['creating measure'])
                        mActive = Measure()
                        # some attributes may be none
                        # note: not copying here; and first part read will provide
                        # attributes; possible other parts may have other attributes
                        mActive.mergeAttributes(m)
                        mActive.mergeElements(m, classFilterList=(
                            'Barline', 'TimeSignature', 'Clef', 'KeySignature'))

                        # if m.timeSignature is not None:
                        #     mActive.timeSignature = m.timeSignature
                        # if m.keySignature is not None:
                        #     mActive.keySignature = m.keySignature
                        # if m.clef is not None:
                        #     mActive.clef = m.clef
                    else:
                        mActive = pActive.getElementsByClass(Measure)[mIndex]

                    # transfer elements into a voice
                    v = Voice()
                    v.id = pIndex
                    # for now, just take notes, including rests
                    for e in m.getElementsByClass([note.GeneralNote, spanner.Spanner]):
                        if setStems and isinstance(e, note.Note):
                            e.stemDirection = 'up' if pIndex % 2 == 0 else 'down'
                        v.insert(e.getOffsetBySite(m), e)
                    # insert voice in new measure
                    # environLocal.printDebug(['inserting voice', v, v.id, 'into measure', mActive])
                    mActive.insert(0, v)
                    # mActive.show('t')
                    # only insert measure if new part does not already have measures
                    if not hasMeasures:
                        pActive.insert(m.getOffsetBySite(p), mActive)

                # merge spanners from current part into active part
                for sp in p.spanners:
                    pActive.insert(sp.getOffsetBySite(p), sp)

            s.insert(0, pActive)
            pActive = None
        return s

    def implode(self):
        '''
        Reduce a polyphonic work into two staves.

        Currently, this is just a synonym for `partsToVoices` with
        `voiceAllocation = 2`, and `permitOneVoicePerPart = False`,
        but someday this will have better methods for finding identical
        parts, etc.
        '''
        voiceAllocation = 2
        permitOneVoicePerPart = False

        return self.partsToVoices(
            voiceAllocation=voiceAllocation,
            permitOneVoicePerPart=permitOneVoicePerPart
        )

    def makeNotation(
        self,
        meterStream=None,
        refStreamOrTimeRange=None,
        inPlace=False,
        bestClef=False,
        **subroutineKeywords
    ):
        '''
        This method overrides the makeNotation method on Stream,
        such that a Score object with one or more Parts or Streams
        that may not contain well-formed notation may be transformed
        and replaced by well-formed notation.

        If `inPlace` is True, this is done in-place;
        if `inPlace` is False, this returns a modified deep copy.
        '''
        # returnStream: Score
        if inPlace:
            returnStream = self
        else:
            returnStream = self.coreCopyAsDerivation('makeNotation')
        returnStream.coreGatherMissingSpanners()  # get spanners needed but not here!

        # do not assume that we have parts here
        if self.hasPartLikeStreams():
            # s: Stream
            for s in returnStream.getElementsByClass('Stream'):
                # process all component Streams inPlace
                s.makeNotation(meterStream=meterStream,
                               refStreamOrTimeRange=refStreamOrTimeRange,
                               inPlace=True,
                               bestClef=bestClef,
                               **subroutineKeywords)
            # note: while the local-streams have updated their caches, the
            # containing score has an out-of-date cache of flat.
            # thus, must call elements changed
            # but, since all we have done in this method is call coreGatherMissingSpanners()
            # and makeNotation(), neither of which are supposed to leave the stream
            # unusable (with an out-of-date cache), the original issue was likely deeper
            # no matter, let's just be extra cautious and run this here (Feb 2021 - JTW)
            returnStream.coreElementsChanged()
        else:  # call the base method
            super(Score, returnStream).makeNotation(meterStream=meterStream,
                                                    refStreamOrTimeRange=refStreamOrTimeRange,
                                                    inPlace=True,
                                                    bestClef=bestClef,
                                                    **subroutineKeywords)

        if inPlace:
            return None
        else:
            return returnStream


class Opus(Stream):
    '''
    A Stream subclass for handling multi-work music encodings.
    Many ABC files, for example, define multiple works or parts within a single file.

    Opus objects can contain multiple Score objects, or even other Opus objects!
    '''
    recursionType = RecursionType.ELEMENTS_ONLY

    # TODO: get by title, possibly w/ regex

    def getNumbers(self):
        '''
        Return a list of all numbers defined in this Opus.

        >>> o = corpus.parse('josquin/oVenusBant')
        >>> o.getNumbers()
        ['1', '2', '3']
        '''
        post = []
        for s in self.getElementsByClass(Score):
            post.append(s.metadata.number)
        return post

    def getScoreByNumber(self, opusMatch):
        # noinspection PyShadowingNames
        '''
        Get Score objects from this Stream by number.
        Performs title search using the
        :meth:`~music21.metadata.Metadata.search` method,
        and returns the first result.

        >>> o = corpus.parse('josquin/oVenusBant')
        >>> o.getNumbers()
        ['1', '2', '3']
        >>> s = o.getScoreByNumber(2)
        >>> s.metadata.title
        'O Venus bant'
        >>> s.metadata.alternativeTitle
        'Tenor'
        '''
        for s in self.getElementsByClass(Score):
            match, unused_field = s.metadata.search(opusMatch, 'number')
            if match:
                return s

    # noinspection SpellCheckingInspection
    def getScoreByTitle(self, titleMatch):
        # noinspection SpellCheckingInspection, PyShadowingNames
        '''
        Get Score objects from this Stream by a title.
        Performs title search using the :meth:`~music21.metadata.Metadata.search` method,
        and returns the first result.

        >>> o = corpus.parse('essenFolksong/erk5')
        >>> s = o.getScoreByTitle('Vrienden, kommt alle gaere')
        >>> s.metadata.title
        'Vrienden, kommt alle gaere'

        Regular expressions work fine

        >>> s = o.getScoreByTitle('(.*)kommt(.*)')
        >>> s.metadata.title
        'Vrienden, kommt alle gaere'
        '''
        for s in self.getElementsByClass(Score):
            match, unused_field = s.metadata.search(titleMatch, 'title')
            if match:
                return s

    @property
    def scores(self):
        '''
        Return all :class:`~music21.stream.Score` objects
        in an iterator
        '''
        return self.getElementsByClass('Score')  # replacing with bare Score is not working.

    def mergeScores(self):
        # noinspection PyShadowingNames
        '''
        Some Opus objects represent numerous scores
        that are individual parts of the same work.
        This method will treat each contained Score as a Part,
        merging and returning a single Score with merged Metadata.

        >>> o = corpus.parse('josquin/milleRegrets')
        >>> s = o.mergeScores()
        >>> s.metadata.title
        'Mille regrets'
        >>> len(s.parts)
        4
        '''
        sNew = Score()
        mdNew = metadata.Metadata()

        for s in self.scores:
            p = s.parts.first().makeNotation()  # assuming only one part
            sNew.insert(0, p)

            md = s.metadata
            # presently just getting the first of attributes encountered
            if md is not None:
                # environLocal.printDebug(['sub-score metadata', md,
                #   'md.composer', md.composer, 'md.title', md.title])
                if md.title is not None and mdNew.title is None:
                    mdNew.title = md.title
                if md.composer is not None and mdNew.composer is None:
                    mdNew.composer = md.composer

        sNew.insert(0, mdNew)
        return sNew

    # -------------------------------------------------------------------------
    def write(self, fmt=None, fp=None, **keywords):
        '''
        Displays an object in a format provided by the `fmt` argument or, if not
        provided, the format set in the user's Environment.

        This method overrides the behavior specified in
        :class:`~music21.base.Music21Object` for all formats besides explicit
        lily.x calls.

        Individual files are written for each score; returns the last file written.

        >>> sc1 = stream.Score()
        >>> sc2 = stream.Score()
        >>> o = stream.Opus()
        >>> o.append([sc1, sc2])

        #_DOCS_SHOW >>> o.write()
        #_DOCS_SHOW PosixPath('/some/temp/path-2.xml')
        '''
        if not self.scores:
            return None

        if fmt is not None and 'lily' in fmt:
            return Stream.write(self, fmt, fp, **keywords)
        elif common.runningInNotebook():
            return Stream.write(self, fmt, fp, **keywords)

        delete = False
        if fp is None:
            if fmt is None:
                suffix = '.' + environLocal['writeFormat']
            else:
                unused_format, suffix = common.findFormat(fmt)
            fp = environLocal.getTempFile(suffix=suffix, returnPathlib=False)
            # Mark for deletion, because it won't actually be used
            delete = True
        if isinstance(fp, str):
            fp = pathlib.Path(fp)

        fpParent = fp.parent
        fpStem = fp.stem
        fpSuffix = '.'.join(fp.suffixes)

        post = []
        placesRequired = math.ceil(math.log10(len(self.scores)))
        for i, s in enumerate(self.scores):
            # if i = 9, num = 10, take log10(11) so the result is strictly greater than 1.0
            placesConsumed = math.ceil(math.log10(i + 2))
            zeroesNeeded = placesRequired - placesConsumed
            zeroes = '0' * zeroesNeeded
            scoreName = fpStem + '-' + zeroes + str(i + 1) + fpSuffix
            fpToUse = fpParent / scoreName
            fpReturned = s.write(fmt=fmt, fp=fpToUse, **keywords)
            environLocal.printDebug(f'Component {s} written to {fpReturned}')
            post.append(fpReturned)

        if delete:
            os.remove(fp)

        return post[-1] if post else None

    def show(self, fmt=None, app=None, **keywords):
        '''
        Show an Opus file.

        This method overrides the behavior specified in
        :class:`~music21.base.Music21Object` for all
        formats besides explicit lily.x calls. or when running under Jupyter notebook.
        '''
        if fmt is not None and 'lily' in fmt:
            return Stream.show(self, fmt, app, **keywords)
        elif common.runningInNotebook():
            return Stream.show(self, fmt, app, **keywords)
        else:
            for s in self.scores:
                s.show(fmt=fmt, app=app, **keywords)