# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.harmony import *


class Test(unittest.TestCase):

    def testChordAttributes(self):
        from music21 import harmony
        cs = harmony.ChordSymbol('Cm')
        self.assertEqual(str(cs), '<music21.harmony.ChordSymbol Cm>')
        self.assertEqual(
            str(cs.pitches),
            '(<music21.pitch.Pitch C3>, <music21.pitch.Pitch E-3>, <music21.pitch.Pitch G3>)')
        self.assertEqual(str(cs.bass()), 'C3')
        self.assertTrue(cs.isConsonant())

    def testBasic(self):
        from music21 import harmony
        h = harmony.Harmony()
        hd = harmony.ChordStepModification('add', 4)
        h.addChordStepModification(hd)
        self.assertEqual(len(h.chordStepModifications), 1)

    def testChordKindSetting(self):
        from music21 import harmony
        cs = harmony.ChordSymbol()
        cs.root('E-')
        cs.bass('B-', allow_add=True)
        cs.inversion(2, transposeOnSet=False)
        cs.romanNumeral = 'I64'
        cs.chordKind = 'major'
        cs.chordKindStr = 'M'
        self.assertEqual(repr(cs), '<music21.harmony.ChordSymbol E-/B->')

    def testDoubleSharpsEtc(self):
        # noinspection SpellCheckingInspection
        cisisdim = chord.Chord(('c##5', 'e#5', 'g#5'))
        fig = chordSymbolFigureFromChord(cisisdim)
        self.assertEqual(fig, 'C##dim')

    def testChordSymbolSetsBassOctave(self):
        d = ChordSymbol('Cm/E-')
        root = d.root()
        self.assertEqual(root.nameWithOctave, 'C4')
        b = d.bass()
        self.assertEqual(b.nameWithOctave, 'E-3')

    def testHarmonyPreservesInversionAndBass(self):
        '''
        Test that bass is preserved even when both bass and inversion are given
        '''
        explicitFm6 = ChordSymbol(root='F', bass='A-', inversion=1, kind='minor')
        self.assertEqual(explicitFm6.inversion(), 1)
        self.assertEqual(explicitFm6.bass(find=False).name, 'A-')
        self.assertEqual(explicitFm6.root(find=False).name, 'F')
        self.assertLess(explicitFm6.bass(find=False).octave,
                        explicitFm6.root(find=False).octave)

    def testClassSortOrderHarmony(self):
        '''
        This tests a former bug in getContextByClass
        because ChordSymbol used to have the same `.classSortOrder`
        as Note.
        '''
        from music21 import note
        from music21 import stream

        cs = ChordSymbol('C')
        n = note.Note('C')
        m = stream.Measure(1)

        m.insert(0, n)
        m.insert(0, cs)
        self.assertIs(n.getContextByClass('ChordSymbol'), cs)

        # check that it works also with append
        cs = ChordSymbol('C')
        n = note.Note('C')
        n.duration.quarterLength = 0
        m = stream.Measure(1)
        m.append(n)
        m.append(cs)
        self.assertIs(n.getContextByClass('ChordSymbol'), cs)

    def testNoChord(self):
        from music21 import harmony
        nc = harmony.NoChord()
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('N.C.', nc.chordKindStr)
        self.assertEqual('N.C.', nc.figure)

        nc = harmony.NoChord('NC')
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('NC', nc.chordKindStr)
        self.assertEqual('NC', nc.figure)

        nc = harmony.NoChord('None')
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('None', nc.chordKindStr)
        self.assertEqual('None', nc.figure)

        nc = harmony.NoChord(kind='none')
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('N.C.', nc.chordKindStr)
        self.assertEqual('N.C.', nc.figure)

        nc = harmony.NoChord(kindStr='No Chord')
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('No Chord', nc.chordKindStr)
        self.assertEqual('No Chord', nc.figure)

        nc = harmony.NoChord('NC', kindStr='No Chord')
        self.assertEqual('none', nc.chordKind)
        self.assertEqual('No Chord', nc.chordKindStr)
        self.assertEqual('NC', nc.figure)

        nc = harmony.NoChord(root='C', bass='E', kind='none')
        self.assertEqual('N.C.', nc.chordKindStr)
        self.assertEqual('N.C.', nc.figure)

        self.assertEqual(str(nc), '<music21.harmony.NoChord N.C.>')
        self.assertEqual(0, len(nc.pitches))
        self.assertIsNone(nc.root())
        self.assertIsNone(nc.bass())

        nc._updatePitches()
        self.assertEqual(0, len(nc.pitches))

    def testInvalidRoots(self):
        from music21 import harmony
        with self.assertRaises(ValueError) as context:
            harmony.ChordSymbol('H-7')

        self.assertEqual(
            str(context.exception),
            'Chord H-7 does not begin with a valid root note.'
        )

        with self.assertRaises(ValueError) as context:
            # noinspection SpellCheckingInspection
            harmony.ChordSymbol('Garg7')

        self.assertEqual(
            str(context.exception),
            "Invalid chord abbreviation 'arg7'; see "
            + 'music21.harmony.CHORD_TYPES for valid '
            + 'abbreviations or specify all alterations.'
        )

    def testInvalidSymbol(self):
        from music21 import harmony
        c = chord.Chord(('A#', 'C', 'E'))
        cs = harmony.chordSymbolFromChord(c)
        self.assertEqual(cs.figure, 'Chord Symbol Cannot Be Identified')

    def testRegexEdgeCases(self):
        cs = ChordSymbol('FFr+6')
        self.assertEqual([p.name for p in cs.pitches], ['F', 'G', 'B', 'D-'])
        cs = ChordSymbol('dadd6')
        self.assertEqual([p.name for p in cs.pitches], ['D', 'F#', 'A', 'B'])
        cs = ChordSymbol('atristan')
        self.assertEqual([p.name for p in cs.pitches], ['A', 'B#', 'D#', 'F##'])


    def runTestOnChord(self, xmlString, figure, pitches):
        '''
        Run a series of tests on the given chord.

        xmlString: an XML harmony object

        figure: the equivalent figure representation

        pitches: the list of pitches of the chord
        '''
        from xml.etree.ElementTree import fromstring as EL
        from music21 import musicxml

        pitches = tuple(pitch.Pitch(p) for p in pitches)

        MP = musicxml.xmlToM21.MeasureParser()
        mxHarmony = EL(xmlString)

        cs1 = MP.xmlToChordSymbol(mxHarmony)
        cs2 = ChordSymbol(cs1.figure)
        cs3 = ChordSymbol(figure)

        self.assertEqual(pitches, cs1.pitches)
        self.assertEqual(pitches, cs2.pitches)
        self.assertEqual(pitches, cs3.pitches)

        kind1 = cs1.chordKind
        kind2 = cs2.chordKind
        kind3 = cs3.chordKind
        if kind1 in CHORD_ALIASES:
            kind1 = CHORD_ALIASES[kind1]
        if kind2 in CHORD_ALIASES:
            kind2 = CHORD_ALIASES[kind2]
        if kind3 in CHORD_ALIASES:
            kind3 = CHORD_ALIASES[kind3]
        self.assertEqual(kind1, kind2)
        self.assertEqual(kind1, kind3)

        self.assertEqual(cs1.root(), cs2.root())
        self.assertEqual(cs1.root(), cs3.root())

        self.assertEqual(cs1.bass(), cs2.bass())
        self.assertEqual(cs1.bass(), cs3.bass())

    def testChordWithBass(self):

        xmlString = '''
          <harmony>
            <root>
              <root-step>A</root-step>
            </root>
            <kind text="7">dominant</kind>
            <inversion>3</inversion>
            <bass>
              <bass-step>G</bass-step>
            </bass>
          </harmony>
          '''
        figure = 'A7/G'
        pitches = ('G2', 'A2', 'C#3', 'E3')

        self.runTestOnChord(xmlString, figure, pitches)

    def testChordFlatSharpInFigure(self):
        # Octave placement of this A2 neither great nor intolerable
        pitches = ('G2', 'A2', 'B2', 'D#3', 'F3')
        figure = 'G+9'
        cs = ChordSymbol(figure)
        self.assertEqual(cs.pitches, tuple(pitch.Pitch(p) for p in pitches))

        pitches = ('G2', 'B2', 'D#3', 'F3', 'A3')
        figure = 'G9#5'
        cs = ChordSymbol(figure)
        self.assertEqual(cs.pitches, tuple(pitch.Pitch(p) for p in pitches))

        pitches = ('A2', 'C3', 'E3', 'G#3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)
        self.assertEqual(pitches, ChordSymbol('AmM7').pitches)
        self.assertEqual(pitches, ChordSymbol('Aminmaj7').pitches)
        pitches = ('A1', 'C2', 'E2', 'G#3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)
        self.assertEqual(pitches, ChordSymbol('Am#7').pitches)

        pitches = ('C2', 'F2', 'G2', 'B-3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)
        self.assertEqual(pitches, ChordSymbol('Csusaddb7').pitches)

    def testRootBassParsing(self):
        '''
        This tests a bug where the root and bass were wrongly parsed,
        since the matched root and bass were globally removed from figure,
        and not only where matched.
        '''

        xmlString = '''
          <harmony>
            <root>
              <root-step>E</root-step>
            </root>
            <kind text="7">dominant</kind>
            <bass>
              <bass-step>E</bass-step>
              <bass-alter>-1</bass-alter>
            </bass>
          </harmony>
        '''
        figure = 'E7/E-'
        pitches = ('E-2', 'E3', 'G#3', 'B3', 'D4')
        self.runTestOnChord(xmlString, figure, pitches)


    def testChordStepBass(self):
        '''
        This tests a bug where the chord modification (add 2) was placed at a
        wrong octave, resulting in a D bass instead of the proper E.
        '''

        xmlString = '''
          <harmony>
            <root>
              <root-step>C</root-step>
            </root>
            <kind>major</kind>
            <bass>
              <bass-step>E</bass-step>
            </bass>
            <degree>
              <degree-value>2</degree-value>
              <degree-alter>0</degree-alter>
              <degree-type text="add">add</degree-type>
            </degree>
          </harmony>
           '''
        figure = 'C/E add 2'
        pitches = ('E3', 'G3', 'C4', 'D4')

        self.runTestOnChord(xmlString, figure, pitches)

    def testSusBass(self):
        '''
        This tests a bug where the bass addition was considered as the fifth
        inversion in suspended chords. Now, this is considered as a non-valid
        inversion, and the bass is simply added before the root.
        '''
        from xml.etree.ElementTree import fromstring as EL
        from music21 import musicxml

        pitches = ('G2', 'D3', 'G3', 'A3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)

        xmlString = '''
          <harmony>
            <root>
              <root-step>D</root-step>
            </root>
            <kind text="sus">suspended-fourth</kind>
            <bass>
              <bass-step>G</bass-step>
            </bass>
          </harmony>
         '''

        MP = musicxml.xmlToM21.MeasureParser()
        mxHarmony = EL(xmlString)

        cs1 = MP.xmlToChordSymbol(mxHarmony)
        cs2 = ChordSymbol(cs1.figure)
        cs3 = ChordSymbol('Dsus/G')

        self.assertEqual(pitches, cs1.pitches)
        self.assertEqual(pitches, cs2.pitches)
        self.assertEqual(pitches, cs3.pitches)

    def testBassNotInChord(self):
        from xml.etree.ElementTree import fromstring as EL
        from music21 import musicxml

        pitches = ('E-3', 'E3', 'G3', 'C4')
        pitches = tuple(pitch.Pitch(p) for p in pitches)

        xmlString = '''
          <harmony>
            <root>
              <root-step>C</root-step>
            </root>
            <kind text="">major</kind>
            <bass>
              <bass-step>E-</bass-step>
            </bass>
          </harmony>
         '''

        MP = musicxml.xmlToM21.MeasureParser()
        mxHarmony = EL(xmlString)

        cs1 = MP.xmlToChordSymbol(mxHarmony)
        cs2 = ChordSymbol(cs1.figure)
        cs3 = ChordSymbol('C/E-')

        self.assertEqual(pitches, cs1.pitches)
        self.assertEqual(pitches, cs2.pitches)
        self.assertEqual(pitches, cs3.pitches)

        # There was a bug where the bass was E3, because E-3 was assumed to be
        # in the chord.
        self.assertEqual('E-3', cs1.bass().nameWithOctave)

    def testSus2Bass(self):
        from xml.etree.ElementTree import fromstring as EL
        from music21 import musicxml

        pitches = ('E3', 'G3', 'C4', 'D4')
        pitches = tuple(pitch.Pitch(p) for p in pitches)

        xmlString = '''
          <harmony>
            <root>
              <root-step>C</root-step>
            </root>
            <kind text="sus2">suspended-second</kind>
            <bass>
              <bass-step>E</bass-step>
            </bass>
          </harmony>
       '''

        MP = musicxml.xmlToM21.MeasureParser()
        mxHarmony = EL(xmlString)

        cs1 = MP.xmlToChordSymbol(mxHarmony)
        cs2 = ChordSymbol(cs1.figure)
        cs3 = ChordSymbol('Csus2/E')

        self.assertEqual('E3', cs1.bass().nameWithOctave)

        self.assertEqual(pitches, cs1.pitches)
        self.assertEqual(pitches, cs2.pitches)
        self.assertEqual(pitches, cs3.pitches)

    def testNinth(self):
        '''
        This tests a bug in _adjustOctaves.
        '''

        xmlString = '''
        <harmony >
            <root>
              <root-step>D</root-step>
            </root>
            <kind text="min9">minor-ninth</kind>
        </harmony>
           '''
        pitches = ('D2', 'F2', 'A2', 'C3', 'E3')
        figure = 'Dm9'

        self.runTestOnChord(xmlString, figure, pitches)

    def testInversion(self):
        from xml.etree.ElementTree import fromstring as EL
        from music21 import musicxml

        xmlString = '''
        <harmony>
          <root>
            <root-step>C</root-step>
          </root>
          <kind>major</kind>
          <inversion>1</inversion>
        </harmony>
        '''

        pitches = ('E2', 'G2', 'C3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)

        MP = musicxml.xmlToM21.MeasureParser()
        mxHarmony = EL(xmlString)

        cs1 = MP.xmlToChordSymbol(mxHarmony)
        cs2 = ChordSymbol('C/E')

        self.assertEqual(1, cs1.inversion())
        self.assertEqual(1, cs2.inversion())

        pitches = ('E3', 'G3', 'C4')
        pitches = tuple(pitch.Pitch(p) for p in pitches)
        self.assertEqual(cs1.pitches, pitches)
        self.assertEqual(cs2.pitches, pitches)

        self.assertEqual(cs1.root(), cs2.root())
        self.assertEqual(cs1.bass(), cs2.bass())

    def testChordWithoutKind(self):
        cs = ChordSymbol(root='C', bass='E')

        self.assertEqual(1, cs.inversion())
        self.assertEqual('C4', str(cs.root()))
        self.assertEqual('E3', str(cs.bass()))


    def testChordStepFromFigure(self):
        xmlString = '''
          <harmony>
            <root>
              <root-step>G</root-step>
            </root>
            <kind text="7alt">dominant</kind>
            <degree>
              <degree-value>5</degree-value>
              <degree-alter>0</degree-alter>
              <degree-type>subtract</degree-type>
            </degree>
            <degree>
              <degree-value>9</degree-value>
              <degree-alter>-1</degree-alter>
              <degree-type>add</degree-type>
            </degree>
            <degree>
              <degree-value>9</degree-value>
              <degree-alter>1</degree-alter>
              <degree-type>add</degree-type>
            </degree>
            <degree>
              <degree-value>11</degree-value>
              <degree-alter>1</degree-alter>
              <degree-type>add</degree-type>
            </degree>
            <degree>
              <degree-value>13</degree-value>
              <degree-alter>-1</degree-alter>
              <degree-type>add</degree-type>
            </degree>
          </harmony>
        '''
        figure = 'G7 subtract 5 add b9 add #9 add #11 add b13'
        pitches = ('G2', 'B2', 'F3', 'A-3', 'A#3', 'C#4', 'E-4')
        self.runTestOnChord(xmlString, figure, pitches)

        figure = 'G7 subtract5 addb9 add#9 add#11 addb13'
        self.runTestOnChord(xmlString, figure, pitches)

        figure = 'G7subtract5addb9add#9add#11addb13'
        self.runTestOnChord(xmlString, figure, pitches)

        #########

        xmlString = '''
            <harmony>
            <root>
              <root-step>C</root-step>
            </root>
            <kind text="7b9">dominant</kind>
            <degree>
              <degree-value>9</degree-value>
              <degree-alter>-1</degree-alter>
              <degree-type>add</degree-type>
            </degree>
          </harmony>
        '''
        figure = 'C7 b9'
        pitches = ('C3', 'E3', 'G3', 'B-3', 'D-4')

        self.runTestOnChord(xmlString, figure, pitches)

        figure = 'C7 add b9'
        self.runTestOnChord(xmlString, figure, pitches)

        # Test alter
        cs = ChordSymbol('A7 alter #5')
        self.assertEqual('(<music21.pitch.Pitch A2>, <music21.pitch.Pitch '
                         'C#3>, <music21.pitch.Pitch E#3>, '
                         '<music21.pitch.Pitch G3>)', str(cs.pitches))

        #########

        xmlString = '''
          <harmony>
            <root>
              <root-step>A</root-step>
              </root>
            <kind>dominant</kind>
            <degree>
              <degree-value>5</degree-value>
              <degree-alter>1</degree-alter>
              <degree-type>alter</degree-type>
              </degree>
            <degree>
              <degree-value>9</degree-value>
              <degree-alter>1</degree-alter>
              <degree-type>add</degree-type>
              </degree>
            <degree>
              <degree-value>11</degree-value>
              <degree-alter>1</degree-alter>
              <degree-type>add</degree-type>
              </degree>
            </harmony>
        '''
        figure = 'A7 alter #5 add #9 add #11'
        pitches = ('A2', 'C#3', 'E#3', 'G3', 'B#3', 'D#4')

        self.runTestOnChord(xmlString, figure, pitches)

    def testExpressSusUsingAlterations(self):
        ch1 = ChordSymbol('F7 add 4 subtract 3')
        ch2 = ChordSymbol('F7sus4')

        self.assertEqual(ch1.pitches, ch2.pitches)

    def testDoubledCharacters(self):
        ch1 = ChordSymbol('Co omit5')
        ch2 = ChordSymbol('Cdim omit5')

        self.assertEqual(ch1.pitches, ch2.pitches)

    def x_testPower(self):
        '''
        power chords should not have inversions
        '''
        pitches = ('E2', 'A2', 'E3')
        pitches = tuple(pitch.Pitch(p) for p in pitches)

        xmlString = '''
          <harmony>
            <root>
              <root-step>A</root-step>
            </root>
            <kind text="5">power</kind>
            <bass>
              <bass-step>E</bass-step>
            </bass>
          </harmony>
        '''
        figure = 'Apower/E'

        self.runTestOnChord(xmlString, figure, pitches)

    def testSingleChordSymbol(self):
        '''
        Test an edge case where a Stream contains only one ChordSymbol
        at the highest offset: should still have a nonzero duration
        if there is a subsequent highest time.
        '''
        from music21 import note
        from music21 import stream

        m = stream.Measure()  # NB: no barline!
        cs = ChordSymbol('A7')
        m.insert(0, note.Note(type='whole'))
        m.insert(1.0, cs)
        realizeChordSymbolDurations(m)
        self.assertEqual(cs.quarterLength, 3.0)

    def testUpdatePitchesFalse(self):
        bass_note = pitch.Pitch('C3')
        h = Harmony(bass=bass_note, updatePitches=False)
        # No other pitches are created
        self.assertEqual(h.pitches, (bass_note,))


class TestExternal(unittest.TestCase):

    def testReadInXML(self):
        from music21 import harmony
        from music21 import corpus
        from music21 import stream
        testFile = corpus.parse('leadSheet/fosterBrownHair.xml')

        # testFile.show('text')
        testFile = harmony.realizeChordSymbolDurations(testFile)
        # testFile.show()
        chordSymbols = testFile.flatten().getElementsByClass(harmony.ChordSymbol)
        s = stream.Stream()

        for cS in chordSymbols:
            cS.writeAsChord = False
            s.append(cS)

        # csChords = s.flatten().getElementsByClass(chord.Chord)
        # s.show()
        # self.assertEqual(len(csChords), 40)

    def testChordRealization(self):
        from music21 import harmony
        from music21 import corpus
        from music21 import note
        from music21 import stream
        # There is a test file under demos called ComprehensiveChordSymbolsTestFile.xml
        # that should contain a complete iteration of tests of chord symbol objects
        # this test makes sure that no error exists, and checks that 57 chords were
        # created out of that file.  Feel free to add to file if you find missing
        # tests, and adjust 57 accordingly
        testFile = corpus.parse('demos/ComprehensiveChordSymbolsTestFile.xml')

        testFile = harmony.realizeChordSymbolDurations(testFile)
        chords = testFile.flatten().getElementsByClass(harmony.ChordSymbol)
        # testFile.show()
        s = stream.Stream()
        # i = 0
        for x in chords:
            # print(x.pitches)
            x.quarterLength = 0
            s.insert(x.offset, x)
            # i += 4
            #
            # x.show()

        s.makeRests(fillGaps=True, inPlace=True)
        s.append(note.Rest(quarterLength=4))
        unused_csChords = s.flatten().getElementsByClass(chord.Chord)
        # self.assertEqual(len(csChords), 57)
        # s.show()
        # s.show('text')

    def testALLChordKinds(self):
        notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        mod = ['', '-', '#']
        for n in notes:
            for m in mod:
                for unused_key, val in CHORD_TYPES.items():
                    # example val = ['1,-3,5,6', ['m6', 'min6']]
                    for harmony_type in val[1]:
                        symbol = n + m + harmony_type
                        ChordSymbol(symbol)

    # def labelChordSymbols(self):
    #     '''
    #     A very rough sketch of code to label the chord symbols in a bach
    #     chorale (in response to a post to the music21 list asking if this is
    #     possible).
    #     '''
    #     from music21.alpha.theoryAnalysis import theoryAnalyzer
    #     from music21 import harmony, corpus
    #
    #     score = corpus.parse('bach/bwv380')
    #     excerpt = score.measures(2, 3)
    #
    #     # remove passing and/or neighbor tones?
    #     analyzer = theoryAnalyzer.Analyzer()
    #     analyzer.removePassingTones(excerpt)
    #     analyzer.removeNeighborTones(excerpt)
    #
    #     slices = analyzer.getVerticalities(excerpt)
    #     for vs in slices:
    #         x = harmony.chordSymbolFigureFromChord(vs.getChord())
    #         if x  != 'Chord Symbol Cannot Be Identified':
    #             vs.lyric = x.replace('-', 'b')
    #         print(x.replace('-', 'b'))


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
