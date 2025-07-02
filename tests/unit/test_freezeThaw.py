# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.freezeThaw import *


class Test(unittest.TestCase):

    def testSimpleFreezeThaw(self):
        from music21 import stream
        from music21 import note
        s = stream.Stream()
        sDummy = stream.Stream()
        n = note.Note()
        s.insert(2.0, n)
        sDummy.insert(3.0, n)

        sf = StreamFreezer(s)
        out = sf.writeStr()

        del s
        del sDummy
        del n

        st = StreamThawer()
        st.openStr(out)
        outStream = st.stream
        self.assertEqual(len(outStream), 1)
        self.assertEqual(outStream[0].offset, 2.0)

    def testFreezeThawWithSpanner(self):
        from music21 import stream
        from music21 import note
        s = stream.Stream()
        sDummy = stream.Stream()
        n = note.Note()
        sl1 = spanner.Slur([n])
        s.insert(0.0, sl1)
        s.insert(2.0, n)
        sDummy.insert(3.0, n)

        self.assertIs(s.spanners[0].getFirst(), s.notes[0])

        sf = StreamFreezer(s)
        out = sf.writeStr(fmt='jsonpickle')  # easier to read

        del s
        del sDummy
        del n

        st = StreamThawer()
        st.openStr(out)
        outStream = st.stream
        self.assertEqual(len(outStream), 2)
        self.assertEqual(outStream.notes[0].offset, 2.0)
        self.assertIs(outStream.spanners[0].getFirst(), outStream.notes[0])

    def testFreezeThawJsonPickleEnum(self):
        '''
        Versions of jsonpickle prior to  0.9.3 were having problems serializing Enums.

        Works now
        '''
        from music21 import corpus
        c = corpus.parse('luca/gloria').parts[2].measures(1, 2)
        sf2 = StreamFreezer(c)
        data2 = sf2.writeStr(fmt='jsonpickle')
        st2 = StreamThawer()
        st2.openStr(data2)

    def testFreezeThawCorpusFileWithSpanners(self):
        from music21 import corpus
        c = corpus.parse('luca/gloria')
        sf = StreamFreezer(c)
        data = sf.writeStr(fmt='pickle')

        st = StreamThawer()
        st.openStr(data)
        s = st.stream
        self.assertEqual(len(s.parts[0].measure(7).notes), 6)

    def x_testSimplePickle(self):
        from music21 import freezeThaw
        from music21 import corpus

        c = corpus.parse('bwv66.6').parts[0].measure(0).notes
        #  c.show('t')
        #
        # for el in c:
        #     storedIds.append(el.id)
        #     storedSitesIds.append(id(el.sites))
        #
        # return

        n1 = c[0]
        n2 = c[1]
        sf = freezeThaw.StreamFreezer(c, fastButUnsafe=True)
        sf.setupSerializationScaffold()
        for dummy in n1.sites.siteDict:
            pass
            # print(idKey)
            # print(n1.sites.siteDict[idKey]['obj'])
        for dummy in n2.sites.siteDict:
            pass
            # print(idKey)
            # print(n2.sites.siteDict[idKey]['obj'])

        dummy = pickle.dumps(c, protocol=-1)
        # data = sf.writeStr(fmt='pickle')
        # st = freezeThaw.StreamThawer()
        # st.openStr(data)
        # s = st.stream
        # for el in s._elements:
        #    idEl = el.id
        #    if idEl not in storedIds:
        #        print('Could not find ID %s for element %r at offset %f' %
        #              (idEl, el, el.offset))
        # print(storedIds)
        # s.show('t')

    def x_testFreezeThawPickle(self):
        from music21 import freezeThaw
        from music21 import corpus

        c = corpus.parse('luca/gloria')
        # c.show('t')

        sf = freezeThaw.StreamFreezer(c, fastButUnsafe=True)
        d = sf.writeStr()
        # print(d)

        st = freezeThaw.StreamThawer()
        st.openStr(d)
        s = st.stream

        # test to see if we can find everything
        for dummy in s.recurse():
            pass

    def testFreezeThawSimpleVariant(self):
        from music21 import freezeThaw
        from music21 import stream
        from music21 import note

        s = stream.Stream()
        m = stream.Measure()
        m.append(note.Note(type='whole'))
        s.append(m)

        s2 = stream.Stream()
        m2 = stream.Measure()
        n2 = note.Note('D#4')
        n2.duration.type = 'whole'
        m2.append(n2)
        s2.append(m2)
        v = variant.Variant(s2)

        s.insert(0, v)

        sf = freezeThaw.StreamFreezer(s)
        d = sf.writeStr()

        st = freezeThaw.StreamThawer()
        st.openStr(d)
        s = st.stream

    def testFreezeThawVariant(self):
        from music21 import freezeThaw
        from music21 import corpus
        from music21 import stream
        from music21 import note

        c = corpus.parse('luca/gloria')

        data2M2 = [('f', 'eighth'), ('c', 'quarter'), ('a', 'eighth'), ('a', 'quarter')]
        stream2 = stream.Stream()
        m = stream.Measure()
        for pitchName, durType in data2M2:
            n = note.Note(pitchName)
            n.duration.type = durType
            m.append(n)
        stream2.append(m)
        # c.show('t')
        variant.addVariant(c.parts[0], 6.0, stream2,
                           variantName='rhythmic_switch', replacementDuration=3.0)

        # test Variant is in stream
        unused_v1 = c.parts.first().getElementsByClass(variant.Variant).first()

        sf = freezeThaw.StreamFreezer(c, fastButUnsafe=True)
        # sf.v = v
        d = sf.writeStr()
        # print(d)

        # print('thawing.')

        st = freezeThaw.StreamThawer()
        st.openStr(d)
        s = st.stream
        # s.show('lily.pdf')
        p0 = s.parts[0]
        variants = p0.getElementsByClass(variant.Variant)
        v2 = variants[0]
        self.assertEqual(v2._stream[0][1].offset, 0.5)
        # v2.show('t')

    def testSerializationScaffoldA(self):
        from music21 import note
        from music21 import stream
        from music21 import freezeThaw

        n1 = note.Note()

        s1 = stream.Stream()
        s2 = stream.Stream()

        s1.append(n1)
        s2.append(n1)

        sf = freezeThaw.StreamFreezer(s2, fastButUnsafe=False)
        sf.setupSerializationScaffold()

        # test safety
        self.assertTrue(n1 in s2)
        self.assertTrue(n1 in s1)

    def testJSONPickleSpanner(self):
        from music21 import converter
        from music21 import note
        from music21 import stream
        n1 = note.Note('C')
        n2 = note.Note('D')
        s1 = stream.Stream()
        sp = spanner.Line([n1, n2])
        s1.insert(0, sp)
        s1.append(n1)
        s1.append(n2)
        frozen = converter.freezeStr(s1, 'jsonPickle')
        # print(frozen)
        unused_thawed = converter.thawStr(frozen)

    def testPickleMidi(self):
        from music21 import converter
        from music21 import note

        a = str(common.getSourceFilePath()
                         / 'midi'
                         / 'testPrimitive'
                         / 'test03.mid')

        # a = 'https://github.com/ELVIS-Project/vis/raw/master/test_corpus/prolationum-sanctus.midi'
        c = converter.parse(a)
        f = converter.freezeStr(c)
        d = converter.thawStr(f)
        self.assertIsInstance(
            d.parts[1].flatten().notes[20].volume.client,
            note.NotRest)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
