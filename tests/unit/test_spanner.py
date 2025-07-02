# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.spanner import *


class Test(unittest.TestCase):

    def setUp(self):
        from music21.musicxml.m21ToXml import GeneralObjectExporter
        self.GEX = GeneralObjectExporter()

    def xmlStr(self, obj):
        xmlBytes = self.GEX.parse(obj)
        return xmlBytes.decode('utf-8')

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testBasic(self):

        # how parts might be grouped
        from music21 import stream
        from music21 import note
        from music21 import layout
        s = stream.Score()
        p1 = stream.Part()
        p2 = stream.Part()

        sg1 = layout.StaffGroup(p1, p2)

        # place all on Stream
        s.insert(0, p1)
        s.insert(0, p2)
        s.insert(0, sg1)

        self.assertEqual(len(s), 3)
        self.assertEqual(sg1.getSpannedElements(), [p1, p2])

        # make sure spanners is unified

        # how slurs might be defined
        n1 = note.Note()
        n2 = note.Note()
        n3 = note.Note()
        p1.append(n1)
        p1.append(n2)
        p1.append(n3)

        slur1 = Slur()
        slur1.addSpannedElements([n1, n3])

        p1.append(slur1)

        self.assertEqual(len(s), 3)
        self.assertEqual(slur1.getSpannedElements(), [n1, n3])

        # a note can access what spanners it is part of
        self.assertEqual(n1.getSpannerSites(), [slur1])

        # can a spanner hold spanners: yes
        sl1 = Slur()
        sl2 = Slur()
        sl3 = Slur()
        sp = Spanner([sl1, sl2, sl3])
        self.assertEqual(len(sp.getSpannedElements()), 3)
        self.assertEqual(sp.getSpannedElements(), [sl1, sl2, sl3])

        self.assertEqual(sl1.getSpannerSites(), [sp])

    def testSpannerAnchorRepr(self):
        from music21 import stream
        from music21 import spanner

        # SpannerAnchor with no activeSite
        sa1 = spanner.SpannerAnchor()
        self.assertEqual(repr(sa1), '<music21.spanner.SpannerAnchor unanchored>')

        # SpannerAnchor with activeSite, but no duration
        m = stream.Measure()
        m.insert(0.5, sa1)
        self.assertEqual(repr(sa1), '<music21.spanner.SpannerAnchor at 0.5>')

        # SpannerAnchor with activeSite and duration
        sa1.quarterLength = 2.5
        self.assertEqual(repr(sa1), '<music21.spanner.SpannerAnchor at 0.5-3.0>')

    def testSpannerRepr(self):
        from music21 import spanner
        su1 = spanner.Slur()
        self.assertEqual(repr(su1), '<music21.spanner.Slur>')

    def testSpannerFill(self):
        from music21 import stream
        from music21 import note
        from music21 import spanner
        theNotes = [note.Note('A'), note.Note('B'), note.Note('C'), note.Note('D')]
        m = stream.Measure(theNotes)

        # Spanner with no fillElementTypes
        sp = spanner.Spanner(theNotes[0], theNotes[3])
        sp.fill(m)
        # should not have done anything
        noFillElements = [theNotes[0], theNotes[3]]
        self.assertEqual(len(sp), 2)
        for i, el in enumerate(sp.getSpannedElements()):
            self.assertIs(el, noFillElements[i])

        # Ottava with filledStatus == True
        ott1 = spanner.Ottava(noFillElements)
        ott1.filledStatus = True  # pretend it has already been filled
        ott1.fill(m)
        # should not have done anything
        self.assertEqual(len(sp), 2)
        for i, el in enumerate(sp.getSpannedElements()):
            self.assertIs(el, noFillElements[i])

        # same Ottava but with filledStatus == False
        ott1.filledStatus = False
        ott1.fill(m)
        # ott1 should have been filled
        self.assertIs(ott1.filledStatus, True)
        self.assertEqual(len(ott1), 4)
        for i, el in enumerate(ott1.getSpannedElements()):
            self.assertIs(el, theNotes[i])

        # Ottava with no elements
        ott2 = spanner.Ottava()
        ott2.fill(m)
        self.assertEqual(len(ott2), 0)

        # Ottava with only element not in searchStream
        expectedElements = [note.Note('E')]
        ott3 = spanner.Ottava(expectedElements)
        ott3.fill(m)
        self.assertEqual(len(ott3), 1)
        self.assertIs(ott3.getFirst(), expectedElements[0])

        # Ottava with start element not in searchStream, end element is
        expectedElements = [note.Note('F'), m.notes[0]]
        ott4 = spanner.Ottava(expectedElements)
        ott4.fill(m)
        self.assertEqual(len(ott4), 2)
        for i, el in enumerate(ott4.getSpannedElements()):
            self.assertIs(el, expectedElements[i])

        # Ottava with endElement not in searchStream, startElement is
        expectedElements = [m.notes[0], note.Note('G')]
        ott5 = spanner.Ottava(expectedElements)
        ott5.fill(m)
        self.assertEqual(len(ott5), 2)
        for i, el in enumerate(ott5.getSpannedElements()):
            self.assertIs(el, expectedElements[i])

    def testSpannerBundle(self):
        from music21 import spanner
        from music21 import stream

        su1 = spanner.Slur()
        su1.idLocal = 1
        su2 = spanner.Slur()
        su2.idLocal = 2
        sb = spanner.SpannerBundle()
        sb.append(su1)
        sb.append(su2)
        self.assertEqual(len(sb), 2)
        self.assertEqual(sb[0], su1)
        self.assertEqual(sb[1], su2)

        su3 = spanner.Slur()
        su4 = spanner.Slur()

        s = stream.Stream()
        s.append(su3)
        s.append(su4)
        sb2 = spanner.SpannerBundle(list(s))
        self.assertEqual(len(sb2), 2)
        self.assertEqual(sb2[0], su3)
        self.assertEqual(sb2[1], su4)

    def testDeepcopySpanner(self):
        from music21 import spanner
        from music21 import note

        # how slurs might be defined
        n1 = note.Note()
        # n2 = note.Note()
        n3 = note.Note()

        su1 = Slur()
        su1.addSpannedElements([n1, n3])

        self.assertEqual(n1.getSpannerSites(), [su1])
        self.assertEqual(n3.getSpannerSites(), [su1])

        su2 = copy.deepcopy(su1)

        self.assertEqual(su1.getSpannedElements(), [n1, n3])
        self.assertEqual(su2.getSpannedElements(), [n1, n3])

        self.assertEqual(n1.getSpannerSites(), [su1, su2])
        self.assertEqual(n3.getSpannerSites(), [su1, su2])

        sb1 = spanner.SpannerBundle([su1, su2])
        sb2 = copy.deepcopy(sb1)
        self.assertEqual(sb1[0].getSpannedElements(), [n1, n3])
        self.assertEqual(sb2[0].getSpannedElements(), [n1, n3])
        # spanners stored within are not the same objects
        self.assertNotEqual(id(sb2[0]), id(sb1[0]))

    def testReplaceSpannedElement(self):
        from music21 import note
        from music21 import spanner

        n1 = note.Note()
        n2 = note.Note()
        n3 = note.Note()
        n4 = note.Note()
        n5 = note.Note()

        su1 = spanner.Slur()
        su1.addSpannedElements([n1, n3])

        self.assertEqual(su1.getSpannedElements(), [n1, n3])
        self.assertEqual(n1.getSpannerSites(), [su1])

        su1.replaceSpannedElement(n1, n2)
        self.assertEqual(su1.getSpannedElements(), [n2, n3])
        # this note now has no spanner sites
        self.assertEqual(n1.getSpannerSites(), [])
        self.assertEqual(n2.getSpannerSites(), [su1])

        # replace n2 w/ n1
        su1.replaceSpannedElement(n2, n1)
        self.assertEqual(su1.getSpannedElements(), [n1, n3])
        self.assertEqual(n2.getSpannerSites(), [])
        self.assertEqual(n1.getSpannerSites(), [su1])

        su2 = spanner.Slur()
        su2.addSpannedElements([n3, n4])

        su3 = spanner.Slur()
        su3.addSpannedElements([n4, n5])

        # n1a = note.Note()
        # n2a = note.Note()
        n3a = note.Note()
        n4a = note.Note()
        # n5a = note.Note()

        sb1 = spanner.SpannerBundle([su1, su2, su3])
        self.assertEqual(len(sb1), 3)
        self.assertEqual(list(sb1), [su1, su2, su3])

        # n3 is found in su1 and su2

        sb1.replaceSpannedElement(n3, n3a)
        self.assertEqual(len(sb1), 3)
        self.assertEqual(list(sb1), [su1, su2, su3])

        self.assertEqual(sb1[0].getSpannedElements(), [n1, n3a])
        # check su2
        self.assertEqual(sb1[1].getSpannedElements(), [n3a, n4])

        sb1.replaceSpannedElement(n4, n4a)
        self.assertEqual(sb1[1].getSpannedElements(), [n3a, n4a])

        # check su3
        self.assertEqual(sb1[2].getSpannedElements(), [n4a, n5])

    def testRepeatBracketA(self):
        from music21 import spanner
        from music21 import stream

        m1 = stream.Measure()
        rb1 = spanner.RepeatBracket(m1)
        # if added again; it is not really added, it simply is ignored
        rb1.addSpannedElements(m1)
        self.assertEqual(len(rb1), 1)

    def testRepeatBracketB(self):
        from music21 import note
        from music21 import spanner
        from music21 import stream
        from music21 import bar

        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note('c4'), 4)
        p.append(m1)
        m2 = stream.Measure()
        m2.repeatAppend(note.Note('d#4'), 4)
        p.append(m2)

        m3 = stream.Measure()
        m3.repeatAppend(note.Note('g#4'), 4)
        m3.rightBarline = bar.Repeat(direction='end')
        p.append(m3)
        p.append(spanner.RepeatBracket(m3, number=1))

        m4 = stream.Measure()
        m4.repeatAppend(note.Note('a4'), 4)
        m4.rightBarline = bar.Repeat(direction='end')
        p.append(m4)
        p.append(spanner.RepeatBracket(m4, number=2))

        m5 = stream.Measure()
        m5.repeatAppend(note.Note('b4'), 4)
        m5.rightBarline = bar.Repeat(direction='end')
        p.append(m5)
        p.append(spanner.RepeatBracket(m5, number=3))

        m6 = stream.Measure()
        m6.repeatAppend(note.Note('c#5'), 4)
        p.append(m6)

        # all spanners should be at the part level
        self.assertEqual(len(p.spanners), 3)

    # noinspection DuplicatedCode
    def testRepeatBracketC(self):
        from music21 import note
        from music21 import spanner
        from music21 import stream
        from music21 import bar

        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note('c4'), 4)
        p.append(m1)

        m2 = stream.Measure()
        m2.repeatAppend(note.Note('d#4'), 4)
        p.append(m2)

        m3 = stream.Measure()
        m3.repeatAppend(note.Note('g#4'), 4)
        m3.rightBarline = bar.Repeat(direction='end')
        p.append(m3)
        rb1 = spanner.RepeatBracket(number=1)
        rb1.addSpannedElements(m2, m3)
        self.assertEqual(len(rb1), 2)
        p.insert(0, rb1)

        m4 = stream.Measure()
        m4.repeatAppend(note.Note('a4'), 4)
        m4.rightBarline = bar.Repeat(direction='end')
        p.append(m4)
        p.append(spanner.RepeatBracket(m4, number=2))

        m5 = stream.Measure()
        m5.repeatAppend(note.Note('b4'), 4)
        p.append(m5)

        # p.show()
        # all spanners should be at the part level
        self.assertEqual(len(p.spanners), 2)

        # p.show()
        raw = self.xmlStr(p)
        self.assertGreater(raw.find('''<ending number="1" type="start" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="stop" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="start" />'''), 1)

    # noinspection DuplicatedCode
    def testRepeatBracketD(self):
        from music21 import note
        from music21 import spanner
        from music21 import stream
        from music21 import bar

        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note('c4'), 4)
        p.append(m1)

        m2 = stream.Measure()
        m2.repeatAppend(note.Note('d#4'), 4)
        p.append(m2)

        m3 = stream.Measure()
        m3.repeatAppend(note.Note('g#4'), 4)
        m3.rightBarline = bar.Repeat(direction='end')
        p.append(m3)
        rb1 = spanner.RepeatBracket(number=1)
        rb1.addSpannedElements(m2, m3)
        self.assertEqual(len(rb1), 2)
        p.insert(0, rb1)

        m4 = stream.Measure()
        m4.repeatAppend(note.Note('a4'), 4)
        p.append(m4)

        m5 = stream.Measure()
        m5.repeatAppend(note.Note('b4'), 4)
        m5.rightBarline = bar.Repeat(direction='end')
        p.append(m5)

        rb2 = spanner.RepeatBracket(number=2)
        rb2.addSpannedElements(m4, m5)
        self.assertEqual(len(rb2), 2)
        p.insert(0, rb2)

        m6 = stream.Measure()
        m6.repeatAppend(note.Note('a4'), 4)
        p.append(m6)

        m7 = stream.Measure()
        m7.repeatAppend(note.Note('b4'), 4)
        p.append(m7)

        m8 = stream.Measure()
        m8.repeatAppend(note.Note('a4'), 4)
        m8.rightBarline = bar.Repeat(direction='end')
        p.append(m8)

        rb3 = spanner.RepeatBracket(number=3)
        rb3.addSpannedElements(m6, m8)
        self.assertEqual(len(rb3), 2)
        p.insert(0, rb3)

        m9 = stream.Measure()
        m9.repeatAppend(note.Note('a4'), 4)
        p.append(m9)

        m10 = stream.Measure()
        m10.repeatAppend(note.Note('b4'), 4)
        p.append(m10)

        m11 = stream.Measure()
        m11.repeatAppend(note.Note('a4'), 4)
        p.append(m11)

        m12 = stream.Measure()
        m12.repeatAppend(note.Note('a4'), 4)
        m12.rightBarline = bar.Repeat(direction='end')
        p.append(m12)

        rb4 = spanner.RepeatBracket(number=4)
        rb4.addSpannedElements(m9, m10, m11, m12)
        self.assertEqual(len(rb4), 4)
        p.insert(0, rb4)

        # p.show()
        # all spanners should be at the part level
        self.assertEqual(len(p.getElementsByClass(stream.Measure)), 12)
        self.assertEqual(len(p.spanners), 4)

        raw = self.xmlStr(p)
        self.assertGreater(raw.find('''<ending number="1" type="start" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="stop" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="start" />'''), 1)

        p1 = copy.deepcopy(p)
        raw = self.xmlStr(p1)
        self.assertGreater(raw.find('''<ending number="1" type="start" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="stop" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="start" />'''), 1)

        p2 = copy.deepcopy(p1)
        raw = self.xmlStr(p2)
        self.assertGreater(raw.find('''<ending number="1" type="start" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="stop" />'''), 1)
        self.assertGreater(raw.find('''<ending number="2" type="start" />'''), 1)

    def testRepeatBracketE(self):
        from music21 import note
        from music21 import spanner
        from music21 import stream
        from music21 import bar

        p = stream.Part()
        m1 = stream.Measure(number=1)
        m1.repeatAppend(note.Note('c4'), 1)
        p.append(m1)
        m2 = stream.Measure(number=2)
        m2.repeatAppend(note.Note('d#4'), 1)
        p.append(m2)

        m3 = stream.Measure(number=3)
        m3.repeatAppend(note.Note('g#4'), 1)
        m3.rightBarline = bar.Repeat(direction='end')
        p.append(m3)
        p.append(spanner.RepeatBracket(m3, number=1))

        m4 = stream.Measure(number=4)
        m4.repeatAppend(note.Note('a4'), 1)
        m4.rightBarline = bar.Repeat(direction='end')
        p.append(m4)
        p.append(spanner.RepeatBracket(m4, number=2))

        m5 = stream.Measure(number=5)
        m5.repeatAppend(note.Note('b4'), 1)
        m5.rightBarline = bar.Repeat(direction='end')
        p.append(m5)
        p.append(spanner.RepeatBracket(m5, number=3))

        m6 = stream.Measure(number=6)
        m6.repeatAppend(note.Note('c#5'), 1)
        p.append(m6)

        # all spanners should be at the part level
        self.assertEqual(len(p.spanners), 3)

        # try copying once
        p1 = copy.deepcopy(p)
        self.assertEqual(len(p1.spanners), 3)
        m5 = p1.getElementsByClass(stream.Measure)[-2]
        sp3 = p1.spanners[2]
        self.assertTrue(sp3.hasSpannedElement(m5))
        # for m in p1.getElementsByClass(stream.Measure):
        #     print(m, id(m))
        # for sp in p1.spanners:
        #     print(sp, id(sp), [c for c in sp.getSpannedElementIds()])
        # p1.show()

        p2 = copy.deepcopy(p1)
        self.assertEqual(len(p2.spanners), 3)
        m5 = p2.getElementsByClass(stream.Measure)[-2]
        sp3 = p2.spanners[2]
        self.assertTrue(sp3.hasSpannedElement(m5))

        p3 = copy.deepcopy(p2)
        self.assertEqual(len(p3.spanners), 3)
        m5 = p3.getElementsByClass(stream.Measure)[-2]
        sp3 = p3.spanners[2]
        self.assertTrue(sp3.hasSpannedElement(m5))

    def testOttavaShiftA(self):
        '''
        Test basic octave shift creation and output, as well as passing
        objects through make measure calls.
        '''
        from music21 import stream
        from music21 import note
        from music21 import chord
        from music21.spanner import Ottava   # need to do it this way for classSet
        s = stream.Stream()
        s.repeatAppend(chord.Chord(['c-3', 'g4']), 12)
        # s.repeatAppend(note.Note(), 12)
        n1 = s.notes[0]
        n2 = s.notes[-1]
        sp1 = Ottava(n1, n2)  # default is 8va
        s.append(sp1)
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('octave-shift'), 2)
        self.assertEqual(raw.count('type="down"'), 1)
        # s.show()

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        n1 = s.notes[0]
        n2 = s.notes[-1]
        sp1 = Ottava(n1, n2, type='8vb')
        s.append(sp1)
        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('octave-shift'), 2)
        self.assertEqual(raw.count('type="up"'), 1)

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        n1 = s.notes[0]
        n2 = s.notes[-1]
        sp1 = Ottava(n1, n2, type='15ma')
        s.append(sp1)
        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('octave-shift'), 2)
        self.assertEqual(raw.count('type="down"'), 1)

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        n1 = s.notes[0]
        n2 = s.notes[-1]
        sp1 = Ottava(n1, n2, type='15mb')
        s.append(sp1)
        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('octave-shift'), 2)
        self.assertEqual(raw.count('type="up"'), 1)

    def testOttavaShiftB(self):
        '''
        Test a single note octave
        '''
        from music21 import stream
        from music21 import note
        from music21 import spanner
        s = stream.Stream()
        n = note.Note('c4')
        sp = spanner.Ottava(n)
        s.append(n)
        s.append(sp)
        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('octave-shift'), 2)
        self.assertEqual(raw.count('type="down"'), 1)

    def testCrescendoA(self):
        from music21 import stream
        from music21 import note
        from music21 import dynamics
        s = stream.Stream()
        # n1 = note.Note('C')
        # n2 = note.Note('D')
        # n3 = note.Note('E')
        #
        # s.append(n1)
        # s.append(note.Note('A'))
        # s.append(n2)
        # s.append(note.Note('B'))
        # s.append(n3)

        # s.repeatAppend(chord.Chord(['c-3', 'g4']), 12)
        s.repeatAppend(note.Note(type='half'), 4)
        n1 = s.notes[0]
        n1.pitch.step = 'D'
        # s.insert(n1.offset, dynamics.Dynamic('fff'))
        n2 = s.notes[len(s.notes) // 2]
        n2.pitch.step = 'E'
        # s.insert(n2.offset, dynamics.Dynamic('ppp'))
        n3 = s.notes[-1]
        n3.pitch.step = 'F'
        # s.insert(n3.offset, dynamics.Dynamic('ff'))
        sp1 = dynamics.Diminuendo(n1, n2)
        sp2 = dynamics.Crescendo(n2, n3)
        s.append(sp1)
        s.append(sp2)
        # s._reprText()
        # s.show('t')
        raw = self.xmlStr(s)
        # print(raw)
        self.assertEqual(raw.count('<wedge'), 4)

        # self.assertEqual(raw.count('octave-shift'), 2)

    def testLineA(self):
        from music21 import stream
        from music21 import note
        from music21 import spanner

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        n1 = s.notes[0]
        n2 = s.notes[len(s.notes) // 2]
        n3 = s.notes[-1]
        sp1 = spanner.Line(n1, n2, startTick='up', lineType='dotted')
        sp2 = spanner.Line(n2, n3, startTick='down', lineType='dashed',
                                    endHeight=40)
        s.append(sp1)
        s.append(sp2)
        # s.show('t')
        raw = self.xmlStr(s)
        # print(raw)
        self.assertEqual(raw.count('<bracket'), 4)

    def testLineB(self):
        from music21 import stream
        from music21 import note
        from music21 import spanner

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        n1 = s.notes[4]
        n2 = s.notes[-1]

        n3 = s.notes[0]
        n4 = s.notes[2]

        sp1 = spanner.Line(n1, n2, startTick='up', endTick='down', lineType='solid')
        sp2 = spanner.Line(n3, n4, startTick='arrow', endTick='none', lineType='solid')

        s.append(sp1)
        s.append(sp2)

        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('<bracket'), 4)
        self.assertEqual(raw.count('line-end="arrow"'), 1)
        self.assertEqual(raw.count('line-end="none"'), 1)
        self.assertEqual(raw.count('line-end="up"'), 1)
        self.assertEqual(raw.count('line-end="down"'), 1)

    def testGlissandoA(self):
        from music21 import stream
        from music21 import note
        from music21 import spanner

        s = stream.Stream()
        s.repeatAppend(note.Note(), 3)
        for i, n in enumerate(s.notes):
            n.transpose(i + (i % 2 * 12), inPlace=True)

        # note: this does not support glissandi between non-adjacent notes
        n1 = s.notes[0]
        n2 = s.notes[len(s.notes) // 2]
        n3 = s.notes[-1]
        sp1 = spanner.Glissando(n1, n2)
        sp2 = spanner.Glissando(n2, n3)
        sp2.lineType = 'dashed'
        s.append(sp1)
        s.append(sp2)
        s = s.makeNotation()
        # s.show('t')
        raw = self.xmlStr(s)
        # print(raw)
        self.assertEqual(raw.count('<glissando'), 4)
        self.assertEqual(raw.count('line-type="dashed"'), 2)

    def testGlissandoB(self):
        from music21 import stream
        from music21 import note
        from music21 import spanner

        s = stream.Stream()
        s.repeatAppend(note.Note(), 12)
        for i, n in enumerate(s.notes):
            n.transpose(i + (i % 2 * 12), inPlace=True)

        # note: this does not support glissandi between non-adjacent notes
        n1 = s.notes[0]
        n2 = s.notes[1]
        sp1 = spanner.Glissando(n1, n2)
        sp1.lineType = 'solid'
        sp1.label = 'gliss.'
        s.append(sp1)

        # s.show()
        raw = self.xmlStr(s)
        self.assertEqual(raw.count('<glissando'), 2)
        self.assertEqual(raw.count('line-type="solid"'), 2)
        self.assertEqual(raw.count('>gliss.<'), 1)

    # def testDashedLineA(self):
    #     from music21 import stream, note, spanner, chord, dynamics
    #     s = stream.Stream()
    #     s.repeatAppend(note.Note(), 12)
    #     for i, n in enumerate(s.notes):
    #         n.transpose(i + (i % 2 * 12), inPlace=True)
    #
    #     # note: Musedata presently does not support these
    #     n1 = s.notes[0]
    #     n2 = s.notes[len(s.notes) // 2]
    #     n3 = s.notes[-1]
    #     sp1 = spanner.DashedLine(n1, n2)
    #     sp2 = spanner.DashedLine(n2, n3)
    #     s.append(sp1)
    #     s.append(sp2)
    #     raw = s.musicxml
    #     self.assertEqual(raw.count('<dashes'), 4)

    def testOneElementSpanners(self):
        from music21 import note
        from music21.spanner import Spanner

        n1 = note.Note()
        sp = Spanner()
        sp.addSpannedElements(n1)
        sp.completeStatus = True
        self.assertTrue(sp.completeStatus)
        self.assertTrue(sp.isFirst(n1))
        self.assertTrue(sp.isLast(n1))

    def testRemoveSpanners(self):
        from music21 import stream
        from music21 import note
        from music21.spanner import Spanner, Slur

        p = stream.Part()
        m1 = stream.Measure()
        m2 = stream.Measure()
        m1.number = 1
        m2.number = 2
        n1 = note.Note('C#4', type='whole')
        n2 = note.Note('D#4', type='whole')
        m1.insert(0, n1)
        m2.insert(0, n2)
        p.append(m1)
        p.append(m2)
        sl = Slur([n1, n2])
        p.insert(0, sl)
        for x in p:
            if isinstance(x, Spanner):
                p.remove(x)
        self.assertEqual(len(p.spanners), 0)

    def testFreezeSpanners(self):
        from music21 import stream
        from music21 import note
        from music21 import converter
        from music21.spanner import Slur

        p = stream.Part()
        m1 = stream.Measure()
        m2 = stream.Measure()
        m1.number = 1
        m2.number = 2
        n1 = note.Note('C#4', type='whole')
        n2 = note.Note('D#4', type='whole')
        m1.insert(0, n1)
        m2.insert(0, n2)
        p.append(m1)
        p.append(m2)
        sl = Slur([n1, n2])
        p.insert(0, sl)
        unused_data = converter.freezeStr(p, fmt='pickle')

    def testDeepcopyJustSpannerAndNotes(self):
        from music21 import note
        from music21 import clef
        from music21.spanner import Spanner

        n1 = note.Note('g')
        n2 = note.Note('f#')
        c1 = clef.AltoClef()

        sp1 = Spanner(n1, n2, c1)
        sp2 = copy.deepcopy(sp1)
        self.assertEqual(len(sp2.spannerStorage), 3)
        self.assertIsNot(sp1, sp2)
        self.assertIs(sp2[0], sp1[0])
        self.assertIs(sp2[2], sp1[2])
        self.assertIs(sp1[0], n1)
        self.assertIs(sp2[0], n1)

    def testDeepcopySpannerInStreamNotNotes(self):
        from music21 import note
        from music21 import clef
        from music21 import stream
        from music21.spanner import Spanner

        n1 = note.Note('g')
        n2 = note.Note('f#')
        c1 = clef.AltoClef()

        sp1 = Spanner(n1, n2, c1)
        st1 = stream.Stream()
        st1.insert(0.0, sp1)
        st2 = copy.deepcopy(st1)

        sp2 = st2.spanners[0]
        self.assertEqual(len(sp2.spannerStorage), 3)
        self.assertIsNot(sp1, sp2)
        self.assertIs(sp2[0], sp1[0])
        self.assertIs(sp2[2], sp1[2])
        self.assertIs(sp1[0], n1)
        self.assertIs(sp2[0], n1)

    def testDeepcopyNotesInStreamNotSpanner(self):
        from music21 import note
        from music21 import clef
        from music21 import stream
        from music21.spanner import Spanner

        n1 = note.Note('g')
        n2 = note.Note('f#')
        c1 = clef.AltoClef()

        sp1 = Spanner(n1, n2, c1)
        st1 = stream.Stream()
        st1.insert(0.0, n1)
        st1.insert(1.0, n2)
        st2 = copy.deepcopy(st1)

        n3 = st2.notes[0]
        self.assertEqual(len(n3.getSpannerSites()), 1)
        sp2 = n3.getSpannerSites()[0]
        self.assertIs(sp1, sp2)
        self.assertIsNot(n1, n3)
        self.assertIs(sp2[2], sp1[2])
        self.assertIs(sp1[0], n1)
        self.assertIs(sp2[0], n1)

    def testDeepcopyNotesAndSpannerInStream(self):
        from music21 import note
        from music21 import stream
        from music21.spanner import Spanner

        n1 = note.Note('G4')
        n2 = note.Note('F#4')

        sp1 = Spanner(n1, n2)
        st1 = stream.Stream()
        st1.insert(0.0, sp1)
        st1.insert(0.0, n1)
        st1.insert(1.0, n2)
        st2 = copy.deepcopy(st1)
        n3 = st2.notes[0]
        self.assertEqual(len(n3.getSpannerSites()), 1)
        sp2 = n3.getSpannerSites()[0]
        self.assertIsNot(sp1, sp2)
        self.assertIsNot(n1, n3)

        sp3 = st2.spanners[0]
        self.assertIs(sp2, sp3)
        self.assertIs(sp1[0], n1)
        self.assertIs(sp2[0], n3)

    def testDeepcopyStreamWithSpanners(self):
        from music21 import note
        from music21 import stream
        from music21.spanner import Slur

        n1 = note.Note()
        su1 = Slur((n1,))
        s = stream.Stream()
        s.insert(0.0, su1)
        s.insert(0.0, n1)
        self.assertIs(s.spanners[0].getFirst(), n1)
        self.assertIs(s.notes[0].getSpannerSites()[0], su1)

        s2 = copy.deepcopy(s)
        su2 = s2.spanners[0]
        n2 = s2.notes[0]
        self.assertIsNot(su2, su1)
        self.assertIsNot(n2, n1)
        self.assertIs(s2.spanners[0].getFirst(), n2)
        self.assertIs(s2.notes[0].getSpannerSites()[0], su2)
        self.assertIsNot(s.notes[0].getSpannerSites()[0], su2)
        self.assertEqual(len(s2.spannerBundle), 1)
        tn2 = s2.spannerBundle.getBySpannedElement(n2)
        self.assertEqual(len(tn2), 1)

    def testGetSpannedElementIds(self):
        from music21 import note
        from music21.spanner import Spanner

        n1 = note.Note('g')
        n2 = note.Note('f#')
        n3 = note.Note('e')
        n4 = note.Note('d-')
        n5 = note.Note('c')

        sl = Spanner()
        sl.addSpannedElements(n1)
        sl.addSpannedElements(n2, n3)
        sl.addSpannedElements([n4, n5])
        idList = [id(n) for n in [n1, n2, n3, n4, n5]]
        slList = sl.getSpannedElementIds()
        self.assertEqual(idList, slList)

    def testHammerOnPullOff(self):
        from music21 import converter
        from music21.musicxml import testPrimitive

        s = converter.parse(testPrimitive.notations32a)

        num_hammer_on = len(s.flatten().getElementsByClass('HammerOn'))
        num_pull_off = len(s.flatten().getElementsByClass('PullOff'))
        self.assertEqual(num_hammer_on, 1)
        self.assertEqual(num_pull_off, 1)

        hammer_on = s.flatten().getElementsByClass('HammerOn')[0]
        hammer_n0 = hammer_on.getSpannedElements()[0]
        hammer_n1 = hammer_on.getSpannedElements()[1]
        self.assertEqual(hammer_n0.getSpannerSites()[0], hammer_on)
        self.assertEqual(hammer_n1.getSpannerSites()[0], hammer_on)

        pull_off = s.flatten().getElementsByClass('PullOff')[0]
        pull_n0 = pull_off.getSpannedElements()[0]
        pull_n1 = pull_off.getSpannedElements()[1]
        self.assertEqual(pull_n0.getSpannerSites()[0], pull_off)
        self.assertEqual(pull_n1.getSpannerSites()[0], pull_off)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
