# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/measure.py
# Purpose:      Measure class extracted from stream/base.py
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
Measure class for music21 streams.

Extracted from stream/base.py as part of Phase 2 dependency reduction.
'''
from __future__ import annotations

import copy
import typing as t

from music21 import bar
from music21 import common
from music21.common.numberTools import opFrac
from music21.common.types import OffsetQL
from music21 import duration
from music21 import exceptions21
from music21 import meter
from music21 import note

from music21.stream.enums import ShowNumber

if t.TYPE_CHECKING:
    from music21.musicxml import m21ToXml
    from music21 import converter
    from music21 import musicxml
    
from music21.stream.enums import RecursionType
from music21.stream import makeNotation

# PHASE 2 NOTE: This creates a circular import (measure.py -> base.py -> measure.py)
# This will be resolved in Phase 3 through dependency injection/factory patterns
# For now, we accept this circular import to maintain functionality
from music21.stream.base import Stream


class Measure(Stream):
    '''
    A representation of a Measure organized as a Stream.

    All properties of a Measure that are Music21 objects are found as part of
    the Stream's elements.

    Measure number can be explicitly set with the `number` keyword:

    >>> m4 = stream.Measure(number=4)
    >>> m4
    <music21.stream.Measure 4 offset=0.0>
    >>> m4.number
    4

    If passed a single integer as an argument, assumes that this int
    is the measure number.

    >>> m5 = stream.Measure(5)
    >>> m5
    <music21.stream.Measure 5 offset=0.0>

    Number can also be a string if there is a suffix:

    >>> m4 = stream.Measure(number='4a')
    >>> m4
    <music21.stream.Measure 4a offset=0.0>
    >>> m4.numberSuffix
    'a'

    Though they have all the features of general streams,
    Measures have specific attributes that allow for setting their number
    and numberSuffix, keep track of whether they have a different clef or
    key or timeSignature than previous measures, allow for padding (and pickups),
    and can be found as a "measure slice" within a score and parts.
    '''
    recursionType = RecursionType.ELEMENTS_FIRST
    isMeasure = True

    # define order for presenting names in documentation; use strings
    _DOC_ORDER = ['Measure']
    # documentation for all attributes (not properties or methods)
    _DOC_ATTR: dict[str, str] = {
        'timeSignatureIsNew': '''
            Boolean describing if the TimeSignature
            is different than the previous Measure.''',
        'clefIsNew': 'Boolean describing if the Clef is different than the previous Measure.',
        'keyIsNew': 'Boolean describing if KeySignature is different than the previous Measure.',
        'number': '''
            A number representing the displayed or shown
            Measure number as presented in a written Score.''',
        'numberSuffix': '''
            If a Measure number has a string annotation, such as "a" or similar,
            this string is stored here. Note that in MusicXML, such
            suffixes often appear as
            prefixes to measure numbers.  In music21 (like most measure
            numbering systems), these
            numbers appear as suffixes.''',
        'showNumber': '''
            Enum describing if the measure number should be displayed.''',
        'layoutWidth': '''
            A suggestion for layout width, though most rendering systems do not support
            this designation. Use :class:`~music21.layout.SystemLayout`
            objects instead.''',
        'paddingLeft': '''
            defines empty space at the front of the measure for purposes of determining
            beat, etc for pickup/anacrusis bars.  In 4/4, a
            measure with a one-beat pickup
            note will have a `paddingLeft` of 3.0.
            (The name comes from the CSS graphical term
            for the amount of padding on the left side of a region.)''',
        'paddingRight': '''
            defines empty space at the end of the measure for purposes of determining
            whether or not a measure is filled.
            In 4/4, a piece beginning a one-beat pickup
            note will often have a final measure of three beats, instead of four.
            The final
            measure should have a `paddingRight` of 1.0.
            (The name comes from the CSS graphical term
            for the amount of padding on the right side of a region.)''',
    }

    def __init__(self, *args, number: int|str = 0, **keywords):
        if len(args) == 1 and isinstance(args[0], int) and number == 0:
            number = args[0]
            args = ()

        super().__init__(*args, **keywords)

        # clef and timeSignature is defined as a property below
        self.timeSignatureIsNew = False
        self.clefIsNew = False
        self.keyIsNew = False

        self.filled = False

        # padding: defining a context for offsets contained within this Measure
        # padding defines dead regions of offsets into the measure
        # the paddingLeft is used by TimeSignature objects to determine beat
        # position; paddingRight defines a QL from the end of the time signature
        # to the last valid offset
        # paddingLeft is used to define pickup/anacrusis bars
        self.paddingLeft: OffsetQL = 0.0
        self.paddingRight: OffsetQL = 0.0

        self.numberSuffix = None  # for measure 14a would be 'a'
        if isinstance(number, str):
            realNum, suffix = common.getNumFromStr(number)
            self.number = int(realNum)
            if suffix:
                self.numberSuffix = suffix
        else:
            self.number = number
        self.showNumber = ShowNumber.DEFAULT
        # we can request layout width, using the same units used
        # in layout.py for systems; most musicxml readers do not support this
        # on input
        self.layoutWidth = None

    def measureNumberWithSuffix(self):
        '''
        Return the measure `.number` with the `.numberSuffix` as a string.

        >>> m = stream.Measure()
        >>> m.number = 4
        >>> m.numberSuffix = 'A'
        >>> m.measureNumberWithSuffix()
        '4A'

        Test that it works as musicxml

        >>> xml = musicxml.m21ToXml.GeneralObjectExporter().parse(m)
        >>> print(xml.decode('utf-8'))
        <?xml version="1.0"...?>
        ...
        <part id="...">
            <!--========================= Measure 4 ==========================-->
            <measure implicit="no" number="4A">
        ...

        Test round tripping:

        >>> s2 = converter.parseData(xml)
        >>> print(s2[stream.Measure].first().measureNumberWithSuffix())
        4A

        Note that we use print here because in parsing the data will become a unicode string.
        '''
        if self.numberSuffix:
            return str(self.number) + self.numberSuffix
        else:
            return str(self.number)

    def _reprInternal(self):
        return self.measureNumberWithSuffix() + f' offset={self.offset}'

    # -------------------------------------------------------------------------
    def mergeAttributes(self, other):
        '''
        Given another Measure, configure all non-element attributes of this
        Measure with the attributes of the other Measure. No elements
        will be changed or copied.

        This method is necessary because Measures, unlike some Streams,
        have attributes independent of any stored elements.

        Overrides base.Music21Object.mergeAttributes

        >>> m1 = stream.Measure()
        >>> m1.id = 'MyMeasure'
        >>> m1.clefIsNew = True
        >>> m1.number = 2
        >>> m1.numberSuffix = 'b'
        >>> m1.layoutWidth = 200

        >>> m2 = stream.Measure()
        >>> m2.mergeAttributes(m1)
        >>> m2.layoutWidth
        200
        >>> m2.id
        'MyMeasure'
        >>> m2
        <music21.stream.Measure 2b offset=0.0>

        Try with not another Measure:

        >>> m3 = stream.Stream()
        >>> m3.id = 'hello'
        >>> m2.mergeAttributes(m3)
        >>> m2.id
        'hello'
        >>> m2.layoutWidth
        200
        '''
        # calling bass class sets id, groups
        super().mergeAttributes(other)

        for attr in ('timeSignatureIsNew', 'clefIsNew', 'keyIsNew', 'filled',
                     'paddingLeft', 'paddingRight', 'number', 'numberSuffix', 'layoutWidth'):
            if hasattr(other, attr):
                setattr(self, attr, getattr(other, attr))

    # -------------------------------------------------------------------------
    def makeNotation(self,
                     inPlace=False,
                     **subroutineKeywords):
        # noinspection PyShadowingNames
        '''
        This method calls a sequence of Stream methods on this
        :class:`~music21.stream.Measure` to prepare notation.

        If `inPlace` is True, this is done in-place; if
        `inPlace` is False, this returns a modified deep copy.

        >>> m = stream.Measure()
        >>> n1 = note.Note('g#')
        >>> n2 = note.Note('g')
        >>> m.append([n1, n2])
        >>> m.makeNotation(inPlace=True)
        >>> m.notes[1].pitch.accidental
        <music21.pitch.Accidental natural>
        '''
        # environLocal.printDebug(['Measure.makeNotation'])
        # TODO: this probably needs to look to see what processes need to be done;
        # for example, existing beaming may be destroyed.

        # do this before deepcopy

        # assuming we are not trying to get context of previous measure
        if not inPlace:  # make a copy
            m = copy.deepcopy(self)
        else:
            m = self

        srkCopy = subroutineKeywords.copy()

        for illegalKey in ('meterStream', 'refStreamOrTimeRange', 'bestClef'):
            if illegalKey in srkCopy:
                del srkCopy[illegalKey]

        m.makeAccidentals(searchKeySignatureByContext=True, inPlace=True, **srkCopy)
        # makeTies is for cross-bar associations, and cannot be used
        # at just the measure level
        # m.makeTies(meterStream, inPlace=True)

        # must have a time signature before calling make beams
        if m.timeSignature is None:
            # get a time signature if not defined, searching the context if
            # necessary
            contextMeters = m.getTimeSignatures(searchContext=True,
                                                returnDefault=False)
            defaultMeters = m.getTimeSignatures(searchContext=False,
                                                returnDefault=True)
            if contextMeters:
                ts = contextMeters[0]
            else:
                try:
                    ts = self.bestTimeSignature()
                except (exceptions21.StreamException, meter.MeterException):
                    # there must be one here
                    ts = defaultMeters[0]
            m.timeSignature = ts  # a Stream; get the first element

        makeNotation.splitElementsToCompleteTuplets(m, recurse=True, addTies=True)
        makeNotation.consolidateCompletedTuplets(m, recurse=True, onlyIfTied=True)

        m.makeBeams(inPlace=True)
        for m_or_v in [m, *m.voices]:
            makeNotation.makeTupletBrackets(m_or_v, inPlace=True)

        if not inPlace:
            return m
        else:
            return None

    def barDurationProportion(self, barDuration=None):
        '''
        Return a floating point value greater than 0 showing the proportion
        of the bar duration that is filled based on the highest time of
        all elements. 0.0 is empty, 1.0 is filled; 1.5 specifies of an
        overflow of half.

        Bar duration refers to the duration of the Measure as suggested by
        the `TimeSignature`. This value cannot be determined without a `TimeSignature`.

        An already-obtained Duration object can be supplied with the `barDuration`
        optional argument.

        >>> import copy
        >>> m = stream.Measure()
        >>> m.timeSignature = meter.TimeSignature('3/4')
        >>> n = note.Note()
        >>> n.quarterLength = 1
        >>> m.append(copy.deepcopy(n))
        >>> m.barDurationProportion()
        Fraction(1, 3)
        >>> m.append(copy.deepcopy(n))
        >>> m.barDurationProportion()
        Fraction(2, 3)
        >>> m.append(copy.deepcopy(n))
        >>> m.barDurationProportion()
        1.0
        >>> m.append(copy.deepcopy(n))
        >>> m.barDurationProportion()
        Fraction(4, 3)
        '''
        # passing a barDuration may save time in the lookup process
        if barDuration is None:
            barDuration = self.barDuration
        return opFrac(self.highestTime / barDuration.quarterLength)

    def padAsAnacrusis(self, useGaps=True, useInitialRests=False):
        '''
        Given an incompletely filled Measure, adjust the `paddingLeft` value to
        represent contained events as shifted to fill the right-most duration of the bar.

        Calling this method will overwrite any previously set `paddingLeft` value,
        based on the current TimeSignature-derived `barDuration` attribute.

        >>> m = stream.Measure()
        >>> m.timeSignature = meter.TimeSignature('3/4')
        >>> n = note.Note()
        >>> n.quarterLength = 1.0
        >>> m.append(n)
        >>> m.padAsAnacrusis()
        >>> m.paddingLeft
        2.0

        >>> m.timeSignature = meter.TimeSignature('5/4')
        >>> m.padAsAnacrusis()
        >>> m.paddingLeft
        4.0

        Empty space at the beginning of the measure will not be taken in account:

        >>> m = stream.Measure()
        >>> m.timeSignature = meter.TimeSignature('3/4')
        >>> n = note.Note(type='quarter')
        >>> m.insert(2.0, n)
        >>> m.padAsAnacrusis()
        >>> m.paddingLeft
        0.0

        If useInitialRests is True, then rests at the beginning of the measure
        are removed.  This is especially useful for formats that don't give a
        way to specify a pickup measure (such as tinynotation) or software
        that generates incorrect opening measures.  So, to fix the problem before,
        put a rest at the beginning and call useInitialRests:

        >>> r = note.Rest(type='half')
        >>> m.insert(0, r)
        >>> m.padAsAnacrusis(useInitialRests=True)
        >>> m.paddingLeft
        2.0

        And the rest is gone!

        >>> m.show('text')
        {0.0} <music21.meter.TimeSignature 3/4>
        {0.0} <music21.note.Note C>

        Only initial rests count for useInitialRests:

        >>> m = stream.Measure()
        >>> m.timeSignature = meter.TimeSignature('3/4')
        >>> m.append(note.Rest(type='eighth'))
        >>> m.append(note.Rest(type='eighth'))
        >>> m.append(note.Note('C4', type='quarter'))
        >>> m.append(note.Rest(type='eighth'))
        >>> m.append(note.Note('D4', type='eighth'))
        >>> m.show('text')
        {0.0} <music21.meter.TimeSignature 3/4>
        {0.0} <music21.note.Rest eighth>
        {0.5} <music21.note.Rest eighth>
        {1.0} <music21.note.Note C>
        {2.0} <music21.note.Rest eighth>
        {2.5} <music21.note.Note D>
        >>> m.padAsAnacrusis(useInitialRests=True)
        >>> m.paddingLeft
        1.0
        >>> m.show('text')
        {0.0} <music21.meter.TimeSignature 3/4>
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Rest eighth>
        {1.5} <music21.note.Note D>
        '''
        if useInitialRests:
            removeList = []
            for gn in self.notesAndRests:
                if not isinstance(gn, note.Rest):
                    break
                removeList.append(gn)
            if removeList:
                self.remove(removeList, shiftOffsets=True)

        # note: may need to set paddingLeft to 0 before examining

        # bar duration is that suggested by time signature; it
        # may not be the same as Stream duration, which is based on contents
        barDuration = self.barDuration
        proportion = self.barDurationProportion(barDuration=barDuration)
        if proportion < 1:
            # get 1 complement
            proportionShift = 1 - proportion
            self.paddingLeft = opFrac(barDuration.quarterLength * proportionShift)

            # shift = barDuration.quarterLength * proportionShift
            # environLocal.printDebug(['got anacrusis shift:', shift,
            #                    barDuration.quarterLength, proportion])
            # this will shift all elements
            # self.shiftElements(shift, classFilterList=(note.GeneralNote,))
        else:
            pass
            # environLocal.printDebug(['padAsAnacrusis() called; however,
            # no anacrusis shift necessary:', barDuration.quarterLength, proportion])

    # --------------------------------------------------------------------------
    @property
    def barDuration(self):
        '''
        Return the bar duration, or the Duration specified by the TimeSignature,
        regardless of what elements are found in this Measure or the highest time.
        TimeSignature is found first within the Measure,
        or within a context based search.

        To get the duration of the total length of elements, just use the
        `.duration` property.

        Here we create a 3/4 measure and "over-stuff" it with five quarter notes.
        `barDuration` still gives a duration of 3.0, or a dotted quarter note,
        while `.duration` gives a whole note tied to a quarter.

        >>> m = stream.Measure()
        >>> m.timeSignature = meter.TimeSignature('3/4')
        >>> m.barDuration
        <music21.duration.Duration 3.0>
        >>> m.repeatAppend(note.Note(type='quarter'), 5)
        >>> m.barDuration
        <music21.duration.Duration 3.0>
        >>> m.duration
        <music21.duration.Duration 5.0>

        The objects returned by `barDuration` and `duration` are
        full :class:`~music21.duration.Duration`
        objects, will all the relevant properties:

        >>> m.barDuration.fullName
        'Dotted Half'
        >>> m.duration.fullName
        'Whole tied to Quarter (5 total QL)'
        '''
        # TODO: it is possible that this should be cached or exposed as a method
        #     as this search may take some time.
        if self.timeSignature is not None:
            ts = self.timeSignature
        else:  # do a context-based search
            tsStream = self.getTimeSignatures(searchContext=True,
                                              returnDefault=False,
                                              sortByCreationTime=True)
            if not tsStream:
                try:
                    ts = self.bestTimeSignature()
                except exceptions21.Music21Exception:
                    return duration.Duration(self.highestTime)

                # raise StreamException(
                #   'cannot determine bar duration without a time signature reference')
            else:  # it is the first found
                ts = tsStream[0]
        return ts.barDuration

    # --------------------------------------------------------------------------
    # Music21Objects are stored in the Stream's elements list
    # properties are provided to store and access these attribute

    def bestTimeSignature(self):
        '''
        Given a Measure with elements in it,
        get a TimeSignature that contains all elements.
        Calls meter.bestTimeSignature(self)

        Note: this does not yet accommodate triplets.

        We create a simple stream that should be in 3/4

        >>> s = converter.parse('C4 D4 E8 F8', format='tinyNotation', makeNotation=False)
        >>> m = stream.Measure()
        >>> for el in s:
        ...     m.insert(el.offset, el)

        But there is no TimeSignature!

        >>> m.show('text')
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Note D>
        {2.0} <music21.note.Note E>
        {2.5} <music21.note.Note F>

        So, we get the best Time Signature and put it in the Stream.

        >>> ts = m.bestTimeSignature()
        >>> ts
        <music21.meter.TimeSignature 3/4>
        >>> m.timeSignature = ts
        >>> m.show('text')
        {0.0} <music21.meter.TimeSignature 3/4>
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Note D>
        {2.0} <music21.note.Note E>
        {2.5} <music21.note.Note F>

        For further details about complex time signatures, etc.
        see `meter.bestTimeSignature()`

        '''
        return meter.bestTimeSignature(self)

    def _getLeftBarline(self):
        barList = []
        # directly access _elements, as do not want to get any bars
        # in _endElements
        for e in self._elements:
            if isinstance(e, bar.Barline):  # take the first
                if self.elementOffset(e) == 0.0:
                    barList.append(e)
                    break
        if not barList:
            return None
        else:
            return barList[0]

    def _setLeftBarline(self, barlineObj):
        insert = True
        if isinstance(barlineObj, str):
            barlineObj = bar.Barline(barlineObj)
            barlineObj.location = 'left'
        elif barlineObj is None:  # assume removal
            insert = False
        else:  # assume a Barline object
            barlineObj.location = 'left'

        oldLeftBarline = self._getLeftBarline()
        if oldLeftBarline is not None:
            # environLocal.printDebug(['_setLeftBarline()', 'removing left barline'])
            junk = self.pop(self.index(oldLeftBarline))
        if insert:
            # environLocal.printDebug(['_setLeftBarline()',
            # 'inserting new left barline', barlineObj])
            self.insert(0, barlineObj)

    leftBarline = property(_getLeftBarline,
                           _setLeftBarline,
                           doc='''
        Get or set the left barline, or the Barline object
        found at offset zero of the Measure.  Can be set either with a string
        representing barline style or a bar.Barline() object or None.
        Note that not all bars have
        barline objects here -- regular barlines don't need them.
        ''')

    def _getRightBarline(self):
        # TODO: Move to Stream or make setting .rightBarline, etc. on Stream raise an exception
        # look on _endElements
        barList = []
        for e in self._endElements:
            if isinstance(e, bar.Barline):  # take the first
                barList.append(e)
                break
        # barList = self.getElementsByClass(bar.Barline)
        if not barList:  # do this before searching for barQL
            return None
        else:
            return barList[0]

    def _setRightBarline(self, barlineObj):
        insert = True
        if isinstance(barlineObj, str):
            barlineObj = bar.Barline(barlineObj)
            barlineObj.location = 'right'
        elif barlineObj is None:  # assume removal
            insert = False
        else:  # assume a Barline object
            barlineObj.location = 'right'

        # if a repeat, setup direction if not assigned
        if barlineObj is not None and isinstance(barlineObj, bar.Repeat):
            # environLocal.printDebug(['got barline obj w/ direction', barlineObj.direction])
            if barlineObj.direction in ['start', None]:
                barlineObj.direction = 'end'
        oldRightBarline = self._getRightBarline()

        if oldRightBarline is not None:
            # environLocal.printDebug(['_setRightBarline()', 'removing right barline'])
            junk = self.pop(self.index(oldRightBarline))
        # insert into _endElements
        if insert:
            self.storeAtEnd(barlineObj)

        # environLocal.printDebug(['post _setRightBarline', barlineObj,
        #    'len of elements highest', len(self._endElements)])

    rightBarline = property(_getRightBarline,
                            _setRightBarline,
                            doc='''
        Get or set the right barline, or the Barline object
        found at the offset equal to the bar duration.

        >>> b = bar.Barline('final')
        >>> m = stream.Measure()
        >>> print(m.rightBarline)
        None
        >>> m.rightBarline = b
        >>> m.rightBarline.type
        'final'

        A string can also be used instead:

        >>> c = converter.parse('tinynotation: 3/8 C8 D E F G A B4.')
        >>> c.measure(1).rightBarline = 'light-light'
        >>> c.measure(3).rightBarline = 'light-heavy'
        >>> #_DOCS_SHOW c.show()

        .. image:: images/stream_barline_demo.*
            :width: 211

        OMIT_FROM_DOCS

        .measure currently isn't the same as the
        original measure.

        ''')