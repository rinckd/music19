# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         spanner.py
# Purpose:      The Spanner base-class and subclasses
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2010-2012 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
A spanner is a music21 object that represents a connection usually between
two or more music21 objects that might live in different streams but need
some sort of connection between them.  A slur is one type of spanner -- it might
connect notes in different Measure objects or even between different parts.

This package defines some of the most common spanners.  Other spanners
can be found in modules such as :ref:`moduleDynamics` (for things such as crescendos).
'''
from __future__ import annotations

from collections.abc import Sequence, Iterable
import copy
import typing as t
from music21 import base
from music21 import common
from music21.common.types import OffsetQL
from music21 import defaults
from music21 import environment
from music21 import exceptions21
from music21 import prebase
from music21 import sites
from music21 import style

environLocal = environment.Environment('spanner')

# ------------------------------------------------------------------------------
class SpannerException(exceptions21.Music21Exception):
    pass

class SpannerBundleException(exceptions21.Music21Exception):
    pass

# ------------------------------------------------------------------------------
class Spanner(base.Music21Object):
    # suppress this inspection because it fails when class is defined in
    # the __doc__
    # noinspection PyTypeChecker
    '''
    Spanner objects live on Streams in the same manner as other Music21Objects,
    but represent and store connections between one or more other Music21Objects.

    Commonly used Spanner subclasses include the :class:`~music21.spanner.Slur`,
    :class:`~music21.spanner.RepeatBracket`, :class:`~music21.spanner.Crescendo`,
    and :class:`~music21.spanner.Diminuendo`
    objects.

    In some cases you will want to subclass Spanner
    for specific purposes.

    In the first demo, we create
    a spanner to represent a written-out accelerando, such
    as Elliott Carter uses in his second string quartet (he marks them
    with an arrow).

    >>> class CarterAccelerandoSign(spanner.Spanner):
    ...    pass
    >>> n1 = note.Note('C4')
    >>> n2 = note.Note('D4')
    >>> n3 = note.Note('E4')
    >>> sp1 = CarterAccelerandoSign(n1, n2, n3)  # or as a list: [n1, n2, n3]
    >>> sp1.getSpannedElements()
    [<music21.note.Note C>, <music21.note.Note D>, <music21.note.Note E>]

    We can iterate over a spanner to get the contexts:

    >>> print(' '.join([repr(n) for n in sp1]))
    <music21.note.Note C> <music21.note.Note D> <music21.note.Note E>

    Now we put the notes and the spanner into a Stream object.  Note that
    the convention is to put the spanner at the beginning of the innermost
    Stream that contains all the Spanners:

    >>> s = stream.Stream()
    >>> s.append([n1, n2, n3])
    >>> s.insert(0, sp1)

    Now we can get at the spanner in one of three ways.

    (1) it is just a normal element in the stream:

    >>> for e in s:
    ...    print(e)
    <music21.note.Note C>
    <music21.CarterAccelerandoSign <music21.note.Note C><music21.note.Note D><music21.note.Note E>>
    <music21.note.Note D>
    <music21.note.Note E>

    (2) we can get a stream of spanners (equiv. to getElementsByClass(spanner.Spanner))
        by calling the .spanner property on the stream.

    >>> spannerCollection = s.spanners  # a stream object
    >>> for thisSpanner in spannerCollection:
    ...     print(thisSpanner)
    <music21.CarterAccelerandoSign <music21.note.Note C><music21.note.Note D><music21.note.Note E>>

    (3) we can get the spanner by looking at the list getSpannerSites() on
    any object that has a spanner:

    >>> n2.getSpannerSites()
    [<music21.CarterAccelerandoSign
            <music21.note.Note C><music21.note.Note D><music21.note.Note E>>]

    In this example we will slur a few notes and then iterate over the stream to
    see which are slurred:

    >>> n1 = note.Note('C4')
    >>> n2 = note.Note('D4')
    >>> n3 = note.Note('E4')
    >>> n4 = note.Note('F4')
    >>> n5 = note.Note('G4')
    >>> n6 = note.Note('A4')

    Create a slur over the second and third notes at instantiation:

    >>> slur1 = spanner.Slur([n2, n3])

    Slur the fifth and the sixth notes by adding them to an existing slur:

    >>> slur2 = spanner.Slur()
    >>> slur2.addSpannedElements([n5, n6])

    Now add them all to a stream:

    >>> part1 = stream.Part()
    >>> part1.append([n1, n2, n3, n4, n5, n6])
    >>> part1.insert(0, slur1)
    >>> part1.insert(0, slur2)

    Say we wanted to know which notes in a piece started a
    slur, here's how we could do it:

    >>> for n in part1.notes:
    ...    ss = n.getSpannerSites()
    ...    for thisSpanner in ss:
    ...       if 'Slur' in thisSpanner.classes:
    ...            if thisSpanner.isFirst(n):
    ...                print(n.nameWithOctave)
    D4
    G4

    Alternatively, you could iterate over the spanners
    of part1 and get their first elements:

    >>> for thisSpanner in part1.spanners:
    ...     firstNote = thisSpanner.getSpannedElements()[0]
    ...     print(firstNote.nameWithOctave)
    D4
    G4

    The second method is shorter, but the first is likely to
    be useful in cases where you are doing other things to
    each note object along the way.

    Oh, and of course, slurs do print properly in musicxml:

    >>> #_DOCS_SHOW part1.show()

    .. image:: images/slur1_example.*
        :width: 400

    (the Carter example would not print an arrow since that
    element has no corresponding musicxml representation).

    *Implementation notes:*

    The elements that are included in a spanner are stored in a
    Stream subclass called :class:`~music21.stream.SpannerStorage`
    found as the `.spannerStorage` attribute.  That Stream has an
    attribute called `client` which links to the original spanner.
    Thus, `spannerStorage` is smart enough to know where it's stored, but
    it makes deleting/garbage-collecting a spanner a tricky operation:

    Ex. Prove that the spannedElement Stream is linked to container via
    `client`:

    >>> sp1.spannerStorage.client is sp1
    True

    Spanners have a `.completeStatus` attribute which can be used to find out if
    all spanned elements have been added yet. It's up to the processing agent to
    set this, but it could be useful in deciding where to append a spanner.

    >>> sp1.completeStatus
    False

    When we're done adding elements:

    >>> sp1.completeStatus = True
    '''

    equalityAttributes = ('spannerStorage',)

    def __init__(self,
                 *spannedElements: t.Union[base.Music21Object,
                                           Sequence[base.Music21Object]],
                 **keywords):
        super().__init__(**keywords)

        # store a Stream inside of Spanner
        from music21 import stream

        # create a stream subclass, spanner storage; pass a reference
        # to this spanner for getting this spanner from the SpannerStorage
        # directly

        # TODO: Move here! along with VariantStorage to variant.
        self.spannerStorage = stream.SpannerStorage(client=self)

        # we do not want to auto sort based on offset or class, as
        # both are meaningless inside this Stream (and only have meaning
        # in Stream external to this)
        self.spannerStorage.autoSort = False

        # add arguments as a list or single item
        proc: list[base.Music21Object] = []
        for spannedElement in spannedElements:
            if isinstance(spannedElement, base.Music21Object):
                proc.append(spannedElement)
            elif spannedElement is not None:
                proc += spannedElement
        self.addSpannedElements(proc)

        # parameters that spanners need in loading and processing
        # local id is the id for the local area; used by musicxml
        self.idLocal: str|None = None
        # after all spannedElements have been gathered, setting complete
        # will mark that all parts have been gathered.
        self.completeStatus: bool = False

        # data for fill:

        # fillElementTypes is a list of types of object to search for.  This
        # can be set to something different in the __init__ of a particular
        # type of Spanner.
        # Set here to the empty list, so that by default, fill() does nothing.
        self.fillElementTypes: list[t.Type] = []

        # After a fill operation, filledStatus will be set to True.
        # Parsers and other clients can also set this to False or
        # True to mark whether or not a fill operation is needed
        # (False means fill is needed, True means fill is not
        # needed, presumably because the fill was done by hand).
        # Initialized to 'unknown'.
        self.filledStatus: bool|t.Literal['unknown'] = 'unknown'

    def _reprInternal(self):
        msg = []
        for c in self.getSpannedElements():
            objRef = c
            msg.append(repr(objRef))
        return ''.join(msg)

    def _deepcopySubclassable(self, memo=None, *, ignoreAttributes=None):
        '''
        see __deepcopy__ for tests and docs
        '''
        # NOTE: this is a performance critical operation
        defaultIgnoreSet = {'spannerStorage'}
        if ignoreAttributes is None:
            ignoreAttributes = defaultIgnoreSet
        else:
            ignoreAttributes = ignoreAttributes | defaultIgnoreSet
        new = t.cast(Spanner,
                     super()._deepcopySubclassable(memo, ignoreAttributes=ignoreAttributes))

        # we are temporarily putting in the PREVIOUS elements, to replace them later
        # with replaceSpannedElement()
        new.spannerStorage = type(self.spannerStorage)(client=new)
        for c in self.spannerStorage._elements:
            new.spannerStorage.coreAppend(c)
        # updateIsSorted too?
        new.spannerStorage.coreElementsChanged(updateIsFlat=False)
        return new

    def __deepcopy__(self, memo=None):
        '''
        This produces a new, independent object containing references
        to the same spannedElements.
        SpannedElements linked in this Spanner must be manually re-set,
        likely using the
        replaceSpannedElement() method.

        Notice that we put the references to the same object so that
        later we can replace them;
        otherwise in a deepcopy of a stream, the notes in the stream
        will become independent of the notes in the spanner.

        >>> import copy
        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> c1 = clef.AltoClef()

        >>> sp1 = spanner.Spanner(n1, n2, c1)
        >>> sp2 = copy.deepcopy(sp1)
        >>> len(sp2.spannerStorage)
        3
        >>> sp1 is sp2
        False
        >>> sp2[0] is sp1[0]
        True
        >>> sp2[2] is sp1[2]
        True
        >>> sp1[0] is n1
        True
        >>> sp2[0] is n1
        True
        '''
        return self._deepcopySubclassable(memo)

    # --------------------------------------------------------------------------
    # as spannedElements is private Stream, unwrap/wrap methods need to override
    # Music21Object to get at these objects
    # this is the same as with Variants

    def purgeOrphans(self, excludeStorageStreams=True):
        if self.spannerStorage:
            # might not be defined in the middle of a deepcopy.
            self.spannerStorage.purgeOrphans(excludeStorageStreams)
        base.Music21Object.purgeOrphans(self, excludeStorageStreams)

    def purgeLocations(self, rescanIsDead=False):
        # must override Music21Object to purge locations from the contained
        # Stream
        # base method to perform purge on the Stream
        if self.spannerStorage:
            # might not be defined in the middle of a deepcopy.
            self.spannerStorage.purgeLocations(rescanIsDead=rescanIsDead)
        base.Music21Object.purgeLocations(self, rescanIsDead=rescanIsDead)

    # --------------------------------------------------------------------------
    def __getitem__(self, key):
        '''

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> c1 = clef.BassClef()
        >>> sl = spanner.Spanner(n1, n2, c1)
        >>> sl[0] == n1
        True
        >>> sl[-1] == c1
        True
        >>> sl[clef.BassClef][0] == c1
        True
        '''
        # delegate to Stream subclass
        return self.spannerStorage.__getitem__(key)

    def __iter__(self):
        return iter(self.spannerStorage)

    def __len__(self):
        # Check _elements to avoid StreamIterator overhead.
        # Safe, because impossible to put spanned elements at end.
        return len(self.spannerStorage._elements)

    def getSpannedElements(self):
        '''
        Return all the elements of `.spannerStorage` for this Spanner
        as a list of Music21Objects.

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements(n1)
        >>> sl.getSpannedElements() == [n1]
        True
        >>> sl.addSpannedElements(n2)
        >>> sl.getSpannedElements() == [n1, n2]
        True
        >>> sl.getSpannedElementIds() == [id(n1), id(n2)]
        True
        >>> c1 = clef.TrebleClef()
        >>> sl.addSpannedElements(c1)
        >>> sl.getSpannedElements() == [n1, n2, c1]  # make sure that not sorting
        True
        '''
        # Check _elements to avoid StreamIterator overhead.
        # Safe, because impossible to put spanned elements at end.
        return list(self.spannerStorage._elements)

    def getSpannedElementsByClass(self, classFilterList):
        '''

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> c1 = clef.AltoClef()
        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements([n1, n2, c1])
        >>> sl.getSpannedElementsByClass('Note') == [n1, n2]
        True
        >>> sl.getSpannedElementsByClass(clef.Clef) == [c1]
        True
        '''
        # returns an iterator
        postStream = self.spannerStorage.getElementsByClass(classFilterList)
        # return raw elements list for speed
        return list(postStream)

    def getSpannedElementIds(self):
        '''
        Return all id() for all stored objects.
        Was performance critical, until most uses removed in v7.
        Used only as a testing tool now.
        Spanner.__contains__() was optimized in 839c7e5.
        '''
        return [id(n) for n in self.spannerStorage._elements]

    def addSpannedElements(
        self,
        spannedElements: t.Union[Sequence[base.Music21Object],
                                 base.Music21Object],
        *otherElements: base.Music21Object,
    ):
        '''
        Associate one or more elements with this Spanner.

        The order in which elements are added is retained and
        may or may not be significant to the spanner.

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> n3 = note.Note('e')
        >>> n4 = note.Note('d-')
        >>> n5 = note.Note('c')

        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements(n1)
        >>> sl.addSpannedElements(n2, n3)
        >>> sl.addSpannedElements([n4, n5])
        >>> sl.getSpannedElementIds() == [id(n) for n in [n1, n2, n3, n4, n5]]
        True
        '''
        # presently, this does not look for redundancies
        # add mypy disables because isListLike() performs type-narrowing
        if not common.isListLike(spannedElements):
            spannedElements = [spannedElements]  # type: ignore[list-item]
        if otherElements:
            # copy
            spannedElements = spannedElements[:]  # type: ignore[index]
            # assume all other arguments are music21 objects
            spannedElements += otherElements  # type: ignore[operator]
        for c in spannedElements:  # type: ignore[union-attr]
            if c is None:
                continue
            if not self.hasSpannedElement(c):  # not already in storage
                self.spannerStorage.coreAppend(c)
            else:
                pass
                # it makes sense to not have multiple copies
                # environLocal.printDebug(['''attempting to add an object (%s) that is
                #    already found in the SpannerStorage stream of spanner %s;
                #    this may not be an error.''' % (c, self)])

        self.spannerStorage.coreElementsChanged()

    def hasSpannedElement(self, spannedElement: base.Music21Object) -> bool:
        '''
        Return True if this Spanner has the spannedElement.

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> span = spanner.Spanner()
        >>> span.addSpannedElements(n1)
        >>> span.hasSpannedElement(n1)
        True
        >>> span.hasSpannedElement(n2)
        False

        Note that a simple `in` does the same thing:

        >>> n1 in span
        True
        >>> n2 in span
        False
        '''
        return spannedElement in self

    def __contains__(self, spannedElement):
        # Cannot check `in` spannerStorage._elements,
        # because it would check __eq__, not identity.
        for x in self.spannerStorage._elements:
            if x is spannedElement:
                return True
        return False

    def replaceSpannedElement(self, old, new) -> None:
        '''
        When copying a Spanner, we need to update the
        spanner with new references for copied  (if the Notes of a
        Slur have been copied, that Slur's Note references need
        references to the new Notes). Given the old spanned element,
        this method will replace the old with the new.

        The `old` parameter can be either an object or object id.

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> c1 = clef.AltoClef()
        >>> c2 = clef.BassClef()
        >>> sl = spanner.Spanner(n1, n2, c1)
        >>> sl.replaceSpannedElement(c1, c2)
        >>> sl[-1] == c2
        True
        '''
        if old is None:
            return None  # do nothing
        if common.isNum(old):
            # this must be id(obj), not obj.id
            e = self.spannerStorage.coreGetElementByMemoryLocation(old)
            # e here is the old element that was spanned by this Spanner

            # environLocal.printDebug(['current Spanner.getSpannedElementIdsIds()',
            #    self.getSpannedElementIds()])
            # environLocal.printDebug(['Spanner.replaceSpannedElement:', 'getElementById result',
            #    e, 'old target', old])
            if e is not None:
                # environLocal.printDebug(['Spanner.replaceSpannedElement:', 'old', e, 'new', new])
                # do not do all Sites: only care about this one
                self.spannerStorage.replace(e, new, allDerived=False)
        else:
            # do not do all Sites: only care about this one
            self.spannerStorage.replace(old, new, allDerived=False)
            # environLocal.printDebug(['Spanner.replaceSpannedElement:', 'old', e, 'new', new])

        # while this Spanner now has proper elements in its spannerStorage Stream,
        # the element replaced likely has a site left-over from its previous Spanner

        # environLocal.printDebug(['replaceSpannedElement()', 'id(old)', id(old),
        #    'id(new)', id(new)])

    def fill(
        self,
        searchStream=None,  # stream.Stream|None, but cannot import stream here
        *,
        includeEndBoundary: bool = False,
        mustFinishInSpan: bool = False,
        mustBeginInSpan: bool = True,
        includeElementsThatEndAtStart: bool = False
    ):
        '''
        Fills in the intermediate elements of a spanner, that are found in searchStream between
        the first element's offset and the last element's offset+duration.  If searchStream
        is None, the first element's activeSite is used.  If the first element's activeSite
        is None, a SpannerException is raised.

        Ottava is an example of a Spanner that can be filled. The Ottava does not need
        to be inserted into the stream in order to be filled.

        >>> m = stream.Measure([note.Note('A'), note.Note('B'), note.Note('C')])
        >>> ott1 = spanner.Ottava(m.notes[0], m.notes[2])
        >>> ott1.fill(m)
        >>> ott1
        <music21.spanner.Ottava 8va transposing<...Note A><...Note B><...Note C>>

        If the searchStream is not passed in, fill still happens in this case, because
        the first note's activeSite is used instead.

        >>> ott2 = spanner.Ottava(m.notes[0], m.notes[2])
        >>> ott2.fill()
        >>> ott2
        <music21.spanner.Ottava 8va transposing<...Note A><...Note B><...Note C>>

        If the searchStream is not passed, and the spanner's first element doesn't have
        an activeSite, a SpannerException is raised.

        >>> ott3 = spanner.Ottava(note.Note('D'), note.Note('E'))
        >>> ott3.fill()
        Traceback (most recent call last):
        music21.spanner.SpannerException: Spanner.fill() requires a searchStream
            or getFirst().activeSite
        '''

        if not self.fillElementTypes:
            # nothing to fill
            return

        if self.filledStatus is True:
            # Don't fill twice.  If client wants a refill they can set filledStatus to False.
            return

        startElement: base.Music21Object|None = self.getFirst()
        if startElement is None:
            # no spanned elements?  Nothing to fill.
            return

        if searchStream is None:
            searchStream = startElement.activeSite
            if searchStream is None:
                raise SpannerException(
                    'Spanner.fill() requires a searchStream or getFirst().activeSite'
                )

        if t.TYPE_CHECKING:
            from music21 import stream
            assert isinstance(searchStream, stream.Stream)

        endElement: base.Music21Object|None = self.getLast()
        if endElement is startElement:
            endElement = None

        if endElement is not None:
            # Start and end elements are different; we can't just append everything, we need
            # to save the end element, remove it, add everything, then add the end element
            # again.  Note that if there are actually more than 2 elements before we start
            # filling, the new intermediate elements will come after the existing ones,
            # regardless of offset.  But first and last will still be the same two elements
            # as before, which is the most important thing.
            self.spannerStorage.remove(endElement)

        try:
            startOffsetInHierarchy: OffsetQL = startElement.getOffsetInHierarchy(searchStream)
        except sites.SitesException:
            # print('start element not in searchStream')
            if endElement is not None:
                self.addSpannedElements(endElement)
            return

        endOffsetInHierarchy: OffsetQL
        if endElement is not None:
            try:
                endOffsetInHierarchy = (
                    endElement.getOffsetInHierarchy(searchStream) + endElement.quarterLength
                )
            except sites.SitesException:
                # print('end element not in searchStream')
                self.addSpannedElements(endElement)
                return
        else:
            endOffsetInHierarchy = (
                startOffsetInHierarchy + startElement.quarterLength
            )

        matchIterator = (searchStream
            .recurse()
            .getElementsByOffsetInHierarchy(
                startOffsetInHierarchy,
                endOffsetInHierarchy,
                includeEndBoundary=includeEndBoundary,
                mustFinishInSpan=mustFinishInSpan,
                mustBeginInSpan=mustBeginInSpan,
                includeElementsThatEndAtStart=includeElementsThatEndAtStart)
            .getElementsByClass(self.fillElementTypes)
        )

        for foundElement in matchIterator:
            if foundElement is startElement:
                # it's already in the spanner, skip it
                continue
            if foundElement is endElement:
                # we'll add it below, skip it
                continue
            self.addSpannedElements(foundElement)

        if endElement is not None:
            # add it back in as the end element
            self.addSpannedElements(endElement)

        self.filledStatus = True

    def isFirst(self, spannedElement):
        '''
        Given a spannedElement, is it first?

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> n3 = note.Note('e')
        >>> n4 = note.Note('c')
        >>> n5 = note.Note('d-')

        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements(n1, n2, n3, n4, n5)
        >>> sl.isFirst(n2)
        False
        >>> sl.isFirst(n1)
        True
        >>> sl.isLast(n1)
        False
        >>> sl.isLast(n5)
        True
        '''
        return self.getFirst() is spannedElement

    def getFirst(self):
        '''
        Get the object of the first spannedElement (or None if it's an empty spanner)

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> n3 = note.Note('e')
        >>> n4 = note.Note('c')
        >>> n5 = note.Note('d-')

        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements(n1, n2, n3, n4, n5)
        >>> sl.getFirst() is n1
        True

        >>> spanner.Slur().getFirst() is None
        True
        '''
        try:
            return self.spannerStorage[0]
        except (IndexError, exceptions21.StreamException):
            return None

    def isLast(self, spannedElement):
        '''
        Given a spannedElement, is it last?  Returns True or False
        '''
        return self.getLast() is spannedElement

    def getLast(self):
        '''
        Get the object of the last spannedElement (or None if it's an empty spanner)

        >>> n1 = note.Note('g')
        >>> n2 = note.Note('f#')
        >>> n3 = note.Note('e')
        >>> n4 = note.Note('c')
        >>> n5 = note.Note('d-')

        >>> sl = spanner.Spanner()
        >>> sl.addSpannedElements(n1, n2, n3, n4, n5)
        >>> sl.getLast() is n5
        True

        >>> spanner.Slur().getLast() is None
        True
        '''
        try:
            return self.spannerStorage[-1]
        except (IndexError, exceptions21.StreamException):
            return None

# ------------------------------------------------------------------------------
class _SpannerRef(t.TypedDict):
    # noinspection PyTypedDict
    spanner: 'Spanner'
    className: str

class SpannerAnchor(base.Music21Object):
    '''
    A simple Music21Object that can be used to define the beginning or end
    of a Spanner, in the place of a GeneralNote.

    This is useful for (e.g.) a Crescendo that ends partway through a
    note (e.g. in a violin part).  Exporters (like MusicXML) are configured
    to remove the SpannerAnchor itself on output, exporting only the Spanner
    start and stop locations.

    Here's an example of a whole note that has a Crescendo for the first
    half of the note, and a Diminuendo for the second half of the note.

    >>> n = note.Note('C4', quarterLength=4)
    >>> measure = stream.Measure([n], number=1)
    >>> part = stream.Part([measure], id='violin')
    >>> score = stream.Score([part])

    Add a crescendo from the note's start to the first anchor, place in the
    middle of the note, and then a diminuendo from that first anchor to the
    second, placed at the end of the note.

    >>> anchor1 = spanner.SpannerAnchor()
    >>> anchor2 = spanner.SpannerAnchor()
    >>> measure.insert(2.0, anchor1)
    >>> measure.insert(4.0, anchor2)
    >>> cresc = dynamics.Crescendo(n, anchor1)
    >>> dim = dynamics.Diminuendo(anchor1, anchor2)
    >>> score.append((cresc, dim))
    >>> score.show('text')
    {0.0} <music21.stream.Part violin>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.note.Note C>
            {2.0} <music21.spanner.SpannerAnchor at 2.0>
            {4.0} <music21.spanner.SpannerAnchor at 4.0>
    {4.0} <music21.dynamics.Crescendo <music21.note.Note C><...SpannerAnchor at 2.0>>
    {4.0} <music21.dynamics.Diminuendo <...SpannerAnchor at 2.0><...SpannerAnchor at 4.0>>
    '''
    def __init__(self, **keywords):
        super().__init__(**keywords)

    def _reprInternal(self) -> str:
        if self.activeSite is None:
            return 'unanchored'

        ql: OffsetQL = self.duration.quarterLength
        if ql == 0:
            return f'at {self.offset}'

        return f'at {self.offset}-{self.offset + ql}'

class SpannerBundle(prebase.ProtoM21Object):
    '''
    An advanced utility object for collecting and processing
    collections of Spanner objects. This is necessary because
    often processing routines that happen at many
    levels still need access to the same collection of spanners.

    Because SpannerBundles are so commonly used with
    :class:`~music21.stream.Stream` objects, the Stream has a
    :attr:`~music21.stream.Stream.spannerBundle` property that stores
    and caches a SpannerBundle of the Stream.

    If a Stream or Stream subclass is provided as an argument,
    all Spanners on this Stream will be accumulated herein.

    Not to be confused with SpannerStorage (which is a Stream class inside
    a spanner that stores Elements that are spanned)

    * Changed in v7: only argument must be a List of spanners.
      Creators of SpannerBundles are required to check that this constraint is True
    '''
    # TODO: make SpannerBundle a Generic type
    def __init__(self, spanners: list[Spanner]|None = None):
        self._cache: dict[str, t.Any] = {}  # cache is defined on Music21Object not ProtoM21Object

        self._storage: list[Spanner] = []
        if spanners:
            self._storage = spanners[:]  # a simple List, not a Stream

        # special spanners, stored in storage, can be identified in the
        # SpannerBundle as missing a spannedElement; the next obj that meets
        # the class expectation will then be assigned and the spannedElement
        # cleared
        self._pendingSpannedElementAssignment: list[_SpannerRef] = []

    def append(self, other: Spanner):
        '''
        adds a Spanner to the bundle. Will be done automatically when adding a Spanner
        to a Stream.
        '''
        self._storage.append(other)
        self._cache.clear()

    def __len__(self):
        return len(self._storage)

    def __iter__(self):
        return self._storage.__iter__()

    def __getitem__(self, key) -> Spanner:
        return self._storage[key]

    def remove(self, item: Spanner):
        '''
        Remove a stored Spanner from the bundle with an instance.
        Each reference must have a matching id() value.

        >>> su1 = spanner.Slur()
        >>> su1.idLocal = 1
        >>> su2 = spanner.Slur()
        >>> su2.idLocal = 2
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> len(sb)
        2
        >>> sb
        <music21.spanner.SpannerBundle of size 2>

        >>> sb.remove(su2)
        >>> len(sb)
        1
        '''
        if item in self._storage:
            self._storage.remove(item)
        else:
            raise SpannerBundleException(f'cannot match object for removal: {item}')
        self._cache.clear()

    def _reprInternal(self):
        return f'of size {len(self)}'

    def getSpannerStorageIds(self) -> list[int]:
        '''
        Return all SpannerStorage ids from all contained Spanners
        '''
        post: list[int] = []
        for x in self._storage:
            post.append(id(x.spannerStorage))
        return post

    def getByIdLocal(self, idLocal: int|None = None) -> SpannerBundle:
        '''
        Get spanners by `idLocal`.

        Returns a new SpannerBundle object

        >>> su = spanner.Slur()
        >>> su.idLocal = 1
        >>> rb = spanner.RepeatBracket()
        >>> rb.idLocal = 2
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su)
        >>> sb.append(rb)
        >>> len(sb)
        2

        >>> sb.getByIdLocal(2)
        <music21.spanner.SpannerBundle of size 1>
        >>> sb.getByIdLocal(2)[0]
        <music21.spanner.RepeatBracket >

        >>> len(sb.getByIdLocal(1))
        1

        >>> sb.getByIdLocal(3)
        <music21.spanner.SpannerBundle of size 0>
        '''
        cacheKey = f'idLocal-{idLocal}'
        if cacheKey not in self._cache or self._cache[cacheKey] is None:
            out: list[Spanner] = []
            for sp in self._storage:
                if sp.idLocal == idLocal:
                    out.append(sp)
            self._cache[cacheKey] = self.__class__(out)
        return self._cache[cacheKey]

    def getByCompleteStatus(self, completeStatus: bool) -> SpannerBundle:
        '''
        Get spanners by matching status of `completeStatus` to the same attribute

        >>> su1 = spanner.Slur()
        >>> su1.idLocal = 1
        >>> su1.completeStatus = True
        >>> su2 = spanner.Slur()
        >>> su2.idLocal = 2
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> sb2 = sb.getByCompleteStatus(True)
        >>> len(sb2)
        1
        >>> sb2 = sb.getByIdLocal(1).getByCompleteStatus(True)
        >>> sb2[0] == su1
        True
        '''
        # cannot cache, as complete status may change internally
        post: list[Spanner] = []
        for sp in self._storage:
            if sp.completeStatus == completeStatus:
                post.append(sp)
        return self.__class__(post)

    def getBySpannedElement(self, spannedElement: Spanner) -> SpannerBundle:
        '''
        Given a spanner spannedElement (an object),
        return a new SpannerBundle of all Spanner objects that
        have this object as a spannedElement.

        >>> n1 = note.Note()
        >>> n2 = note.Note()
        >>> n3 = note.Note()
        >>> su1 = spanner.Slur(n1, n2)
        >>> su2 = spanner.Slur(n2, n3)
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> list(sb.getBySpannedElement(n1)) == [su1]
        True
        >>> list(sb.getBySpannedElement(n2)) == [su1, su2]
        True
        >>> list(sb.getBySpannedElement(n3)) == [su2]
        True
        '''
        # NOTE: this is a performance critical operation

        # idTarget = id(spannedElement)
        # post = self.__class__()
        # for sp in self._storage:  # storage is a list
        #     if idTarget in sp.getSpannedElementIds():
        #         post.append(sp)
        # return post

        idTarget = id(spannedElement)
        cacheKey = f'getBySpannedElement-{idTarget}'
        if cacheKey not in self._cache or self._cache[cacheKey] is None:
            out: list[Spanner] = []
            for sp in self._storage:  # storage is a list of spanners
                # __contains__() will test for identity, not equality
                # see Spanner.hasSpannedElement(), which just calls __contains__()
                if spannedElement in sp:
                    out.append(sp)
            self._cache[cacheKey] = self.__class__(out)
        return self._cache[cacheKey]

    def replaceSpannedElement(
        self,
        old: base.Music21Object,
        new: base.Music21Object
    ) -> list[Spanner]:
        # noinspection PyShadowingNames
        '''
        Given a spanner spannedElement (an object), replace all old spannedElements
        with new spannedElements
        for all Spanner objects contained in this bundle.

        The `old` parameter must be an object, not an object id.

        If no replacements are found, no errors are raised.

        Returns a list of spanners that had elements replaced.

        >>> n1 = note.Note('C')
        >>> n2 = note.Note('D')
        >>> su1 = spanner.Line(n1, n2)
        >>> su2 = spanner.Glissando(n2, n1)
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)

        >>> su1
        <music21.spanner.Line <music21.note.Note C><music21.note.Note D>>
        >>> su2
        <music21.spanner.Glissando <music21.note.Note D><music21.note.Note C>>

        >>> n3 = note.Note('E')
        >>> replacedSpanners = sb.replaceSpannedElement(n2, n3)
        >>> replacedSpanners == [su1, su2]
        True

        >>> su1
        <music21.spanner.Line <music21.note.Note C><music21.note.Note E>>
        >>> su2
        <music21.spanner.Glissando <music21.note.Note E><music21.note.Note C>>

        * Changed in v7: id() is no longer allowed for `old`.

        >>> sb.replaceSpannedElement(id(n1), n2)
        Traceback (most recent call last):
        TypeError: send elements to replaceSpannedElement(), not ids.
        '''
        if isinstance(old, int):
            raise TypeError('send elements to replaceSpannedElement(), not ids.')

        replacedSpanners: list[Spanner] = []
        # post = self.__class__()  # return a bundle of spanners that had changes
        self._cache.clear()

        for sp in self._storage:  # Spanners in a list
            # environLocal.printDebug(['looking at spanner', sp, sp.getSpannedElementIds()])
            sp._cache = {}
            # accurate, so long as Spanner.__contains__() checks identity, not equality
            # see discussion at https://github.com/cuthbertLab/music21/pull/905
            if old in sp:
                sp.replaceSpannedElement(old, new)
                replacedSpanners.append(sp)
                # post.append(sp)
                # environLocal.printDebug(['replaceSpannedElement()', sp, 'old', old,
                #    'id(old)', id(old), 'new', new, 'id(new)', id(new)])

        self._cache.clear()

        return replacedSpanners

    def getByClass(self, searchClass: str|type|tuple[type, ...]) -> 'SpannerBundle':
        '''
        Given a spanner class, return a new SpannerBundle of all Spanners of the desired class.

        >>> su1 = spanner.Slur()
        >>> su2 = layout.StaffGroup()
        >>> su3 = layout.StaffGroup()
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> sb.append(su3)

        `searchClass` should be a Class.

        >>> slurs = sb.getByClass(spanner.Slur)
        >>> slurs
        <music21.spanner.SpannerBundle of size 1>
        >>> list(slurs) == [su1]
        True
        >>> list(sb.getByClass(spanner.Slur)) == [su1]
        True
        >>> list(sb.getByClass(layout.StaffGroup)) == [su2, su3]
        True

        A tuple of classes can also be given:

        >>> len(sb.getByClass((spanner.Slur, layout.StaffGroup)))
        3

        Note that the ability to search via a string will be removed in
        version 10.
        '''
        # NOTE: this is called very frequently and is optimized.

        cacheKey = f'getByClass-{searchClass}'
        searchStr = searchClass if isinstance(searchClass, str) else ''
        searchClasses = () if isinstance(searchClass, str) else searchClass

        if cacheKey not in self._cache or self._cache[cacheKey] is None:
            out: list[Spanner] = []
            for sp in self._storage:
                if searchStr and searchStr in sp.classes:
                    out.append(sp)
                else:
                    if isinstance(sp, searchClasses):
                        # PyCharm thinks this is a type, not a Spanner
                        # noinspection PyTypeChecker
                        out.append(sp)
            self._cache[cacheKey] = self.__class__(out)
        return self._cache[cacheKey]

    def setIdLocalByClass(self, className, maxId=6):
        # noinspection PyShadowingNames
        '''
        (See :meth:`setIdLocals` for an explanation of what an idLocal is.)

        Automatically set idLocal values for all members of the provided class.
        This is necessary in cases where spanners are newly created in
        potentially overlapping boundaries and need to be tagged for MusicXML
        or other output. Note that, if some Spanners already have idLocals,
        they will be overwritten.

        The `maxId` parameter sets the largest number that is available for this
        class.  In MusicXML it is 6.

        Currently, this method just iterates over the spanners of this class
        and counts the number from 1-6 and then recycles numbers.  It does
        not check whether more than 6 overlapping spanners of the same type
        exist, nor does it reset the count to 1 after all spanners of that
        class have been closed.  The example below demonstrates that the
        position of the contents of the spanner have no bearing on
        its idLocal (since we don't even put anything into the spanners).

        >>> su1 = spanner.Slur()
        >>> su2 = layout.StaffGroup()
        >>> su3 = spanner.Slur()
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> sb.append(su3)
        >>> [sp.idLocal for sp in sb.getByClass(spanner.Slur)]
        [None, None]
        >>> sb.setIdLocalByClass('Slur')
        >>> [sp.idLocal for sp in sb.getByClass(spanner.Slur)]
        [1, 2]
        '''
        # note that this overrides previous values
        for i, sp in enumerate(self.getByClass(className)):
            # 6 seems to be limit in musicxml processing
            sp.idLocal = (i % maxId) + 1

    def setIdLocals(self):
        # noinspection PyShadowingNames
        '''
        Utility method for outputting MusicXML (and potentially
        other formats) for spanners.

        Each Spanner type (slur, line, glissando, etc.) in MusicXML
        has a number assigned to it.
        We call this number, `idLocal`.  idLocal is a number from 1 to 6.
        This does not mean that your piece can only have six slurs total!
        But it does mean that within a single
        part, only up to 6 slurs can happen simultaneously.
        But as soon as a slur stops, its idLocal can be reused.

        This method sets all idLocals for all classes in this SpannerBundle.
        This will assure that each class has a unique idLocal number.

        Calling this method is destructive: existing idLocal values will be lost.

        >>> su1 = spanner.Slur()
        >>> su2 = layout.StaffGroup()
        >>> su3 = spanner.Slur()
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> sb.append(su3)
        >>> [sp.idLocal for sp in sb.getByClass('Slur')]
        [None, None]
        >>> sb.setIdLocals()
        >>> [(sp, sp.idLocal) for sp in sb]
        [(<music21.spanner.Slur>, 1),
         (<music21.layout.StaffGroup>, 1),
         (<music21.spanner.Slur>, 2)]

        :class:`~music21.dynamics.DynamicWedge` objects are commingled. That is,
        :class:`~music21.dynamics.Crescendo` and
        :class:`~music21.dynamics.Diminuendo`
        are not numbered separately:

        >>> sb2 = spanner.SpannerBundle()
        >>> c = dynamics.Crescendo()
        >>> d = dynamics.Diminuendo()
        >>> sb2.append(c)
        >>> sb2.append(d)
        >>> sb2.setIdLocals()
        >>> [(sp, sp.idLocal) for sp in sb2]
        [(<music21.dynamics.Crescendo>, 1),
         (<music21.dynamics.Diminuendo>, 2)]
        '''
        # Crescendo and Diminuendo share the same numbering
        # So number by DynamicWedge instead (next parent class)
        skip_classes = ('Crescendo', 'Diminuendo')
        classes = set()
        for sp in self._storage:
            for klass in sp.classes:
                if klass not in skip_classes:
                    classes.add(klass)
                    break
        for className in classes:
            self.setIdLocalByClass(className)

    def getByClassIdLocalComplete(self, className, idLocal, completeStatus):
        '''
        Get all spanners of a specified class `className`, an id `idLocal`, and a `completeStatus`.
        This is a convenience routine for multiple filtering when searching for relevant Spanners
        to pair with.

        >>> su1 = spanner.Slur()
        >>> su2 = layout.StaffGroup()
        >>> su2.idLocal = 3
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> sb.append(su2)
        >>> list(sb.getByClassIdLocalComplete(layout.StaffGroup, 3, False)) == [su2]
        True
        >>> su2.completeStatus = True
        >>> list(sb.getByClassIdLocalComplete(layout.StaffGroup, 3, False)) == []
        True
        '''
        # TODO: write utility classes that just modify lists and cast to a spannerBundle
        #    at the end.
        return self.getByClass(className).getByIdLocal(
            idLocal).getByCompleteStatus(completeStatus)

    def setPendingSpannedElementAssignment(
        self,
        sp: Spanner,
        className: str,
    ):
        '''
        A SpannerBundle can be set up so that a particular spanner (sp)
        is looking for an element of class (className) to complete it. Any future
        element that matches the className which is passed to the SpannerBundle
        via freePendingSpannedElementAssignment() will get it.

        >>> n1 = note.Note('C')
        >>> r1 = note.Rest()
        >>> n2 = note.Note('D')
        >>> n3 = note.Note('E')
        >>> su1 = spanner.Slur([n1])
        >>> sb = spanner.SpannerBundle()
        >>> sb.append(su1)
        >>> su1.getSpannedElements()
        [<music21.note.Note C>]

        >>> n1.getSpannerSites()
        [<music21.spanner.Slur <music21.note.Note C>>]

        Now set up su1 to get the next note assigned to it.

        >>> sb.setPendingSpannedElementAssignment(su1, 'Note')

        Call freePendingSpannedElementAssignment to attach.

        Should not get a rest, because it is not a 'Note'

        >>> sb.freePendingSpannedElementAssignment(r1)
        >>> su1.getSpannedElements()
        [<music21.note.Note C>]

        But will get the next note:

        >>> sb.freePendingSpannedElementAssignment(n2)
        >>> su1.getSpannedElements()
        [<music21.note.Note C>, <music21.note.Note D>]

        >>> n2.getSpannerSites()
        [<music21.spanner.Slur <music21.note.Note C><music21.note.Note D>>]

        And now that the assignment has been made, the pending assignment
        has been cleared, so n3 will not get assigned to the slur:

        >>> sb.freePendingSpannedElementAssignment(n3)
        >>> su1.getSpannedElements()
        [<music21.note.Note C>, <music21.note.Note D>]

        >>> n3.getSpannerSites()
        []

        '''
        ref: _SpannerRef = {'spanner': sp, 'className': className}
        self._pendingSpannedElementAssignment.append(ref)

    def freePendingSpannedElementAssignment(self, spannedElementCandidate):
        '''
        Assigns and frees up a pendingSpannedElementAssignment if one is
        active and the candidate matches the class.  See
        setPendingSpannedElementAssignment for documentation and tests.

        It is set up via a first-in, first-out priority.
        '''

        if not self._pendingSpannedElementAssignment:
            return

        remove = None
        for i, ref in enumerate(self._pendingSpannedElementAssignment):
            # environLocal.printDebug(['calling freePendingSpannedElementAssignment()',
            #    self._pendingSpannedElementAssignment])
            if ref['className'] in spannedElementCandidate.classSet:
                ref['spanner'].addSpannedElements(spannedElementCandidate)
                remove = i
                # environLocal.printDebug(['freePendingSpannedElementAssignment()',
                #    'added spannedElement', ref['spanner']])
                break
        if remove is not None:
            self._pendingSpannedElementAssignment.pop(remove)

# ------------------------------------------------------------------------------
# connect two or more notes anywhere in the score
class Slur(Spanner):
    '''
    A slur represented as a spanner between two Notes.

    Slurs have `.placement` options ('above' or 'below') and `.lineType` ('dashed' or None)
    '''

    def __init__(self, *spannedElements, **keywords):
        super().__init__(*spannedElements, **keywords)
        self.placement = None  # can above or below, after musicxml
        self.lineType = None  # can be 'dashed' or None
        # from music21 import note
        # self.fillElementTypes = [note.NotRest]

    # TODO: add property for placement

# ------------------------------------------------------------------------------

class MultiMeasureRest(Spanner):
    '''
    A grouping symbol that indicates that a collection of rests lasts
    multiple measures.
    '''
    _styleClass = style.TextStyle

    _DOC_ATTR: dict[str, str] = {
        'useSymbols': '''
            Boolean to indicate whether rest symbols
            (breve, longa, etc.) should be used when
            displaying the rest. Your music21 inventor
            is a medievalist, so this defaults to True.

            Change defaults.multiMeasureRestUseSymbols to
            change globally.
            ''',
        'maxSymbols': '''
            An int, specifying the maximum number of rests
            to display as symbols.  Default is 11.
            If useSymbols is False then this setting
            does nothing.

            Change defaults.multiMeasureRestMaxSymbols to
            change globally.
            ''',
    }

    def __init__(self, *spannedElements, **keywords):
        super().__init__(*spannedElements, **keywords)

        # from music21 import note
        # self.fillElementTypes = [note.Rest]
        self._overriddenNumber = None
        self.useSymbols = keywords.get('useSymbols', defaults.multiMeasureRestUseSymbols)
        self.maxSymbols = keywords.get('maxSymbols', defaults.multiMeasureRestMaxSymbols)

    def _reprInternal(self):
        plural = 's' if self.numRests != 1 else ''
        return f'{self.numRests} measure{plural}'

    @property
    def numRests(self):
        '''
        Returns the number of measures involved in the
        multi-measure rest.

        Calculated automatically from the number of rests in
        the spanner.  Or can be set manually to override the number.

        >>> mmr = spanner.MultiMeasureRest()
        >>> for i in range(6):
        ...     mmr.addSpannedElements([note.Rest(type='whole')])
        >>> mmr.numRests
        6
        >>> mmr.numRests = 10
        >>> mmr.numRests
        10
        '''
        if self._overriddenNumber is not None:
            return self._overriddenNumber
        else:
            return len(self)

    @numRests.setter
    def numRests(self, overridden):
        self._overriddenNumber = overridden

# ------------------------------------------------------------------------------
# first/second repeat bracket

class RepeatBracket(Spanner):
    '''
    A grouping of one or more measures, presumably in sequence, that mark an alternate repeat.

    These gather what are sometimes called first-time bars and second-time bars.

    It is assumed that numbering starts from 1. Numberings above 2 are permitted.
    The `number` keyword argument can be used to pass in the desired number.

    `overrideDisplay` if set will display something other than the number.  For instance
    `ouvert` and `clos` for medieval music.  However, if you use it for something like '1-3'
    be sure to set number properly too.

    >>> m = stream.Measure()
    >>> sp = spanner.RepeatBracket(m, number=1)
    >>> sp  # can be one or more measures
    <music21.spanner.RepeatBracket 1 <music21.stream.Measure 0 offset=0.0>>

    >>> sp.number = 3
    >>> sp
    <music21.spanner.RepeatBracket 3 <music21.stream.Measure 0 offset=0.0>>
    >>> sp.numberRange  # the list of repeat numbers
    [3]
    >>> sp.number
    '3'

    Range of repeats as string:

    >>> sp.number = '1-3'
    >>> sp.numberRange
    [1, 2, 3]
    >>> sp.number
    '1-3'

    Range of repeats as list:

    >>> sp.number = [2, 3]
    >>> sp.numberRange
    [2, 3]
    >>> sp.number
    '2, 3'

    Comma separated numbers:

    >>> sp.number = '1, 2, 3'
    >>> sp.numberRange
    [1, 2, 3]
    >>> sp.number
    '1-3'

    Disjunct numbers:

    >>> sp.number = '1, 2, 3, 7'
    >>> sp.numberRange
    [1, 2, 3, 7]
    >>> sp.number
    '1, 2, 3, 7'

    Override the display.

    >>> sp.overrideDisplay = '1-3, 7'
    >>> sp
    <music21.spanner.RepeatBracket 1-3, 7
         <music21.stream.Measure 0 offset=0.0>>

    number is not affected by display overrides:

    >>> sp.number
    '1, 2, 3, 7'
    '''

    _DOC_ATTR = {
        'numberRange': '''
            Get a contiguous list of repeat numbers that are applicable for this instance.

            Will always have at least one element, but [0] means undefined

            >>> rb = spanner.RepeatBracket()
            >>> rb.numberRange
            [0]

            >>> rb.number = '1,2'
            >>> rb.numberRange
            [1, 2]
        ''',
        'overrideDisplay': '''
            Override the string representation of this bracket, or use
            None to not override.
        ''',
    }

    def __init__(self,
                 *spannedElements,
                 number: int|str|Iterable[int] = 0,
                 overrideDisplay: str|None = None,
                 **keywords):
        super().__init__(*spannedElements, **keywords)

        # from music21 import stream
        # self.fillElementTypes = [stream.Measure]

        # store a range, inclusive of the single number assignment
        self.numberRange: list[int] = []
        self.overrideDisplay = overrideDisplay
        self.number = number

    @property
    def _numberSpanIsAdjacent(self) -> bool:
        '''
        are there exactly two numbers that should be written as 3, 4 not 3-4.
        '''
        return len(self.numberRange) == 2 and self.numberRange[0] == self.numberRange[1] - 1

    @property
    def _numberSpanIsContiguous(self) -> bool:
        '''
        can we write as '3, 4' or '5-10' and not as '1, 5, 6, 11'
        '''
        return common.contiguousList(self.numberRange)

    # property to enforce numerical numbers
    def _getNumber(self) -> str:
        '''
        This must return a string, as we may have single numbers or lists.
        For a raw numerical list, look at `.numberRange`.
        '''
        if len(self.numberRange) == 1:
            if self.numberRange[0] == 0:
                return ''
            return str(self.numberRange[0])
        else:
            if not self._numberSpanIsContiguous:
                return ', '.join([str(x) for x in self.numberRange])
            elif self._numberSpanIsAdjacent:
                return f'{self.numberRange[0]}, {self.numberRange[-1]}'
            else:  # range of values
                return f'{self.numberRange[0]}-{self.numberRange[-1]}'

    def _setNumber(self, value: int|str|Iterable[int]):
        '''
        Set the bracket number. There may be range of values provided
        '''
        if value == '':
            # undefined.
            self.numberRange = [0]
        elif common.holdsType(value, int):
            self.numberRange = []  # clear
            for x in value:
                self.numberRange.append(x)
        elif isinstance(value, str):
            # assume defined a range with a dash; assumed inclusive
            if '-' in value:
                start, end = value.split('-')
                self.numberRange = list(range(int(start), int(end) + 1))

            elif ',' in value:
                self.numberRange = []  # clear
                for one_letter_value in value.split(','):
                    one_number = int(one_letter_value.strip())
                    self.numberRange.append(one_number)
            elif value.isdigit():
                self.numberRange = [int(value)]
            else:
                raise SpannerException(f'number for RepeatBracket must be a number, not {value!r}')
        elif common.isInt(value):
            self.numberRange = []  # clear
            if value not in self.numberRange:
                self.numberRange.append(value)
        else:
            raise SpannerException(f'number for RepeatBracket must be a number, not {value!r}')

    number = property(_getNumber, _setNumber, doc='''
            Get or set the number -- returning a string always.

            >>> rb = spanner.RepeatBracket()
            >>> rb.number
            ''
            >>> rb.number = '5-7'
            >>> rb.number
            '5-7'
            >>> rb.numberRange
            [5, 6, 7]
            >>> rb.number = 1
        ''')

    @common.deprecated('v9', 'v10', 'Look at .numberRange instead')
    def getNumberList(self):  # pragma: no cover
        '''
        Deprecated -- just look at .numberRange
        '''
        return self.numberRange

    def _reprInternal(self):
        if self.overrideDisplay is not None:
            msg = self.overrideDisplay + ' '
        else:
            msg = self.number + ' '
        return msg + super()._reprInternal()

# ------------------------------------------------------------------------------
# line-based spanners

class Ottava(Spanner):
    '''
    An octave shift line:

    >>> ottava = spanner.Ottava(type='8va')
    >>> ottava.type
    '8va'
    >>> ottava.type = 15
    >>> ottava.type
    '15ma'
    >>> ottava.type = (8, 'down')
    >>> ottava.type
    '8vb'
    >>> print(ottava)
    <music21.spanner.Ottava 8vb transposing>

    An Ottava spanner can either be transposing or non-transposing.
    In a transposing Ottava spanner, the notes in the stream should be
    in their written octave (as if the spanner were not there) and all the
    notes in the spanner will be transposed on Stream.toSoundingPitch().

    A non-transposing spanner has notes that are at the pitch that
    they would sound (therefore the Ottava spanner is a decorative
    line).

    >>> ottava.transposing
    True
    >>> n1 = note.Note('D4')
    >>> n2 = note.Note('E4')
    >>> n2.offset = 2.0
    >>> ottava.addSpannedElements([n1, n2])

    >>> s = stream.Stream([ottava, n1, n2])
    >>> s.atSoundingPitch = False
    >>> s2 = s.toSoundingPitch()
    >>> s2.show('text')
    {0.0} <music21.spanner.Ottava 8vb non-transposing<music21.note.Note D><music21.note.Note E>>
    {0.0} <music21.note.Note D>
    {2.0} <music21.note.Note E>

    >>> for n in s2.notes:
    ...     print(n.nameWithOctave)
    D3
    E3

    All valid types are given below:

    >>> ottava.validOttavaTypes
    ('8va', '8vb', '15ma', '15mb', '22da', '22db')

    OMIT_FROM_DOCS

    Test the round-trip back:

    >>> s3 = s2.toWrittenPitch()
    >>> s3.show('text')
    {0.0} <music21.spanner.Ottava 8vb transposing<music21.note.Note D><music21.note.Note E>>
    {0.0} <music21.note.Note D>
    {2.0} <music21.note.Note E>

    >>> for n in s3.notes:
    ...    print(n.nameWithOctave)
    D4
    E4
    '''
    validOttavaTypes = ('8va', '8vb', '15ma', '15mb', '22da', '22db')

    def __init__(self,
                 *spannedElements,
                 type: str = '8va',  # pylint: disable=redefined-builtin
                 transposing: bool = True,
                 placement: t.Literal['above', 'below'] = 'above',
                 **keywords):
        from music21 import note
        super().__init__(*spannedElements, **keywords)
        self.fillElementTypes = [note.NotRest]
        self._type = None  # can be 8va, 8vb, 15ma, 15mb
        self.type = type

        self.placement = placement  # can above or below, after musicxml
        self.transposing = transposing

    def _getType(self):
        return self._type

    def _setType(self, newType):
        if common.isNum(newType) and newType in (8, 15):
            if newType == 8:
                self._type = '8va'
            else:
                self._type = '15ma'
        # try to parse as list of size, dir
        elif common.isListLike(newType) and len(newType) >= 1:
            stub = []
            if newType[0] in (8, '8'):
                stub.append(str(newType[0]))
                stub.append('v')
            elif newType[0] in (15, '15'):
                stub.append(str(newType[0]))
                stub.append('m')
            if len(newType) >= 2 and newType[1] == 'down':
                stub.append('b')
            else:  # default if not provided
                stub.append('a')
            self._type = ''.join(stub)
        else:
            if (not isinstance(newType, str)
                    or newType.lower() not in self.validOttavaTypes):
                raise SpannerException(
                    f'cannot create Ottava of type: {newType}')
            self._type = newType.lower()

    type = property(_getType, _setType, doc='''
        Get or set Ottava type. This can be set by as complete string
        (such as 8va or 15mb) or with a pair specifying size and direction.

        >>> os = spanner.Ottava()
        >>> os.type = '8vb'
        >>> os.type
        '8vb'
        >>> os.type = 15, 'down'
        >>> os.type
        '15mb'
        ''')

    def _reprInternal(self):
        transposing = 'transposing'
        if not self.transposing:
            transposing = 'non-transposing'
        return f'{self.type} {transposing}' + super()._reprInternal()

    def shiftMagnitude(self):
        '''
        Get basic parameters of shift.

        Returns either 8, 15, or 22 depending on the amount of shift
        '''
        if self._type.startswith('8'):
            return 8
        elif self._type.startswith('15'):
            return 15
        elif self._type.startswith('22'):
            return 22
        else:
            raise SpannerException(f'Cannot get shift magnitude from {self._type!r}')

    def shiftDirection(self, reverse=False):
        '''
        Returns up or down depending on the type of shift:
        '''
        # an 8va mark means that the notes must be shifted down with the mark
        if self._type.endswith('a'):
            if reverse:
                return 'down'
            else:
                return 'up'
        # an 8vb means that the notes must be shifted upward with the mark
        if self._type.endswith('b'):
            if reverse:
                return 'up'
            else:
                return 'down'

    def interval(self, reverse=False):
        '''
        return an interval.Interval() object representing this ottava

        >>> ottava = spanner.Ottava(type='15mb')
        >>> i = ottava.interval()
        >>> i
        <music21.interval.Interval P-15>
        '''
        from music21.interval import Interval
        if self.shiftDirection(reverse=reverse) == 'down':
            header = 'P-'
        else:
            header = 'P'

        header += str(self.shiftMagnitude())
        return Interval(header)

    def performTransposition(self):
        '''
        On a transposing spanner, switch to non-transposing,
        and transpose all notes and chords in the spanner.
        The note/chords will all be transposed to their sounding
        pitch (at least as far as the ottava is concerned;
        transposing instruments are handled separately).

        >>> ottava = spanner.Ottava(type='8va')
        >>> n1 = note.Note('D#4')
        >>> n2 = note.Note('E#4')
        >>> ottava.addSpannedElements([n1, n2])
        >>> ottava.transposing
        True

        >>> ottava.performTransposition()

        >>> ottava.transposing
        False
        >>> n1.nameWithOctave
        'D#5'
        '''
        if not self.transposing:
            return
        self.transposing = False

        myInterval = self.interval()
        for n in self.getSpannedElements():
            if not hasattr(n, 'pitches'):
                continue
            for p in n.pitches:
                p.transpose(myInterval, inPlace=True)

    def undoTransposition(self):
        '''
        Change a non-transposing spanner to a transposing spanner,
        and transpose back all the notes and chords in the spanner.
        The notes/chords will all be transposed to their written
        pitch (at least as far as the ottava is concerned;
        transposing instruments are handled separately).

        >>> ottava = spanner.Ottava(type='8va')
        >>> n1 = note.Note('D#4')
        >>> n2 = note.Note('E#4')
        >>> ottava.addSpannedElements([n1, n2])
        >>> ottava.transposing = False

        >>> ottava.undoTransposition()

        >>> ottava.transposing
        True
        >>> n1.nameWithOctave
        'D#3'
        '''
        if self.transposing:
            return
        self.transposing = True

        myInterval = self.interval(reverse=True)
        for n in self.getSpannedElements():
            if not hasattr(n, 'pitches'):
                continue
            for p in n.pitches:
                p.transpose(myInterval, inPlace=True)

class Line(Spanner):
    '''
    A line or bracket represented as a spanner above two Notes.

    Brackets can take many line types.

    >>> b = spanner.Line()
    >>> b.lineType = 'dotted'
    >>> b.lineType
    'dotted'
    >>> b = spanner.Line(endHeight=20)
    >>> b.endHeight
    20
    '''
    validLineTypes = ('solid', 'dashed', 'dotted', 'wavy')
    validTickTypes = ('up', 'down', 'arrow', 'both', 'none')

    def __init__(
        self,
        *spannedElements,
        lineType: str = 'solid',
        tick: str = 'down',
        startTick: str = 'down',
        endTick: str = 'down',
        startHeight: int|float|None = None,
        endHeight: int|float|None = None,
        **keywords
    ):
        super().__init__(*spannedElements, **keywords)
        # from music21 import note
        # self.fillElementTypes = [note.GeneralNote]

        DEFAULT_TICK = 'down'
        self._endTick = DEFAULT_TICK  # can be up/down/arrow/both/None
        self._startTick = DEFAULT_TICK  # can be up/down/arrow/both/None

        self._endHeight = None  # for up/down, specified in tenths
        self._startHeight = None  # for up/down, specified in tenths

        DEFAULT_LINE_TYPE = 'solid'
        self._lineType = DEFAULT_LINE_TYPE  # can be solid, dashed, dotted, wavy

        DEFAULT_PLACEMENT = 'above'
        self.placement = DEFAULT_PLACEMENT  # can above or below, after musicxml

        if lineType != DEFAULT_LINE_TYPE:
            self.lineType = lineType  # use property

        if startTick != DEFAULT_TICK:
            self.startTick = startTick  # use property
        if endTick != DEFAULT_TICK:
            self.endTick = endTick  # use property
        if tick != DEFAULT_TICK:
            self.tick = tick  # use property

        if endHeight is not None:
            self.endHeight = endHeight  # use property
        if startHeight is not None:
            self.startHeight = startHeight  # use property

    def _getEndTick(self):
        return self._endTick

    def _setEndTick(self, value):
        if value.lower() not in self.validTickTypes:
            raise SpannerException(f'not a valid value: {value}')
        self._endTick = value.lower()

    endTick = property(_getEndTick, _setEndTick, doc='''
        Get or set the endTick property.
        ''')

    def _getStartTick(self):
        return self._startTick

    def _setStartTick(self, value):
        if value.lower() not in self.validTickTypes:
            raise SpannerException(f'not a valid value: {value}')
        self._startTick = value.lower()

    startTick = property(_getStartTick, _setStartTick, doc='''
        Get or set the startTick property.
        ''')

    def _getTick(self):
        return self._startTick  # just returning start

    def _setTick(self, value):
        if value.lower() not in self.validTickTypes:
            raise SpannerException(f'not a valid value: {value}')
        self._startTick = value.lower()
        self._endTick = value.lower()

    tick = property(_getTick, _setTick, doc='''
        Set the start and end tick to the same value

        >>> b = spanner.Line()
        >>> b.tick = 'arrow'
        >>> b.startTick
        'arrow'
        >>> b.endTick
        'arrow'
        ''')

    def _getLineType(self):
        return self._lineType

    def _setLineType(self, value):
        if value is not None and value.lower() not in self.validLineTypes:
            raise SpannerException(f'not a valid value: {value}')
        # not sure if we should permit setting as None
        if value is not None:
            self._lineType = value.lower()

    lineType = property(_getLineType, _setLineType, doc='''
        Get or set the lineType property. Valid line types are listed in .validLineTypes.

        >>> b = spanner.Line()
        >>> b.lineType = 'dotted'
        >>> b.lineType = 'navyblue'
        Traceback (most recent call last):
        music21.spanner.SpannerException: not a valid value: navyblue

        >>> b.validLineTypes
        ('solid', 'dashed', 'dotted', 'wavy')
        ''')

    def _getEndHeight(self):
        return self._endHeight

    def _setEndHeight(self, value):
        if not (common.isNum(value) and value >= 0):
            raise SpannerException(f'not a valid value: {value}')
        self._endHeight = value

    endHeight = property(_getEndHeight, _setEndHeight, doc='''
        Get or set the endHeight property.

        >>> b = spanner.Line()
        >>> b.endHeight = -20
        Traceback (most recent call last):
        music21.spanner.SpannerException: not a valid value: -20
        ''')

    def _getStartHeight(self):
        return self._startHeight

    def _setStartHeight(self, value):
        if not (common.isNum(value) and value >= 0):
            raise SpannerException(f'not a valid value: {value}')
        self._startHeight = value

    startHeight = property(_getStartHeight, _setStartHeight, doc='''
        Get or set the startHeight property.

        >>> b = spanner.Line()
        >>> b.startHeight = None
        Traceback (most recent call last):
        music21.spanner.SpannerException: not a valid value: None
        ''')

class Glissando(Spanner):
    '''
    A between two Notes specifying a glissando or similar alteration.
    Different line types can be specified.

    Glissandos can have a label and a lineType.  Label is a string or None.
    lineType defaults to 'wavy'

    >>> gl = spanner.Glissando()
    >>> gl.lineType
    'wavy'
    >>> print(gl.label)
    None

    >>> gl.label = 'gliss.'

    Note -- not a Line subclass for now, but that might change.
    '''
    validLineTypes = ('solid', 'dashed', 'dotted', 'wavy')
    validSlideTypes = ('chromatic', 'continuous', 'diatonic', 'white', 'black')

    def __init__(self,
                 *spannedElements,
                 lineType: str = 'wavy',
                 label: str|None = None,
                 **keywords):
        super().__init__(*spannedElements, **keywords)
        # from music21 import note
        # self.fillElementTypes = [note.NotRest]

        GLISSANDO_DEFAULT_LINE_TYPE = 'wavy'
        self._lineType = GLISSANDO_DEFAULT_LINE_TYPE
        self._slideType = 'chromatic'

        self.label = None

        if lineType != GLISSANDO_DEFAULT_LINE_TYPE:
            self.lineType = lineType  # use property
        if label is not None:
            self.label = label  # use property

    def _getLineType(self):
        return self._lineType

    def _setLineType(self, value):
        if value.lower() not in self.validLineTypes:
            raise SpannerException(f'not a valid value: {value}')
        self._lineType = value.lower()

    lineType = property(_getLineType, _setLineType, doc='''
        Get or set the lineType property. See Line for valid line types.
        ''')

    @property
    def slideType(self):
        '''
        Get or set the slideType which determines how
        the glissando or slide is to be played.  Values
        are 'chromatic' (default), 'continuous' (like a slide or smear),
        'diatonic' (like a harp gliss), 'white' (meaning a white-key gliss
        as on a marimba), or 'black' (black-key gliss).

        'continuous' slides export to MusicXML as a <slide> object.
        All others export as <glissando>.
        '''
        return self._slideType

    @slideType.setter
    def slideType(self, value):
        if value.lower() not in self.validSlideTypes:
            raise SpannerException(f'not a valid value: {value}')
        self._slideType = value.lower()

# ------------------------------------------------------------------------------

# pylint: disable=redefined-outer-name

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER: list[type] = [Spanner]
