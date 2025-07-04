# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         realizerScale.py
# Purpose:      a figured bass scale
# Authors:      Jose Cabal-Ugaz
#
# Copyright:    Copyright © 2010-2011 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

import copy
import itertools
from music21 import exceptions21
from music21 import note
from music21 import pitch
from music21 import key
from music21 import scale
from music21.figuredBass import notation
from music21.figuredBass.notation import convertToPitch

scaleModes = {'major': scale.MajorScale,
              'minor': scale.MinorScale,
              'dorian': scale.DorianScale,
              'phrygian': scale.PhrygianScale,
              'hypophrygian': scale.HypophrygianScale}

# ------------------------------------------------------------------------------

class FiguredBassScale:
    '''
    Acts as a wrapper for :class:`~music21.scale.Scale`. Used to represent the
    concept of a figured bass scale, with a scale value and mode.

    Accepted scale types: major, minor, dorian, phrygian, and hypophrygian.
    A FiguredBassScaleException is raised if an invalid scale type is provided.

    >>> from music21.figuredBass import realizerScale
    >>> fbScale = realizerScale.FiguredBassScale()
    >>> fbScale.realizerScale
    <music21.scale.MajorScale C major>
    >>> fbScale.keySig
    <music21.key.KeySignature of no sharps or flats>

    >>> fbScale = realizerScale.FiguredBassScale('d', 'minor')
    >>> fbScale.realizerScale
    <music21.scale.MinorScale D minor>
    >>> fbScale.keySig
    <music21.key.KeySignature of 1 flat>
    '''
    _DOC_ATTR: dict[str, str] = {
        'realizerScale': '''
            A :class:`~music21.scale.Scale` based on the
            desired value and mode.
            ''',
        'keySig': '''
            A :class:`~music21.key.KeySignature` corresponding to
            the scale value and mode.
            ''',
    }

    def __init__(self, scaleValue='C', scaleMode='major'):
        try:
            scaleClass = scaleModes[scaleMode]
            self.realizerScale = scaleClass(scaleValue)
            self.keySig = key.KeySignature(key.pitchToSharps(scaleValue, scaleMode))
        except KeyError:
            raise FiguredBassScaleException('Unsupported scale type-> ' + scaleMode)

    def getPitchNames(self, bassPitch, notationString=None):
        '''
        Takes a bassPitch and notationString and returns a list of corresponding
        pitch names based on the scale value and mode above and inclusive of the
        bassPitch name.

        >>> from music21.figuredBass import realizerScale
        >>> fbScale = realizerScale.FiguredBassScale()
        >>> fbScale.getPitchNames('D3', '6')
        ['D', 'F', 'B']
        >>> fbScale.getPitchNames('G3')
        ['G', 'B', 'D']
        >>> fbScale.getPitchNames('B3', '6,#5')
        ['B', 'D', 'F#', 'G']
        >>> fbScale.getPitchNames('C#3', '-7')  # Fully diminished seventh chord
        ['C#', 'E', 'G', 'B-']
        '''
        bassPitch = convertToPitch(bassPitch)  # Convert string to pitch (if necessary)
        bassSD = self.realizerScale.getScaleDegreeFromPitch(bassPitch)
        nt = notation.Notation(notationString)

        if bassSD is None:
            bassPitchCopy = copy.deepcopy(bassPitch)
            bassNote = note.Note(bassPitchCopy)
            if (self.keySig.accidentalByStep(bassNote.pitch.step)
                    != bassNote.pitch.accidental):
                bassNote.pitch.accidental = self.keySig.accidentalByStep(bassNote.pitch.step)
            bassSD = self.realizerScale.getScaleDegreeFromPitch(bassNote.pitch)

        pitchNames = []
        for i in range(len(nt.numbers)):
            pitchSD = (bassSD + nt.numbers[i] - 1) % 7
            samplePitch = self.realizerScale.pitchFromDegree(pitchSD)
            pitchName = nt.modifiers[i].modifyPitchName(samplePitch.name)
            pitchNames.append(pitchName)

        pitchNames.append(bassPitch.name)
        pitchNames.reverse()
        return pitchNames

    def getSamplePitches(self, bassPitch, notationString=None):
        '''
        Returns all pitches for a bassPitch and notationString within
        an octave of the bassPitch, inclusive of the bassPitch but
        exclusive at the upper bound. In other words, this method
        returns the most compact complete chord implied by the bassPitch
        and its figures.

        >>> from music21.figuredBass import realizerScale
        >>> fbScale = realizerScale.FiguredBassScale()

        >>> fbScale.getSamplePitches('D3', '6')  # First inversion triad
        [<music21.pitch.Pitch D3>, <music21.pitch.Pitch F3>, <music21.pitch.Pitch B3>]

        Root position triad

        >>> [str(p) for p in fbScale.getSamplePitches('G3') ]
        ['G3', 'B3', 'D4']

        First inversion seventh chord

        >>> [str(p) for p in fbScale.getSamplePitches('B3', '6,5') ]
        ['B3', 'D4', 'F4', 'G4']

        Neapolitan chord

        >>> [str(p) for p in fbScale.getSamplePitches('F3', '-6,-') ]
        ['F3', 'A-3', 'D-4']

        Second inversion seventh chord

        >>> [str(p) for p in fbScale.getSamplePitches('C5', '4,3') ]
        ['C5', 'E5', 'F5', 'A5']

        Fully diminished seventh chord

        >>> [str(p) for p in fbScale.getSamplePitches('C#3', '-7') ]
        ['C#3', 'E3', 'G3', 'B-3']
        '''
        bassPitch = convertToPitch(bassPitch)  # Convert string to pitch (if necessary)
        maxPitch = bassPitch.transpose('d8')

        samplePitches = self.getPitches(bassPitch, notationString, maxPitch)
        return samplePitches

    def getPitches(self, bassPitch, notationString=None, maxPitch=None):
        '''
        Takes in a bassPitch, a notationString, and a maxPitch representing the highest
        possible pitch that can be returned. Returns a sorted list of pitches which
        correspond to the pitches of each specific pitch name found through getPitchNames
        that fall between the bassPitch and the maxPitch, inclusive of both.

        if maxPitch is None, then B5 s used instead.

        >>> from music21.figuredBass import realizerScale
        >>> fbScale = realizerScale.FiguredBassScale()

        Root position triad

        >>> [str(p) for p in fbScale.getPitches('C3') ]
        ['C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'C5', 'E5', 'G5']

        First inversion triad

        >>> [str(p) for p in fbScale.getPitches('D3', '6') ]
        ['D3', 'F3', 'B3', 'D4', 'F4', 'B4', 'D5', 'F5', 'B5']

        Root position seventh chord, showing MaxPitch

        >>> fbScale.getPitches(pitch.Pitch('G3'), '7', 'F4')
        [<music21.pitch.Pitch G3>, <music21.pitch.Pitch B3>,
         <music21.pitch.Pitch D4>, <music21.pitch.Pitch F4>]
        '''
        if maxPitch is None:
            maxPitch = pitch.Pitch('B5')

        bassPitch = convertToPitch(bassPitch)
        maxPitch = convertToPitch(maxPitch)
        pitchNames = self.getPitchNames(bassPitch, notationString)
        iter1 = itertools.product(pitchNames, range(maxPitch.octave + 1))
        iter2 = map(lambda x: pitch.Pitch(x[0] + str(x[1])), iter1)
        iter3 = itertools.filterfalse(lambda samplePitch: bassPitch > samplePitch, iter2)
        iter4 = itertools.filterfalse(lambda samplePitch: samplePitch > maxPitch, iter3)
        allPitches = list(iter4)
        allPitches.sort()
        return allPitches

    def _reprInternal(self):
        return f'{self.realizerScale!r}'

class FiguredBassScaleException(exceptions21.Music21Exception):
    pass

# ------------------------------------------------------------------------------
