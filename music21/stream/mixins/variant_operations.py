# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/variant_operations.py
# Purpose:      Variant operations mixin for Stream objects
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Variant operations mixin for Stream objects.

This module contains the VariantOperationsMixin class that provides
variant-related functionality for Stream objects. Methods were extracted
from stream/base.py to improve code organization.
"""
from __future__ import annotations

import copy
import typing as t
from collections import deque

from music21 import common
from music21 import exceptions21

if t.TYPE_CHECKING:
    from music21.common.types import StreamType, M21ObjType
    from music21.stream.base import Stream

# Exception shortcuts
StreamException = exceptions21.StreamException


class VariantOperationsMixin:
    """
    Mixin providing variant-related operations for Stream objects.
    
    This mixin contains methods for:
    - Variant activation (activateVariants)
    - Variant insertion operations (_insertReplacementVariant, _insertDeletionVariant, _insertInsertionVariant)
    - Ossia-like part display (showVariantAsOssialikePart)
    
    Extracted from stream/base.py to improve code organization.
    Methods total: ~953 lines from original base.py
    
    These operations provide sophisticated music variant handling,
    enabling multiple versions or interpretations of musical passages
    to coexist within the same musical structure.
    """
    
    def activateVariants(self, group=None, *, matchBySpan=True, inPlace=False):
        '''
        For any :class:`~music21.variant.Variant` objects defined in this Stream
        (or selected by matching the `group` parameter),
        replace elements defined in the Variant with those in the calling Stream.
        Elements replaced will be gathered into a new Variant
        given the group 'default'. If a variant is activated with
        .replacementDuration different from its length, the appropriate elements
        in the stream will have their offsets shifted, and measure numbering
        will be fixed. If matchBySpan is True, variants with lengthType
        'replacement' will replace all the elements in the
        replacement region of comparable class. If matchBySpan is False,
        elements will be swapped in when a match is found between an element
        in the variant and an element in the replacement region of the string.

        >>> sStr   = 'd4 e4 f4 g4   a2 b-4 a4    g4 a8 g8 f4 e4    d2 a2              '
        >>> v1Str  = '              a2. b-8 a8 '
        >>> v2Str1 = '                                             d4 f4 a2 '
        >>> v2Str2 = '                                                      d4 f4 AA2 '

        >>> sStr += "d4 e4 f4 g4    a2 b-4 a4    g4 a8 b-8 c'4 c4    f1"

        >>> s = converter.parse('tinynotation: 4/4 ' + sStr, makeNotation=False)
        >>> s.makeMeasures(inPlace=True)  # maybe not necessary?
        >>> v1stream = converter.parse('tinynotation: 4/4 ' + v1Str, makeNotation=False)
        >>> v2stream1 = converter.parse('tinynotation: 4/4 ' + v2Str1, makeNotation=False)
        >>> v2stream2 = converter.parse('tinynotation: 4/4 ' + v2Str2, makeNotation=False)

        >>> v1 = variant.Variant()
        >>> v1measure = stream.Measure()
        >>> v1.insert(0.0, v1measure)
        >>> for e in v1stream.notesAndRests:
        ...    v1measure.insert(e.offset, e)

        >>> v2 = variant.Variant()
        >>> v2.replacementDuration = 4.0
        >>> v2measure1 = stream.Measure()
        >>> v2measure2 = stream.Measure()
        >>> v2.insert(0.0, v2measure1)
        >>> v2.insert(4.0, v2measure2)
        >>> for e in v2stream1.notesAndRests:
        ...    v2measure1.insert(e.offset, e)
        >>> for e in v2stream2.notesAndRests:
        ...    v2measure2.insert(e.offset, e)

        >>> v3 = variant.Variant()
        >>> v3.replacementDuration = 4.0
        >>> v1.groups = ['docVariants']
        >>> v2.groups = ['docVariants']
        >>> v3.groups = ['docVariants']

        >>> s.insert(4.0, v1)   # replacement variant
        >>> s.insert(12.0, v2)  # insertion variant (2 bars replace 1 bar)
        >>> s.insert(20.0, v3)  # deletion variant (0 bars replace 1 bar)
        >>> s.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {4.0} <music21.variant.Variant object of length 4.0>
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
        {12.0} <music21.variant.Variant object of length 8.0>
        {12.0} <music21.stream.Measure 4 offset=12.0>
            {0.0} <music21.note.Note D>
            {2.0} <music21.note.Note A>
        {16.0} <music21.stream.Measure 5 offset=16.0>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {20.0} <music21.variant.Variant object of length 0.0>
        {20.0} <music21.stream.Measure 6 offset=20.0>
            {0.0} <music21.note.Note A>
            {2.0} <music21.note.Note B->
            {3.0} <music21.note.Note A>
        {24.0} <music21.stream.Measure 7 offset=24.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {1.5} <music21.note.Note B->
            {2.0} <music21.note.Note C>
            {3.0} <music21.note.Note C>
        {28.0} <music21.stream.Measure 8 offset=28.0>
            {0.0} <music21.note.Note F>
            {4.0} <music21.bar.Barline type=final>

        >>> docVariant = s.activateVariants('docVariants')

        >>> #_DOCS_SHOW s.show()

        .. image:: images/stream_activateVariants1.*
            :width: 600

        >>> #_DOCS_SHOW docVariant.show()

        .. image:: images/stream_activateVariants2.*
            :width: 600

        >>> docVariant.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {4.0} <music21.variant.Variant object of length 4.0>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note A>
            {3.0} <music21.note.Note B->
            {3.5} <music21.note.Note A>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {1.5} <music21.note.Note G>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note E>
        {12.0} <music21.variant.Variant object of length 4.0>
        {12.0} <music21.stream.Measure 4 offset=12.0>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note F>
            {2.0} <music21.note.Note A>
        {16.0} <music21.stream.Measure 5 offset=16.0>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note F>
            {2.0} <music21.note.Note A>
        {20.0} <music21.stream.Measure 6 offset=20.0>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {24.0} <music21.variant.Variant object of length 4.0>
        {24.0} <music21.stream.Measure 7 offset=24.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {1.5} <music21.note.Note B->
            {2.0} <music21.note.Note C>
            {3.0} <music21.note.Note C>
        {28.0} <music21.stream.Measure 8 offset=28.0>
            {0.0} <music21.note.Note F>
            {4.0} <music21.bar.Barline type=final>

        After a variant group has been activated, the regions it replaced are
        stored as variants with the group 'default'.
        It should be noted that this means .activateVariants should rarely if
        ever be used on a stream which is returned
        by activateVariants because the group information is lost.

        >>> defaultVariant = docVariant.activateVariants('default')
        >>> #_DOCS_SHOW defaultVariant.show()

        .. image:: images/stream_activateVariants3.*
            :width: 600

        >>> defaultVariant.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {4.0} <music21.variant.Variant object of length 4.0>
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
        {12.0} <music21.variant.Variant object of length 8.0>
        {12.0} <music21.stream.Measure 4 offset=12.0>
            {0.0} <music21.note.Note D>
            {2.0} <music21.note.Note A>
        {16.0} <music21.stream.Measure 5 offset=16.0>
            {0.0} <music21.note.Note D>
            {1.0} <music21.note.Note E>
            {2.0} <music21.note.Note F>
            {3.0} <music21.note.Note G>
        {20.0} <music21.variant.Variant object of length 0.0>
        {20.0} <music21.stream.Measure 6 offset=20.0>
            {0.0} <music21.note.Note A>
            {2.0} <music21.note.Note B->
            {3.0} <music21.note.Note A>
        {24.0} <music21.stream.Measure 7 offset=24.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {1.5} <music21.note.Note B->
            {2.0} <music21.note.Note C>
            {3.0} <music21.note.Note C>
        {28.0} <music21.stream.Measure 8 offset=28.0>
            {0.0} <music21.note.Note F>
            {4.0} <music21.bar.Barline type=final>
        '''
        from music21 import variant
        if not inPlace:  # make a copy if inPlace is False
            returnObj = self.coreCopyAsDerivation('activateVariants')
        else:
            returnObj = self

        # Define Lists to cache variants
        elongationVariants = []
        deletionVariants = []

        # Loop through all variants, deal with replacement variants and
        # save insertion and deletion for later.
        for v in returnObj.getElementsByClass(variant.Variant):
            if group is not None and group not in v.groups:
                continue  # skip those that are not part of this group

            lengthType = v.lengthType

            # save insertions to perform last
            if lengthType == 'elongation':
                elongationVariants.append(v)
            # save deletions to perform after replacements
            elif lengthType == 'deletion':
                deletionVariants.append(v)
            # Deal with cases in which variant is the same length as what it replaces first.
            elif lengthType == 'replacement':
                returnObj._insertReplacementVariant(v, matchBySpan)

        # Now deal with deletions before insertion variants.
        # For keeping track of which measure numbers have been removed
        deletedMeasures = []
        # For keeping track of where new measures without measure numbers have been inserted,
        # will be a list of tuples (measureNumberPrior, [List, of, inserted, measures])
        insertedMeasures = []
        # For keeping track of the sections that are deleted
        # (so the offset gap can be closed later)
        deletedRegionsForRemoval = []
        for v in deletionVariants:
            (deletedRegion, vDeletedMeasures, vInsertedMeasuresTuple
             ) = returnObj._insertDeletionVariant(v, matchBySpan)  # deletes and inserts
            deletedRegionsForRemoval.append(deletedRegion)  # Saves the deleted region
            deletedMeasures.extend(vDeletedMeasures)  # Saves the deleted measure numbers
            # saves the inserted numberless measures (this will be empty unless there are
            # more bars in the variant than in the replacement region, which is unlikely
            # for a deletion variant).
            insertedMeasures.append(vInsertedMeasuresTuple)

        # Squeeze out the gaps that were saved.
        returnObj._removeOrExpandGaps(deletedRegionsForRemoval, isRemove=True, inPlace=True)

        # Before we can deal with insertions, we have to expand the stream to make space.
        insertionRegionsForExpansion = []  # For saving the insertion regions
        # go through all elongation variants to find the insertion regions.
        for v in elongationVariants:
            lengthDifference = v.replacementDuration - v.containedHighestTime
            insertionStart = v.getOffsetBySite(returnObj) + v.replacementDuration
            # Saves the information for each gap to be expanded
            insertionRegionsForExpansion.append((insertionStart, -1 * lengthDifference, [v]))

        # Expands the appropriate gaps in the stream.
        returnObj._removeOrExpandGaps(insertionRegionsForExpansion, isRemove=False, inPlace=True)
        # Now deal with elongation variants properly
        for v in elongationVariants:
            (vInsertedMeasuresTuple, vDeletedMeasures
             ) = returnObj._insertInsertionVariant(v, matchBySpan)  # deletes and inserts
            insertedMeasures.append(vInsertedMeasuresTuple)
            # Saves the numberless inserted measures
            # Saves deleted measures if any (it is unlikely that there will be unless
            # there are fewer measures in the variant than the replacement region,
            # which is unlikely for an elongation variant)
            deletedMeasures.extend(vDeletedMeasures)

        # Now fix measure numbers given the saved information
        returnObj._fixMeasureNumbers(deletedMeasures, insertedMeasures)

        # have to clear cached variants, as they are no longer the same
        returnObj.coreElementsChanged()

        if not inPlace:
            return returnObj
        else:
            return None

    def _insertReplacementVariant(self, v, matchBySpan=True):
        # noinspection PyShadowingNames
        '''
        Helper function for activateVariants. Activates variants which are the same size there the
        region they replace.

        >>> v = variant.Variant()
        >>> variantDataM1 = [('b', 'eighth'), ('c', 'eighth'),
        ...                  ('a', 'quarter'), ('a', 'quarter'),('b', 'quarter')]
        >>> variantDataM2 = [('c', 'quarter'), ('d', 'quarter'), ('e', 'quarter'), ('e', 'quarter')]
        >>> variantData = [variantDataM1, variantDataM2]
        >>> for d in variantData:
        ...    m = stream.Measure()
        ...    for pitchName,durType in d:
        ...        n = note.Note(pitchName)
        ...        n.duration.type = durType
        ...        m.append(n)
        ...    v.append(m)
        >>> v.groups = ['paris']
        >>> v.replacementDuration = 8.0

        >>> s = stream.Stream()
        >>> streamDataM1 = [('a', 'quarter'), ('b', 'quarter'), ('a', 'quarter'), ('g', 'quarter')]
        >>> streamDataM2 = [('b', 'eighth'), ('c', 'quarter'), ('a', 'eighth'),
        ...                 ('a', 'quarter'), ('b', 'quarter')]
        >>> streamDataM3 = [('c', 'quarter'), ('b', 'quarter'), ('a', 'quarter'), ('a', 'quarter')]
        >>> streamDataM4 = [('c', 'quarter'), ('b', 'quarter'), ('a', 'quarter'), ('a', 'quarter')]
        >>> streamData = [streamDataM1, streamDataM2, streamDataM3, streamDataM4]
        >>> for d in streamData:
        ...    m = stream.Measure()
        ...    for pitchName,durType in d:
        ...        n = note.Note(pitchName)
        ...        n.duration.type = durType
        ...        m.append(n)
        ...    s.append(m)
        >>> s.insert(4.0, v)

        >>> deletedMeasures, insertedMeasuresTuple = s._insertReplacementVariant(v)
        >>> deletedMeasures
        []
        >>> insertedMeasuresTuple
        (0, [])
        >>> s.show('text')
        {0.0} <music21.stream.Measure 0 offset=0.0>
            {0.0} <music21.note.Note A>
            {1.0} <music21.note.Note B>
            {2.0} <music21.note.Note A>
            {3.0} <music21.note.Note G>
        {4.0} <music21.variant.Variant object of length 8.0>
        {4.0} <music21.stream.Measure 0 offset=4.0>
            {0.0} <music21.note.Note B>
            {0.5} <music21.note.Note C>
            {1.0} <music21.note.Note A>
            {2.0} <music21.note.Note A>
            {3.0} <music21.note.Note B>
        {8.0} <music21.stream.Measure 0 offset=8.0>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note D>
            {2.0} <music21.note.Note E>
            {3.0} <music21.note.Note E>
        {12.0} <music21.stream.Measure 0 offset=12.0>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note B>
            {2.0} <music21.note.Note A>
            {3.0} <music21.note.Note A>
        '''
        from music21 import variant

        removed = variant.Variant()  # replacement variant
        removed.groups = ['default']  # for now, default
        vStart = self.elementOffset(v)
        # this method matches and removes on an individual basis
        if not matchBySpan:
            targetsMatched = 0
            for e in v.elements:  # get components in the Variant
                # get target offset relative to Stream
                oInStream = vStart + e.getOffsetBySite(v.containedSite)
                # get all elements at this offset, force a class match
                targets = self.getElementsByOffset(oInStream).getElementsByClass(e.classes[0])
                # only replace if we match the start
                if targets:
                    targetsMatched += 1
                    # always assume we just want the first one?
                    targetToReplace = targets[0]
                    # environLocal.printDebug(['matchBySpan', matchBySpan,
                    #     'found target to replace:', targetToReplace])
                    # remove the target, place in removed Variant
                    removed.append(targetToReplace)
                    self.remove(targetToReplace)
                    # extract the variant component and insert into place
                    self.insert(oInStream, e)

                    if getattr(targetToReplace, 'isMeasure', False):
                        e.number = targetToReplace.number
            # only remove old and add removed if we matched
            if targetsMatched > 0:
                # remove the original variant
                self.remove(v)
                # place newly contained elements in position
                self.insert(vStart, removed)

        # matching by span means that we remove all elements with the
        # span defined by the variant
        else:
            deletedMeasures = deque()
            insertedMeasures = []
            highestNumber = None

            targets = v.replacedElements(self)

            # this will always remove elements before inserting
            for e in targets:
                # need to get time relative to variant container's position
                oInVariant = self.elementOffset(e) - vStart
                removed.insert(oInVariant, e)
                # environLocal.printDebug(
                #     ['matchBySpan', matchBySpan, 'activateVariants', 'removing', e])
                self.remove(e)
                if self._stream_factory.isinstance_check(e, ['Measure']):
                    # Save deleted measure numbers.
                    deletedMeasures.append(e.number)

            for e in v.elements:
                oInStream = vStart + e.getOffsetBySite(v.containedSite)
                self.insert(oInStream, e)
                if self._stream_factory.isinstance_check(e, ['Measure']):
                    if deletedMeasures:  # If there measure numbers left to use, use them.
                        # Assign the next highest deleted measure number
                        e.number = deletedMeasures.popleft()
                        # Save the highest number used so far (for use in the case
                        # that there are extra measures with no numbers at the end)
                        highestNumber = e.number

                    else:
                        e.number = 0
                        # If no measure numbers left, add this
                        # numberless measure to insertedMeasures
                        insertedMeasures.append(e)
            # remove the source variant
            self.remove(v)
            # place newly contained elements in position
            self.insert(vStart, removed)

            # If deletedMeasures != [], then there were more deleted measures than
            # inserted and the remaining numbers in deletedMeasures are those that were removed.
            return (list(deletedMeasures),
                    (highestNumber, insertedMeasures))
            # In the case that the variant and stream are in the same time-signature,
            # this should return []
    def _insertDeletionVariant(self, v, matchBySpan=True):
        # noinspection PyShadowingNames
        '''
        Helper function for activateVariants used for inserting variants that are shorter than
        the region they replace. Inserts elements in the variant and deletes elements in the
        replaced region but does not close gaps.

        Returns a tuple describing the region where elements were removed, the
        gap is left behind to be dealt with by _removeOrExpandGaps.
        Tuple is of form (startOffset, lengthOfDeletedRegion, []). The empty list is
        expected by _removeOrExpandGaps
        and describes the list of elements which should be exempted from shifting
        for a particular gap. In the
        case of deletion, no elements need be exempted.
        '''
        from music21 import variant

        deletedMeasures = deque()  # For keeping track of what measure numbers are deleted
        # length of the deleted region
        lengthDifference = v.replacementDuration - v.containedHighestTime

        removed = variant.Variant()  # what group should this have?
        removed.groups = ['default']  # for now, default
        removed.replacementDuration = v.containedHighestTime

        vStart = self.elementOffset(v)
        deletionStart = vStart + v.containedHighestTime

        targets = v.replacedElements(self)

        # this will always remove elements before inserting
        for e in targets:
            if self._stream_factory.isinstance_check(e, ['Measure']):  # if a measure is deleted, save its number
                deletedMeasures.append(e.number)
            oInVariant = self.elementOffset(e) - vStart
            removed.insert(oInVariant, e)
            self.remove(e)

        # Next put in the elements from the variant
        highestNumber = None
        insertedMeasures = []
        for e in v.elements:
            if self._stream_factory.isinstance_check(e, ['Measure']):
                # If there are deleted numbers still saved, assign this measure the
                # next highest and remove it from the list.
                if deletedMeasures:
                    e.number = deletedMeasures.popleft()
                    # Save the highest number assigned so far. If there are numberless
                    # inserted measures at the end, this will name where to begin numbering.
                    highestNumber = e.number
                else:
                    e.number = 0
                    # If there are no deleted numbers left (unlikely)
                    # save the inserted measures for renumbering later.
                    insertedMeasures.append(e)

            oInStream = vStart + e.getOffsetBySite(v.containedSite)
            self.insert(oInStream, e)

        # remove the source variant
        self.remove(v)
        # place newly contained elements in position
        self.insert(vStart, removed)

        # each variant leaves a gap, this saves the required information about those gaps
        # In most cases, inserted measures should be [].
        return (
            (deletionStart, lengthDifference, []),
            list(deletedMeasures),
            (highestNumber, insertedMeasures)
        )

    def _insertInsertionVariant(self, v, matchBySpan=True):
        # noinspection PyShadowingNames
        '''
        Helper function for activateVariants. _removeOrExpandGaps must be called on the
        expanded regions before this function,
        or it will not work properly.
        '''
        from music21 import variant

        deletedMeasures = deque()
        removed = variant.Variant()  # what group should this have?
        removed.groups = ['default']  # for now, default
        removed.replacementDuration = v.containedHighestTime
        vStart = self.elementOffset(v)

        # First deal with the elements in the overlapping section (limit by class)
        targets = v.replacedElements(self)

        # this will always remove elements before inserting
        for e in targets:
            if self._stream_factory.isinstance_check(e, ['Measure']):  # Save deleted measure numbers.
                deletedMeasures.append(e.number)
            oInVariant = self.elementOffset(e) - vStart
            removed.insert(oInVariant, e)
            self.remove(e)

        # Next put in the elements from the variant
        highestMeasure = None
        insertedMeasures = []
        for e in v.elements:
            if self._stream_factory.isinstance_check(e, ['Measure']):
                # If there are deleted measure numbers left, assign the next
                # inserted measure the next highest number and remove it.
                if deletedMeasures:
                    e.number = deletedMeasures.popleft()
                    highestMeasure = e.number
                    # Save the highest number assigned so far,
                    # so we know where to begin numbering new measures.
                else:
                    e.number = 0
                    insertedMeasures.append(e)
                    # If there are no deleted measures, we have begun inserting as yet
                    # unnumbered measures, save which those are.
            oInStream = vStart + e.getOffsetBySite(v.containedSite)
            self.insert(oInStream, e)

        if highestMeasure is None:
            # If the highestMeasure is None (which will occur if the variant is
            # a strict insertion and replaces no measures),
            # we need to choose the highest measure number prior to the variant.
            measuresToCheck = self.getElementsByOffset(0.0,
                                                       self.elementOffset(v),
                                                       includeEndBoundary=True,
                                                       mustFinishInSpan=False,
                                                       mustBeginInSpan=True,
                                                       )._stream_factory.get_elements_by_class(self, 'Measure')
            highestMeasure = 0
            for m in measuresToCheck:
                if highestMeasure is None or m.number > highestMeasure:
                    highestMeasure = m.number

        # remove the source variant
        self.remove(v)
        # place newly contained elements in position
        self.insert(vStart, removed)

        return (highestMeasure, insertedMeasures), deletedMeasures

    def _removeOrExpandGaps(self, listOffsetDurExemption,
                            isRemove=True, inPlace=False):
        '''
        Helper for activateVariants. Takes a list of tuples in the form
        (startOffset, duration, [list, of, exempt, objects]). If isRemove is True,
        gaps with duration will be closed at each startOffset.
        Exempt objects are useful for gap-expansion with variants. The gap must push all objects
        that occur after the insertion ahead, but the variant object
        itself should not be moved except by other gaps. This is poorly written
        and should be re-written, but it is difficult to describe.
        '''
        if inPlace is True:
            returnObj = self
        else:
            returnObj = copy.deepcopy(self)

        returnObjDuration = returnObj.duration.quarterLength

        # If any classes should be exempt from gap closing or expanding, this deals with those.
        if isRemove is True:
            shiftDur = 0.0
            listSorted = sorted(listOffsetDurExemption, key=lambda target: target[0])
            for i, durTuple in enumerate(listSorted):
                startOffset, durationAmount, exemptObjects = durTuple
                exemptObjectSet = set(id(e) for e in exemptObjects)  # use set id, not == checking
                if i + 1 < len(listSorted):
                    endOffset = listSorted[i + 1][0]
                    includeEnd = False
                else:
                    endOffset = returnObjDuration
                    includeEnd = True

                shiftDur = shiftDur + durationAmount
                for e in returnObj.getElementsByOffset(startOffset + durationAmount,
                                                       endOffset,
                                                       includeEndBoundary=includeEnd,
                                                       mustFinishInSpan=False,
                                                       mustBeginInSpan=True):

                    if id(e) in exemptObjectSet:
                        continue
                    if not inPlace and e.derivation.originId in exemptObjectSet:
                        continue

                    elementOffset = e.getOffsetBySite(returnObj)
                    returnObj.coreSetElementOffset(e, elementOffset - shiftDur)
        else:
            shiftDur = 0.0
            shiftsDict = {}
            listSorted = sorted(listOffsetDurExemption, key=lambda target: target[0])
            for i, durTuple in enumerate(listSorted):
                startOffset, durationAmount, exemptObjects = durTuple

                if i + 1 < len(listSorted):
                    endOffset = listSorted[i + 1][0]
                    includeEnd = False
                else:
                    endOffset = returnObjDuration
                    includeEnd = True

                exemptShift = shiftDur
                shiftDur = shiftDur + durationAmount
                shiftsDict[startOffset] = (shiftDur, endOffset, includeEnd,
                                           exemptObjects, exemptShift)

            for offset in sorted(shiftsDict, key=lambda off: -1 * off):
                shiftDur, endOffset, includeEnd, exemptObjects, exemptShift = shiftsDict[offset]
                # for speed and ID not == checking
                exemptObjectSet = set(id(e) for e in exemptObjects)
                for e in returnObj.getElementsByOffset(offset,
                                                       endOffset,
                                                       includeEndBoundary=includeEnd,
                                                       mustFinishInSpan=False,
                                                       mustBeginInSpan=True):

                    if (
                        id(e) in exemptObjectSet
                        or (not inPlace and e.derivation.originId in exemptObjectSet)
                    ):
                        elementOffset = e.getOffsetBySite(returnObj)
                        returnObj.coreSetElementOffset(e, elementOffset + exemptShift)
                        continue

                    elementOffset = e.getOffsetBySite(returnObj)
                    returnObj.coreSetElementOffset(e, elementOffset + shiftDur)

        # ran coreSetElementOffset
        returnObj.coreElementsChanged()

        if inPlace is True:
            return
        else:
            return returnObj

    def showVariantAsOssialikePart(self, containedPart, variantGroups, *, inPlace=False):
        # noinspection PyShadowingNames
        '''
        Takes a part within the score and a list of variant groups within that part.
        Puts the variant object
        in a part surrounded by hidden rests to mimic the appearance of an ossia despite limited
        musicXML support for ossia staves. Note that this will ignore variants with .lengthType
        'elongation' and 'deletion' as there is no good way to represent ossia staves like those
        by this method.
        '''
        from music21 import variant
        from music21 import note

        # containedPart must be in self, or an exception is raised.
        if not (containedPart in self):
            raise variant.VariantException(f'Could not find {containedPart} in {self}')

        if inPlace is True:
            returnObj = self
            returnPart = containedPart
        else:
            returnObj = self.coreCopyAsDerivation('showVariantAsOssialikePart')
            containedPartIndex = self.parts.stream().index(containedPart)
            returnPart = returnObj.iter().parts[containedPartIndex]

        # First build a new part object that is the same length as returnPart
        # but entirely hidden rests.
        # This is done by copying the part and removing unnecessary objects
        # including irrelevant variants
        # but saving relevant variants.
        for variantGroup in variantGroups:
            newPart = copy.deepcopy(returnPart)
            expressedVariantsExist = False
            for e in newPart.elements:
                eClasses = e.classes
                if 'Variant' in eClasses:
                    elementGroups = e.groups
                    if (not (variantGroup in elementGroups)
                            or e.lengthType in ['elongation', 'deletion']):
                        newPart.remove(e)
                    else:
                        expressedVariantsExist = True
                elif 'GeneralNote' in eClasses:
                    nQuarterLength = e.duration.quarterLength
                    nOffset = e.getOffsetBySite(newPart)
                    newPart.remove(e)
                    r = note.Rest()
                    r.style.hideObjectOnPrint = True
                    r.duration.quarterLength = nQuarterLength
                    newPart.insert(nOffset, r)
                elif 'Measure' in eClasses:  # Recurse if measure
                    measureDuration = e.duration.quarterLength
                    for n in e.notesAndRests:
                        e.remove(n)
                    r = note.Rest()
                    r.duration.quarterLength = measureDuration
                    r.style.hideObjectOnPrint = True
                    e.insert(0.0, r)

                e.style.hideObjectOnPrint = True

            newPart.activateVariants(variantGroup, inPlace=True, matchBySpan=True)
            if expressedVariantsExist:
                returnObj.insert(0.0, newPart)

        if inPlace:
            return
        else:
            return returnObj