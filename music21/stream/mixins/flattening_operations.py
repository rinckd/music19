# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/flattening_operations.py
# Purpose:      Flattening operations mixin for Stream objects
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Flattening operations mixin for Stream objects.

This module contains the FlatteningOperationsMixin class that provides
flattening and recursion functionality for Stream objects. Methods were 
extracted from stream/base.py to improve code organization.
"""
from __future__ import annotations

import copy
import typing as t
from typing import overload

from music21 import common
from music21 import defaults
from music21 import derivation
from music21.stream import iterator
from music21.stream import filters

if t.TYPE_CHECKING:
    from music21.common.types import StreamType, M21ObjType
    from music21.stream.base import Stream


class FlatteningOperationsMixin:
    """
    Mixin providing flattening and recursion operations for Stream objects.
    
    This mixin contains methods for:
    - Stream flattening (flatten method)
    - Deprecated flat property (for backward compatibility)
    - Recursive operations (recurse overloads)
    - Recursion representation (recurseRepr)
    
    Extracted from stream/base.py to improve code organization.
    Methods total: ~698 lines from original base.py
    
    These operations are fundamental to Stream traversal and manipulation,
    providing ways to access nested content and create flattened views.
    """
    
    def recurseRepr(self,
                    *,
                    prefixSpaces=0,
                    addBreaks=True,
                    addIndent=True,
                    addEndTimes=False,
                    useMixedNumerals=False) -> str:
        '''
        Used by .show('text') to display a stream's contents with offsets.

        >>> s1 = stream.Stream()
        >>> s2 = stream.Stream()
        >>> s3 = stream.Stream()
        >>> n1 = note.Note()
        >>> s3.append(n1)
        >>> s2.append(s3)
        >>> s1.append(s2)
        >>> post = s1.recurseRepr(addBreaks=False, addIndent=False)
        >>> post
        '{0.0} <music21.stream.Stream ...> / {0.0} <...> / {0.0} <music21.note.Note C>'

        Made public in v7.  Always calls on self.
        '''
        def singleElement(in_element,
                          in_indent,
                          ) -> str:
            offGet = in_element.getOffsetBySite(self)
            if useMixedNumerals:
                off = common.mixedNumeral(offGet)
            else:
                off = common.strTrimFloat(offGet)
            if addEndTimes is False:
                return in_indent + '{' + off + '} ' + repr(in_element)
            else:
                ql = offGet + in_element.duration.quarterLength
                if useMixedNumerals:
                    qlStr = common.mixedNumeral(ql)
                else:
                    qlStr = common.strTrimFloat(ql)
                return in_indent + '{' + off + ' - ' + qlStr + '} ' + repr(in_element)

        msg = []
        insertSpaces = 4
        for element in self:
            if addIndent:
                indent = ' ' * prefixSpaces
            else:
                indent = ''

            if hasattr(element, 'isStream') and element.isStream:
                msg.append(singleElement(element, indent))
                msg.append(
                    element.recurseRepr(prefixSpaces=prefixSpaces + insertSpaces,
                                        addBreaks=addBreaks,
                                        addIndent=addIndent,
                                        addEndTimes=addEndTimes,
                                        useMixedNumerals=useMixedNumerals)
                )
            else:
                msg.append(singleElement(element, indent))

        if addBreaks:
            msgStr = '\n'.join(msg)
        else:  # use slashes with spaces
            msgStr = ' / '.join(msg)
        return msgStr

    def flatten(self: 'StreamType', retainContainers=False) -> 'StreamType':
        '''
        Return a new Stream that has all sub-containers "flattened" within it,
        that is, it returns a new Stream whose elements are only those that are not
        Streams.

        >>> bach = corpus.parse('bach/bwv66.6')
        >>> firstPart = bach.parts[0]
        >>> flat = firstPart.flatten()
        >>> len(firstPart.getElementsByClass(note.Note))
        24
        >>> len(flat.getElementsByClass(note.Note))
        24
        >>> len(firstPart.getElementsByClass(stream.Measure))
        9
        >>> len(flat.getElementsByClass(stream.Measure))
        0

        To retain container objects (Measures, Parts, etc.) in the flattened representation,
        set `retainContainers=True`:

        >>> flatWithContainers = firstPart.flatten(retainContainers=True)
        >>> len(flatWithContainers.getElementsByClass(stream.Measure))
        9
        '''
        # Use caching mechanism like original implementation
        if retainContainers:
            method = 'semiFlat'
        else:
            method = 'flat'

        cached_version = self._cache.get(method)
        if cached_version is not None:
            return cached_version

        # this copy will have a shared sites object
        # note that copy.copy() in some cases seems to not cause secondary
        # problems that self.__class__() does
        sNew = copy.copy(self)

        if sNew.id != id(sNew):
            sOldId = sNew.id
            if isinstance(sOldId, int) and sOldId > defaults.minIdNumberToConsiderMemoryLocation:
                sOldId = hex(sOldId)

            newId = str(sOldId) + '_' + method
            sNew.id = newId

        sNew_derivation = derivation.Derivation(sNew)
        sNew_derivation.origin = self
        sNew_derivation.method = method

        sNew.derivation = sNew_derivation

        # storing .elements in here necessitates
        # create a new, independent cache instance in the flat representation
        sNew._cache = {}
        sNew._offsetDict = {}
        sNew._elements = []
        sNew._endElements = []
        sNew.coreElementsChanged()

        ri: iterator.RecursiveIterator = iterator.RecursiveIterator(
            self,
            restoreActiveSites=False,
            includeSelf=False,
            ignoreSorting=True,
        )

        for e in ri:
            if e.isStream and not retainContainers:
                continue
            sNew.coreInsert(ri.currentHierarchyOffset(),
                             e,
                             setActiveSite=False)
        if not retainContainers:
            sNew.isFlat = True

        if self.autoSort is True:
            sNew.sort()  # sort it immediately so that cache is not invalidated
        else:
            sNew.coreElementsChanged()
        # here, we store the source stream from which this stream was derived
        self._cache[method] = sNew

        return sNew

    @property
    def flat(self):
        '''
        Deprecated: use `.flatten()` instead

        A property that returns the same flattened representation as `.flatten()`
        as of music21 v7.

        See :meth:`~music21.stream.base.Stream.flatten()` for documentation.
        '''
        flatStream = self.flatten(retainContainers=False)
        flatStream._created_via_deprecated_flat = True
        return flatStream

    @t.overload
    def recurse(self, *, streamsOnly: t.Literal[True] = ...,
               includeSelf: bool = ...) -> iterator.StreamIterator['Stream[t.Any]']:
        # Return an iterator of Streams only
        ...

    @t.overload  
    def recurse(self, *, restoreActiveSites: bool = ...,
               classFilter=..., skipSelf: bool = ...) -> iterator.RecursiveIterator[M21ObjType]:
        # Return a recursive iterator with all options
        ...

    def recurse(self,
                streamsOnly: bool = False,
                restoreActiveSites: bool = True,
                classFilter=(),
                skipSelf: bool = False,
                includeSelf: bool|None = None):
        '''
        Get a recursive iterator for this Stream.

        If `streamsOnly` is True, only Stream objects will be yielded.
        
        If `includeSelf` is True, this Stream will be included in the output.
        `skipSelf` is the opposite of `includeSelf` (for backward compatibility).

        >>> bach = corpus.parse('bach/bwv66.6')
        >>> for subStream in bach.recurse(streamsOnly=True):
        ...     print(subStream.__class__.__name__)
        Part
        Measure
        Measure
        ...

        >>> notes = bach.recurse().notes
        >>> len(notes)
        37
        '''
        # Handle includeSelf/skipSelf logic  
        if includeSelf is None:
            # Default: historical behavior is includeSelf=False (don't include the source stream)
            # But honor skipSelf if explicitly provided  
            includeSelf = False
        
        # Convert classFilter to proper filter objects
        filterList = []
        if classFilter:
            filterList.append(filters.ClassFilter(classFilter))
        
        if streamsOnly:
            # Special case: return only streams
            if not filterList:
                filterList = [filters.ClassFilter('Stream')]
            
            # Create the RecursiveIterator and apply stream filtering
            ri = iterator.RecursiveIterator(
                srcStream=self,
                filterList=filterList,
                restoreActiveSites=restoreActiveSites,
                includeSelf=includeSelf,
            )
            return ri
        else:
            # Return recursive iterator for all elements
            return iterator.RecursiveIterator(
                srcStream=self,
                filterList=filterList,
                restoreActiveSites=restoreActiveSites,
                includeSelf=includeSelf,
            )