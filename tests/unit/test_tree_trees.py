# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.tree.trees import *


class Test(unittest.TestCase):

    def testGetPositionAfterOffset(self):
        '''
        test that get position after works with
        an offset when the tree is built on SortTuples.
        '''
        from music21 import stream
        from music21 import note

        et = ElementTree()

        s = stream.Stream()
        for i in range(100):
            n = note.Note()
            n.duration.quarterLength = 2.0
            s.insert(i * 2, n)

        for n in s:
            et.insert(n)
        self.assertTrue(repr(et).startswith('<ElementTree {100} (0.0 <0.20'))

        n2 = s[-1]

        self.assertEqual(et.index(n2, n2.sortTuple()), 99)

        st3 = et.getPositionAfter(5.0)
        self.assertIsNotNone(st3)

#     def testBachDoctest(self):
#         from music21 import corpus, note, chord, tree
#         bach = corpus.parse('bwv66.6')
#         tree = tree.fromStream.asTimespans(bach, flatten=True,
#                                               classList=(note.Note, chord.Chord))
#         for verticalities in tree.iterateVerticalitiesNwise(n=3):
#             print(verticalities)
#             if verticalities[-1].offset == 25:
#                 pass
#             horizontalities = tree.unwrapVerticalities(verticalities)
#             for unused_part, horizontality in horizontalities.items():
#                 if horizontality.hasNeighborTone:
#                     merged = horizontality[0].new(endTime=horizontality[2].endTime,)
#                     # tree.remove(horizontality[0])
#                     # tree.remove(horizontality[1])
#                     # tree.remove(horizontality[2])
#                     # tree.insert(merged)
#
#
#         newBach = tree.toStream.partwise(tree, templateStream=bach,)
#         newBach.parts[1].measure(7).show('text')
# #     {0.0} <music21.chord.Chord F#4>
# #     {1.5} <music21.chord.Chord F#3>
# #     {2.0} <music21.chord.Chord C#4>
#

    def testElementsStoppingAt(self):
        '''
        this was reporting:

        <music21.note.Note G#>
        <music21.note.Note C#>
        <music21.note.Note A>
        <music21.note.Note A>

        G# was coming from an incorrect activeSite.  activeSite should not be used!
        '''
        from music21 import corpus
        from music21 import stream
        from music21 import note
        s = stream.Stream()
        n0 = note.Note('A')
        n0.duration.quarterLength = 3.0
        s.insert(0, n0)
        n1 = note.Note('B')
        n1.duration.quarterLength = 2.0
        s.insert(1, n1)
        n2 = note.Note('C')
        n2.duration.quarterLength = 1.0
        s.insert(2, n2)
        # and one later to be sure that order is right
        n3 = note.Note('A#')
        n3.duration.quarterLength = 2.5
        s.insert(0.5, n3)

        st = s.asTree(groupOffsets=True)
        stList = st.elementsStoppingAt(3.0)
        self.assertEqual(len(stList), 4)
        self.assertEqual([n.name for n in stList],
                         ['A', 'A#', 'B', 'C'])
        # making the tree more complex does not change anything, I hope?
        for i in range(30):
            s.insert(0, note.Rest())
        for i in range(22):
            s.insert(10 + i, note.Rest())
        st = s.asTree(groupOffsets=True)
        stList = st.elementsStoppingAt(3.0)
        self.assertEqual(len(stList), 4)
        self.assertEqual([n.name for n in stList],
                         ['A', 'A#', 'B', 'C'])

        # real world example
        score = corpus.parse('bwv66.6')
        scoreTree = score.asTree(flatten=True, groupOffsets=True)
        elementList = scoreTree.elementsStoppingAt(0.5)
        self.assertEqual(len(elementList), 3)
        self.assertEqual(elementList[0].name, 'C#')
        self.assertEqual(elementList[1].name, 'A')
        self.assertEqual(elementList[2].name, 'A')


#     def testBachDoctest(self):
#         from music21 import corpus, note, chord, tree
#         bach = corpus.parse('bwv66.6')
#         scoreTree = tree.fromStream.asTimespans(bach, flatten=True,
#                                               classList=(note.Note, chord.Chord))
#         print(scoreTree)
#         for verticalities in scoreTree.iterateVerticalitiesNwise(n=3):
#             if verticalities[-1].offset == 25:
#                 pass
#             horizontalities = scoreTree.unwrapVerticalities(verticalities)
#             for unused_part, horizontality in horizontalities.items():
#                 if horizontality.hasNeighborTone:
#                     merged = horizontality[0].new(endTime=horizontality[2].endTime,)
#                     scoreTree.remove(horizontality[0])
#                     scoreTree.remove(horizontality[1])
#                     scoreTree.remove(horizontality[2])
#                     scoreTree.insert(merged)
#
#
#         newBach = tree.toStream.partwise(scoreTree, templateStream=bach,)
#         newBach.show()
#         newBach.parts[1].measure(7).show('text')
# #     {0.0} <music21.chord.Chord F#4>
# #     {1.5} <music21.chord.Chord F#3>
# #     {2.0} <music21.chord.Chord C#4>


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
