# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.duration import *


class Test(unittest.TestCase):

    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def testTuple(self):
        # create a tuplet with 5 dotted eighths in the place of 3 double-dotted
        # eighths
        dur1 = Duration()
        dur1.type = 'eighth'
        dur1.dots = 1

        dur2 = Duration()
        dur2.type = 'eighth'
        dur2.dots = 2

        tup1 = Tuplet()
        tup1.tupletActual = [5, dur1]
        tup1.tupletNormal = [3, dur2]

        self.assertEqual(tup1.totalTupletLength(), 2.625)

        # create a new dotted quarter and apply the tuplet to it
        dur3 = Duration()
        dur3.type = 'quarter'
        dur3.dots = 1
        dur3.tuplets = (tup1,)
        self.assertEqual(dur3.quarterLength, fractions.Fraction(21, 20))

        # create a tuplet with 3 sixteenths in the place of 2 sixteenths
        tup2 = Tuplet()
        dur4 = Duration()
        dur4.type = '16th'
        tup2.tupletActual = [3, dur4]
        tup2.tupletNormal = [2, dur4]

        self.assertEqual(tup2.totalTupletLength(), 0.5)
        self.assertEqual(tup2.tupletMultiplier(), fractions.Fraction(2, 3))

        dur3.tuplets = (tup1, tup2)
        self.assertEqual(dur3.quarterLength, opFrac(7 / 10))

        myTuplet = Tuplet()
        self.assertEqual(myTuplet.tupletMultiplier(), opFrac(2 / 3))
        myTuplet.tupletActual = [5, durationTupleFromTypeDots('eighth', 0)]
        self.assertEqual(myTuplet.tupletMultiplier(), opFrac(2 / 5))

    def testTupletTypeComplete(self):
        '''
        Test setting of tuplet type when durations sum to expected completion
        '''
        # default tuplets group into threes when possible
        from music21 import note  # only Notes/Rests/Chords can have tuplets, not music21Objects
        from music21 import stream
        test, match = ([0.333333] * 3 + [0.1666666] * 6,
                       ['start', None, 'stop', 'start', None, 'stop', 'start', None, 'stop'])
        inputTuplets = []
        for qLen in test:
            d = Duration()
            d.quarterLength = qLen
            inputTuplets.append(d)

        inputTupletStream = stream.Stream()
        for dur in inputTuplets:
            m21Obj = note.Note(duration=dur)
            inputTupletStream.append(m21Obj)

        stream.makeNotation.makeTupletBrackets(inputTupletStream, inPlace=True)
        output = []
        for d in inputTuplets:
            output.append(d.tuplets[0].type)
        self.assertEqual(output, match)

    def testTupletTypeComplete2(self):
        from music21 import note
        from music21 import stream

        tup6 = Duration()
        tup6.quarterLength = 0.16666666
        tup6.tuplets[0].numberNotesActual = 6
        tup6.tuplets[0].numberNotesNormal = 4

        tup5 = Duration()
        tup5.quarterLength = 0.2  # default is 5 in the space of 4 16th

        inputTuplets = [
            copy.deepcopy(tup6), copy.deepcopy(tup6), copy.deepcopy(tup6),
            copy.deepcopy(tup6), copy.deepcopy(tup6), copy.deepcopy(tup6),
            copy.deepcopy(tup5), copy.deepcopy(tup5), copy.deepcopy(tup5),
            copy.deepcopy(tup5), copy.deepcopy(tup5),
        ]

        inputTupletStream = stream.Stream()
        for dur in inputTuplets:
            m21Obj = note.Note(duration=dur)
            inputTupletStream.append(m21Obj)

        match = ['start', None, None, None, None, 'stop',
                 'start', None, None, None, 'stop']

        stream.makeNotation.makeTupletBrackets(inputTupletStream, inPlace=True)
        output = []
        for d in inputTuplets:
            output.append(d.tuplets[0].type)
        self.assertEqual(output, match)

    def testTupletTypeIncomplete(self):
        '''
        Test setting of tuplet type when durations do not sum to expected
        completion.
        '''
        from music21 import note
        from music21 import stream
        # the current match results here are a good compromise
        # for a difficult situation.

        # this is close to 1/3 and 1/6 but not exact and that's part of the test.
        test, match = ([0.333333] * 2 + [0.1666666] * 5,
                       ['start', None, None, 'stop', 'start', None, 'stop']
                       )
        inputDurations = []
        for qLen in test:
            d = Duration()
            d.quarterLength = qLen
            inputDurations.append(d)

        inputTupletStream = stream.Stream()
        for dur in inputDurations:
            m21Obj = note.Note(duration=dur)
            inputTupletStream.append(m21Obj)

        stream.makeNotation.makeTupletBrackets(inputTupletStream, inPlace=True)
        output = []
        for d in inputDurations:
            output.append(d.tuplets[0].type)
        # environLocal.printDebug(['got', output])
        self.assertEqual(output, match)

    def testTupletTypeNested(self):
        '''
        Nested tuplets are not fully supported (TODO).
        '''
        from music21 import note
        from music21 import stream

        gapful = stream.Measure()
        half = note.Note(type='half')
        gapful.repeatAppend(half, 3)
        for n in gapful:
            n.duration.appendTuplet(Tuplet(3, 2))

        # create nested tuplet on middle note
        gapful.notes[1].duration.appendTuplet(Tuplet(2, 1))

        gapless = stream.Measure()
        for n in gapful:
            gapless.append(n)

        # Redirect stderr to suppress printed warning
        # TODO: change to python warnings
        file_like = io.StringIO()
        with contextlib.redirect_stderr(file_like):
            made = stream.makeNotation.makeTupletBrackets(gapless)

        self.assertEqual(
            [el.duration.tuplets[0].type for el in made],
            ['startStop', None, 'startStop'],  # was ['start', None, 'stop']
        )

    def testAugmentOrDiminish(self):

        # test halfs and doubles

        for ql, half, double in [(2, 1, 4), (0.5, 0.25, 1), (1.5, 0.75, 3),
                                 (2 / 3, 1 / 3, 4 / 3)]:

            d = Duration()
            d.quarterLength = ql
            a = d.augmentOrDiminish(0.5)
            self.assertEqual(a.quarterLength, opFrac(half), 5)

            b = d.augmentOrDiminish(2)
            self.assertEqual(b.quarterLength, opFrac(double), 5)

        # testing tuplets in duration units

        a = Duration()
        a.type = 'eighth'
        tup1 = Tuplet(3, 2, 'eighth')
        a.appendTuplet(tup1)
        self.assertEqual(a.quarterLength, opFrac(1 / 3))
        self.assertEqual(a.aggregateTupletMultiplier(), opFrac(2 / 3))
        self.assertEqual(repr(a.tuplets[0].durationNormal),
                         "DurationTuple(type='eighth', dots=0, quarterLength=0.5)")

        b = a.augmentOrDiminish(2)
        self.assertEqual(b.quarterLength, opFrac(2 / 3))
        self.assertEqual(b.aggregateTupletMultiplier(), opFrac(2 / 3), 5)
        self.assertEqual(repr(b.tuplets[0].durationNormal),
                         "DurationTuple(type='quarter', dots=0, quarterLength=1.0)")

        c = b.augmentOrDiminish(0.25)
        self.assertEqual(c.aggregateTupletMultiplier(), opFrac(2 / 3), 5)
        self.assertEqual(repr(c.tuplets[0].durationNormal),
                         "DurationTuple(type='16th', dots=0, quarterLength=0.25)")

        # testing tuplets on Durations
        a = Duration()
        a.quarterLength = 1 / 3
        self.assertEqual(a.aggregateTupletMultiplier(), opFrac(2 / 3), 5)
        self.assertEqual(repr(a.tuplets[0].durationNormal),
                         "DurationTuple(type='eighth', dots=0, quarterLength=0.5)")

        b = a.augmentOrDiminish(2)
        self.assertEqual(b.aggregateTupletMultiplier(), opFrac(2 / 3), 5)
        self.assertEqual(repr(b.tuplets[0].durationNormal),
                         "DurationTuple(type='quarter', dots=0, quarterLength=1.0)")

        c = b.augmentOrDiminish(0.25)
        self.assertEqual(c.aggregateTupletMultiplier(), opFrac(2 / 3), 5)
        self.assertEqual(repr(c.tuplets[0].durationNormal),
                         "DurationTuple(type='16th', dots=0, quarterLength=0.25)")

    def testUnlinkedTypeA(self):
        from music21 import duration

        du = duration.Duration()
        du.linked = False
        du.quarterLength = 5.0
        du.type = 'quarter'
        self.assertEqual(du.quarterLength, 5.0)
        self.assertEqual(du.type, 'quarter')

        d = duration.Duration()
        self.assertTrue(d.linked)  # note set
        d.linked = False
        d.type = 'quarter'

        self.assertEqual(d.type, 'quarter')
        self.assertEqual(d.quarterLength, 0.0)  # note set
        self.assertFalse(d.linked)  # note set

        d.quarterLength = 20
        self.assertEqual(d.quarterLength, 20.0)
        self.assertFalse(d.linked)  # note set
        self.assertEqual(d.type, 'quarter')

        # can set type  and will remain unlinked
        d.type = '16th'
        self.assertEqual(d.type, '16th')
        self.assertEqual(d.quarterLength, 20.0)
        self.assertFalse(d.linked)  # note set

        # can set quarter length and will remain unlinked
        d.quarterLength = 0.0
        self.assertEqual(d.type, '16th')
        self.assertFalse(d.linked)  # note set

        # d = duration.Duration()
        # d.setTypeUnlinked('quarter')
        # self.assertEqual(d.type, 'quarter')
        # self.assertEqual(d.quarterLength, 0.0)  # note set
        # self.assertFalse(d.linked)  # note set
        #
        # d.setQuarterLengthUnlinked(20)
        # self.assertEqual(d.quarterLength, 20.0)
        # self.assertFalse(d.linked)  # note set


    def x_testStrangeMeasure(self):
        from music21 import corpus
        from music21 import stream
        j1 = corpus.parse('trecento/PMFC_06-Jacopo-03a')
        x = j1.parts[0].getElementsByClass(stream.Measure)[42]
        x._cache = {}
        print(x.duration)
        print(x.duration.components)

    def testSimpleSetQuarterLength(self):
        d = Duration()
        d.quarterLength = 1 / 3
        self.assertEqual(repr(d.quarterLength), 'Fraction(1, 3)')
        self.assertEqual(d._components, ())
        self.assertTrue(d._componentsNeedUpdating)
        self.assertEqual(str(d.components),
                         "(DurationTuple(type='eighth', dots=0, quarterLength=0.5),)")
        self.assertFalse(d._componentsNeedUpdating)
        self.assertFalse(d._quarterLengthNeedsUpdating)
        self.assertEqual(repr(d.quarterLength), 'Fraction(1, 3)')
        self.assertEqual(str(unitSpec(d)), "(Fraction(1, 3), 'eighth', 0, 3, 2, 'eighth')")

    def testTupletDurations(self):
        '''
        Test tuplet durations are assigned with proper duration

        This test was written while adding support for dotted tuplet notes
        '''
        # Before the fix, the duration was "Quarter Tuplet of 5/3rds (3/5 QL)"
        self.assertEqual(
            'Eighth Triplet (1/3 QL)',
            Duration(fractions.Fraction(1 / 3)).fullName
        )
        self.assertEqual(
            'Quarter Triplet (2/3 QL)',
            Duration(fractions.Fraction(2 / 3)).fullName
        )

        self.assertEqual(
            '16th Quintuplet (1/5 QL)',
            Duration(fractions.Fraction(1 / 5)).fullName
        )
        self.assertEqual(
            'Eighth Quintuplet (2/5 QL)',
            Duration(fractions.Fraction(2 / 5)).fullName
        )
        self.assertEqual(
            'Dotted Eighth Quintuplet (3/5 QL)',
            Duration(fractions.Fraction(3 / 5)).fullName
        )
        self.assertEqual(
            'Quarter Quintuplet (4/5 QL)',
            Duration(fractions.Fraction(4 / 5)).fullName
        )

        self.assertEqual(
            '16th Septuplet (1/7 QL)',
            Duration(fractions.Fraction(1 / 7)).fullName
        )
        self.assertEqual(
            'Eighth Septuplet (2/7 QL)',
            Duration(fractions.Fraction(2 / 7)).fullName
        )
        self.assertEqual(
            'Dotted Eighth Septuplet (3/7 QL)',
            Duration(fractions.Fraction(3 / 7)).fullName
        )
        self.assertEqual(
            'Quarter Septuplet (4/7 QL)',
            Duration(fractions.Fraction(4 / 7)).fullName
        )
        self.assertEqual(
            'Dotted Quarter Septuplet (6/7 QL)',
            Duration(fractions.Fraction(6 / 7)).fullName
        )

    def testTinyDuration(self):
        # e.g. delta from chordify: 1/9 - 1/8 = 1/72
        # exercises quarterLengthToNonPowerOf2Tuplet()
        d = Duration(1 / 72)
        self.assertEqual(d.type, 'inexpressible')

        # this failure happens earlier in quarterConversion()
        d = Duration(1 / 2049)
        self.assertEqual(d.type, 'inexpressible')

    def testExpressionIsInferred(self):
        d = Duration(0.5)
        self.assertEqual(d.expressionIsInferred, True)

        d.type = 'whole'
        self.assertEqual(d.expressionIsInferred, False)

        d.quarterLength = 0.25
        self.assertEqual(d.expressionIsInferred, True)

        d.dots = 1
        self.assertEqual(d.expressionIsInferred, False)

        d.appendTuplet(Tuplet(3, 2))
        # No change
        self.assertEqual(d.expressionIsInferred, False)

        d.linked = False
        d.quarterLength = 4
        d.dots = 1
        # No change, since this relationship between type
        # and quarterLength is usually accomplished in multiple
        # attribute assignments that could occur in any order
        self.assertEqual(d.expressionIsInferred, False)

    def testExceptions(self):
        '''
        These errors are user errors, so they raise generic exceptions
        so that catches for DurationException only get library calculation
        failures (e.g. bound checking).
        '''
        with self.assertRaises(TypeError):
            Duration('redundant type', type='eighth')
        dt = DurationTuple('quarter', 0, float('nan'))
        msg = 'Invalid quarterLength for DurationTuple: nan'
        with self.assertRaisesRegex(ValueError, msg):
            Duration(dt)
        # opFrac raises the ValueError for Duration(float('nan')), but
        # if opFrac ever changes still need to block creating duration
        # could cause infinite loop in makeMeasures() since nan != 0.0
        with self.assertRaises(ValueError):
            Duration(float('nan'))

        d = Duration(1 / 3)
        with self.assertRaises(TypeError):
            d.linked = 'do not link'
        with self.assertRaises(ValueError):
            d.componentIndexAtQtrPosition(400)
        with self.assertRaises(ValueError):
            d.componentIndexAtQtrPosition(-0.001)
        with self.assertRaises(TypeError):
            d.dotGroups = None
        with self.assertRaises(TypeError):
            d.dots = None
        with self.assertRaises(ValueError):
            d.type = 'custom'

        gd = GraceDuration()
        with self.assertRaises(ValueError):
            gd.makeTime = 'True'
        with self.assertRaises(ValueError):
            gd.slash = 'none'


class TestExternal(unittest.TestCase):
    show = True

    def testSingle(self):
        from music21 import note
        a = Duration()
        a.quarterLength = 2.66666
        n = note.Note()
        n.duration = a
        if self.show:
            n.show()

    def testBasic(self):
        import random
        from music21 import stream
        from music21 import note

        a = stream.Stream()

        for i in range(30):
            ql = random.choice([1, 2, 3, 4, 5]) + random.choice([0, 0.25, 0.5, 0.75])
            # w/ random.choice([0, 0.33333, 0.666666] gets an error
            n = note.Note()
            b = Duration()
            b.quarterLength = ql
            n.duration = b
            a.append(n)

        if self.show:
            a.show()


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
