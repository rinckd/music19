# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.search.lyrics import *


class Test(unittest.TestCase):
    pass

    def testMultipleLyricsInNote(self):
        '''
        This score uses a non-breaking space as an elision
        '''
        from music21 import converter
        from music21 import search

        partXML = '''
        <score-partwise>
            <part-list>
                <score-part id="P1">
                <part-name>MusicXML Part</part-name>
                </score-part>
            </part-list>
            <part id="P1">
                <measure number="1">
                    <note>
                        <pitch>
                            <step>G</step>
                            <octave>4</octave>
                        </pitch>
                        <duration>1</duration>
                        <voice>1</voice>
                        <type>quarter</type>
                        <lyric number="1">
                            <syllabic>middle</syllabic>
                            <text>la</text>
                            <elision> </elision>
                            <syllabic>middle</syllabic>
                            <text>la</text>
                        </lyric>
                    </note>
                </measure>
            </part>
        </score-partwise>
        '''
        s = converter.parse(partXML, format='MusicXML')
        ly = s.flatten().notes[0].lyrics[0]

        def runSearch():
            ls = search.lyrics.LyricSearcher(s)
            # there is a non-breaking space between the two la's.
            self.assertEqual(ls.indexText, 'la la')

        runSearch()
        ly.components[0].syllabic = 'begin'
        ly.components[1].syllabic = 'end'
        runSearch()
        ly.components[0].syllabic = 'single'
        ly.components[1].syllabic = 'single'
        runSearch()

    def testMultipleVerses(self):
        from music21 import converter
        from music21 import search

        # noinspection SpellCheckingInspection
        partXML = '''
        <score-partwise>
            <part-list>
                <score-part id="P1">
                <part-name>MusicXML Part</part-name>
                </score-part>
            </part-list>
            <part id="P1">
                <measure number="1">
                    <note>
                        <pitch>
                            <step>G</step>
                            <octave>4</octave>
                        </pitch>
                        <duration>2</duration>
                        <voice>1</voice>
                        <type>half</type>
                        <lyric number="1">
                            <syllabic>single</syllabic>
                            <text>hi</text>
                        </lyric>
                        <lyric number="2">
                            <syllabic>single</syllabic>
                            <text>bye</text>
                        </lyric>
                    </note>
                </measure>
                <measure number="2">
                    <note>
                        <pitch>
                            <step>A</step>
                            <octave>4</octave>
                        </pitch>
                        <duration>1</duration>
                        <voice>1</voice>
                        <type>quarter</type>
                        <lyric number="1">
                            <syllabic>begin</syllabic>
                            <text>there!</text>
                        </lyric>
                        <lyric number="2">
                            <syllabic>begin</syllabic>
                            <text>Mi</text>
                        </lyric>
                    </note>
                    <note>
                        <pitch>
                            <step>B</step>
                            <octave>4</octave>
                        </pitch>
                        <duration>1</duration>
                        <voice>1</voice>
                        <type>quarter</type>
                        <lyric number="2">
                            <syllabic>end</syllabic>
                            <text>chael.</text>
                        </lyric>
                    </note>
                </measure>
            </part>
        </score-partwise>
        '''
        s = converter.parse(partXML, format='MusicXML')
        ls = search.lyrics.LyricSearcher(s)
        self.assertEqual(ls.indexText, 'hi there! // bye Michael.')
        tuples = ls.indexTuples
        self.assertEqual(len(tuples), 5)
        notes = list(s.flatten().notes)
        self.assertIs(tuples[0].lyric, notes[0].lyrics[0])
        self.assertIs(tuples[1].lyric, notes[1].lyrics[0])
        self.assertIs(tuples[2].lyric, notes[0].lyrics[1])
        self.assertIs(tuples[3].lyric, notes[1].lyrics[1])
        self.assertIs(tuples[4].lyric, notes[2].lyrics[0])

        match = ls.search('Michael')
        self.assertEqual(len(match), 1)
        m0 = match[0]
        self.assertEqual(m0.mStart, 2)
        self.assertEqual(m0.mEnd, 2)
        self.assertEqual(m0.els, (notes[1], notes[2]))
        self.assertEqual(m0.identifier, 2)
        self.assertEqual(len(m0.indices), 2)
        self.assertIs(m0.indices[0].lyric, notes[1].lyrics[1])
        self.assertIs(m0.indices[1].lyric, notes[2].lyrics[0])

        e_with_letter = re.compile(r'e[a-z]')
        match = ls.search(e_with_letter)
        self.assertEqual(len(match), 2)
        m0 = match[0]
        self.assertEqual(m0.mStart, 2)
        self.assertEqual(m0.mEnd, 2)
        self.assertEqual(m0.matchText, 'er')
        self.assertEqual(m0.identifier, 1)
        self.assertEqual(m0.els, (notes[1],))
        m1 = match[1]
        self.assertEqual(m1.mStart, 2)
        self.assertEqual(m1.mEnd, 2)
        self.assertEqual(m1.matchText, 'el')
        self.assertEqual(m1.identifier, 2)
        self.assertEqual(m1.els, (notes[2],))

        match = ls.search('i t')
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0].mStart, 1)
        self.assertEqual(match[0].mEnd, 2)
        self.assertEqual(match[0].identifier, 1)

    def testCustomSeparator(self):
        from music21 import converter
        from music21 import search
        import more_itertools

        partXML = '''<score-partwise version="4.0">
  <identification>
    <encoding>
      <software>MuseScore 4.5.2</software>
      <encoding-date>2025-06-22</encoding-date>
      <supports element="accidental" type="yes"/>
      <supports element="beam" type="yes"/>
      <supports element="print" attribute="new-page" type="no"/>
      <supports element="print" attribute="new-system" type="no"/>
      <supports element="stem" type="yes"/>
      </encoding>
    </identification>
  <part-list>
    <score-part id="P1">
      <part-name>钢琴, Track1</part-name>
      <part-abbreviation>Pno.</part-abbreviation>
      <score-instrument id="P1-I1">
        <instrument-name>钢琴</instrument-name>
        <instrument-sound>keyboard.piano</instrument-sound>
        </score-instrument>
      <midi-device id="P1-I1" port="1"></midi-device>
      <midi-instrument id="P1-I1">
        <midi-channel>1</midi-channel>
        <midi-program>1</midi-program>
        <volume>78.7402</volume>
        <pan>0</pan>
        </midi-instrument>
      </score-part>
    </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>2</divisions>
        <key>
          <fifths>0</fifths>
          </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
          </time>
        <clef>
          <sign>F</sign>
          <line>4</line>
          </clef>
        </attributes>
      <note dynamics="50">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>长</text>
          </lyric>
        </note>
      <note dynamics="50">
        <pitch>
          <step>E</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" number="1"/>
          </notations>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>亭</text>
          </lyric>
        </note>
      <note dynamics="50">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note dynamics="50">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>外</text>
          </lyric>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="2">
      <note dynamics="50">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>古</text>
          </lyric>
        </note>
      <note dynamics="50">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>道</text>
          </lyric>
        </note>
      <note dynamics="50">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <lyric number="1">
          <syllabic>single</syllabic>
          <text>边</text>
          </lyric>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <barline location="right">
        <bar-style>light-heavy</bar-style>
        </barline>
      </measure>
    </part>
  </score-partwise>'''
        s = converter.parse(partXML, format='MusicXML')
        for lenWordSep in range(5):
            wordSep = ' ' * lenWordSep
            ls = search.lyrics.LyricSearcher(s, wordSeparator=wordSep)
            for pair in more_itertools.pairwise('长亭外古道边'):
                keyword = pair[0] + wordSep + pair[1]
                match = ls.search(keyword)
                self.assertEqual(len(match), 1)
                self.assertEqual(len(match[0].els), 2)
                self.assertEqual(match[0].els[0].lyric, pair[0])
                self.assertEqual(match[0].els[1].lyric, pair[1])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
