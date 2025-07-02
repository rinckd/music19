# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.variant import *


class Test(unittest.TestCase):
    def testCopyAndDeepcopy(self):
        from music21.test.commonTest import testCopyAll
        testCopyAll(self, globals())

    def pitchOut(self, listIn):
        out = '['
        for p in listIn:
            out += str(p) + ', '
        out = out[0:len(out) - 2]
        out += ']'
        return out

    def testBasicA(self):
        o = Variant()
        o.append(note.Note('G3', quarterLength=2.0))
        o.append(note.Note('f3', quarterLength=2.0))

        self.assertEqual(o.highestOffset, 0)
        self.assertEqual(o.highestTime, 0)

        o.exposeTime = True

        self.assertEqual(o.highestOffset, 2.0)
        self.assertEqual(o.highestTime, 4.0)


    def testBasicB(self):
        '''
        Testing relaying attributes requests to private Stream with __getattr__
        '''
        v = Variant()
        v.append(note.Note('G3', quarterLength=2.0))
        v.append(note.Note('f3', quarterLength=2.0))
        # these are Stream attributes
        self.assertEqual(v.highestOffset, 0.0)
        self.assertEqual(v.highestTime, 0.0)

        self.assertEqual(len(v.notes), 2)
        self.assertTrue(v.hasElementOfClass('Note'))
        v.pop(1)  # remove the last item

        self.assertEqual(v.highestOffset, 0.0)
        self.assertEqual(v.highestTime, 0.0)
        self.assertEqual(len(v.notes), 1)


    def testVariantGroupA(self):
        '''
        Variant groups are used to distinguish
        '''
        v1 = Variant()
        v1.groups.append('alt-a')

        v1 = Variant()
        v1.groups.append('alt-b')
        self.assertIn('alt-b', v1.groups)


    def testVariantClassA(self):
        m1 = stream.Measure()
        v1 = Variant()
        v1.append(m1)

        self.assertIn('Variant', v1.classes)

        self.assertFalse(v1.hasElementOfClass(Variant))
        self.assertTrue(v1.hasElementOfClass(stream.Measure))

    def testDeepCopyVariantA(self):
        from music21 import variant

        s = stream.Stream()
        s.repeatAppend(note.Note('G4'), 8)
        vn1 = note.Note('F#4')
        vn2 = note.Note('A-4')

        v1 = variant.Variant()
        v1.insert(0, vn1)
        v1.insert(0, vn2)
        v1Copy = copy.deepcopy(v1)
        # copies stored objects; they point to the different Notes vn1/vn2
        self.assertIsNot(v1Copy[0], v1[0])
        self.assertIsNot(v1Copy[1], v1[1])
        self.assertIs(v1[0], vn1)
        self.assertIsNot(v1Copy[0], vn1)

        # normal in-place variant functionality
        s.insert(5, v1)
        self.assertEqual(self.pitchOut(s.pitches),
            '[G4, G4, G4, G4, G4, G4, G4, G4]')
        sv = s.activateVariants(inPlace=False)
        self.assertEqual(self.pitchOut(sv.pitches),
            '[G4, G4, G4, G4, G4, F#4, A-4, G4, G4]')

        # test functionality on a deepcopy
        sCopy = copy.deepcopy(s)
        self.assertEqual(len(sCopy.getElementsByClass(variant.Variant)), 1)
        self.assertEqual(self.pitchOut(sCopy.pitches),
            '[G4, G4, G4, G4, G4, G4, G4, G4]')
        sCopy.activateVariants(inPlace=True)
        self.assertEqual(self.pitchOut(sCopy.pitches),
            '[G4, G4, G4, G4, G4, F#4, A-4, G4, G4]')

    def testDeepCopyVariantB(self):
        from music21 import variant

        s = stream.Stream()
        s.repeatAppend(note.Note('G4'), 8)
        vn1 = note.Note('F#4')
        vn2 = note.Note('A-4')
        v1 = variant.Variant()
        v1.insert(0, vn1)
        v1.insert(0, vn2)
        s.insert(5, v1)

        # as we deepcopy the elements in the variants, we have new Notes
        sCopy = copy.deepcopy(s)
        sCopy.activateVariants(inPlace=True)
        self.assertEqual(self.pitchOut(sCopy.pitches),
            '[G4, G4, G4, G4, G4, F#4, A-4, G4, G4]')
        # can transpose the note in place
        sCopy.notes[5].transpose(12, inPlace=True)
        self.assertEqual(self.pitchOut(sCopy.pitches),
            '[G4, G4, G4, G4, G4, F#5, A-4, G4, G4]')

        # however, if the Variant deepcopy still references the original
        # notes it had, then when we try to activate the variant in the
        # in original Stream, we would get unexpected results (the octave shift)

        s.activateVariants(inPlace=True)
        self.assertEqual(self.pitchOut(s.pitches),
            '[G4, G4, G4, G4, G4, F#4, A-4, G4, G4]')


class TestExternal(unittest.TestCase):
    show = True

    def testMergeJacopoVariants(self):
        from music21 import corpus
        j1 = corpus.parse('trecento/PMFC_06-Jacopo-03a')
        j2 = corpus.parse('trecento/PMFC_06-Jacopo-03b')
        jMerged = mergeVariantScores(j1, j2)
        if self.show:
            jMerged.show('musicxml.png')


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
