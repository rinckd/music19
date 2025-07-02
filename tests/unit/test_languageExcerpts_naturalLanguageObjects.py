# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.languageExcerpts.naturalLanguageObjects import *


class Test(unittest.TestCase):

    def testConvertPitches(self):
        # testing defaults in case of invalid language and invalid input
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', '')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', '')))

        # testing defaults in case of invalid language and valid input
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Eis', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Eis', '')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('H', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('H', '')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Sol', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Sol', '')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Re', 'hello')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('Re', '')))

        # testing defaults in case of invalid input string and valid language
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', 'de')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', 'de')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', 'fr')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', 'fr')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', 'es')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', 'es')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('hello', 'it')))
        self.assertEqual('<music21.pitch.Pitch C>', repr(toPitch('', 'it')))

        # testing defaults in case of valid input string and valid language
        self.assertEqual('<music21.pitch.Pitch C##>', repr(toPitch('do doppio diesis',
                                                                   'it')))
        self.assertEqual('<music21.pitch.Pitch F##>', repr(toPitch('fa doble sostenido',
                                                                   'es')))
        self.assertEqual('<music21.pitch.Pitch G--->', repr(toPitch('sol triple bemol',
                                                                    'es')))
        self.assertEqual('<music21.pitch.Pitch D>', repr(toPitch('re', 'it')))
        self.assertEqual('<music21.pitch.Pitch B-->', repr(toPitch('Heses', 'de')))
        self.assertEqual('<music21.pitch.Pitch E##>', repr(toPitch('Eisis', 'de')))
        self.assertEqual('<music21.pitch.Pitch A####>',
                         repr(toPitch('la quadruple dièse', 'fr')))
        self.assertEqual('<music21.pitch.Pitch B--->', repr(toPitch('si triple bémol', 'fr')))

    def testConvertNotes(self):
        # testing defaults in case of invalid language and invalid input
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', '')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', '')))

        # testing defaults in case of invalid language and valid input
        self.assertEqual('<music21.note.Note C>', repr(toNote('Eis', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('Eis', '')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('H', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('H', '')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('Sol', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('Sol', '')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('Re', 'hello')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('Re', '')))

        # testing defaults in case of invalid input string and valid language
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', 'de')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', 'de')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', 'fr')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', 'fr')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', 'es')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', 'es')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('hello', 'it')))
        self.assertEqual('<music21.note.Note C>', repr(toNote('', 'it')))

        # testing defaults in case of valid input string and valid language
        self.assertEqual('<music21.note.Note C##>', repr(toNote('do doppio diesis', 'it')))
        self.assertEqual('<music21.note.Note F##>', repr(toNote('fa doble sostenido', 'es')))
        self.assertEqual('<music21.note.Note G--->', repr(toNote('sol triple bemol', 'es')))
        self.assertEqual('<music21.note.Note D>', repr(toNote('re', 'it')))
        self.assertEqual('<music21.note.Note B-->', repr(toNote('Heses', 'de')))
        self.assertEqual('<music21.note.Note E##>', repr(toNote('Eisis', 'de')))
        self.assertEqual('<music21.note.Note A####>',
                            repr(toNote('la quadruple dièse', 'fr')))
        self.assertEqual('<music21.note.Note B--->', repr(toNote('si triple bémol', 'fr')))

    def testConvertChords(self):
        # testing defaults in case of invalid language and no input
        self.assertEqual((), toChord([], '').pitches)
        self.assertEqual((), toChord([], 'hello').pitches)

        # testing defaults in case of valid language and no input
        self.assertEqual((), toChord([], 'de').pitches)
        self.assertEqual((), toChord([], 'fr').pitches)
        self.assertEqual((), toChord([], 'es').pitches)
        self.assertEqual((), toChord([], 'it').pitches)

        # testing defaults in case of invalid language and valid list
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Eis'], 'hello')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Eis'], '')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['H'], 'hello')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['H'], '')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Sol'], 'hello')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Sol'], '')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Re'], 'hello')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['Re'], '')))

        # testing defaults in case of invalid input list and valid language
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['hello'], 'de')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord([''], 'de')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['hello'], 'fr')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord([''], 'fr')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['hello'], 'es')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord([''], 'es')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord(['hello'], 'it')))
        self.assertEqual('<music21.chord.Chord C>', repr(toChord([''], 'it')))

        # testing defaults in case of valid input list and valid language
        self.assertEqual('<music21.chord.Chord C##>',
                         repr(toChord(['do doppio diesis'], 'it')))
        self.assertEqual('<music21.chord.Chord F##>',
                         repr(toChord(['fa doble sostenido'], 'es')))
        self.assertEqual('<music21.chord.Chord G--->',
                         repr(toChord(['sol triple bemol'], 'es')))
        self.assertEqual('<music21.chord.Chord D>', repr(toChord(['re'], 'it')))
        self.assertEqual('<music21.chord.Chord B-->', repr(toChord(['Heses'], 'de')))
        self.assertEqual('<music21.chord.Chord E##>', repr(toChord(['Eisis'], 'de')))
        self.assertEqual('<music21.chord.Chord A####>',
                         repr(toChord(['la quadruple dièse'], 'fr')))
        self.assertEqual('<music21.chord.Chord B--->',
                         repr(toChord(['si triple bémol'], 'fr')))

        self.assertEqual('<music21.chord.Chord C## D>',
                         repr(toChord(['do doppio diesis', 're'], 'it')))
        self.assertEqual('<music21.chord.Chord F## G--->',
                         repr(toChord(['fa doble sostenido', 'sol triple bemol'], 'es')))
        self.assertEqual('<music21.chord.Chord B-- E##>',
                         repr(toChord(['Heses', 'Eisis'], 'de')))
        self.assertEqual('<music21.chord.Chord A#### B--->',
                         repr(toChord(['la quadruple dièse', 'si triple bémol'], 'fr')))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
