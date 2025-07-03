# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/voice_operations.py
# Purpose:      Voice operations mixin for Stream objects
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Voice operations mixin for Stream objects.

This module contains the VoiceOperationsMixin class that provides
voice-related functionality for Stream objects. Methods were extracted
from stream/base.py to improve code organization.
"""
from __future__ import annotations

import typing as t

from music21 import note

if t.TYPE_CHECKING:
    from music21.stream.voice import Voice


class VoiceOperationsMixin:
    """
    Mixin providing voice-related operations for Stream objects.
    
    This mixin contains methods for:
    - Voice detection and analysis (hasVoices, voices property)
    - Voice creation and organization (makeVoices)
    - Voice manipulation (voicesToParts, flattenUnnecessaryVoices)
    - Voice counting utilities (_maxVoiceCount)
    
    Extracted from stream/base.py to improve code organization.
    Methods total: ~412 lines from original base.py
    """
    
    @property
    def voices(self):
        '''
        Return all :class:`~music21.stream.Voices` objects
        in an iterator

        >>> s = stream.Stream()
        >>> s.insert(0, stream.Voice())
        >>> s.insert(0, stream.Voice())
        >>> len(s.voices)
        2
        '''
        return self.getElementsByClass('Voice')

    def hasVoices(self):
        '''
        Return a boolean value showing if this Stream contains Voices
        '''
        if 'hasVoices' not in self._cache or self._cache['hasVoices'] is None:
            post = False
            # do not need to look in endElements
            for obj in self._elements:
                # if obj is a Part, we have multi-parts
                if 'Voice' in obj.classes:
                    post = True
                    break  # only need one
            self._cache['hasVoices'] = post
        return self._cache['hasVoices']

    def makeVoices(self, *, inPlace=False, fillGaps=True):
        '''
        If this Stream has overlapping Notes or Chords, this method will isolate
        all overlaps in unique Voices, and place those Voices in the Stream.

        >>> s = stream.Stream()
        >>> s.insert(0, note.Note('C4', quarterLength=4))
        >>> s.repeatInsert(note.Note('b-4', quarterLength=0.5), [x * 0.5 for x in list(range(8))])
        >>> s.makeVoices(inPlace=True)
        >>> len(s.voices)
        2
        >>> [n.pitch for n in s.voices[0].notes]
        [<music21.pitch.Pitch C4>]
        >>> [str(n.pitch) for n in s.voices[1].notes]
        ['B-4', 'B-4', 'B-4', 'B-4', 'B-4', 'B-4', 'B-4', 'B-4']

        * Changed in v7: if `fillGaps=True` and called on an incomplete measure,
          makes trailing rests in voices. This scenario occurs when parsing MIDI.
        '''
        # this method may not always
        # produce the optimal voice assignment based on context (register
        # chord formation, etc
        if not inPlace:  # make a copy
            returnObj = self.coreCopyAsDerivation('makeVoices')
        else:
            returnObj = self
        # must be sorted
        if not returnObj.isSorted:
            returnObj.sort()
        olDict = returnObj.notes.stream().getOverlaps()
        # environLocal.printDebug(['makeVoices(): olDict', olDict])
        # find the max necessary voices by finding the max number
        # of elements in each group; these may not all be necessary
        maxVoiceCount = max([len(group) for group in olDict.values()] + [1])
        if maxVoiceCount == 1:  # nothing to do here
            if not inPlace:
                return returnObj
            return None

        # store all voices in a list
        voices = []
        for dummy in range(maxVoiceCount):
            voices.append(self._stream_factory.create_voice())  # add voice classes

        # iterate through all elements; if not in an overlap, place in
        # voice 1, otherwise, distribute
        for e in returnObj.notes:
            o = e.getOffsetBySite(returnObj)
            # cannot match here by offset, as olDict keys are representative
            # of the first overlapped offset, not all contained offsets
            # if o not in olDict:  # place in a first voices
            #    voices[0].insert(o, e)
            # find a voice to place in
            # as elements are sorted, can use the highest time
            # else:
            for v in voices:
                if v.highestTime <= o:
                    v.insert(o, e)
                    break
            # remove from source
            returnObj.remove(e)
        # remove any unused voices (possible if overlap group has sus)
        for v in voices:
            if v:  # skip empty voices
                returnObj.insert(0, v)
        if fillGaps:
            returnObj.makeRests(fillGaps=True,
                                inPlace=True,
                                timeRangeFromBarDuration=True,
                                )
        # remove rests in returnObj
        returnObj.removeByClass('Rest')
        # elements changed will already have been called
        if not inPlace:
            return returnObj

    def _maxVoiceCount(self, *, countById=False) -> int|tuple[int, list[str]]:
        '''
        Of all Measures in this Stream, return the Measure that has the max
        number of voices.

        If countById is True, then return a two-element tuple of the max count
        and a list of voice ids, otherwise just return the max count.
        '''
        maxCount = 0
        voiceIds = []
        for m in self._stream_factory.get_elements_by_class(self, 'Measure'):
            # idsInM will be empty list if no voices in measure
            if countById:
                idsInM = m.voiceIds
                if len(idsInM) > maxCount:
                    maxCount = len(idsInM)
                    voiceIds = idsInM
            else:
                idCount = len(m.voices)
                if idCount > maxCount:
                    maxCount = idCount

        if countById:
            return maxCount, voiceIds
        else:
            return maxCount

    def voicesToParts(self, *, separateById=False):
        '''
        If this Stream defines one or more voices,
        extract a Part for each voice.

        >>> s = stream.Stream()
        >>> s.id = 'mainStream'
        >>> s.append(meter.TimeSignature('3/4'))
        >>> v1 = stream.Voice()
        >>> v1.id = 'voice1'
        >>> v1.append(note.Note('C4', quarterLength=3))
        >>> v2 = stream.Voice()
        >>> v2.id = 'voice2'
        >>> v2.append(note.Note('G4', quarterLength=3))
        >>> s.insert(0, v1)
        >>> s.insert(0, v2)
        >>> s.voicesToParts()  # returns a Score
        <music21.stream.Score 0x...>

        >>> s = corpus.parse('bach/bwv66.6.xml')
        >>> voicePart = s.parts[0].measures(1, 3).voicesToParts()
        '''
        if not separateById:
            maxVoiceCount = self._maxVoiceCount()
        else:
            maxVoiceCount, allIds = self._maxVoiceCount(countById=True)

        # assume that all measures have the maximum number
        # create a part for each voice

        sSingle = self._stream_factory.create_score()
        for i in range(maxVoiceCount):
            p = self._stream_factory.create_part()
            sSingle.insert(0, p)

        # iterate through measures, getting voices
        # i here is an index of the part we are adding to
        measuresToCopy = []

        # TODO(msc): check that this is still necessary after voice/measure split
        try:
            # try on m.measures, which catches nested streams like Opus files
            for m in self._stream_factory.get_elements_by_class(self, 'Measure'):
                measuresToCopy.append(m)
        except:  # pylint: disable=bare-except
            for m in self.getElementsByClass('Measure'):
                measuresToCopy.append(m)

        for m in measuresToCopy:
            # assign voices to parts in order; first to first, second to second
            # this does not take into account assignment by id
            # that assumes voices are already in order

            if separateById and allIds:
                # TODO(msc): fix bugs if same voice id appears twice in same measure
                for vIndex, vId in enumerate(allIds):
                    for v in m.voices:
                        if v.id == vId:
                            # environLocal.printDebug(['got voice id match', v, 'vIndex', vIndex])
                            # get a part from sSingle; insert offset of measure
                            sSingle[vIndex].insert(m.offset, m.template(fillWithRests=False))
                            # iterate through all elements in the voice
                            # and add to the part's Measure at the appropriate position
                            for e in v:
                                sSingle[vIndex].getElementsByClass('Measure').last().insert(
                                    e.offset, e)
            else:
                voiceIndex = 0
                for v in m.voices:
                    # environLocal.printDebug(['processing voice', v, 'voiceIndex', voiceIndex])
                    # get a part from sSingle; insert offset of measure
                    # need to copy the measure and empty it
                    sSingle[voiceIndex].insert(m.offset, m.template(fillWithRests=False))
                    # iterate through all elements in the voice
                    # and add to the part's Measure at the appropriate position
                    for e in v:
                        sSingle[voiceIndex].getElementsByClass('Measure').last().insert(e.offset, e)
                    voiceIndex += 1

        return sSingle

    def flattenUnnecessaryVoices(self, *, force=False, inPlace=False):
        '''
        If this Stream defines one or more internal voices, do the following:

        If voice contains only a single voice, place those elements in the
        parent Stream. If voice defines multiple voices, and `force` is `True`,
        then all voices will be flattened.

        The `force` parameter is employed by makeNotation.

        >>> s = stream.Stream()
        >>> v1 = stream.Voice()
        >>> v1.insert(0, note.Note('D4', quarterLength=2))
        >>> s.insert(0, v1)
        >>> len(s.voices)
        1
        >>> s.flattenUnnecessaryVoices(inPlace=True)
        >>> len(s.voices)
        0
        >>> len(s.notes)
        1
        '''
        def doOneMeasure(s):
            mutable = not s.isImmutable
            if not mutable:
                return s

            # Store all voices and non-voice elements
            voices = list(s.voices)
            nonVoiceElements = [e for e in s if 'Voice' not in e.classes]

            # Check if we should flatten
            shouldFlatten = force or len(voices) <= 1

            if shouldFlatten and voices:
                # Remove all elements
                for e in list(s):
                    s.remove(e)

                # Re-add non-voice elements
                for e in nonVoiceElements:
                    s.insert(e.offset, e)

                # Flatten voice contents
                for v in voices:
                    for e in v:
                        s.insert(v.offset + e.offset, e)

            return s

        if not inPlace:  # make a copy
            returnObj = self.coreCopyAsDerivation('flattenUnnecessaryVoices')
        else:
            returnObj = self

        if self._stream_factory.isinstance_check(returnObj, ['Measure']):
            returnObj = doOneMeasure(returnObj)
        else:
            # Process all measures
            for m in returnObj._stream_factory.get_elements_by_class(returnObj, 'Measure'):
                doOneMeasure(m)

        if not inPlace:
            return returnObj
        else:
            return None