# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.features.base import *


class Test(unittest.TestCase):

    def testStreamFormsA(self):
        from music21 import features
        self.maxDiff = None

        s = corpus.parse('corelli/opus3no1/1grave')
        # s.chordify().show()
        di = features.DataInstance(s)
        self.assertEqual(len(di['flat']), 292)
        self.assertEqual(len(di['flat.notes']), 238)

        # di['chordify'].show('t')
        self.assertEqual(len(di['chordify']), 27)
        chordifiedChords = di['chordify.flat.getElementsByClass(Chord)']
        self.assertEqual(len(chordifiedChords), 145)
        histo = di['chordify.flat.getElementsByClass(Chord).setClassHistogram']
        # print(histo)

        self.assertEqual(histo,
                         {'3-11': 30, '2-4': 26, '1-1': 25, '2-3': 16, '3-9': 12, '2-2': 6,
                          '3-7': 6, '2-5': 6, '3-4': 5, '3-6': 5, '3-10': 4,
                          '3-8': 2, '3-2': 2})

        self.assertEqual(di['chordify.flat.getElementsByClass(Chord).typesHistogram'],
                           {'isMinorTriad': 6, 'isAugmentedTriad': 0,
                            'isTriad': 34, 'isSeventh': 0, 'isDiminishedTriad': 4,
                            'isDiminishedSeventh': 0, 'isIncompleteMajorTriad': 26,
                            'isHalfDiminishedSeventh': 0, 'isMajorTriad': 24,
                            'isDominantSeventh': 0, 'isIncompleteMinorTriad': 16})

        self.assertEqual(di['flat.notes.quarterLengthHistogram'],
                         {0.5: 116, 1.0: 39, 1.5: 27, 2.0: 31, 3.0: 2, 4.0: 3,
                          0.75: 4, 0.25: 16})

        # can access parts by index
        self.assertEqual(len(di['parts']), 3)
        # stored in parts are StreamForms instances, caching their results
        self.assertEqual(len(di['parts'][0]['flat.notes']), 71)
        self.assertEqual(len(di['parts'][1]['flat.notes']), 66)

        # getting a measure by part
        self.assertEqual(len(di['parts'][0]['getElementsByClass(Measure)']), 19)
        self.assertEqual(len(di['parts'][1]['getElementsByClass(Measure)']), 19)

        self.assertEqual(di['parts'][0]['pitches.pitchClassHistogram'],
                         [9, 1, 11, 0, 9, 13, 0, 11, 0, 12, 5, 0])
        # the sum of the two arrays is the pitch class histogram of the complete
        # work
        self.assertEqual(di['pitches.pitchClassHistogram'],
                         [47, 2, 25, 0, 25, 42, 0, 33, 0, 38, 22, 4])

    def testStreamFormsB(self):
        from music21 import features

        s = stream.Stream()
        for p in ['c4', 'c4', 'd-4', 'd#4', 'f#4', 'a#4', 'd#5', 'a5', 'a5']:
            s.append(note.Note(p))
        di = features.DataInstance(s)
        self.assertEqual(di['pitches.midiIntervalHistogram'],
                         [2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def testStreamFormsC(self):
        from pprint import pformat
        from music21 import features

        s = stream.Stream()
        for p in ['c4', 'c4', 'd-4', 'd#4', 'f#4', 'a#4', 'd#5', 'a5']:
            s.append(note.Note(p))
        di = features.DataInstance(s)

        self.assertEqual(pformat(di['flat.secondsMap']), '''[{'durationSeconds': 0.5,
  'element': <music21.note.Note C>,
  'endTimeSeconds': 0.5,
  'offsetSeconds': 0.0,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note C>,
  'endTimeSeconds': 1.0,
  'offsetSeconds': 0.5,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note D->,
  'endTimeSeconds': 1.5,
  'offsetSeconds': 1.0,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note D#>,
  'endTimeSeconds': 2.0,
  'offsetSeconds': 1.5,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note F#>,
  'endTimeSeconds': 2.5,
  'offsetSeconds': 2.0,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note A#>,
  'endTimeSeconds': 3.0,
  'offsetSeconds': 2.5,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note D#>,
  'endTimeSeconds': 3.5,
  'offsetSeconds': 3.0,
  'voiceIndex': None},
 {'durationSeconds': 0.5,
  'element': <music21.note.Note A>,
  'endTimeSeconds': 4.0,
  'offsetSeconds': 3.5,
  'voiceIndex': None}]''', pformat(di['secondsMap']))

    def testDataSetOutput(self):
        from music21 import features
        from music21.features import outputFormats
        # test just a few features
        featureExtractors = features.extractorsById(['ql1', 'ql2', 'ql4'], 'native')

        # need to define what the class label will be
        ds = features.DataSet(classLabel='Composer')
        ds.runParallel = False
        ds.addFeatureExtractors(featureExtractors)

        # add works, defining the class value
        ds.addData('bwv66.6', classValue='Bach')
        ds.addData('corelli/opus3no1/1grave', classValue='Corelli')

        ds.process()

        # manually create an output format and get output
        of = outputFormats.OutputCSV(ds)
        post = of.getString(lineBreak='//')
        self.assertEqual(
            post,
            'Identifier,Unique_Note_Quarter_Lengths,'
            'Most_Common_Note_Quarter_Length,Range_of_Note_Quarter_Lengths,'
            'Composer//bwv66.6,3,1.0,1.5,Bach//corelli/opus3no1/1grave,8,0.5,3.75,Corelli')

        # without id
        post = of.getString(lineBreak='//', includeId=False)
        self.assertEqual(
            post,
            'Unique_Note_Quarter_Lengths,Most_Common_Note_Quarter_Length,'
            'Range_of_Note_Quarter_Lengths,Composer//3,1.0,1.5,Bach//8,0.5,3.75,Corelli')

        fp1 = ds.write(format='tab')
        fp2 = ds.write(format='csv')
        # Also test providing fp
        fp3 = environLocal.getTempFile(suffix='.arff')
        ds.write(fp=fp3, format='arff')

        for fp in (fp1, fp2, fp3):
            os.remove(fp)

    def testFeatureFail(self):
        from music21 import features
        from music21 import base

        featureExtractors = ['p10', 'p11', 'p12', 'p13']

        featureExtractors = features.extractorsById(featureExtractors,
                                                    'jSymbolic')

        ds = features.DataSet(classLabel='Composer')
        ds.addFeatureExtractors(featureExtractors)

        # create problematic streams
        s = stream.Stream()
        # s.append(None)  # will create a wrapper -- NOT ANYMORE
        s.append(base.ElementWrapper(None))
        ds.addData(s, classValue='Monteverdi')
        ds.addData(s, classValue='Handel')

        # process with all feature extractors, store all features
        ds.failFast = True
        # Tests that some exception is raised, not necessarily that only one is
        with self.assertRaises(features.FeatureException):
            ds.process()

    def x_testComposerClassificationJSymbolic(self):  # pragma: no cover
        '''
        Demonstrating writing out data files for feature extraction. Here,
        features are used from the jSymbolic library.
        '''
        from music21 import features

        featureExtractors = ['r31', 'r32', 'r33', 'r34', 'r35', 'p1', 'p2', 'p3',
                             'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12',
                             'p13', 'p14', 'p15', 'p16', 'p19', 'p20', 'p21']

        # will return a list
        featureExtractors = features.extractorsById(featureExtractors,
                                                    'jSymbolic')

        # worksBach = corpus.getBachChorales()[100:143]  # a middle range
        worksMonteverdi = corpus.search('monteverdi').search('.xml')[:43]

        worksBach = corpus.search('bach').search(numberOfParts=4)[:5]

        # need to define what the class label will be
        ds = features.DataSet(classLabel='Composer')
        ds.addFeatureExtractors(featureExtractors)

        # add works, defining the class value
        # for w in worksBach:
        #     ds.addData(w, classValue='Bach')
        for w in worksMonteverdi:
            ds.addData(w, classValue='Monteverdi')
        for w in worksBach:
            ds.addData(w, classValue='Bach')

        # process with all feature extractors, store all features
        ds.process()
        ds.write(format='tab')
        ds.write(format='csv')
        ds.write(format='arff')

    def x_testRegionClassificationJSymbolicA(self):  # pragma: no cover
        '''
        Demonstrating writing out data files for feature extraction. Here,
        features are used from the jSymbolic library.
        '''
        from music21 import features

        featureExtractors = features.extractorsById(['r31', 'r32', 'r33', 'r34', 'r35',
                                                     'p1', 'p2', 'p3', 'p4', 'p5', 'p6',
                                                     'p7', 'p8', 'p9', 'p10', 'p11', 'p12',
                                                     'p13', 'p14', 'p15', 'p16', 'p19',
                                                     'p20', 'p21'], 'jSymbolic')

        oChina1 = corpus.parse('essenFolksong/han1')
        oChina2 = corpus.parse('essenFolksong/han2')

        oMitteleuropa1 = corpus.parse('essenFolksong/boehme10')
        oMitteleuropa2 = corpus.parse('essenFolksong/boehme20')

        ds = features.DataSet(classLabel='Region')
        ds.addFeatureExtractors(featureExtractors)

        # add works, defining the class value
        for o, name in [(oChina1, 'han1'),
                        (oChina2, 'han2')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='China', id=songId)

        for o, name in [(oMitteleuropa1, 'boehme10'),
                        (oMitteleuropa2, 'boehme20')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='Mitteleuropa', id=songId)

        # process with all feature extractors, store all features
        ds.process()
        ds.getString(outputFmt='tab')
        ds.getString(outputFmt='csv')
        ds.getString(outputFmt='arff')

    def x_testRegionClassificationJSymbolicB(self):  # pragma: no cover
        '''
        Demonstrating writing out data files for feature extraction.
        Here, features are used from the jSymbolic library.
        '''
        from music21 import features

        # features common to both collections
        featureExtractors = features.extractorsById(
            ['r31', 'r32', 'r33', 'r34', 'r35', 'p1', 'p2', 'p3', 'p4',
                             'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13',
                             'p14', 'p15', 'p16', 'p19', 'p20', 'p21'], 'jSymbolic')

        # first bundle
        ds = features.DataSet(classLabel='Region')
        ds.addFeatureExtractors(featureExtractors)

        oChina1 = corpus.parse('essenFolksong/han1')
        oMitteleuropa1 = corpus.parse('essenFolksong/boehme10')

        # add works, defining the class value
        for o, name in [(oChina1, 'han1')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='China', id=songId)

        for o, name in [(oMitteleuropa1, 'boehme10')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='Mitteleuropa', id=songId)

        # process with all feature extractors, store all features
        ds.process()
        ds.write('/_scratch/chinaMitteleuropaSplit-a.tab')
        ds.write('/_scratch/chinaMitteleuropaSplit-a.csv')
        ds.write('/_scratch/chinaMitteleuropaSplit-a.arff')

        # create second data set from alternate collections
        ds = features.DataSet(classLabel='Region')
        ds.addFeatureExtractors(featureExtractors)

        oChina2 = corpus.parse('essenFolksong/han2')
        oMitteleuropa2 = corpus.parse('essenFolksong/boehme20')
        # add works, defining the class value
        for o, name in [(oChina2, 'han2')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='China', id=songId)

        for o, name in [(oMitteleuropa2, 'boehme20')]:
            for w in o.scores:
                songId = f'essenFolksong/{name}-{w.metadata.number}'
                ds.addData(w, classValue='Mitteleuropa', id=songId)

        # process with all feature extractors, store all features
        ds.process()
        ds.write('/_scratch/chinaMitteleuropaSplit-b.tab')
        ds.write('/_scratch/chinaMitteleuropaSplit-b.csv')
        ds.write('/_scratch/chinaMitteleuropaSplit-b.arff')

    # all these are written using orange-Py2 code; need better.

    # def xtestOrangeBayesA(self):  # pragma: no cover
    #     '''
    #     Using an already created test file with a BayesLearner.
    #     '''
    #     import orange  # pylint: disable=import-error
    #     data = orange.ExampleTable(
    #         '~/music21Ext/mlDataSets/bachMonteverdi-a/bachMonteverdi-a.tab')
    #     classifier = orange.BayesLearner(data)
    #     for i in range(len(data)):
    #         c = classifier(data[i])
    #         print('original', data[i].getclass(), 'BayesLearner:', c)


    # def xtestClassifiersA(self):  # pragma: no cover
    #     '''
    #     Using an already created test file with a BayesLearner.
    #     '''
    #     import orange, orngTree  # pylint: disable=import-error
    #     data1 = orange.ExampleTable(
    #             '~/music21Ext/mlDataSets/chinaMitteleuropa-b/chinaMitteleuropa-b1.tab')
    #
    #     data2 = orange.ExampleTable(
    #             '~/music21Ext/mlDataSets/chinaMitteleuropa-b/chinaMitteleuropa-b2.tab')
    #
    #     majority = orange.MajorityLearner
    #     bayes = orange.BayesLearner
    #     tree = orngTree.TreeLearner
    #     knn = orange.kNNLearner
    #
    #     for classifierType in [majority, bayes, tree, knn]:
    #         print('')
    #         for classifierData, classifierStr, matchData, matchStr in [
    #             (data1, 'data1', data1, 'data1'),
    #             (data1, 'data1', data2, 'data2'),
    #             (data2, 'data2', data2, 'data2'),
    #             (data2, 'data2', data1, 'data1'),
    #             ]:
    #
    #             # train with data1
    #             classifier = classifierType(classifierData)
    #             mismatch = 0
    #             for i in range(len(matchData)):
    #                 c = classifier(matchData[i])
    #                 if c != matchData[i].getclass():
    #                     mismatch += 1
    #
    #             print('%s %s: misclassified %s/%s of %s' % (
    #                     classifierStr, classifierType, mismatch, len(matchData), matchStr))
    #
    #         # if classifierType == orngTree.TreeLearner:
    #         #     orngTree.printTxt(classifier)



    # def xtestClassifiersB(self):  # pragma: no cover
    #     '''
    #     Using an already created test file with a BayesLearner.
    #     '''
    #     import orange, orngTree  # pylint: disable=import-error
    #     data1 = orange.ExampleTable(
    #             '~/music21Ext/mlDataSets/chinaMitteleuropa-b/chinaMitteleuropa-b1.tab')
    #
    #     data2 = orange.ExampleTable(
    #             '~/music21Ext/mlDataSets/chinaMitteleuropa-b/chinaMitteleuropa-b2.tab',
    #             use=data1.domain)
    #
    #     data1.extend(data2)
    #     data = data1
    #
    #     majority = orange.MajorityLearner
    #     bayes = orange.BayesLearner
    #     tree = orngTree.TreeLearner
    #     knn = orange.kNNLearner
    #
    #     folds = 10
    #     for classifierType in [majority, bayes, tree, knn]:
    #         print('')
    #
    #         cvIndices = orange.MakeRandomIndicesCV(data, folds)
    #         for fold in range(folds):
    #             train = data.select(cvIndices, fold, negate=1)
    #             test = data.select(cvIndices, fold)
    #
    #             for classifierData, classifierStr, matchData, matchStr in [
    #                 (train, 'train', test, 'test'),
    #                 ]:
    #
    #                 # train with data1
    #                 classifier = classifierType(classifierData)
    #                 mismatch = 0
    #                 for i in range(len(matchData)):
    #                     c = classifier(matchData[i])
    #                     if c != matchData[i].getclass():
    #                         mismatch += 1
    #
    #                 print('%s %s: misclassified %s/%s of %s' % (
    #                         classifierStr, classifierType, mismatch, len(matchData), matchStr))


    # def xtestOrangeClassifiers(self):  # pragma: no cover
    #     '''
    #     This test shows how to compare four classifiers; replace the file path
    #     with a path to the .tab data file.
    #     '''
    #     import orange, orngTree  # pylint: disable=import-error
    #     data = orange.ExampleTable(
    #         '~/music21Ext/mlDataSets/bachMonteverdi-a/bachMonteverdi-a.tab')
    #
    #     # setting up the classifiers
    #     majority = orange.MajorityLearner(data)
    #     bayes = orange.BayesLearner(data)
    #     tree = orngTree.TreeLearner(data, sameMajorityPruning=1, mForPruning=2)
    #     knn = orange.kNNLearner(data, k=21)
    #
    #     majority.name='Majority'
    #     bayes.name='Naive Bayes'
    #     tree.name='Tree'
    #     knn.name='kNN'
    #     classifiers = [majority, bayes, tree, knn]
    #
    #     # print the head
    #     print('Possible classes:', data.domain.classVar.values)
    #     print('Original Class', end=' ')
    #     for l in classifiers:
    #         print('%-13s' % (l.name), end=' ')
    #     print()
    #
    #     for example in data:
    #         print('(%-10s)  ' % (example.getclass()), end=' ')
    #         for c in classifiers:
    #             p = c([example, orange.GetProbabilities])
    #             print('%5.3f        ' % (p[0]), end=' ')
    #         print('')


    # def xtestOrangeClassifierTreeLearner(self):  # pragma: no cover
    #     import orange, orngTree  # pylint: disable=import-error
    #     data = orange.ExampleTable(
    #         '~/music21Ext/mlDataSets/bachMonteverdi-a/bachMonteverdi-a.tab')
    #
    #     tree = orngTree.TreeLearner(data, sameMajorityPruning=1, mForPruning=2)
    #     # tree = orngTree.TreeLearner(data)
    #     for i in range(len(data)):
    #         p = tree(data[i], orange.GetProbabilities)
    #         print('%s: %5.3f (originally %s)' % (i + 1, p[1], data[i].getclass()))
    #
    #     orngTree.printTxt(tree)

    def testParallelRun(self):
        from music21 import features
        # test just a few features
        featureExtractors = features.extractorsById(['ql1', 'ql2', 'ql4'], 'native')

        # need to define what the class label will be
        ds = features.DataSet(classLabel='Composer')
        ds.addFeatureExtractors(featureExtractors)

        # add works, defining the class value
        ds.addData('bwv66.6', classValue='Bach')
        ds.addData('corelli/opus3no1/1grave', classValue='Corelli')
        ds.runParallel = True
        ds.quiet = True
        ds.process()
        self.assertEqual(len(ds.features), 2)
        self.assertEqual(len(ds.features[0]), 3)
        fe00 = ds.features[0][0]
        self.assertEqual(fe00.vector, [3])

    # # pylint: disable=redefined-outer-name
    # def x_fix_parallel_first_testMultipleSearches(self):
    #     from music21.features import outputFormats
    #     from music21 import features
    #
    #     # Need explicit import for pickling within the testSingleCoreAll context
    #     from music21.features.base import _pickleFunctionNumPitches
    #     import textwrap
    #
    #     self.maxDiff = None
    #
    #     fewBach = corpus.search('bach/bwv6')
    #
    #     self.assertEqual(len(fewBach), 13)
    #     ds = features.DataSet(classLabel='NumPitches')
    #     ds.addMultipleData(fewBach, classValues=_pickleFunctionNumPitches)
    #     featureExtractors = features.extractorsById(['ql1', 'ql4'], 'native')
    #     ds.addFeatureExtractors(featureExtractors)
    #     ds.runParallel = True
    #     ds.process()
    #     # manually create an output format and get output
    #     of = outputFormats.OutputCSV(ds)
    #     post = of.getString(lineBreak='\n')
    #     self.assertEqual(post.strip(), textwrap.dedent('''
    #         Identifier,Unique_Note_Quarter_Lengths,Range_of_Note_Quarter_Lengths,NumPitches
    #         bach/bwv6.6.mxl,4,1.75,164
    #         bach/bwv60.5.mxl,6,2.75,282
    #         bach/bwv62.6.mxl,5,1.75,182
    #         bach/bwv64.2.mxl,4,1.5,179
    #         bach/bwv64.4.mxl,5,2.5,249
    #         bach/bwv64.8.mxl,5,3.5,188
    #         bach/bwv65.2.mxl,4,3.0,148
    #         bach/bwv65.7.mxl,7,2.75,253
    #         bach/bwv66.6.mxl,3,1.5,165
    #         bach/bwv67.4.xml,3,1.5,173
    #         bach/bwv67.7.mxl,4,2.5,132
    #         bach/bwv69.6-a.mxl,4,1.5,170
    #         bach/bwv69.6.xml,8,4.25,623
    #         ''').strip())


def _pickleFunctionNumPitches(bachStream):
    '''
    A function for documentation testing of a pickleable function
    '''
    return len(bachStream.pitches)


if __name__ == '__main__':
    import music21
    music21.mainTest(Test)
