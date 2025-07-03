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

import typing as t

from music21.stream import iterator

if t.TYPE_CHECKING:
    from music21.common.types import StreamType


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
                    prefixIndent: str = '',
                    addBreaks: bool = True,
                    addIndent: bool = True,
                    addEndTimes: bool = False,
                    useMixedNumerals: bool = False
                    ) -> str:
        '''
        Used internally by Stream.__repr__
        Returns a string representation of the Stream.
        
        Recursively visits all embedded Streams, showing the elements in each.

        * Added in v6.7: indent on repr.
        '''
        msg: list[str] = []
        if addBreaks:
            msg.append('\n')
        
        indent = prefixIndent
        if addIndent:
            indent += '    '
        
        # Use depth-first search to walk through all nested streams
        for el in self:
            if hasattr(el, 'recurseRepr'):  # nested stream
                msg.append(f'{indent}{el.__class__.__name__}:')
                msg.append(el.recurseRepr(
                    prefixIndent=indent,
                    addBreaks=addBreaks,
                    addIndent=addIndent,
                    addEndTimes=addEndTimes,
                    useMixedNumerals=useMixedNumerals
                ))
            else:  # normal element
                elStr = repr(el).strip()
                offset = el.getOffsetBySite(self)
                if addEndTimes and hasattr(el, 'duration') and el.duration is not None:
                    endTime = offset + el.duration.quarterLength
                    if useMixedNumerals:
                        offsetStr = common.mixedNumeral(offset)
                        endTimeStr = common.mixedNumeral(endTime)
                    else:
                        offsetStr = f'{offset:g}'
                        endTimeStr = f'{endTime:g}'
                    msg.append(f'{indent}{offsetStr}-{endTimeStr}: {elStr}')
                else:
                    if useMixedNumerals:
                        offsetStr = common.mixedNumeral(offset)
                    else:
                        offsetStr = f'{offset:g}'
                    msg.append(f'{indent}{offsetStr}: {elStr}')
        
        if addBreaks:
            msg.append('')
        return '\n'.join(msg)

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
        # Use the iterator system for flattening
        outObj = self.coreCopyAsDerivation('flatten')
        
        # Clear all elements
        outObj.coreElementsChanged()
        
        # Use recursive iterator to get all elements
        ri = iterator.RecursiveIterator(
            srcStream=self,
            restoreActiveSites=False,
            ignoreSorting=self.isSorted is not False,
        )
        
        if retainContainers:
            ri.includeSelf = True
            ri.includeStreamLayers = True
        else:
            ri.includeSelf = False
            ri.includeStreamLayers = False
            
        for e in ri:
            if retainContainers or not hasattr(e, 'isStream') or not e.isStream:
                # Calculate offset in flattened structure
                flatOffset = ri.currentHierarchyOffset()
                outObj.coreInsert(flatOffset, e)
        
        outObj.coreElementsChanged()
        return outObj

    @property
    def flat(self):
        '''
        A property that returns a flattened version of the Stream.
        
        .. deprecated:: v7
            Use :meth:`~music21.stream.Stream.flatten` instead.
        '''
        # Mark this as created via deprecated flat for warning in __iter__
        flatStream = self.flatten()
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
            includeSelf = not skipSelf
        
        if streamsOnly:
            # Special case: return only streams
            return iterator.StreamIterator(
                srcStream=self,
                filterList=classFilter or ['Stream'],
                restoreActiveSites=restoreActiveSites,
                activeInformation={},
            ).recurse()
        else:
            # Return recursive iterator for all elements
            return iterator.RecursiveIterator(
                srcStream=self,
                filterList=classFilter,
                restoreActiveSites=restoreActiveSites,
                includeSelf=includeSelf,
            )