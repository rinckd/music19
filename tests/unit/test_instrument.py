# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.instrument import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testMusicXMLExport(self):
        from music21 import stream

        s1 = stream.Stream()
        i1 = Violin()
        i1.partName = 'test'
        s1.append(i1)
        s1.repeatAppend(note.Note(), 10)
        # s.show()

        s2 = stream.Stream()
        i2 = Piano()
        i2.partName = 'test2'
        s2.append(i2)
        s2.repeatAppend(note.Note('g4'), 10)

        s3 = stream.Score()
        s3.insert(0, s1)
        s3.insert(0, s2)

        # s3.show()

    def testPartitionByInstrumentA(self):
        from music21 import instrument
        from music21 import stream

        # basic case of instruments in Parts
        s = stream.Score()
        p1 = stream.Part()
        p1.append(instrument.Piano())

        p2 = stream.Part()
        p2.append(instrument.Piccolo())
        s.insert(0, p1)
        s.insert(0, p2)

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 2)
        self.assertEqual(len(post.flatten().getElementsByClass(instrument.Instrument)), 2)

        # post.show('t')

        # one Stream with multiple instruments
        s = stream.Stream()
        s.insert(0, instrument.PanFlute())
        s.insert(20, instrument.ReedOrgan())

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 2)
        self.assertEqual(len(post[instrument.Instrument]), 2)
        # post.show('t')

    def testPartitionByInstrumentB(self):
        from music21 import instrument
        from music21 import stream

        # basic case of instruments in Parts
        s = stream.Score()
        p1 = stream.Part()
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note(), 6)

        p2 = stream.Part()
        p2.append(instrument.Piccolo())
        p2.repeatAppend(note.Note(), 12)
        s.insert(0, p1)
        s.insert(0, p2)

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 2)
        self.assertEqual(len(post[instrument.Instrument]), 2)
        self.assertEqual(len(post.parts[0].notes), 6)
        self.assertEqual(len(post.parts[1].notes), 12)

    def testPartitionByInstrumentC(self):
        from music21 import instrument
        from music21 import stream

        # basic case of instruments in Parts
        s = stream.Score()
        p1 = stream.Part()
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('a'), 6)
        # will go in next available offset
        p1.append(instrument.AcousticGuitar())
        p1.repeatAppend(note.Note('b'), 3)

        p2 = stream.Part()
        p2.append(instrument.Piccolo())
        p2.repeatAppend(note.Note('c'), 2)
        p2.append(instrument.Flute())
        p2.repeatAppend(note.Note('d'), 4)

        s.insert(0, p1)
        s.insert(0, p2)

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 4)  # 4 instruments
        self.assertEqual(len(post[instrument.Instrument]), 4)
        self.assertEqual(post.parts[0].getInstrument().instrumentName, 'Piano')
        self.assertEqual(len(post.parts[0].notes), 6)
        self.assertEqual(post.parts[1].getInstrument().instrumentName, 'Acoustic Guitar')
        self.assertEqual(len(post.parts[1].notes), 3)
        self.assertEqual(post.parts[2].getInstrument().instrumentName, 'Piccolo')
        self.assertEqual(len(post.parts[2].notes), 2)
        self.assertEqual(post.parts[3].getInstrument().instrumentName, 'Flute')
        self.assertEqual(len(post.parts[3].notes), 4)

        # environLocal.printDebug(['post processing'])
        # post.show('t')

    def testPartitionByInstrumentD(self):
        from music21 import instrument
        from music21 import stream

        # basic case of instruments in Parts
        s = stream.Score()
        p1 = stream.Part()
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('a'), 6)
        # will go in next available offset
        p1.append(instrument.AcousticGuitar())
        p1.repeatAppend(note.Note('b'), 3)
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('e'), 5)

        p2 = stream.Part()
        p2.append(instrument.Piccolo())
        p2.repeatAppend(note.Note('c'), 2)
        p2.append(instrument.Flute())
        p2.repeatAppend(note.Note('d'), 4)
        p2.append(instrument.Piano())
        p2.repeatAppend(note.Note('f'), 1)

        s.insert(0, p1)
        s.insert(0, p2)

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 4)  # 4 instruments
        self.assertEqual(len(post[instrument.Instrument]), 4)
        # piano spans are joined together
        self.assertEqual(post.parts[0].getInstrument().instrumentName, 'Piano')
        self.assertEqual(len(post.parts[0].notes), 12)

        self.assertEqual([n.offset for n in post.parts[0].notes],
                         [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 9.0, 10.0, 11.0, 12.0, 13.0])

        # environLocal.printDebug(['post processing'])
        # post.show('t')

    def testPartitionByInstrumentE(self):
        from music21 import instrument
        from music21 import stream

        # basic case of instruments in Parts
        # s = stream.Score()
        p1 = stream.Part()
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('a'), 6)
        # will go in next available offset
        p1.append(instrument.AcousticGuitar())
        p1.repeatAppend(note.Note('b'), 3)
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('e'), 5)

        p1.append(instrument.Piccolo())
        p1.repeatAppend(note.Note('c'), 2)
        p1.append(instrument.Flute())
        p1.repeatAppend(note.Note('d'), 4)
        p1.append(instrument.Piano())
        p1.repeatAppend(note.Note('f'), 1)

        s = p1

        post = instrument.partitionByInstrument(s)
        self.assertEqual(len(post), 4)  # 4 instruments
        self.assertEqual(len(post[instrument.Instrument]), 4)
        # piano spans are joined together
        self.assertEqual(post.parts[0].getInstrument().instrumentName, 'Piano')

        self.assertEqual(len(post.parts[0].notes), 12)
        offsetList = []
        ppn = post.parts[0].notes
        for n in ppn:
            offsetList.append(n.offset)

        self.assertEqual(offsetList,
                         [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 9.0, 10.0, 11.0, 12.0, 13.0, 20.0])

    def testPartitionByInstrumentF(self):
        from music21 import instrument
        from music21 import stream

        s1 = stream.Stream()
        s1.append(instrument.AcousticGuitar())
        s1.append(note.Note())
        s1.append(instrument.Tuba())
        s1.append(note.Note())

        post = instrument.partitionByInstrument(s1)
        self.assertEqual(len(post), 2)  # 4 instruments

    # def testPartitionByInstrumentDocTest(self):
    #     '''
    #     For debugging the doctest.
    #     '''
    #     from music21 import instrument, converter, stream
    #     p1 = converter.parse("tinynotation: 4/4 c4  d  e  f  g  a  b  c'  c1")
    #     p2 = converter.parse("tinynotation: 4/4 C#4 D# E# F# G# A# B# c#  C#1")
    #
    #     p1.getElementsByClass(stream.Measure)[0].insert(0.0, instrument.Piccolo())
    #     p1.getElementsByClass(stream.Measure)[0].insert(2.0, instrument.AltoSaxophone())
    #     p1.getElementsByClass(stream.Measure)[1].insert(3.0, instrument.Piccolo())
    #
    #     p2.getElementsByClass(stream.Measure)[0].insert(0.0, instrument.Trombone())
    #     p2.getElementsByClass(stream.Measure)[0].insert(3.0, instrument.Piccolo())  # not likely.
    #     p2.getElementsByClass(stream.Measure)[1].insert(1.0, instrument.Trombone())
    #
    #     s = stream.Score()
    #     s.insert(0, p1)
    #     s.insert(0, p2)
    #     s2 = instrument.partitionByInstrument(s)
    #     for p in s2.parts:
    #         p.makeRests(fillGaps=True, inPlace=True)

    def testLanguageChoice(self):
        from music21 import instrument

        # fromString

        testString = 'Klarinette'  # German name

        # Works when language not specified
        self.assertEqual(instrument.fromString(testString).instrumentName,
                         testString)

        workingExamples = ['german',  # Works with correct language for the term
                           'German'  # Not case-sensitive, so 'German' is also fine
                           ]

        for langStr in workingExamples:
            instrName = instrument.fromString(testString, language=langStr).instrumentName
            self.assertEqual(instrName, testString)

        failingExamples = ['french',  # Error when the language doesn't match the term
                           'finnish'  # Error for unsupported language
                           ]

        for langStr in failingExamples:
            self.assertRaises(InstrumentException,
                              instrument.fromString,
                              testString,
                              language=langStr)

        # getAllNamesForInstrument

        inst = instrument.Flute()
        # Working example
        self.assertEqual(instrument.getAllNamesForInstrument(inst,
                                                             language=SearchLanguage.ABBREVIATION),
                         {'abbreviation': ['fl']})
        # Error for unsupported language
        self.assertRaises(InstrumentException,
                          instrument.getAllNamesForInstrument,
                          inst,
                          language='finnish')


class TestExternal(unittest.TestCase):
    pass


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
