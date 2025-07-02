# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.tempo import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testSetup(self):
        mm1 = MetronomeMark(number=60, referent=note.Note(type='quarter'))
        self.assertEqual(mm1.number, 60)

        tm1 = TempoText('Lebhaft')
        self.assertEqual(tm1.text, 'Lebhaft')

    def testUnicode(self):
        # test with no arguments
        TempoText()
        # test with arguments
        TempoText('adagio')

        # environLocal.printDebug(['testing tempo instantiation', tm])
        mm = MetronomeMark('adagio')
        self.assertEqual(mm.number, 56)
        self.assertTrue(mm.numberImplicit)

        self.assertEqual(mm.number, 56)
        tm2 = TempoText('très vite')

        self.assertEqual(tm2.text, 'très vite')
        mm = tm2.getMetronomeMark()
        self.assertEqual(mm.number, 144)

    def testTempoTextStyle(self):
        from music21 import tempo
        tm = tempo.TempoText('adagio')
        self.assertEqual(tm.style.absoluteY, 45)
        self.assertEqual(tm.style.fontStyle, 'bold')
        tm.style.absoluteY = 33
        self.assertEqual(tm.style.absoluteY, 33)
        tm.style.fontStyle = 'italic'
        tm.style.fontWeight = None

        # check that tm.getTextExpression()/tm.text does not modify style
        tx = tm.text
        self.assertEqual(tx, 'adagio')
        te1 = tm.getTextExpression()
        self.assertEqual(te1.content, 'adagio')
        self.assertEqual(tm.style.absoluteY, 33)
        self.assertEqual(tm.style.fontStyle, 'italic')

        # check that tm.setTextExpression sets tm.style to the te's style (if there is one),
        # and links the two styles
        te2 = expressions.TextExpression('andante')
        te2.style.absoluteY = 38
        te2.style.fontStyle = 'bolditalic'
        self.assertEqual(te2.style.absoluteY, 38)
        self.assertEqual(te2.style.fontStyle, 'bolditalic')
        tm.setTextExpression(te2)
        self.assertEqual(tm.style.absoluteY, 38)
        self.assertEqual(tm.style.fontStyle, 'bolditalic')
        self.assertIs(tm.style, te2.style)      # check for linked styles

        # check again that calling tm.getTextExpression/tm.text doesn't modify style
        tm.getTextExpression()
        tx = tm.text
        self.assertEqual(tx, 'andante')
        self.assertEqual(tm.style.absoluteY, 38)
        self.assertEqual(tm.style.fontStyle, 'bolditalic')

        # check that tm.setTextExpression (to a textExpression with no
        # style) leaves tm.style in place and links the two styles.
        te3 = expressions.TextExpression('andante with no style')
        self.assertFalse(te3.hasStyleInformation)
        self.assertTrue(tm.hasStyleInformation)
        tm.setTextExpression(te3)
        self.assertEqual(tm.style.absoluteY, 38)            # same as before
        self.assertEqual(tm.style.fontStyle, 'bolditalic')  # same as before
        self.assertIs(tm.style, te2.style)      # check for linked styles

        # check again that calling tm.getTextExpression/tm.text doesn't modify style
        tm.getTextExpression()
        tx = tm.text
        self.assertEqual(tx, 'andante with no style')
        self.assertEqual(tm.style.absoluteY, 38)
        self.assertEqual(tm.style.fontStyle, 'bolditalic')

        # check that tm.setTextExpression(te4) (with tm and te4 with no style) links the
        # two styles, with default style set in place.
        tm.style = None
        te4 = expressions.TextExpression('andante with no style')
        self.assertFalse(te4.hasStyleInformation)
        self.assertFalse(tm.hasStyleInformation)
        tm.setTextExpression(te4)
        self.assertEqual(tm.style.absoluteY, 45)        # default
        self.assertEqual(tm.style.fontStyle, 'bold')    # default
        self.assertIs(tm.style, te4.style)      # check for linked styles

    def testMetronomeMarkA(self):
        from music21 import tempo
        mm = tempo.MetronomeMark()
        mm.number = 56  # should implicitly set text
        self.assertEqual(mm.text, 'adagio')
        self.assertTrue(mm.textImplicit)
        mm.text = 'slowish'
        self.assertEqual(mm.text, 'slowish')
        self.assertFalse(mm.textImplicit)
        # default
        self.assertEqual(mm.referent.quarterLength, 1.0)

        # setting the text first
        mm = tempo.MetronomeMark()
        mm.text = 'presto'
        mm.referent = duration.Duration(3.0)
        self.assertEqual(mm.text, 'presto')
        self.assertEqual(mm.number, 184)
        self.assertTrue(mm.numberImplicit)
        mm.number = 200
        self.assertEqual(mm.number, 200)
        self.assertFalse(mm.numberImplicit)
        # still have default
        self.assertEqual(mm.referent.quarterLength, 3.0)
        self.assertEqual(repr(mm), '<music21.tempo.MetronomeMark presto Dotted Half=200>')

    def testMetronomeMarkB(self):
        mm = MetronomeMark()
        # with no args these are set to None
        self.assertEqual(mm.numberImplicit, None)
        self.assertEqual(mm.textImplicit, None)

        mm = MetronomeMark(number=100)
        self.assertEqual(mm.number, 100)
        self.assertFalse(mm.numberImplicit)
        self.assertEqual(mm.text, None)
        # not set
        self.assertEqual(mm.textImplicit, None)

        mm = MetronomeMark(number=101, text='rapido')
        self.assertEqual(mm.number, 101)
        self.assertFalse(mm.numberImplicit)
        self.assertEqual(mm.text, 'rapido')
        self.assertFalse(mm.textImplicit)

    def testMetronomeModulationA(self):
        from music21 import tempo
        # need to create a mm without a speed
        # want to say that an eighth is becoming the speed of a sixteenth
        mm1 = tempo.MetronomeMark(referent=0.5, number=120)
        mm2 = tempo.MetronomeMark(referent='16th')

        mmod1 = tempo.MetricModulation()
        mmod1.oldMetronome = mm1
        mmod1.newMetronome = mm2

        # this works and new value is updated:
        self.assertEqual(str(mmod1),
                         '<music21.tempo.MetricModulation '
                         + '<music21.tempo.MetronomeMark animato Eighth=120>='
                         + '<music21.tempo.MetronomeMark animato 16th=120>>')

        # we can get the same result by using setEqualityByReferent()
        mm1 = tempo.MetronomeMark(referent=0.5, number=120)
        mmod1 = tempo.MetricModulation()
        mmod1.oldMetronome = mm1
        # will automatically set right mm, as presently is None
        mmod1.setOtherByReferent(referent='16th')
        # should get the same result as above, but with defined value
        self.assertEqual(str(mmod1),
                         '<music21.tempo.MetricModulation '
                         + '<music21.tempo.MetronomeMark animato Eighth=120>='
                         + '<music21.tempo.MetronomeMark animato 16th=120>>')
        # the effective speed as been slowed by this modulation
        self.assertEqual(mmod1.oldMetronome.getQuarterBPM(), 60.0)
        self.assertEqual(mmod1.newMetronome.getQuarterBPM(), 30.0)

    def testGetPreviousMetronomeMarkA(self):
        from music21 import tempo
        from music21 import stream

        # test getting basic metronome marks
        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note(quarterLength=1), 4)
        m2 = copy.deepcopy(m1)
        mm1 = tempo.MetronomeMark(number=56, referent=0.25)
        m1.insert(0, mm1)
        mm2 = tempo.MetronomeMark(number=150, referent=0.5)
        m2.insert(0, mm2)
        p.append([m1, m2])
        self.assertEqual(str(mm2.getPreviousMetronomeMark()),
                         '<music21.tempo.MetronomeMark adagio 16th=56>')
        # p.show()

    def testGetPreviousMetronomeMarkB(self):
        from music21 import tempo
        from music21 import stream

        # test using a tempo text, will return a default metronome mark if possible
        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note(quarterLength=1), 4)
        m2 = copy.deepcopy(m1)
        mm1 = tempo.TempoText('slow')
        m1.insert(0, mm1)
        mm2 = tempo.MetronomeMark(number=150, referent=0.5)
        m2.insert(0, mm2)
        p.append([m1, m2])
        self.assertEqual(str(mm2.getPreviousMetronomeMark()),
                         '<music21.tempo.MetronomeMark slow Quarter=56>')
        # p.show()

    def testGetPreviousMetronomeMarkC(self):
        from music21 import tempo
        from music21 import stream

        # test using a metric modulation
        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note(quarterLength=1), 4)
        m2 = copy.deepcopy(m1)
        m3 = copy.deepcopy(m2)

        mm1 = tempo.MetronomeMark('slow')
        m1.insert(0, mm1)

        mm2 = tempo.MetricModulation()
        mm2.oldMetronome = tempo.MetronomeMark(referent=1, number=52)
        mm2.setOtherByReferent(referent='16th')
        m2.insert(0, mm2)

        mm3 = tempo.MetronomeMark(number=150, referent=0.5)
        m3.insert(0, mm3)

        p.append([m1, m2, m3])
        # p.show()

        self.assertEqual(str(mm3.getPreviousMetronomeMark()),
                         '<music21.tempo.MetronomeMark lento 16th=52>')

    def testSetReferentA(self):
        '''
        Test setting referents directly via context searches.
        '''
        from music21 import stream
        from music21 import tempo
        p = stream.Part()
        m1 = stream.Measure()
        m1.repeatAppend(note.Note(quarterLength=1), 4)
        m2 = copy.deepcopy(m1)
        m3 = copy.deepcopy(m2)

        mm1 = tempo.MetronomeMark(number=92)
        m1.insert(0, mm1)

        mm2 = tempo.MetricModulation()
        m2.insert(0, mm2)

        p.append([m1, m2, m3])

        mm2.oldReferent = 0.25
        self.assertEqual(str(mm2.oldMetronome),
                         '<music21.tempo.MetronomeMark moderate 16th=368>')
        mm2.setOtherByReferent(referent=2)
        self.assertEqual(str(mm2.newMetronome),
                         '<music21.tempo.MetronomeMark moderate Half=368>')
        # p.show()

    def testSetReferentB(self):
        from music21 import tempo
        from music21 import stream
        s = stream.Stream()
        mm1 = tempo.MetronomeMark(number=60)
        s.append(mm1)
        s.repeatAppend(note.Note(quarterLength=1), 2)
        s.repeatAppend(note.Note(quarterLength=0.5), 4)

        mmod1 = tempo.MetricModulation()
        mmod1.oldReferent = 0.5  # can use Duration objects
        mmod1.newReferent = 'quarter'  # can use Duration objects
        s.append(mmod1)
        mmod1.updateByContext()

        self.assertEqual(str(mmod1.oldMetronome.referent), '<music21.duration.Duration 0.5>')
        self.assertEqual(mmod1.oldMetronome.number, 120)
        self.assertEqual(str(mmod1.newMetronome),
                         '<music21.tempo.MetronomeMark animato Quarter=120>')

        s.append(note.Note())
        s.repeatAppend(note.Note(quarterLength=1.5), 2)

        mmod2 = tempo.MetricModulation()
        mmod2.oldReferent = 1.5
        mmod2.newReferent = 'quarter'  # can use Duration objects
        s.append(mmod2)
        mmod2.updateByContext()
        self.assertEqual(str(mmod2.oldMetronome),
                         '<music21.tempo.MetronomeMark animato Dotted Quarter=80>')
        self.assertEqual(str(mmod2.newMetronome),
                         '<music21.tempo.MetronomeMark andantino Quarter=80>')

        # s.repeatAppend(note.Note(), 4)
        # s.show()

    def testSetReferentC(self):
        from music21 import tempo
        from music21 import stream
        s = stream.Stream()
        mm1 = tempo.MetronomeMark(number=60)
        s.append(mm1)
        s.repeatAppend(note.Note(quarterLength=1), 2)
        s.repeatAppend(note.Note(quarterLength=0.5), 4)

        mmod1 = tempo.MetricModulation()
        s.append(mmod1)
        mmod1.oldReferent = 0.5  # can use Duration objects
        mmod1.newReferent = 'quarter'  # can use Duration objects

        self.assertEqual(str(mmod1.oldMetronome.referent), '<music21.duration.Duration 0.5>')
        self.assertEqual(mmod1.oldMetronome.number, 120)
        self.assertEqual(str(mmod1.newMetronome),
                         '<music21.tempo.MetronomeMark larghetto Quarter=120>')

        s.append(note.Note())
        s.repeatAppend(note.Note(quarterLength=1.5), 2)

        mmod2 = tempo.MetricModulation()
        s.append(mmod2)
        mmod2.oldReferent = 1.5
        mmod2.newReferent = 'quarter'  # can use Duration objects

        self.assertEqual(str(mmod2.oldMetronome),
                         '<music21.tempo.MetronomeMark larghetto Dotted Quarter=80>')
        self.assertEqual(str(mmod2.newMetronome),
                         '<music21.tempo.MetronomeMark larghetto Quarter=80>')
        # s.repeatAppend(note.Note(), 4)
        # s.show()

    def testSetReferentD(self):
        from music21 import tempo
        from music21 import stream
        s = stream.Stream()
        mm1 = tempo.MetronomeMark(number=60)
        s.append(mm1)
        s.repeatAppend(note.Note(quarterLength=1), 2)
        s.repeatAppend(note.Note(quarterLength=0.5), 4)

        mmod1 = tempo.MetricModulation()
        s.append(mmod1)
        # even with we have no assigned metronome, update context will create
        mmod1.updateByContext()

        self.assertEqual(str(mmod1.oldMetronome.referent), '<music21.duration.Duration 1.0>')
        self.assertEqual(mmod1.oldMetronome.number, 60)  # value form last mm
        # still have not set new
        self.assertEqual(mmod1.newMetronome, None)

        mmod1.newReferent = 0.25
        self.assertEqual(str(mmod1.newMetronome), '<music21.tempo.MetronomeMark larghetto 16th=60>')
        # s.append(note.Note())
        # s.repeatAppend(note.Note(quarterLength=1.5), 2)

    def testSetReferentE(self):
        from music21 import stream

        s = stream.Stream()
        mm1 = MetronomeMark(number=70)
        s.append(mm1)
        s.repeatAppend(note.Note(quarterLength=1), 2)
        s.repeatAppend(note.Note(quarterLength=0.5), 4)

        mmod1 = MetricModulation()
        mmod1.oldReferent = 'eighth'
        mmod1.newReferent = 'half'
        s.append(mmod1)
        self.assertEqual(mmod1.oldMetronome.number, 140)
        self.assertEqual(mmod1.newMetronome.number, 140)

        s = stream.Stream()
        mm1 = MetronomeMark(number=70)
        s.append(mm1)
        s.repeatAppend(note.Note(quarterLength=1), 2)
        s.repeatAppend(note.Note(quarterLength=0.5), 4)

        # make sure it works in reverse too
        mmod1 = MetricModulation()
        mmod1.oldReferent = 'eighth'
        mmod1.newReferent = 'half'
        s.append(mmod1)
        self.assertEqual(mmod1.newMetronome.number, 140)
        self.assertEqual(mmod1.oldMetronome.number, 140)
        self.assertEqual(mmod1.number, 140)

    def testSecondsPerQuarterA(self):
        mm = MetronomeMark(referent=1.0, number=120.0)
        self.assertEqual(mm.secondsPerQuarter(), 0.5)
        self.assertEqual(mm.durationToSeconds(120), 60.0)
        self.assertEqual(mm.secondsToDuration(60.0).quarterLength, 120.0)

        mm = MetronomeMark(referent=0.5, number=120.0)
        self.assertEqual(mm.secondsPerQuarter(), 1.0)
        self.assertEqual(mm.durationToSeconds(60), 60.0)
        self.assertEqual(mm.secondsToDuration(60.0).quarterLength, 60.0)

        mm = MetronomeMark(referent=2.0, number=120.0)
        self.assertEqual(mm.secondsPerQuarter(), 0.25)
        self.assertEqual(mm.durationToSeconds(240), 60.0)
        self.assertEqual(mm.secondsToDuration(60.0).quarterLength, 240.0)

        mm = MetronomeMark(referent=1.5, number=120.0)
        self.assertAlmostEqual(mm.secondsPerQuarter(), 1 / 3)
        self.assertEqual(mm.durationToSeconds(180), 60.0)
        self.assertEqual(mm.secondsToDuration(60.0).quarterLength, 180.0)

    def testStylesAreShared(self):
        halfNote = note.Note(type='half')
        mm = MetronomeMark('slow', 40, halfNote)
        mm.style.justify = 'left'
        self.assertIs(mm._tempoText.style, mm.style)
        self.assertIs(mm._tempoText._textExpression.style, mm.style)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
