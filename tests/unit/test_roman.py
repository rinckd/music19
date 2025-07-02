# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.roman import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())


    def testFBN(self):
        fbn = fbNotation.Notation('6,3')
        V = RomanNumeral('V')
        sdb = V.bassScaleDegreeFromNotation(fbn)
        self.assertEqual(sdb, 7)

    def testFigure(self):
        r1 = RomanNumeral('V')
        self.assertEqual(r1.frontAlterationTransposeInterval, None)
        self.assertEqual(r1.pitches, chord.Chord(['G4', 'B4', 'D5']).pitches)
        r1 = RomanNumeral('bbVI6')
        self.assertEqual(r1.figuresWritten, '6')
        self.assertEqual(r1.frontAlterationTransposeInterval.chromatic.semitones, -2)
        self.assertEqual(r1.frontAlterationTransposeInterval.diatonic.directedNiceName,
                         'Descending Doubly-Diminished Unison')
        cM = scale.MajorScale('C')
        r2 = RomanNumeral('ii', cM)
        self.assertIsNotNone(r2)

        dminor = key.Key('d')
        rn = RomanNumeral('ii/o65', dminor)
        self.assertEqual(
            rn.pitches,
            chord.Chord(['G4', 'B-4', 'D5', 'E5']).pitches,
        )
        rnRealSlash = RomanNumeral('iiø65', dminor)
        self.assertEqual(rn, rnRealSlash)

        rnOmit = RomanNumeral('V[no3]', dminor)
        self.assertEqual(rnOmit.pitches, chord.Chord(['A4', 'E5']).pitches)
        rnOmit = RomanNumeral('V[no5]', dminor)
        self.assertEqual(rnOmit.pitches, chord.Chord(['A4', 'C#5']).pitches)
        rnOmit = RomanNumeral('V[no3no5]', dminor)
        self.assertEqual(rnOmit.pitches, chord.Chord(['A4']).pitches)
        rnOmit = RomanNumeral('V13[no11]', key.Key('C'))
        self.assertEqual(rnOmit.pitches, chord.Chord('G4 B4 D5 F5 A5 E5').pitches)

    def testBracketedAlterations(self):
        r1 = RomanNumeral('V9[b7][b5]')
        self.assertEqual(str(r1.bracketedAlterations), "[('b', 7), ('b', 5)]")
        self.assertEqual(str(r1.pitches),
                         '(<music21.pitch.Pitch G4>, <music21.pitch.Pitch B4>, '
                         + '<music21.pitch.Pitch D-5>, '
                         + '<music21.pitch.Pitch F-5>, <music21.pitch.Pitch A5>)')


    def testYieldRemoveA(self):
        from music21 import stream
        # s = corpus.parse('madrigal.3.1.rntxt')
        m = stream.Measure()
        m.append(key.KeySignature(4))
        m.append(note.Note())
        p = stream.Part()
        p.append(m)
        s = stream.Score()
        s.append(p)
        targetCount = 1
        self.assertEqual(
            len(s['KeySignature']),
            targetCount,
        )
        # through sequential iteration
        s1 = copy.deepcopy(s)
        for p in s1.parts:
            for m in p.getElementsByClass(stream.Measure):
                for e in m.getElementsByClass(key.KeySignature):
                    m.remove(e)
        self.assertEqual(len(s1.flatten().getElementsByClass(key.KeySignature)), 0)
        s2 = copy.deepcopy(s)
        self.assertEqual(
            len(s2.flatten().getElementsByClass(key.KeySignature)),
            targetCount,
        )
        for e in s2.flatten().getElementsByClass(key.KeySignature):
            for site in e.sites.get():
                if site is not None:
                    site.remove(e)
        # s2.show()
        # yield elements and containers
        s3 = copy.deepcopy(s)
        self.assertEqual(
            len(s3.flatten().getElementsByClass(key.KeySignature)),
            targetCount,
        )
        for e in s3.recurse(streamsOnly=True):
            if isinstance(e, key.KeySignature):
                # all active sites are None because of deep-copying
                if e.activeSite is not None:
                    e.activeSite.remove(e)
        # s3.show()
        # yield containers
        s4 = copy.deepcopy(s)
        self.assertEqual(
            len(s4.flatten().getElementsByClass(key.KeySignature)),
            targetCount,
        )
        # do not remove in iteration.
        for c in list(s4.recurse(streamsOnly=False)):
            if isinstance(c, stream.Stream):
                for e in c.getElementsByClass(key.KeySignature):
                    c.remove(e)

    def testScaleDegreesA(self):
        from music21 import roman
        k = key.Key('f#')  # 3-sharps minor
        rn = roman.RomanNumeral('V', k)
        self.assertEqual(str(rn.key), 'f# minor')
        self.assertEqual(
            str(rn.pitches),
            '(<music21.pitch.Pitch C#5>, '
            '<music21.pitch.Pitch E#5>, '
            '<music21.pitch.Pitch G#5>)',
        )
        self.assertEqual(
            str(rn.scaleDegrees),
            '[(5, None), (7, <music21.pitch.Accidental sharp>), (2, None)]',
        )

    def testNeapolitanAndHalfDiminished(self):
        from music21 import roman
        alteredChordHalfDim3rdInv = roman.RomanNumeral(
            'bii/o42', scale.MajorScale('F'))
        self.assertEqual(
            [str(p) for p in alteredChordHalfDim3rdInv.pitches],
            ['F-4', 'G-4', 'B--4', 'D--5'],
        )
        iv = alteredChordHalfDim3rdInv.intervalVector
        self.assertEqual([0, 1, 2, 1, 1, 1], iv)
        cn = alteredChordHalfDim3rdInv.commonName
        self.assertEqual(cn, 'half-diminished seventh chord')

    def testOmittedFifth(self):
        from music21 import roman
        c = chord.Chord('A3 E-4 G-4')
        k = key.Key('b-')
        rnDim7 = roman.romanNumeralFromChord(c, k)
        self.assertEqual(rnDim7.figure, 'viio7')

    def testAllFormsOfVII(self):
        from music21 import roman

        def p(c):
            return ' '.join([x.nameWithOctave for x in c.pitches])

        k = key.Key('c')
        rn = roman.RomanNumeral('viio', k)
        self.assertEqual(p(rn), 'B4 D5 F5')
        rn = roman.RomanNumeral('viio6', k)
        self.assertEqual(p(rn), 'D4 F4 B4')
        rn = roman.RomanNumeral('viio64', k)
        self.assertEqual(p(rn), 'F4 B4 D5')

        rn = roman.RomanNumeral('vii', k)
        self.assertEqual(p(rn), 'B4 D5 F#5')
        rn = roman.RomanNumeral('vii6', k)
        self.assertEqual(p(rn), 'D4 F#4 B4')
        rn = roman.RomanNumeral('vii64', k)
        self.assertEqual(p(rn), 'F#4 B4 D5')

        rn = roman.RomanNumeral('viio7', k)
        self.assertEqual(p(rn), 'B4 D5 F5 A-5')
        rn = roman.RomanNumeral('viio65', k)
        self.assertEqual(p(rn), 'D4 F4 A-4 B4')
        rn = roman.RomanNumeral('viio43', k)
        self.assertEqual(p(rn), 'F4 A-4 B4 D5')
        rn = roman.RomanNumeral('viio42', k)
        self.assertEqual(p(rn), 'A-4 B4 D5 F5')

        rn = roman.RomanNumeral('vii/o7', k)
        self.assertEqual(p(rn), 'B4 D5 F5 A5')
        # noinspection SpellCheckingInspection
        rn = roman.RomanNumeral('viiø65', k)
        self.assertEqual(p(rn), 'D4 F4 A4 B4')
        # noinspection SpellCheckingInspection
        rn = roman.RomanNumeral('viiø43', k)
        self.assertEqual(p(rn), 'F4 A4 B4 D5')
        rn = roman.RomanNumeral('vii/o42', k)
        self.assertEqual(p(rn), 'A4 B4 D5 F5')

        rn = roman.RomanNumeral('VII', k)
        self.assertEqual(p(rn), 'B-4 D5 F5')
        rn = roman.RomanNumeral('VII6', k)
        self.assertEqual(p(rn), 'D4 F4 B-4')
        rn = roman.RomanNumeral('VII64', k)
        self.assertEqual(p(rn), 'F4 B-4 D5')

        rn = roman.RomanNumeral('bVII', k)
        self.assertEqual(p(rn), 'B--4 D-5 F-5')
        rn = roman.RomanNumeral('bVII6', k)
        self.assertEqual(p(rn), 'D-4 F-4 B--4')
        rn = roman.RomanNumeral('bVII64', k)
        self.assertEqual(p(rn), 'F-4 B--4 D-5')

        rn = roman.RomanNumeral('bvii', k)
        self.assertEqual(p(rn), 'B-4 D-5 F5')
        rn = roman.RomanNumeral('bvii6', k)
        self.assertEqual(p(rn), 'D-4 F4 B-4')
        rn = roman.RomanNumeral('bvii64', k)
        self.assertEqual(p(rn), 'F4 B-4 D-5')

        rn = roman.RomanNumeral('bviio', k)
        self.assertEqual(p(rn), 'B-4 D-5 F-5')
        rn = roman.RomanNumeral('bviio6', k)
        self.assertEqual(p(rn), 'D-4 F-4 B-4')
        rn = roman.RomanNumeral('bviio64', k)
        self.assertEqual(p(rn), 'F-4 B-4 D-5')

        rn = roman.RomanNumeral('#VII', k)
        self.assertEqual(p(rn), 'B4 D#5 F#5')
        rn = roman.RomanNumeral('#vii', k)
        self.assertEqual(p(rn), 'B#4 D#5 F##5')

        rn = roman.RomanNumeral('VII+', k)
        self.assertEqual(p(rn), 'B-4 D5 F#5')

    def testAllFormsOfVI(self):
        from music21 import roman

        def p(c):
            return ' '.join([x.nameWithOctave for x in c.pitches])

        k = key.Key('c')
        rn = roman.RomanNumeral('vio', k)
        self.assertEqual(p(rn), 'A4 C5 E-5')
        rn = roman.RomanNumeral('vio6', k)
        self.assertEqual(p(rn), 'C4 E-4 A4')
        rn = roman.RomanNumeral('vio64', k)
        self.assertEqual(p(rn), 'E-4 A4 C5')

        rn = roman.RomanNumeral('vi', k)
        self.assertEqual(p(rn), 'A4 C5 E5')
        rn = roman.RomanNumeral('vi6', k)
        self.assertEqual(p(rn), 'C4 E4 A4')
        rn = roman.RomanNumeral('vi64', k)
        self.assertEqual(p(rn), 'E4 A4 C5')

        rn = roman.RomanNumeral('vio7', k)
        self.assertEqual(p(rn), 'A4 C5 E-5 G-5')
        rn = roman.RomanNumeral('vio65', k)
        self.assertEqual(p(rn), 'C4 E-4 G-4 A4')
        rn = roman.RomanNumeral('vio43', k)
        self.assertEqual(p(rn), 'E-4 G-4 A4 C5')
        rn = roman.RomanNumeral('vio42', k)
        self.assertEqual(p(rn), 'G-4 A4 C5 E-5')

        rn = roman.RomanNumeral('viø7', k)
        self.assertEqual(p(rn), 'A4 C5 E-5 G5')
        rn = roman.RomanNumeral('vi/o65', k)
        self.assertEqual(p(rn), 'C4 E-4 G4 A4')
        rn = roman.RomanNumeral('vi/o43', k)
        self.assertEqual(p(rn), 'E-4 G4 A4 C5')
        rn = roman.RomanNumeral('viø42', k)
        self.assertEqual(p(rn), 'G4 A4 C5 E-5')

        rn = roman.RomanNumeral('VI', k)
        self.assertEqual(p(rn), 'A-4 C5 E-5')
        rn = roman.RomanNumeral('VI6', k)
        self.assertEqual(p(rn), 'C4 E-4 A-4')
        rn = roman.RomanNumeral('VI64', k)
        self.assertEqual(p(rn), 'E-4 A-4 C5')

        rn = roman.RomanNumeral('bVI', k)
        self.assertEqual(p(rn), 'A--4 C-5 E--5')
        rn = roman.RomanNumeral('bVI6', k)
        self.assertEqual(p(rn), 'C-4 E--4 A--4')
        rn = roman.RomanNumeral('bVI64', k)
        self.assertEqual(p(rn), 'E--4 A--4 C-5')

        rn = roman.RomanNumeral('bvi', k)
        self.assertEqual(p(rn), 'A-4 C-5 E-5')
        rn = roman.RomanNumeral('bvi6', k)
        self.assertEqual(p(rn), 'C-4 E-4 A-4')
        rn = roman.RomanNumeral('bvi64', k)
        self.assertEqual(p(rn), 'E-4 A-4 C-5')

        rn = roman.RomanNumeral('bvio', k)
        self.assertEqual(p(rn), 'A-4 C-5 E--5')
        rn = roman.RomanNumeral('bvio6', k)
        self.assertEqual(p(rn), 'C-4 E--4 A-4')
        rn = roman.RomanNumeral('bvio64', k)
        self.assertEqual(p(rn), 'E--4 A-4 C-5')

        rn = roman.RomanNumeral('#VI', k)
        self.assertEqual(p(rn), 'A4 C#5 E5')
        rn = roman.RomanNumeral('#vi', k)
        self.assertEqual(p(rn), 'A#4 C#5 E#5')

        rn = roman.RomanNumeral('VI+', k)
        self.assertEqual(p(rn), 'A-4 C5 E5')

    def testAugmented(self):
        from music21 import roman

        def p(c):
            return ' '.join([x.nameWithOctave for x in c.pitches])

        def test_numeral(country, figure_list, result, key_in='a'):
            for figure in figure_list:
                for with_plus in ('', '+'):
                    for kStr in (key_in, key_in.upper()):
                        key_obj = key.Key(kStr)
                        rn_str = country + with_plus + figure
                        rn = roman.RomanNumeral(rn_str, key_obj)
                        self.assertEqual(p(rn), result)


        test_numeral('It', ['6', ''], 'F5 A5 D#6')
        test_numeral('Ger', ['', '6', '65', '6/5'], 'F5 A5 C6 D#6')
        test_numeral('Fr', ['', '6', '43', '4/3'], 'F5 A5 B5 D#6')
        test_numeral('Sw', ['', '6', '43', '4/3'], 'F5 A5 B#5 D#6')

        # these I worked out in C, not A ...  :-)
        test_numeral('It', ['53'], 'F#4 A-4 C5', 'C')
        test_numeral('It', ['64'], 'C4 F#4 A-4', 'C')
        test_numeral('Ger', ['7'], 'F#4 A-4 C5 E-5', 'C')
        test_numeral('Ger', ['43'], 'C4 E-4 F#4 A-4', 'C')
        test_numeral('Ger', ['42'], 'E-4 F#4 A-4 C5', 'C')
        test_numeral('Fr', ['7'], 'D4 F#4 A-4 C5', 'C')
        test_numeral('Fr', ['65'], 'F#4 A-4 C5 D5', 'C')
        test_numeral('Fr', ['42'], 'C4 D4 F#4 A-4', 'C')
        test_numeral('Sw', ['7'], 'D#4 F#4 A-4 C5', 'C')
        test_numeral('Sw', ['65'], 'F#4 A-4 C5 D#5', 'C')
        test_numeral('Sw', ['42'], 'C4 D#4 F#4 A-4', 'C')

    def test_augmented_round_trip(self):
        # only testing properly spelled forms for input, since output will
        # always be properly spelled
        augTests = [
            'It6', 'It64', 'It53',
            'Ger65', 'Ger43', 'Ger42', 'Ger7',
            'Fr43', 'Fr7', 'Fr42', 'Fr65',
            'Sw43', 'Sw7', 'Sw42', 'Sw65',
        ]

        c_minor = key.Key('c')
        c_major = key.Key('C')

        for aug6 in augTests:
            rn = RomanNumeral(aug6, c_minor)
            ch = chord.Chord(rn.pitches)
            # without key
            rn_out = romanNumeralFromChord(ch)
            if aug6 not in ('Ger7', 'Fr7'):
                # TODO(msc): fix these -- currently giving iø7 and Iø7 respectively
                self.assertEqual(rn.figure, rn_out.figure, f'{aug6}: {rn_out}')
                self.assertEqual(rn_out.key.tonicPitchNameWithCase, 'c')

            # with key
            rn_out = romanNumeralFromChord(ch, c_minor)
            self.assertEqual(rn.figure, rn_out.figure, f'{aug6}: {rn_out}')

            rn_out = romanNumeralFromChord(ch, c_major)
            self.assertEqual(rn.figure, rn_out.figure, f'{aug6}: {rn_out}')

    def testSetFigureAgain(self):
        '''
        Setting the figure again doesn't double the alterations
        '''
        ger = RomanNumeral('Ger7')
        pitches_before = ger.pitches
        ger.figure = 'Ger7'
        self.assertEqual(ger.pitches, pitches_before)

        sharp_four = RomanNumeral('#IV')
        pitches_before = sharp_four.pitches
        sharp_four.figure = '#IV'
        self.assertEqual(sharp_four.pitches, pitches_before)

    def testZeroForDiminished(self):
        from music21 import roman
        rn = roman.RomanNumeral('vii07', 'c')
        self.assertEqual([p.name for p in rn.pitches], ['B', 'D', 'F', 'A-'])
        rn = roman.RomanNumeral('vii/07', 'c')
        self.assertEqual([p.name for p in rn.pitches], ['B', 'D', 'F', 'A'])
        # However, when there is a '10' somewhere in the figure, don't replace
        #   the 0 (this occurs in DCML corpora)
        rn = roman.RomanNumeral('V7[add10]', 'c')
        self.assertEqual([p.name for p in rn.pitches], ['G', 'B-', 'B', 'D', 'F'])

    def testIII7(self):
        c = chord.Chord(['E4', 'G4', 'B4', 'D5'])
        k = key.Key('C')
        rn = romanNumeralFromChord(c, k)
        self.assertEqual(rn.figure, 'iii7')

    def testHalfDimMinor(self):
        c = chord.Chord(['A3', 'C4', 'E-4', 'G4'])
        k = key.Key('c')
        rn = romanNumeralFromChord(c, k)
        self.assertEqual(rn.figure, 'viø7')

    def testHalfDimIII(self):
        c = chord.Chord(['F#3', 'A3', 'E4', 'C5'])
        k = key.Key('d')
        rn = romanNumeralFromChord(c, k)
        self.assertEqual(rn.figure, '#iiiø7')

    def testAugmentedOctave(self):
        c = chord.Chord(['C4', 'E5', 'G5', 'C#6'])
        k = key.Key('C')
        f = postFigureFromChordAndKey(c, k)
        self.assertEqual(f, '#853')

        rn = romanNumeralFromChord(c, k)
        self.assertEqual(rn.figure, 'I#853')

    def testSecondaryAugmentedSixth(self):
        rn = RomanNumeral('Ger65/IV', 'C')
        self.assertEqual([p.name for p in rn.pitches], ['D-', 'F', 'A-', 'B'])

    def testV7b5(self):
        rn = RomanNumeral('V7b5', 'C')
        self.assertEqual([p.name for p in rn.pitches], ['G', 'D-', 'F'])

    def testNo5(self):
        rn = RomanNumeral('viio[no5]', 'a')
        self.assertEqual([p.name for p in rn.pitches], ['G#', 'B'])

        rn = RomanNumeral('vii[no5]', 'a')
        self.assertEqual([p.name for p in rn.pitches], ['G#', 'B'])

    def testNeapolitan(self):
        # False:
        falseFigures = ('III',  # Not II
                        'II',  # II but not bII (no frontAlterationAccidental)
                        '#II',  # rn.frontAlterationAccidental != flat
                        'bII',  # bII but not bII6 and default requires first inv
                        'bii6',  # quality != major
                        '#I',  # Enharmonics do not count
                        )
        for fig in falseFigures:
            with self.subTest(figure=fig):
                rn = RomanNumeral(fig, 'a')
                self.assertFalse(rn.isNeapolitan())

        # True:
        trueFigures = ('bII6',
                       'N6',  # Maps to bII6
                       'N'  # NB: also maps to bII6
                       )
        for fig in trueFigures:
            with self.subTest(figure=fig):
                rn = RomanNumeral(fig, 'a')
                self.assertTrue(rn.isNeapolitan())

        # Root position (conditionally true)
        rootPosition = ('N53',  # NB: explicit 53 required
                        'bII',
                        )

        for fig in rootPosition:
            with self.subTest(figure=fig):
                rn = RomanNumeral(fig, 'a')
                self.assertFalse(rn.isNeapolitan())
                self.assertTrue(rn.isNeapolitan(require1stInversion=False))

    def testMixture(self):
        for fig in ['i', 'iio', 'bIII', 'iv', 'v', 'bVI', 'bVII', 'viio7']:
            # True, major key:
            self.assertTrue(RomanNumeral(fig, 'A').isMixture())
            # False, minor key:
            self.assertFalse(RomanNumeral(fig, 'a').isMixture())

        for fig in ['I', 'ii', '#iii', 'IV', 'vi', 'viiø7']:  # NB not #vi
            # False, major key:
            self.assertFalse(RomanNumeral(fig, 'A').isMixture())
            # True, minor key:
            self.assertTrue(RomanNumeral(fig, 'a').isMixture())

    def testMinorTonic7InMajor(self):
        rn = RomanNumeral('i7', 'C')
        pitchStrings = [p.name for p in rn.pitches]
        self.assertEqual(pitchStrings, ['C', 'E-', 'G', 'B-'])
        for k in (key.Key('C'), key.Key('c')):
            ch1 = chord.Chord('C4 E-4 G4 B-4')
            rn2 = romanNumeralFromChord(ch1, k)
            self.assertEqual(rn2.figure, 'i7')
            ch = chord.Chord('E-4 G4 B-4 C5')
            rn = romanNumeralFromChord(ch, k)
            self.assertEqual(rn.figure, 'i65')

        for k in (key.Key('G'), key.Key('g')):
            ch = chord.Chord('G4 B-4 C5 E-5')
            rn = romanNumeralFromChord(ch, k)
            self.assertEqual(rn.figure, 'iv43')
            ch = chord.Chord('B-4 C5 E-5 G5')
            rn = romanNumeralFromChord(ch, k)
            self.assertEqual(rn.figure, 'iv42')

    def testMinorMajor7InMajor(self):
        def new_fig_equals_old_figure(rn_in, k='C'):
            p_old = [p.name for p in rn_in.pitches]
            rn_new = RomanNumeral(rn_in.figure, k)
            p_new = [p.name for p in rn_new.pitches]
            # order matters, octave does not
            self.assertEqual(p_old, p_new, f'{p_old} not equal {p_new} for {rn_in}')

        rn = RomanNumeral('i7[#7]', 'C')
        pitchStrings = [p.name for p in rn.pitches]
        self.assertEqual(pitchStrings, ['C', 'E-', 'G', 'B'])
        ch1 = chord.Chord('C4 E-4 G4 B4')
        rn1 = romanNumeralFromChord(ch1, 'C')
        self.assertEqual(rn1.figure, 'i7[#7]')
        new_fig_equals_old_figure(rn1)
        ch2 = chord.Chord('E-4 G4 B4 C5')
        rn2 = romanNumeralFromChord(ch2, 'C')
        self.assertEqual(rn2.figure, 'i65[#7]')
        new_fig_equals_old_figure(rn2)

        ch3 = chord.Chord('G4 B4 C5 E-5')
        rn3 = romanNumeralFromChord(ch3, 'G')
        self.assertEqual(rn3.figure, 'iv43[#7]')
        new_fig_equals_old_figure(rn3, 'G')
        ch4 = chord.Chord('B4 C5 E-5 G5')
        rn4 = romanNumeralFromChord(ch4, 'G')
        self.assertEqual(rn4.figure, 'iv42[#7]')
        new_fig_equals_old_figure(rn4, 'G')

        # in minor these are more normal #7:
        rn1 = romanNumeralFromChord(ch1, 'c')
        self.assertEqual(rn1.figure, 'i#7')
        new_fig_equals_old_figure(rn1, 'c')
        rn2 = romanNumeralFromChord(ch2, 'c')
        self.assertEqual(rn2.figure, 'i65[#7]')
        new_fig_equals_old_figure(rn2, 'c')

        ch3 = chord.Chord('G4 B4 C5 E-5')
        rn3 = romanNumeralFromChord(ch3, 'g')
        self.assertEqual(rn3.figure, 'iv43[#7]')
        new_fig_equals_old_figure(rn3, 'g')
        # except third-inversion
        ch4 = chord.Chord('B4 C5 E-5 G5')
        rn4 = romanNumeralFromChord(ch4, 'g')
        self.assertEqual(rn4.figure, 'iv42[#7]')
        new_fig_equals_old_figure(rn4, 'g')

    def test_addedPitch_sharp7(self):
        '''
        Fixes issue #1369
        '''
        rn = RomanNumeral('IV[add#7]', 'C')
        self.assertEqual(rn.bass().nameWithOctave, 'F4')
        self.assertEqual([p.nameWithOctave for p in rn.pitches],
                         ['F4', 'A4', 'C5', 'E#5'])

    def test_sevenths_on_alteration(self):
        rn = RomanNumeral('bII7', 'c')
        self.assertEqual(rn.seventh.name, 'C')
        rn = RomanNumeral('bII65', 'c')
        self.assertEqual(rn.seventh.name, 'C')

        # make sure that it works around octave breaks too.
        rn = RomanNumeral('bII65', 'b')
        self.assertEqual(rn.seventh.name, 'B')

        rn = RomanNumeral('bVII7', 'c', seventhMinor=Minor67Default.CAUTIONARY)
        self.assertEqual(rn.seventh.name, 'A-')
        rn = RomanNumeral('bVII7', 'C', seventhMinor=Minor67Default.CAUTIONARY)
        self.assertEqual(rn.seventh.name, 'A')

    def test_int_figure_case_matters(self):
        '''
        Fix for https://github.com/cuthbertLab/music21/issues/1450
        '''
        minorKeyObj = key.Key('c')
        rn = RomanNumeral(2, minorKeyObj)
        self.assertEqual(rn.figure, 'ii')
        rn = RomanNumeral(2, minorKeyObj, caseMatters=False)
        self.assertEqual(rn.figure, 'II')

        rn = RomanNumeral(4, 'c')
        self.assertEqual(rn.figure, 'iv')

        rn = RomanNumeral(6, scale.MajorScale('c'))
        self.assertEqual(rn.figure, 'vi')

        # Major still works
        rn = RomanNumeral(4, 'C')
        self.assertEqual(rn.figure, 'IV')

    def test_scale_caching(self):
        mcs = scale.ConcreteScale('c', pitches=('C', 'D', 'E', 'F', 'G', 'A', 'B'))
        rn = mcs.romanNumeral('IV7')
        self.assertEqual([p.unicodeName for p in rn.pitches], ['F', 'A', 'C', 'E'])
        mcs = scale.ConcreteScale('c', pitches=('C', 'D', 'E-', 'F', 'G', 'A', 'B'))
        rn = mcs.romanNumeral('IV7')
        self.assertEqual([p.unicodeName for p in rn.pitches], ['F', 'A', 'C', 'E♭'])


class TestExternal(unittest.TestCase):
    show = True

    def testFromChordify(self):
        from music21 import corpus
        b = corpus.parse('bwv103.6')
        c = b.chordify()
        cKey = b.analyze('key')
        figuresCache = {}
        for x in c.recurse():
            if isinstance(x, chord.Chord):
                rnc = romanNumeralFromChord(x, cKey)
                figure = rnc.figure
                if figure not in figuresCache:
                    figuresCache[figure] = 1
                else:
                    figuresCache[figure] += 1
                x.lyric = figure

        if self.show:
            sortedList = sorted(figuresCache, key=figuresCache.get, reverse=True)
            for thisFigure in sortedList:
                print(thisFigure, figuresCache[thisFigure])

        b.insert(0, c)
        if self.show:
            b.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
