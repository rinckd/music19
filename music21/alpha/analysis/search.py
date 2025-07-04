# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         search.py
# Purpose:      Tools for searching analysis
#
# Authors:      Christopher Ariza
#
# Copyright:    Copyright © 2011 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

from music21 import chord
from music21 import environment
from music21 import exceptions21
from music21 import note
from music21 import pitch
from music21 import scale
from music21 import stream

environLocal = environment.Environment('alpha.analysis.search')

class SearchModuleException(exceptions21.Music21Exception):
    pass

def findConsecutiveScale(source, targetScale, degreesRequired=5,
                         stepSize=1, comparisonAttribute='name',
                         repeatsAllowed=True, restsAllowed=False):
    '''
    Given a pitch source and a concrete scale, return references to all
    elements found that represent consecutive scale segments in one direction.

    The `targetScale` is a concrete scale instance.

    The `degreesRequired` specifies how many consecutive scale degrees
    are required for grouping. Note that if more are found, they will
    continue to be gathered until a break is found.

    The `stepSize` determines what scale step size is examined

    The `comparisonAttribute` is the Pitch class attribute used
    for all pitch comparisons; this can be used to force enharmonic
    comparison ('name'), pitch space comparison ('nameWithOctave') or
    permit pitch class matching ('pitchClass').

    If `repeatsAllowed` is True, repeated Pitches will be counted as
    part of the consecutive segment.

    If `restsAllowed` is True, rests will not interrupt a consecutive segment.
    '''

    if not isinstance(targetScale, scale.ConcreteScale):
        raise SearchModuleException('scale must be a concrete scale class')

    degreeLast = None
    pLast = None
    pNext = None
    p = None
    d = None
    directionLast = None

    collPitches = []
    collElements = []
    collDegrees = set()  # use a set to remove redundancies

    clearCollect = False
    clearCollectKeepLast = False
    match = False
    collMatch = []  # return a list of streams

    # assume 0 to max unique; this is 1 to 7 for diatonic
    # dMax = targetScale.abstract.getDegreeMaxUnique()

    # if rests are allowed, first
    # strip them out of a copy of the source
    sourceClean = stream.Stream()
    for e in source:
        if isinstance(e, chord.Chord):
            continue  # do not insert for now
        if isinstance(e, note.Rest) and restsAllowed:
            continue  # do not insert if allowed

        # just takes notes or pitches
        if isinstance(e, (pitch.Pitch, note.Note)):
            sourceClean.insert(source.elementOffset(e), e)

    # not taking flat
    for eCount, e in enumerate(sourceClean):
        # at this time, not handling chords

        if eCount < len(sourceClean) - 1:
            eNext = sourceClean[eCount + 1]
        else:
            eNext = None

        if hasattr(e, 'pitch'):
            p = e.pitch
            if eNext is not None and hasattr(eNext, 'pitch'):
                pNext = eNext.pitch
            else:
                pNext = None

            # environLocal.printDebug(['examining pitch', p, 'pNext', pNext, 'pLast', pLast,
            #    'e.getOffsetBySite(sourceClean)', e.getOffsetBySite(sourceClean)])
            collect = False
            # first, see if this is a degreeLast
            if directionLast is None:
                dirDegreeGet = scale.Direction.BI  # note: note sure this is always best
            else:
                dirDegreeGet = directionLast
            d = targetScale.getScaleDegreeFromPitch(p,
                                                    comparisonAttribute=comparisonAttribute,
                                                    direction=dirDegreeGet)

            # if this is not a scale degree, this is the end of a collection
            if d is None:
                clearCollect = True
                # environLocal.printDebug(['not collecting pitch', 'd', d, 'p', p])

            # second, see if the degrees are consecutive with the last
            else:
                # if pLast is not None:
                #     pScaleAscending = targetScale.next(pLast,
                #         direction=scale.Direction.ASCENDING)
                #     pScaleDescending = targetScale.next(pLast,
                #         direction=scale.Direction.DESCENDING)

                if degreeLast is None:  # if we do not have a previous
                    collect = True
                    # cannot determine direction here
                # this will permit octave shifts; need to compare pitch
                # attributes
                elif repeatsAllowed and degreeLast - d == 0:
                    collect = True
                # in this case we know have a previous pitch/degree
                elif (targetScale.isNext(p, pLast, scale.Direction.ASCENDING,
                                         stepSize=stepSize,
                                         comparisonAttribute=comparisonAttribute)
                      and directionLast in [None, scale.Direction.ASCENDING]):

                    # environLocal.printDebug(['found ascending degree', 'degreeLast',
                    #    degreeLast, 'd', d])
                    collect = True
                    directionLast = scale.Direction.ASCENDING

                elif (targetScale.isNext(p, pLast, scale.Direction.DESCENDING,
                                         stepSize=stepSize,
                                         comparisonAttribute=comparisonAttribute)
                      and directionLast in [None, scale.Direction.DESCENDING]):

                    # environLocal.printDebug(['found descending degree', 'degreeLast', degreeLast,
                    #    'd', d])
                    collect = True
                    directionLast = scale.Direction.DESCENDING

                else:
                    # if this condition is not met, then we need to test
                    # and clear the collection
                    collect = False
                    # this is a degree, so we want to keep it for the
                    # next potential sequence
                    clearCollectKeepLast = True
                    # environLocal.printDebug(['no conditions matched for pitch', p,
                    #    'collect = False, clearCollectKeepLAst = True'])

                # gather pitch and degree
                if collect:
                    # environLocal.printDebug(['collecting pitch', 'd', d, 'p', p])
                    collDegrees.add(d)
                    collPitches.append(p)
                    collElements.append(e)

            # directionLast is set above
            degreeLast = d  # set it here
            pLast = p

        # test at for each new pitch; set will measure original instances
        if len(collDegrees) >= degreesRequired:
            # if next pitch is appropriate, then do not collect
            # this makes gathering greedy
            if targetScale.isNext(pNext,
                                  p,
                                  directionLast,
                                  stepSize=1,
                                  comparisonAttribute=comparisonAttribute):
                pass
                # environLocal.printDebug(['matched degree count but next pitch is ' +
                #        'in scale and direction', 'collDegrees', collDegrees])
            else:
                # environLocal.printDebug(['matched degree count', 'collDegrees', collDegrees,
                #    'pNext', pNext])
                match = True

        if match:
            # collected matched elements into a stream
            post = stream.Stream()
            # environLocal.printDebug(['processing match', 'adding collElements',
            #    'collPitches', collPitches])

            for innerEl in collElements:
                # use source offset positions
                post.insert(source.elementOffset(innerEl), innerEl)
            dictionary = {'stream': post, 'direction': directionLast}
            collMatch.append(dictionary)
            match = False

            # if we have not explicitly said to keep the last
            # then we should
            if clearCollect is False and clearCollectKeepLast is False:
                # if the next pitch is part of a directional sequence, keep
                if ((targetScale.isNext(pNext, p, scale.Direction.DESCENDING,
                                        stepSize=stepSize,
                                        comparisonAttribute=comparisonAttribute)
                        or targetScale.isNext(pNext, p, scale.Direction.ASCENDING,
                                              stepSize=stepSize,
                                              comparisonAttribute=comparisonAttribute))):
                    clearCollectKeepLast = True
                else:
                    clearCollect = True

        if clearCollect:
            # environLocal.printDebug(['clearCollect'])

            degreeLast = None
            directionLast = None
            collDegrees = set()
            collPitches = []
            collElements = []
            clearCollect = False

        # case where we need to keep the element that broke
        # the chain; as in a leap to a new degree in the scale
        if clearCollectKeepLast:
            # environLocal.printDebug(['clearCollectKeepLast'])

            # degreeLast = None keep
            # always clear direction last
            directionLast = None
            collDegrees = set()
            collDegrees.add(d)
            collPitches = [p]
            collElements = [e]
            clearCollectKeepLast = False

    return collMatch

# ------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
