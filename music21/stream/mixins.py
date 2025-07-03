# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins.py
# Purpose:      Mixin classes for Stream functionality
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Mixin classes for Stream functionality.

This module contains mixin classes that provide specialized functionality
for Stream objects. These mixins were extracted from stream/base.py to
improve code organization and maintainability.

The mixins are designed to be mixed into the main Stream class to provide
their functionality while keeping the core Stream class focused on
fundamental container operations.
"""
from __future__ import annotations

import types
import typing as t
from fractions import Fraction

from music21 import bar
from music21 import common
from music21 import meter
from music21.common.types import OffsetQL, OffsetQLSpecial
from music21.stream import iterator
from music21.stream.enums import GivenElementsBehavior
from music21 import exceptions21

if t.TYPE_CHECKING:
    from music21 import base
    from music21.stream.base import Stream
    from music21.stream.measure import Measure

# Exception shortcuts
StreamException = exceptions21.StreamException


class MeasureOperationsMixin:
    """
    Mixin providing measure-related operations for Stream objects.
    
    This mixin contains all methods related to measure creation, access,
    manipulation, and analysis. It was extracted from stream/base.py to
    improve code organization.
    
    Methods included:
    - Measure access and iteration (measures, measure, template)
    - Measure creation and numbering (makeMeasures, _fixMeasureNumbers)
    - Measure offset calculations (measureOffsetMap, beatAndMeasureFromOffset)
    - Barline operations (_getFinalBarline, _setFinalBarline)
    - Measure analysis (hasMeasures)
    """
    
    def _getMeasureNumberListByStartEnd(
        self,
        numberStart: int|str,
        numberEnd: int|str,
        *,
        indicesNotNumbers: bool
    ) -> list['Measure']:
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


# Placeholder for future mixins
class VariantOperationsMixin:
    """
    Mixin providing variant-related operations for Stream objects.
    
    This mixin will contain all methods related to musical variant handling,
    including activation, insertion, and management of different readings
    of musical passages.
    """
    pass


class FlatteningOperationsMixin:
    """
    Mixin providing flattening and recursion operations for Stream objects.
    
    This mixin will contain methods for flattening nested streams,
    recursive operations, and related stream transformation operations.
    """
    pass


class VoiceOperationsMixin:
    """
    Mixin providing voice and part-related operations for Stream objects.
    
    This mixin will contain methods for voice creation, part operations,
    and polyphonic music handling.
    """
    pass


class NotationOperationsMixin:
    """
    Mixin providing notation-related operations for Stream objects.
    
    This mixin will contain methods for creating musical notation,
    handling ties, beams, and other visual elements.
    """
    pass