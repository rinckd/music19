# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         transposition.py
# Purpose:      Tools for checking distinct transposition
#
# Authors:      Mark Gotham
#
# Copyright:    Copyright © 2017 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections.abc import Iterable
from music21 import chord
from music21 import common
from music21 import environment
from music21 import pitch

environLocal = environment.Environment('analysis.transposition')

class TranspositionChecker:
    '''
    Given a list of pitches, checks for the number of distinct transpositions.

    >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
    >>> tc = analysis.transposition.TranspositionChecker(pList)
    >>> tc.numDistinctTranspositions()
    4
    >>> allNormalOrderPitchTuples = tc.getPitchesOfDistinctTranspositions()
    >>> allNormalOrderPitchTuples
    [(<music21.pitch.Pitch C>, <music21.pitch.Pitch E>,
                                         <music21.pitch.Pitch G#>),
     (<music21.pitch.Pitch C#>, <music21.pitch.Pitch F>,
                                         <music21.pitch.Pitch A>),
     (<music21.pitch.Pitch D>, <music21.pitch.Pitch F#>,
                                         <music21.pitch.Pitch A#>),
     (<music21.pitch.Pitch E->, <music21.pitch.Pitch G>,
                                         <music21.pitch.Pitch B>)]
    >>> myChord = chord.Chord(['C', 'E-', 'F#', 'A'])
    >>> pList = myChord.pitches
    >>> tc = analysis.transposition.TranspositionChecker(pList)
    >>> allNormalOrderChords = tc.getChordsOfDistinctTranspositions()
    >>> allNormalOrderChords
    [<music21.chord.Chord C E- F# A>,
     <music21.chord.Chord C# E G A#>,
     <music21.chord.Chord D F G# B>]
    '''
    def __init__(self, pitches: Iterable[pitch.Pitch] = ()):
        if not pitches:
            raise TypeError(
                'Must have at least one element in list'
            )
        if not common.isIterable(pitches):
            raise TypeError('Must be a list or tuple')
        # p0 = pitches[0]
        # if not isinstance(p0, pitch.Pitch):
        #     raise TypeError('List must have pitch objects')
        self.pitches: Iterable[pitch.Pitch] = pitches
        self.allTranspositions: list = []
        self.allNormalOrders: list = []
        self.distinctNormalOrders: list = []

    def getTranspositions(self):
        # noinspection PyShadowingNames
        '''
        Gets all 12 transpositions (distinct or otherwise).

        >>> p = [pitch.Pitch('D#')]
        >>> tc = analysis.transposition.TranspositionChecker(p)
        >>> tc.getTranspositions()
        [[<music21.pitch.Pitch E->],
        [<music21.pitch.Pitch E>],
        [<music21.pitch.Pitch F>],
        [<music21.pitch.Pitch F#>],
        [<music21.pitch.Pitch G>],
        [<music21.pitch.Pitch G#>],
        [<music21.pitch.Pitch A>],
        [<music21.pitch.Pitch B->],
        [<music21.pitch.Pitch B>],
        [<music21.pitch.Pitch C>],
        [<music21.pitch.Pitch C#>],
        [<music21.pitch.Pitch D>]]
        '''
        allTranspositions = []
        for i in range(12):
            thisTransposition = []
            for p in self.pitches:
                thisTransposition.append(p.transpose(i))
            allTranspositions.append(thisTransposition)
        self.allTranspositions = allTranspositions
        return allTranspositions

    def listNormalOrders(self):
        '''
        List the normal orders for all 12 transpositions

        >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        >>> tc = analysis.transposition.TranspositionChecker(pList)
        >>> tc.listNormalOrders()
        [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11],
         [0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11],
         [0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
        '''
        if not self.allTranspositions:
            self.getTranspositions()
        allTranspositions = self.allTranspositions
        allNormalOrders = []
        for thisTransposition in allTranspositions:
            # pass
            c = chord.Chord(thisTransposition)
            thisNormalOrder = c.normalOrder
            allNormalOrders.append(thisNormalOrder)
        self.allNormalOrders = allNormalOrders
        return allNormalOrders

    def listDistinctNormalOrders(self):
        '''
        List the distinct normal orders (without duplication).

        >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        >>> tc = analysis.transposition.TranspositionChecker(pList)
        >>> tc.listDistinctNormalOrders()
        [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
        '''
        if not self.allNormalOrders:
            self.listNormalOrders()
        allNormalOrders = self.allNormalOrders
        seen = set()
        distinctNormalOrders = [x for x in allNormalOrders
                                if not (tuple(x) in seen or seen.add(tuple(x)))]
        self.distinctNormalOrders = distinctNormalOrders
        return distinctNormalOrders

    def numDistinctTranspositions(self):
        '''
        Gives the number of distinct transpositions (normal orders).

        >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        >>> tc = analysis.transposition.TranspositionChecker(pList)
        >>> tc.numDistinctTranspositions()
        4
        '''
        if not self.distinctNormalOrders:
            self.listDistinctNormalOrders()
        return len(self.distinctNormalOrders)

    def getChordsOfDistinctTranspositions(self):
        '''
        Outputs chords for each distinct transposition (normal order).

        >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        >>> tc = analysis.transposition.TranspositionChecker(pList)
        >>> tc.getChordsOfDistinctTranspositions()
        [<music21.chord.Chord C E G#>,
         <music21.chord.Chord C# F A>,
         <music21.chord.Chord D F# A#>,
         <music21.chord.Chord E- G B>]
        '''
        if not self.distinctNormalOrders:
            self.listDistinctNormalOrders()
        distinctNormalOrders = self.distinctNormalOrders
        allNormalOrderChords = []
        for thisNormalOrder in distinctNormalOrders:
            thisNormalOrderChord = chord.Chord(thisNormalOrder)
            allNormalOrderChords.append(thisNormalOrderChord)
        return allNormalOrderChords

    def getPitchesOfDistinctTranspositions(self):
        '''
        Outputs pitch tuples for each distinct transposition (normal order).

        >>> pList = [pitch.Pitch('C4'), pitch.Pitch('E4'), pitch.Pitch('G#4')]
        >>> tc = analysis.transposition.TranspositionChecker(pList)
        >>> tc.getPitchesOfDistinctTranspositions()
        [(<music21.pitch.Pitch C>, <music21.pitch.Pitch E>, <music21.pitch.Pitch G#>),
         (<music21.pitch.Pitch C#>, <music21.pitch.Pitch F>, <music21.pitch.Pitch A>),
         (<music21.pitch.Pitch D>, <music21.pitch.Pitch F#>, <music21.pitch.Pitch A#>),
         (<music21.pitch.Pitch E->, <music21.pitch.Pitch G>, <music21.pitch.Pitch B>)]
        '''
        chords = self.getChordsOfDistinctTranspositions()
        allNormalOrderPitchTuples = [c.pitches for c in chords]
        return allNormalOrderPitchTuples

# ------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
