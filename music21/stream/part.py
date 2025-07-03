# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/part.py
# Purpose:      Part-related classes extracted from stream/base.py
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
Part, PartStaff, and System classes for music21 streams.

Extracted from stream/base.py as part of Phase 2 dependency reduction.
'''
from __future__ import annotations

import typing as t

from music21 import instrument
from music21.stream.enums import RecursionType
from music21.stream import makeNotation

# PHASE 2 NOTE: This creates a circular import (part.py -> base.py -> part.py)
# This will be resolved in Phase 3 through dependency injection/factory patterns
# For now, we accept this circular import to maintain functionality
from music21.stream.base import Stream

if t.TYPE_CHECKING:
    from music21.stream.measure import Measure


class Part(Stream):
    '''
    A Stream subclass for designating music that is considered a single part.

    When put into a Score object, Part objects are all collected in the `Score.parts`
    call.  Otherwise, they mostly work like generic Streams.

    Generally the hierarchy goes: Score > Part > Measure > Voice, but you are not
    required to stick to this.

    Part groupings (piano braces, etc.) are found in the :ref:`moduleLayout` module
    in the :class:`~music21.layout.StaffGroup` Spanner object.

    OMIT_FROM_DOCS
    Check that this is True and works for everything before suggesting that it works!

    May be enclosed in a staff (for instance, 2nd and 3rd trombone
    on a single staff), may enclose staves (piano treble and piano bass),
    or may not enclose or be enclosed by a staff (in which case, it
    assumes that this part fits on one staff and shares it with no other
    part
    '''
    recursionType = RecursionType.FLATTEN

    # _DOC_ATTR: dict[str, str] = {
    # }

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self._partName = None
        self._partAbbreviation = None

    def _getPartName(self):
        if self._partName is not None:
            return self._partName
        elif '_partName' in self._cache:
            return self._cache['_partName']
        else:
            pn = None
            for e in self[instrument.Instrument]:
                pn = e.partName
                if pn is None:
                    pn = e.instrumentName
                if pn is not None:
                    break
            self._cache['_partName'] = pn
            return pn

    def _setPartName(self, newName):
        self._partName = newName

    partName = property(_getPartName, _setPartName, doc='''
        Gets or sets a string representing the name of this part
        as a whole (not counting instrument changes, etc.).

        It can be set explicitly (or set on parsing) or it
        can take its name from the first :class:`~music21.instrument.Instrument` object
        encountered in the stream (or within a substream),
        first checking its .partName, then checking its .instrumentName

        Can also return None.

        >>> p = stream.Part()
        >>> p.partName is None
        True
        >>> cl = instrument.Clarinet()
        >>> p.insert(0, cl)
        >>> p.partName
        'Clarinet'
        >>> p.remove(cl)
        >>> p.partName is None
        True
        >>> p.insert(0, instrument.Flute())
        >>> p.partName
        'Flute'
        >>> p.partName = 'Reed 1'
        >>> p.partName
        'Reed 1'

        Note that changing an instrument's .partName or .instrumentName while it
        is already in the Stream will not automatically update this unless
        .coreElementsChanged() is called or this Stream's elements are otherwise altered.
        This is because the value is cached so that O(n) searches through the Stream
        do not need to be done every time.
    ''')

    def _getPartAbbreviation(self):
        if self._partAbbreviation is not None:
            return self._partAbbreviation
        elif '_partAbbreviation' in self._cache:
            return self._cache['_partAbbreviation']
        else:
            pn = None
            for e in self[instrument.Instrument]:
                pn = e.partAbbreviation
                if pn is None:
                    pn = e.instrumentAbbreviation
                if pn is not None:
                    break
            self._cache['_partAbbreviation'] = pn
            return pn

    def _setPartAbbreviation(self, newName):
        self._partAbbreviation = newName

    partAbbreviation = property(_getPartAbbreviation, _setPartAbbreviation, doc='''
        Gets or sets a string representing the abbreviated name of this part
        as a whole (not counting instrument changes, etc.).

        It can be set explicitly (or set on parsing) or it
        can take its name from the first :class:`~music21.instrument.Instrument` object
        encountered in the stream (or within a substream),
        first checking its .partAbbreviation, then checking its .instrumentAbbreviation

        Can also return None.

        >>> p = stream.Part()
        >>> p.partAbbreviation is None
        True
        >>> cl = instrument.Clarinet()
        >>> p.insert(0, cl)
        >>> p.partAbbreviation
        'Cl'
        >>> p.remove(cl)
        >>> p.partAbbreviation is None
        True
        >>> p.insert(0, instrument.Flute())
        >>> p.partAbbreviation
        'Fl'
        >>> p.partAbbreviation = 'Rd 1'
        >>> p.partAbbreviation
        'Rd 1'

        Note that changing an instrument's .partAbbreviation or .instrumentAbbreviation while it
        is already in the Stream will not automatically update this unless
        .coreElementsChanged() is called or this Stream's elements are otherwise altered.
        This is because the value is cached so that O(n) searches through the Stream
        do not need to be done every time.
    ''')

    def makeAccidentals(
        self,
        *,
        alteredPitches=None,
        cautionaryPitchClass=True,
        cautionaryAll=False,
        inPlace=False,
        overrideStatus=False,
        cautionaryNotImmediateRepeat=True,
        tiePitchSet=None,
    ):
        '''
        This overridden method of Stream.makeAccidentals
        walks measures to arrive at desired values for keyword arguments
        `tiePitchSet` and `pitchPastMeasure` when calling `makeAccidentals()`
        on each Measure.

        1. Ties across barlines are detected so that accidentals are not
        unnecessarily reiterated. (`tiePitchSet`)

        2. Pitches appearing on the same step in an immediately preceding measure,
        if foreign to the key signature of that previous measure,
        are printed with cautionary accidentals in the subsequent measure.
        (`pitchPastMeasure`)

        Most of the logic has been factored out to
        :meth:`~music21.stream.makeNotation.makeAccidentalsInMeasureStream`,
        which is called after managing the `inPlace` keyword and finding
        measures to iterate.

        * Changed in v7: `inPlace` defaults False
        '''
        if not inPlace:  # make a copy
            returnObj = self.coreCopyAsDerivation('makeAccidentals')
        else:
            returnObj = self
        # process make accidentals for each measure
        # Use late import to avoid circular dependency with Measure
        from music21.stream.measure import Measure
        measureStream = returnObj.getElementsByClass(Measure)
        makeNotation.makeAccidentalsInMeasureStream(
            measureStream,
            alteredPitches=alteredPitches,
            cautionaryPitchClass=cautionaryPitchClass,
            cautionaryAll=cautionaryAll,
            overrideStatus=overrideStatus,
            cautionaryNotImmediateRepeat=cautionaryNotImmediateRepeat,
            tiePitchSet=tiePitchSet,
        )
        if not inPlace:
            return returnObj
        else:  # in place
            return None

    def mergeAttributes(self, other):
        '''
        Merge relevant attributes from the Other part
        into this one. Key attributes of difference: partName and partAbbreviation.

        TODO: doc test
        '''
        super().mergeAttributes(other)

        for attr in ('_partName', '_partAbbreviation'):
            if hasattr(other, attr):
                setattr(self, attr, getattr(other, attr))


class PartStaff(Part):
    '''
    A Part subclass for designating music that is
    represented on a single staff but may only be one
    of many staves for a single part.
    '''


# class Performer(Stream):
#     '''
#     A Stream subclass for designating music to be performed by a
#     single Performer.  Should only be used when a single performer
#     performs on multiple parts.  E.g. Bass Drum and Triangle on separate
#     staves performed by one player.
#
#     a Part + changes of Instrument is fine for designating most cases
#     where a player changes instrument in a piece.  A part plus staves
#     with individual instrument changes could also be a way of designating
#     music that is performed by a single performer (see, for instance
#     the Piano doubling Celesta part in Lukas Foss's Time Cycle).  The
#     Performer Stream-subclass could be useful for analyses of, for instance,
#     how 5 percussionists chose to play a piece originally designated for 4
#     (or 6) percussionists in the score.
#     '''
#     # NOTE: not yet implemented
#     pass


class System(Stream):
    '''
    Totally optional and used only in OMR and Capella: a designation that all the
    music in this Stream belongs in a single system.

    The system object has two attributes, systemNumber (which number is it)
    and systemNumbering which says at what point the numbering of
    systems resets.  It can be either "Score" (default), "Opus", or "Page".
    '''
    systemNumber = 0
    systemNumbering = 'Score'  # or Page; when do system numbers reset?

    # define order for presenting names in documentation; use strings
    _DOC_ORDER = ['Part', 'PartStaff', 'System']