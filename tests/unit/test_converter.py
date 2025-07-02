# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest
import os

from music21 import stream, common

from music21.converter import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testConversionMX(self):
        from music21.musicxml import testPrimitive
        from music21 import dynamics
        from music21 import note

        mxString = testPrimitive.pitches01a
        a = parse(mxString)
        a = a.flatten()
        b = a.getElementsByClass(note.Note)
        # there should be 102 notes
        self.assertEqual(len(b), 102)

        # test directions, dynamics, wedges
        mxString = testPrimitive.directions31a
        a = parse(mxString)
        a = a.flatten()
        b = a.getElementsByClass(dynamics.Dynamic)
        # there should be 27 dynamics found in this file
        self.assertEqual(len(b), 27)
        c = a.getElementsByClass(note.Note)
        self.assertEqual(len(c), 53)

        # two starts and two stops == 2!
        d = a.getElementsByClass(dynamics.DynamicWedge)
        self.assertEqual(len(d), 2)

        # test lyrics
        mxString = testPrimitive.lyricsMelisma61d
        a = parse(mxString)
        a = a.flatten()
        b = a.getElementsByClass(note.Note)
        found = []
        for noteObj in b:
            for obj in noteObj.lyrics:
                found.append(obj)
        self.assertEqual(len(found), 3)

        # test we are getting rests
        mxString = testPrimitive.restsDurations02a
        a = parse(mxString)
        a = a.flatten()
        b = a.getElementsByClass(note.Rest)
        self.assertEqual(len(b), 19)

        # test if we can get trills
        mxString = testPrimitive.notations32a
        a = parse(mxString)
        a = a.flatten()
        b = a.getElementsByClass(note.Note)

        mxString = testPrimitive.rhythmDurations03a
        a = parse(mxString)
        # a.show('t')
        self.assertEqual(len(a), 2)  # one part, plus metadata
        for part in a.getElementsByClass(stream.Part):
            self.assertEqual(len(part), 7)  # seven measures
            measures = part.getElementsByClass(stream.Measure)
            self.assertEqual(int(measures[0].number), 1)
            self.assertEqual(int(measures[-1].number), 7)

        # print(a.recurseRepr())

        # print(a.recurseRepr())

        # # get the third movement
        # mxFile = corpus.getWork('opus18no1')[2]
        # a = parse(mxFile)
        # a = a.flatten()
        # b = a.getElementsByClass(dynamics.Dynamic)
        # # 110 dynamics
        # self.assertEqual(len(b), 110)
        #
        # c = a.getElementsByClass(note.Note)
        # # over 1000 notes
        # self.assertEqual(len(c), 1289)

    def testConversionMXChords(self):
        from music21 import chord
        from music21.musicxml import testPrimitive

        mxString = testPrimitive.chordsThreeNotesDuration21c
        a = parse(mxString)
        for part in a.getElementsByClass(stream.Part):
            chords = part[chord.Chord]
            self.assertEqual(len(chords), 7)
            knownSize = [3, 2, 3, 3, 3, 3, 3]
            for i in range(len(knownSize)):
                # print(chords[i].pitches, len(chords[i].pitches))
                self.assertEqual(knownSize[i], len(chords[i].pitches))

    def testConversionMXBeams(self):
        from music21 import note
        from music21.musicxml import testPrimitive

        mxString = testPrimitive.beams01
        a = parse(mxString)
        part = a.parts[0]
        notes = part.recurse().notesAndRests
        beams = []
        for n in notes:
            if isinstance(n, note.Note):
                beams += n.beams.beamsList
        self.assertEqual(len(beams), 152)

    def testConversionMXTime(self):

        from music21.musicxml import testPrimitive

        mxString = testPrimitive.timeSignatures11c
        a = parse(mxString)
        unused_part = a.parts[0]

        mxString = testPrimitive.timeSignatures11d
        a = parse(mxString)
        part = a.parts[0]

        notes = part.recurse().notesAndRests
        self.assertEqual(len(notes), 11)

    def testConversionMXClefPrimitive(self):
        from music21 import clef
        from music21.musicxml import testPrimitive
        mxString = testPrimitive.clefs12a
        a = parse(mxString)
        part = a.parts[0]

        clefs = part[clef.Clef]
        self.assertEqual(len(clefs), 18)

    def testConversionMXClefTimeCorpus(self):
        from music21 import corpus
        from music21 import clef
        from music21 import meter
        a = corpus.parse('luca')

        # there should be only one clef in each part
        clefs = a.parts[0][clef.Clef]
        self.assertEqual(len(clefs), 1)
        self.assertEqual(clefs[0].sign, 'G')

        # second part
        clefs = a.parts[1][clef.Clef]
        self.assertEqual(len(clefs), 1)
        self.assertEqual(clefs[0].octaveChange, -1)
        self.assertEqual(type(clefs[0]).__name__, 'Treble8vbClef')

        # third part
        clefs = a.parts[2][clef.Clef]
        self.assertEqual(len(clefs), 1)

        # check time signature count
        ts = a.parts[1][meter.TimeSignature]
        self.assertEqual(len(ts), 4)

    def testConversionMXArticulations(self):
        from music21 import note
        from music21.musicxml import testPrimitive

        mxString = testPrimitive.articulations01
        a = parse(mxString)
        part = a.parts[0]

        notes = part.flatten().getElementsByClass(note.Note)
        self.assertEqual(len(notes), 4)
        post = []
        match = ["<class 'music21.articulations.Staccatissimo'>",
                 "<class 'music21.articulations.Accent'>",
                 "<class 'music21.articulations.Staccato'>",
                 "<class 'music21.articulations.Tenuto'>"]
        for i in range(len(notes)):
            post.append(str(notes[i].articulations[0].__class__))
        self.assertEqual(post, match)
        # a.show()

    def testConversionMXKey(self):
        from music21 import key
        from music21.musicxml import testPrimitive
        mxString = testPrimitive.keySignatures13a
        a = parse(mxString)
        part = a.parts[0]

        keyList = part[key.KeySignature]
        self.assertEqual(len(keyList), 46)

    def testConversionMXMetadata(self):
        from music21.musicxml import testFiles

        a = parse(testFiles.mozartTrioK581Excerpt)
        self.assertEqual(a.metadata.composer, 'Wolfgang Amadeus Mozart')
        self.assertEqual(a.metadata.title, 'Quintet for Clarinet and Strings')
        self.assertEqual(a.metadata.movementName, 'Menuetto (Excerpt from Second Trio)')

        a = parse(testFiles.binchoisMagnificat)
        self.assertEqual(a.metadata.composer, 'Gilles Binchois')
        # this gets the best title available, even though this is movement title
        self.assertEqual(a.metadata.bestTitle, 'Excerpt from Magnificat secundi toni')

    def testConversionMXBarlines(self):
        from music21 import bar
        from music21.musicxml import testPrimitive
        a = parse(testPrimitive.barlines46a)
        part = a.parts[0]
        barlineList = part[bar.Barline]
        self.assertEqual(len(barlineList), 11)

    def testConversionXMLayout(self):

        from music21.musicxml import testPrimitive
        from music21 import layout

        a = parse(testPrimitive.systemLayoutTwoPart)
        # a.show()

        part = a.getElementsByClass(stream.Part).first()
        systemLayoutList = part[layout.SystemLayout]
        measuresWithSL = []
        for e in systemLayoutList:
            measuresWithSL.append(e.measureNumber)
        self.assertEqual(measuresWithSL, [1, 3, 4, 5, 7, 8])
        self.assertEqual(len(systemLayoutList), 6)

    def testConversionMXTies(self):

        from music21.musicxml import testPrimitive
        from music21 import clef

        a = parse(testPrimitive.multiMeasureTies)
        # a.show()

        countTies = 0
        countStartTies = 0
        for p in a.parts:
            post = p.recurse().notes[0].getContextByClass(clef.Clef)
            self.assertIsInstance(post, clef.TenorClef)
            for n in p.recurse().notes:
                if n.tie is not None:
                    countTies += 1
                    if n.tie.type in ('start', 'continue'):
                        countStartTies += 1

        self.assertEqual(countTies, 57)
        self.assertEqual(countStartTies, 40)

    def testConversionMXInstrument(self):
        from music21 import corpus
        from music21 import instrument
        s = corpus.parse('schumann_clara/opus17', 3)
        # s.show()
        is1 = s.parts[0][instrument.Instrument]
        self.assertEqual(len(is1), 1)
        # self.assertIn('Violin', is1[0].classes)
        is2 = s.parts[1][instrument.Instrument]
        self.assertEqual(len(is2), 1)
        # self.assertIn('Violoncello', is1[0].classes)
        is3 = s.parts[2][instrument.Instrument]
        self.assertEqual(len(is3), 1)
        # self.assertIn('Piano', is1[0].classes)

    def testConversionMidiBasic(self):
        dirLib = common.getSourceFilePath() / 'midi' / 'testPrimitive'
        fp = dirLib / 'test01.mid'

        # a simple file created in athenacl

        unused_s = parseFile(fp)
        unused_s = parse(fp)

        c = subConverters.ConverterMidi()
        c.parseFile(fp)

        # try low level string data passing
        with fp.open('rb') as f:
            data = f.read()

        c.parseData(data)

        # try module-level; function
        parseData(data)
        parse(data)

    def testConversionMidiNotes(self):
        from music21 import meter
        from music21 import key
        from music21 import chord
        from music21 import note

        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test01.mid'
        # a simple file created in athenacl
        # for fn in ['test01.mid', 'test02.mid', 'test03.mid', 'test04.mid']:
        s = parseFile(fp)
        # s.show()
        self.assertEqual(len(s[note.Note]), 18)

        # has chords and notes
        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test05.mid'
        s = parseFile(fp)
        # s.show()
        # environLocal.printDebug(['\n' + 'opening fp', fp])

        self.assertEqual(len(s[note.Note]), 2)
        self.assertEqual(len(s[chord.Chord]), 5)

        # MIDI import makes measures, so we will have one 4/4 time sig
        self.assertEqual(len(s[meter.TimeSignature]), 1)
        self.assertEqual(len(s[key.KeySignature]), 0)

        # this sample has eighth note triplets
        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test06.mid'
        s = parseFile(fp)
        # s.show()

        # environLocal.printDebug(['\n' + 'opening fp', fp])

        # s.show()
        from fractions import Fraction as F
        dList = [n.quarterLength for n in s.flatten().notesAndRests[:30]]
        match = [0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5,
                 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
                 0.5, 0.5, 0.5, 0.5, F(1, 3), F(1, 3), F(1, 3), 0.5, 0.5, 1.0]
        self.assertEqual(dList, match)

        self.assertEqual(len(s[meter.TimeSignature]), 1)
        self.assertEqual(len(s[key.KeySignature]), 1)

        # this sample has sixteenth note triplets
        # TODO much work is still needed on getting timing right
        # this produces numerous errors in makeMeasure partitioning
        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test07.mid'
        # environLocal.printDebug(['\n' + 'opening fp', fp])
        s = parseFile(fp)
        # s.show('t')
        self.assertEqual(len(s[meter.TimeSignature]), 1)
        self.assertEqual(len(s[key.KeySignature]), 1)

        # this sample has dynamic changes in key signature
        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test08.mid'
        # environLocal.printDebug(['\n' + 'opening fp', fp])
        s = parseFile(fp)
        # s.show('t')
        self.assertEqual(len(s[meter.TimeSignature]), 1)
        found = s[key.KeySignature]
        self.assertEqual(len(found), 3)
        # test the right keys
        self.assertEqual(found[0].sharps, -3)
        self.assertEqual(found[1].sharps, 3)
        self.assertEqual(found[2].sharps, -1)




    def testConversionMusedata(self):
        # MuseData format has been removed
        pass

    def testMixedArchiveHandling(self):
        '''
        Test getting data out of musicxml zip files.
        '''
        fp = common.getSourceFilePath() / 'musicxml' / 'testMxl.mxl'
        af = ArchiveManager(fp)
        # for now, only support zip
        self.assertEqual(af.archiveType, 'zip')
        self.assertTrue(af.isArchive())
        # if this is a musicxml file, there will only be single file; we
        # can call getData to get this
        post = af.getData()
        self.assertEqual(post[:38], '<?xml version="1.0" encoding="UTF-8"?>')
        self.assertEqual(af.getNames(), ['musicXML.xml', 'META-INF/', 'META-INF/container.xml'])


        # try to load parse the zip file
        # s = parse(fp)

        # MuseData format has been removed


    def testParseMidiQuantize(self):
        '''
        Checks quantization when parsing a stream. Here everything snaps to the 8th note.
        '''
        # OMR functionality has been removed
        pass

    def testParseMidiNoQuantize(self):
        '''
        Checks that quantization is not performed if quantizePost=False.
        Source MIDI file contains only: 3 16th notes, 2 32nd notes.
        '''
        fp = common.getSourceFilePath() / 'midi' / 'testPrimitive' / 'test15.mid'

        # Don't forceSource: test that pickles contemplate quantization keywords
        streamFpQuantized = parse(fp)
        self.assertNotIn(0.875, streamFpQuantized.flatten()._uniqueOffsetsAndEndTimes())

        streamFpNotQuantized = parse(fp, quantizePost=False)
        self.assertIn(0.875, streamFpNotQuantized.flatten()._uniqueOffsetsAndEndTimes())

        streamFpCustomQuantized = parse(fp, quarterLengthDivisors=(2,))
        self.assertNotIn(0.75, streamFpCustomQuantized.flatten()._uniqueOffsetsAndEndTimes())

        # Also check raw data: https://github.com/cuthbertLab/music21/issues/546
        with fp.open('rb') as f:
            data = f.read()
        self.assertIsInstance(data, bytes)
        streamDataNotQuantized = parse(data, quantizePost=False)
        self.assertIn(0.875, streamDataNotQuantized.flatten()._uniqueOffsetsAndEndTimes())

        # Remove pickles so that failures are possible in future
        pf1 = PickleFilter(fp)
        pf1.removePickle()
        pf2 = PickleFilter(fp, quantizePost=False)
        pf2.removePickle()
        pf3 = PickleFilter(fp, quarterLengthDivisors=(2,))
        pf3.removePickle()


    def testConverterFromPath(self):
        fp = common.getSourceFilePath() / 'corpus' / 'bach' / 'bwv66.6.mxl'
        s = parse(fp)
        self.assertIn('Stream', s.classes)

        fp = common.getSourceFilePath() / 'corpus' / 'bach' / 'bwv66.6'

        with self.assertRaises(FileNotFoundError):
            parse(fp)
        with self.assertRaises(ConverterException):
            # nonexistent path ending in incorrect extension
            # no way to tell apart from data, so failure happens later
            parse(str(fp))
        with self.assertRaises(FileNotFoundError):
            parse('nonexistent_path_ending_in_correct_extension.musicxml')


class TestExternal(unittest.TestCase):
    show = True

    def testConversionMusicXml(self):
        c = stream.Score()

        from music21.musicxml import testPrimitive
        mxString = testPrimitive.chordsThreeNotesDuration21c
        a = parseData(mxString)

        mxString = testPrimitive.beams01
        b = parseData(mxString)
        # b.show()

        c.append(a[0])
        c.append(b[0])
        if self.show:
            c.show()
        # TODO: this is only showing the minimum number of measures

    def testFreezer(self):
        from music21 import corpus
        s = corpus.parse('bach/bwv66.6.xml')
        fp = freeze(s)
        s2 = thaw(fp)
        if self.show:
            s2.show()
        os.remove(fp)

    def testMusicXMLTabConversion(self):
        from music21.musicxml import testFiles

        mxString = testFiles.ALL[5]
        a = subConverters.ConverterMusicXML()
        a.parseData(mxString)

        b = parseData(mxString)
        if self.show:
            b.show('text')
            b.show()

        # {0.0} <music21.metadata.Metadata object at 0x04501CD0>
        # {0.0} <music21.stream.Part Electric Guitar>
        #    {0.0} <music21.instrument.Instrument P0: Electric Guitar: >
        #    {0.0} <music21.stream.Measure 0 offset=0.0>
        #        {0.0} <music21.layout.StaffLayout distance None, ...staffLines 6>
        #        {0.0} <music21.clef.TabClef>
        #        {0.0} <music21.tempo.MetronomeMark animato Quarter=120.0>
        #        {0.0} <music21.key.KeySignature of no sharps or flats, mode major>
        #        {0.0} <music21.meter.TimeSignature 4/4>
        #        {0.0} <music21.note.Note F>
        #        {2.0} <music21.note.Note F#>


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
