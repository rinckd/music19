# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         naturalLanguageObjects.py
# Purpose:      Multilingual conversion of pitch, etc. objects
# Authors:      David Perez
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2014-2016 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Multilingual conversion of pitch, etc. objects
'''
from __future__ import annotations

from music21 import pitch

SUPPORTED_LANGUAGES = ['de', 'fr', 'it', 'es']
SUPPORTED_ACCIDENTALS = ['----', '---', '--', '-', '', '#', '##', '###', '####']
SUPPORTED_MICROTONES = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

def generateLanguageDictionary(languageString):

    # Helper method for toPitch

    # Generates a dictionary that allows the conversion of pitches from any language supported,
    # consistent with the standards set by pitch.py

    if languageString not in SUPPORTED_LANGUAGES:
        return {}

    dictionary = {}
    pitchStrings = []

    for microtone in SUPPORTED_MICROTONES:
        for accidental in SUPPORTED_ACCIDENTALS:
            pitchStrings.append(microtone + accidental)

    if languageString == 'de':
        for pitchString in pitchStrings:
            p = pitch.Pitch(pitchString)
            dictionary[p.german] = pitchString
    elif languageString == 'fr':
        for pitchString in pitchStrings:
            p = pitch.Pitch(pitchString)
            dictionary[p.french] = pitchString
    elif languageString == 'it':
        for pitchString in pitchStrings:
            p = pitch.Pitch(pitchString)
            dictionary[p.italian] = pitchString
    elif languageString == 'es':
        for pitchString in pitchStrings:
            p = pitch.Pitch(pitchString)
            dictionary[p.spanish] = pitchString

    return dictionary

def toPitch(pitchString, languageString):
    '''
    Converts a string to a :class:`music21.pitch.Pitch` object given a language.

    Supported languages are French, German, Italian, and Spanish

    Defaults to C natural

    >>> languageExcerpts.naturalLanguageObjects.toPitch('Es', 'de')
    <music21.pitch.Pitch E->

    >>> languageExcerpts.naturalLanguageObjects.toPitch('H', 'de')
    <music21.pitch.Pitch B>
    >>> for i in ['As', 'A', 'Ais']:
    ...     print(languageExcerpts.naturalLanguageObjects.toPitch(i, 'de'))
    A-
    A
    A#
    '''
    langDict = generateLanguageDictionary(languageString)
    if pitchString not in langDict:
        return pitch.Pitch('C')

    return pitch.Pitch(langDict[pitchString])

def toNote(pitchString, languageString):
    '''
    Converts a string to a :class:`music21.note.Note` object given a language

    Supported languages are French, German, Italian, and Spanish

    Defaults to C Natural

    >>> languageExcerpts.naturalLanguageObjects.toNote('Es', 'de')
    <music21.note.Note E->

    >>> languageExcerpts.naturalLanguageObjects.toNote('H', 'de')
    <music21.note.Note B>
    >>> for i in ['As', 'A', 'Ais']:
    ...     print(languageExcerpts.naturalLanguageObjects.toNote(i, 'de'))
    <music21.note.Note A->
    <music21.note.Note A>
    <music21.note.Note A#>
    '''

    from music21 import note

    return note.Note(toPitch(pitchString, languageString))

def toChord(pitchArray, languageString):
    '''
    Converts a list of strings to a :class:`music21.chord.Chord` object given a language

    Supported languages are French, German, Italian, and Spanish

    Unsupported strings default to pitch C Natural

    >>> languageExcerpts.naturalLanguageObjects.toChord(['Es', 'E', 'Eis'], 'de')
    <music21.chord.Chord E- E E#>
    '''
    from music21 import chord

    noteList = [toNote(pitchObj, languageString) for pitchObj in pitchArray]
    return chord.Chord(noteList)

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# define presented order in documentation

_DOC_ORDER: list[type] = []
