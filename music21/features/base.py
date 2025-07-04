# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         features/base.py
# Purpose:      Feature extractors base classes.
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011-2023 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections import Counter
from collections.abc import KeysView
import os
import pathlib
import pickle
from music21 import common
from music21.common.types import StreamType
from music21 import converter
from music21 import corpus
from music21 import environment
from music21 import exceptions21
from music21 import note
from music21 import stream
from music21 import text

from music21.metadata.bundles import MetadataEntry

environLocal = environment.Environment('features.base')
# ------------------------------------------------------------------------------

class FeatureException(exceptions21.Music21Exception):
    pass

class Feature:
    '''
    An object representation of a feature, capable of presentation in a variety of formats,
    and returned from FeatureExtractor objects.

    Feature objects are simple. It is FeatureExtractors that store all metadata and processing
    routines for creating Feature objects.  Normally you wouldn't create one of these yourself.

    >>> myFeature = features.Feature()
    >>> myFeature.dimensions = 3
    >>> myFeature.name = 'Random arguments'
    >>> myFeature.isSequential = True

    This is a continuous Feature, so we will set discrete to false.

    >>> myFeature.discrete = False

    The .vector is the most important part of the feature, and it starts out as None.

    >>> myFeature.vector is None
    True

    Calling .prepareVector() gives it a list of Zeros of the length of dimensions.

    >>> myFeature.prepareVectors()

    >>> myFeature.vector
    [0, 0, 0]

    Now we can set the vector parts:

    >>> myFeature.vector[0] = 4
    >>> myFeature.vector[1] = 2
    >>> myFeature.vector[2] = 1

    It's okay just to assign a new list to .vector itself.

    There is a "normalize()" method which normalizes the values
    of a histogram to sum to 1.

    >>> myFeature.normalize()
    >>> myFeature.vector
    [0.571..., 0.285..., 0.142...]

    And that's it! FeatureExtractors are much more interesting.
    '''

    def __init__(self):
        # these values will be filled by the extractor
        self.dimensions = None  # number of dimensions
        # data storage; possibly use numpy array
        self.vector = None

        # consider not storing this values, as may not be necessary
        self.name = None  # string name representation
        self.description = None  # string description
        self.isSequential = None  # True or False
        self.discrete = None  # is discrete or continuous

    def _getVectors(self):
        '''
        Prepare a vector of appropriate size and return
        '''
        return [0] * self.dimensions

    def prepareVectors(self):
        '''
        Prepare the vector stored in this feature.
        '''
        self.vector = self._getVectors()

    def normalize(self):
        '''
        Normalizes the vector so that the sum of its elements is 1.
        '''
        s = sum(self.vector)
        try:
            scalar = 1.0 / s  # get floating point scalar for speed
        except ZeroDivisionError:
            raise FeatureException('cannot normalize zero vector')
        temp = self._getVectors()
        for i, v in enumerate(self.vector):
            temp[i] = v * scalar
        self.vector = temp

# ------------------------------------------------------------------------------
class FeatureExtractor:
    '''
    A model of process that extracts a feature from a Music21 Stream.
    The main public interface is the extract() method.

    The extractor can be passed a Stream or a reference to a DataInstance.
    All Streams are internally converted to a DataInstance if necessary.
    Usage of a DataInstance offers significant performance advantages, as common forms of
    the Stream are cached for easy processing.
    '''
    def __init__(self,
                 dataOrStream=None,
                 **keywords
                 ) -> None:
        self.stream = None  # the original Stream, or None
        self.data: DataInstance|None = None  # a DataInstance object: use to get data
        self.setData(dataOrStream)

        self.feature = None  # Feature object that results from processing

        if not hasattr(self, 'name'):
            self.name = None  # string name representation
        if not hasattr(self, 'description'):
            self.description = None  # string description
        if not hasattr(self, 'isSequential'):
            self.isSequential = None  # True or False
        if not hasattr(self, 'dimensions'):
            self.dimensions = None  # number of dimensions
        if not hasattr(self, 'discrete'):
            self.discrete = True  # default
        if not hasattr(self, 'normalize'):
            self.normalize = False  # default is no

    def setData(self, dataOrStream):
        '''
        Set the data that this FeatureExtractor will process.
        Either a Stream or a DataInstance object can be provided.
        '''
        if dataOrStream is not None:
            if (hasattr(dataOrStream, 'classes')
                    and isinstance(dataOrStream, stream.Stream)):
                # environLocal.printDebug(['creating new DataInstance: this should be a Stream:',
                #     dataOrStream])
                # if we are passed a stream, create a DataInstance to
                # manage its data; this is less efficient but is good for testing
                self.stream = dataOrStream
                self.data = DataInstance(self.stream)
            # if a DataInstance, do nothing
            else:
                self.stream = None
                self.data = dataOrStream

    def getAttributeLabels(self):
        '''
        Return a list of string in a form that is appropriate for data storage.

        >>> fe = features.jSymbolic.AmountOfArpeggiationFeature()
        >>> fe.getAttributeLabels()
        ['Amount_of_Arpeggiation']

        >>> fe = features.jSymbolic.FifthsPitchHistogramFeature()
        >>> fe.getAttributeLabels()
        ['Fifths_Pitch_Histogram_0', 'Fifths_Pitch_Histogram_1', 'Fifths_Pitch_Histogram_2',
         'Fifths_Pitch_Histogram_3', 'Fifths_Pitch_Histogram_4', 'Fifths_Pitch_Histogram_5',
         'Fifths_Pitch_Histogram_6', 'Fifths_Pitch_Histogram_7', 'Fifths_Pitch_Histogram_8',
         'Fifths_Pitch_Histogram_9', 'Fifths_Pitch_Histogram_10', 'Fifths_Pitch_Histogram_11']

        '''
        post = []
        if self.dimensions == 1:
            post.append(self.name.replace(' ', '_'))
        else:
            for i in range(self.dimensions):
                post.append(f"{self.name.replace(' ', '_')}_{i}")
        return post

    def fillFeatureAttributes(self, feature=None):
        # noinspection GrazieInspection
        '''
        Fill the attributes of a Feature with the descriptors in the FeatureExtractor.
        '''
        # operate on passed-in feature or self.feature
        if feature is None:
            feature = self.feature
        feature.name = self.name
        feature.description = self.description
        feature.isSequential = self.isSequential
        feature.dimensions = self.dimensions
        feature.discrete = self.discrete
        return feature

    def prepareFeature(self):
        '''
        Prepare a new Feature object for data acquisition.

        >>> s = stream.Stream()
        >>> fe = features.jSymbolic.InitialTimeSignatureFeature(s)
        >>> fe.prepareFeature()
        >>> fe.feature.name
        'Initial Time Signature'
        >>> fe.feature.dimensions
        2
        >>> fe.feature.vector
        [0, 0]
        '''
        self.feature = Feature()
        self.fillFeatureAttributes()  # will fill self.feature
        self.feature.prepareVectors()  # will vector with necessary zeros

    def process(self):
        '''
        Do processing necessary, storing result in _feature.
        '''
        # do work in subclass, calling on self.data
        pass

    def extract(self, source=None):
        '''
        Extract the feature and return the result.
        '''
        if source is not None:
            self.stream = source
        # preparing the feature always sets self.feature to a new instance
        self.prepareFeature()
        self.process()  # will set Feature object to _feature
        if self.normalize:
            self.feature.normalize()
        return self.feature

    def getBlankFeature(self):
        '''
        Return a properly configured plain feature as a placeholder

        >>> fe = features.jSymbolic.InitialTimeSignatureFeature()
        >>> fe.name
        'Initial Time Signature'

        >>> blankF = fe.getBlankFeature()
        >>> blankF.vector
        [0, 0]
        >>> blankF.name
        'Initial Time Signature'
        '''
        f = Feature()
        self.fillFeatureAttributes(f)
        f.prepareVectors()  # will vector with necessary zeros
        return f

# ------------------------------------------------------------------------------
class StreamForms:
    '''
    A dictionary-like wrapper of a Stream, providing
    numerous representations, generated on-demand, and cached.

    A single StreamForms object can be created for an
    entire Score, as well as one for each Part and/or Voice.

    A DataSet object manages one or more StreamForms
    objects, and exposes them to FeatureExtractors for usage.

    The streamObj is stored as self.stream and if "prepared" then
    the prepared form is stored as .prepared

    A dictionary `.forms` stores various intermediary representations
    of the stream which is the main power of this routine, making
    it simple to add additional feature extractors at low additional
    time cost.
    '''
    def __init__(self, streamObj: stream.Stream, prepareStream=True):
        self.stream = streamObj
        if self.stream is not None:
            if prepareStream:
                self.prepared = self._prepareStream(self.stream)
            else:
                self.prepared = self.stream
        else:
            self.prepared = None

        # basic data storage is a dictionary
        self.forms: dict[str, stream.Stream] = {}

    def keys(self) -> KeysView[str]:
        # will only return forms that are established
        return self.forms.keys()

    def _prepareStream(self, streamObj: StreamType) -> StreamType:
        '''
        Common routines done on Streams prior to processing. Returns a new Stream

        Currently: runs stripTies.
        '''
        # Let stripTies make a copy so that we don't leave side effects on the input stream
        streamObj = streamObj.stripTies(inPlace=False)
        return streamObj

    def __getitem__(self, key: str) -> stream.Stream:
        '''
        Get a form of this Stream, using a cached version if available.
        '''
        # first, check for cached version
        if key in self.forms:
            return self.forms[key]

        splitKeys = key.split('.')

        prepared = self.prepared
        for i in range(len(splitKeys)):
            subKey = '.'.join(splitKeys[:i + 1])
            if subKey in self.forms:
                continue
            if i > 0:
                previousKey = '.'.join(splitKeys[:i])
                # should always be there.
                prepared = self.forms[previousKey]

            lastKey = splitKeys[i]

            if lastKey in self.keysToMethods:
                prepared = self.keysToMethods[lastKey](self, prepared)
            elif lastKey.startswith('getElementsByClass('):
                classToGet: str = lastKey[len('getElementsByClass('):-1]
                prepared = prepared.getElementsByClass(classToGet).stream()
            else:
                raise AttributeError(f'no such attribute: {lastKey} in {key}')
            self.forms[subKey] = prepared

        return prepared

    def _getIntervalHistogram(self, algorithm='midi') -> list[int]:
        # note that this does not optimize and cache part presentations
        histo = [0] * 128
        # if we have parts, must add one at a time
        parts: list[stream.Stream]
        if isinstance(self.prepared, stream.Score):
            parts = list(self.prepared.parts)
        else:
            parts = [self.prepared]  # emulate a list
        for p in parts:
            # will be flat

            # noNone means that we will see all connections, even w/ a gap
            post = p.findConsecutiveNotes(skipRests=True,
                                          skipChords=True,
                                          skipGaps=True,
                                          noNone=True)

            for i, n in enumerate(post):
                if i < len(post) - 1:  # if not last
                    iNext = i + 1
                    nNext = post[iNext]
                    nValue = getattr(n.pitch, algorithm)
                    nextValue = getattr(nNext.pitch, algorithm)

                    try:
                        histo[abs(nValue - nextValue)] += 1
                    except AttributeError:
                        pass  # problem with not having midi
        return histo
# ----------------------------------------------------------------------------

    def formPartitionByInstrument(self, prepared: stream.Stream):
        from music21 import instrument
        return instrument.partitionByInstrument(prepared)

    def formSetClassHistogram(self, prepared):
        return Counter([c.forteClassTnI for c in prepared])

    def formPitchClassSetHistogram(self, prepared):
        return Counter([c.orderedPitchClassesString for c in prepared])

    def formTypesHistogram(self, prepared):
        histo = {}

        # keys are methods on Chord
        keys = ['isTriad', 'isSeventh', 'isMajorTriad', 'isMinorTriad',
                'isIncompleteMajorTriad', 'isIncompleteMinorTriad', 'isDiminishedTriad',
                'isAugmentedTriad', 'isDominantSeventh', 'isDiminishedSeventh',
                'isHalfDiminishedSeventh']

        for c in prepared:
            for thisKey in keys:
                if thisKey not in histo:
                    histo[thisKey] = 0
                # get the function attr, call it, check bool
                if getattr(c, thisKey)():
                    histo[thisKey] += 1
        return histo

    def formGetElementsByClassMeasure(self, prepared):
        if isinstance(prepared, stream.Score):
            post = stream.Stream()
            for p in prepared.parts:
                # insert in overlapping offset positions
                for m in p.getElementsByClass(stream.Measure):
                    post.insert(m.getOffsetBySite(p), m)
        else:
            post = prepared.getElementsByClass(stream.Measure)
        return post

    def formChordify(self, prepared):
        if isinstance(prepared, stream.Score):
            # options here permit getting part information out
            # of chordified representation
            return prepared.chordify(
                addPartIdAsGroup=True, removeRedundantPitches=False)
        else:  # for now, just return a normal Part or Stream
            # this seems wrong -- what if there are multiple voices
            # in the part?
            return prepared

    def formQuarterLengthHistogram(self, prepared):
        return Counter([float(n.quarterLength) for n in prepared])

    def formMidiPitchHistogram(self, pitches):
        return Counter([p.midi for p in pitches])

    def formPitchClassHistogram(self, pitches):
        cc = Counter([p.pitchClass for p in pitches])
        histo = [0] * 12
        for k in cc:
            histo[k] = cc[k]
        return histo

    def formMidiIntervalHistogram(self, unused):
        return self._getIntervalHistogram('midi')

    def formContourList(self, prepared):
        # list of all directed half steps
        cList = []
        # if we have parts, must add one at a time
        if prepared.hasPartLikeStreams():
            parts = prepared.parts
        else:
            parts = [prepared]  # emulate a list

        for p in parts:
            # this may be unnecessary, but we cannot access cached part data

            # noNone means that we will see all connections, even w/ a gap
            post = p.findConsecutiveNotes(skipRests=True,
                                          skipChords=False,
                                          skipGaps=True,
                                          noNone=True)
            for i, n in enumerate(post):
                if i < (len(post) - 1):  # if not last
                    iNext = i + 1
                    nNext = post[iNext]

                    if n.isChord:
                        ps = n.sortDiatonicAscending().pitches[-1].midi
                    else:  # normal note
                        ps = n.pitch.midi
                    if nNext.isChord:
                        psNext = nNext.sortDiatonicAscending().pitches[-1].midi
                    else:  # normal note
                        psNext = nNext.pitch.midi

                    cList.append(psNext - ps)
        # environLocal.printDebug(['contourList', cList])
        return cList

    def formSecondsMap(self, prepared):
        post = []
        secondsMap = prepared.secondsMap
        # filter only notes; all elements would otherwise be gathered
        for bundle in secondsMap:
            if isinstance(bundle['element'], note.NotRest):
                post.append(bundle)
        return post

    def formBeatHistogram(self, secondsMap):
        secondsList = [d['durationSeconds'] for d in secondsMap]
        bpmList = [round(60.0 / d) for d in secondsList]
        histogram = [0] * 200
        for thisBPM in bpmList:
            if thisBPM < 40 or thisBPM > 200:
                continue
            histogramIndex = int(thisBPM)
            histogram[histogramIndex] += 1
        return histogram

    keysToMethods = {
        'flat': lambda unused, p: p.flatten(),
        'pitches': lambda unused, p: p.pitches,
        'notes': lambda unused, p: p.notes,
        'getElementsByClass(Measure)': formGetElementsByClassMeasure,
        'metronomeMarkBoundaries': lambda unused, p: p.metronomeMarkBoundaries(),
        'chordify': formChordify,
        'partitionByInstrument': formPartitionByInstrument,
        'setClassHistogram': formSetClassHistogram,
        'pitchClassHistogram': formPitchClassHistogram,
        'typesHistogram': formTypesHistogram,
        'quarterLengthHistogram': formQuarterLengthHistogram,
        'pitchClassSetHistogram': formPitchClassSetHistogram,
        'midiPitchHistogram': formMidiPitchHistogram,
        'midiIntervalHistogram': formMidiIntervalHistogram,
        'contourList': formContourList,
        'analyzedKey': lambda unused, f: f.analyze(method='key'),
        'tonalCertainty': lambda unused, foundKey: foundKey.tonalCertainty(),
        'metadata': lambda unused, p: p.metadata,
        'secondsMap': formSecondsMap,
        'assembledLyrics': lambda unused, p: text.assembleLyrics(p),
        'beatHistogram': formBeatHistogram,
    }

# ------------------------------------------------------------------------------
class DataInstance:
    '''
    A data instance for analysis. This object prepares a Stream
    (by stripping ties, etc.) and stores
    multiple commonly-used stream representations once, providing rapid processing.
    '''
    # pylint: disable=redefined-builtin
    # noinspection PyShadowingBuiltins
    def __init__(self, streamOrPath=None, id=None):
        if isinstance(streamOrPath, stream.Stream):
            self.stream = streamOrPath
            self.streamPath = None
        else:
            self.stream = None
            self.streamPath = streamOrPath

        # store an id for the source stream: file path url, corpus url
        # or metadata title
        if id is not None:
            self._id = id
        elif (self.stream is not None
              and hasattr(self.stream, 'metadata')
              and self.stream.metadata is not None
              and self.stream.metadata.title is not None
              ):
            self._id = self.stream.metadata.title
        elif self.stream is not None and hasattr(self.stream, 'sourcePath'):
            self._id = self.stream.sourcePath
        elif self.streamPath is not None:
            if hasattr(self.streamPath, 'sourcePath'):
                self._id = str(self.streamPath.sourcePath)
            else:
                self._id = str(self.streamPath)
        else:
            self._id = ''

        # the attribute name in the data set for this label
        self.classLabel = None
        # store the class value for this data instance
        self._classValue = None

        self.partsCount = 0
        self.forms = None

        # store a list of voices, extracted from each part,
        self.formsByVoice = []
        # if parts exist, store a forms for each
        self.formsByPart = []

        self.featureExtractorClassesForParallelRunning = []

        if self.stream is not None:
            self.setupPostStreamParse()

    def setupPostStreamParse(self):
        '''
        Set up the StreamForms objects and other things that
        need to be done after a Stream is passed in but before
        feature extracting is run.

        Run automatically at instantiation if a Stream is passed in.
        '''
        # perform basic operations that are performed on all
        # streams

        # store a dictionary of StreamForms
        self.forms = StreamForms(self.stream)

        # if parts exist, store a forms for each
        self.formsByPart = []
        if hasattr(self.stream, 'parts'):
            self.partsCount = len(self.stream.parts)
            for p in self.stream.parts:
                # note that this will join ties and expand rests again
                self.formsByPart.append(StreamForms(p))
        else:
            self.partsCount = 0

        for v in self.stream[stream.Voice]:
            self.formsByPart.append(StreamForms(v))

    def setClassLabel(self, classLabel, classValue=None):
        '''
        Set the class label, as well as the class value if known.
        The class label is the attribute name used to define the class of this data instance.

        >>> #_DOCS_SHOW s = corpus.parse('bwv66.6')
        >>> s = stream.Stream() #_DOCS_HIDE
        >>> di = features.DataInstance(s)
        >>> di.setClassLabel('Composer', 'Bach')
        '''
        self.classLabel = classLabel
        self._classValue = classValue

    def getClassValue(self):
        if self._classValue is None or callable(self._classValue) and self.stream is None:
            return ''

        if callable(self._classValue) and self.stream is not None:
            self._classValue = self._classValue(self.stream)

        return self._classValue

    def getId(self):
        if self._id is None or callable(self._id) and self.stream is None:
            return ''

        if callable(self._id) and self.stream is not None:
            self._id = self._id(self.stream)

        # make sure there are no spaces
        try:
            return self._id.replace(' ', '_')
        except AttributeError as e:
            raise AttributeError(str(self._id)) from e

    def parseStream(self):
        '''
        If a path to a Stream has been passed in at creation,
        then this will parse it (whether it's a corpus string,
        a converter string (url or filepath), a pathlib.Path,
        or a metadata.bundles.MetadataEntry).
        '''
        if self.stream is not None:
            return

        if isinstance(self.streamPath, str):
            # could be corpus or file path
            if os.path.exists(self.streamPath) or self.streamPath.startswith('http'):
                s = converter.parse(self.streamPath)
            else:  # assume corpus
                s = corpus.parse(self.streamPath)
        elif isinstance(self.streamPath, pathlib.Path):
            # could be corpus or file path
            if self.streamPath.exists():
                s = converter.parse(self.streamPath)
            else:  # assume corpus
                s = corpus.parse(self.streamPath)
        elif isinstance(self.streamPath, MetadataEntry):
            s = self.streamPath.parse()
        else:
            raise ValueError(f'Invalid streamPath type: {type(self.streamPath)}')

        self.stream = s
        self.setupPostStreamParse()

    def __getitem__(self, key):
        '''
        Get a form of this Stream, using a cached version if available.

        >>> di = features.DataInstance('bach/bwv66.6')
        >>> len(di['flat'])
        197
        >>> len(di['flat.pitches'])
        163
        >>> len(di['flat.notes'])
        163
        >>> len(di['getElementsByClass(Measure)'])
        40
        >>> len(di['flat.getElementsByClass(TimeSignature)'])
        4
        '''
        self.parseStream()
        if key in ['parts']:
            # return a list of Forms for each part
            return self.formsByPart
        elif key in ['voices']:
            # return a list of Forms for voices
            return self.formsByVoice
        # try to create by calling the attribute
        # will raise an attribute error if there is a problem
        return self.forms[key]

# ------------------------------------------------------------------------------
class DataSetException(exceptions21.Music21Exception):
    pass

class DataSet:
    '''
    A set of features, as well as a collection of data to operate on.

    Comprises multiple DataInstance objects, a FeatureSet, and an OutputFormat.

    >>> ds = features.DataSet(classLabel='Composer')
    >>> f = [features.jSymbolic.PitchClassDistributionFeature,
    ...      features.jSymbolic.ChangesOfMeterFeature,
    ...      features.jSymbolic.InitialTimeSignatureFeature]
    >>> ds.addFeatureExtractors(f)
    >>> ds.addData('bwv66.6', classValue='Bach')
    >>> ds.addData('bach/bwv324.xml', classValue='Bach')
    >>> ds.process()
    >>> ds.getFeaturesAsList()[0]
    ['bwv66.6', 0.196..., 0.0736..., 0.006..., 0.098..., 0.0368..., 0.177..., 0.0,
     0.085..., 0.134..., 0.018..., 0.171..., 0.0, 0, 4, 4, 'Bach']
    >>> ds.getFeaturesAsList()[1]
    ['bach/bwv324.xml', 0.25, 0.0288..., 0.125, 0.0, 0.144..., 0.125, 0.0, 0.163..., 0.0, 0.134...,
    0.0288..., 0.0, 0, 4, 4, 'Bach']

    >>> ds = ds.getString()

    By default, all exceptions are caught and printed if debug mode is on.

    Set ds.failFast = True to not catch them.

    Set ds.quiet = False to print them regardless of debug mode.
    '''

    def __init__(self, classLabel=None, featureExtractors=()):
        # assume a two dimensional array
        self.dataInstances = []

        # order of feature extractors is the order used in the presentations
        self._featureExtractors = []
        self._instantiatedFeatureExtractors = []
        # the label of the class
        self._classLabel = classLabel
        # store a multidimensional storage of all features
        self.features = []

        self.failFast = False
        self.quiet = True

        self.runParallel = True
        # set extractors
        self.addFeatureExtractors(featureExtractors)

    def getClassLabel(self):
        return self._classLabel

    def addFeatureExtractors(self, values):
        '''
        Add one or more FeatureExtractor objects, either as a list or as an individual object.
        '''
        # features are instantiated here
        # however, they do not have a data assignment
        if not common.isIterable(values):
            values = [values]
        # need to create instances
        for sub in values:
            self._featureExtractors.append(sub)
            self._instantiatedFeatureExtractors.append(sub())

    def getAttributeLabels(self, includeClassLabel=True,
                           includeId=True):
        '''
        Return a list of all attribute labels. Optionally add a class
        label field and/or an id field.

        >>> f = [features.jSymbolic.PitchClassDistributionFeature,
        ...      features.jSymbolic.ChangesOfMeterFeature]
        >>> ds = features.DataSet(classLabel='Composer', featureExtractors=f)
        >>> ds.getAttributeLabels(includeId=False)
        ['Pitch_Class_Distribution_0',
         'Pitch_Class_Distribution_1',
         ...
         ...
         'Pitch_Class_Distribution_11',
         'Changes_of_Meter',
         'Composer']
        '''
        post = []
        # place ids first
        if includeId:
            post.append('Identifier')
        for fe in self._instantiatedFeatureExtractors:
            post += fe.getAttributeLabels()
        if self._classLabel is not None and includeClassLabel:
            post.append(self._classLabel.replace(' ', '_'))
        return post

    def getDiscreteLabels(self, includeClassLabel=True, includeId=True):
        '''
        Return column labels for discrete status.

        >>> f = [features.jSymbolic.PitchClassDistributionFeature,
        ...      features.jSymbolic.ChangesOfMeterFeature]
        >>> ds = features.DataSet(classLabel='Composer', featureExtractors=f)
        >>> ds.getDiscreteLabels()
        [None, False, False, False, False, False, False, False, False, False,
         False, False, False, True, True]
        '''
        post = []
        if includeId:
            post.append(None)  # just a spacer
        for fe in self._instantiatedFeatureExtractors:
            # need as many statements of discrete as there are dimensions
            post += [fe.discrete] * fe.dimensions
        # class label is assumed always discrete
        if self._classLabel is not None and includeClassLabel:
            post.append(True)
        return post

    def getClassPositionLabels(self, includeId=True):
        '''
        Return column labels for the presence of a class definition

        >>> f = [features.jSymbolic.PitchClassDistributionFeature,
        ...      features.jSymbolic.ChangesOfMeterFeature]
        >>> ds = features.DataSet(classLabel='Composer', featureExtractors=f)
        >>> ds.getClassPositionLabels()
        [None, False, False, False, False, False, False, False, False,
         False, False, False, False, False, True]
        '''
        post = []
        if includeId:
            post.append(None)  # just a spacer
        for fe in self._instantiatedFeatureExtractors:
            # need as many statements of discrete as there are dimensions
            post += [False] * fe.dimensions
        # class label is assumed always discrete
        if self._classLabel is not None:
            post.append(True)
        return post

    def addMultipleData(self, dataList, classValues, ids=None):
        '''
        add multiple data points at the same time.

        Requires an iterable (including MetadataBundle) for dataList holding
        types that can be passed to addData, and an equally sized list of dataValues
        and an equally sized list of ids (or None)

        classValues can also be a pickleable function that will be called on
        each instance after parsing, as can ids.
        '''
        if (not callable(classValues)
                and len(dataList) != len(classValues)):
            raise DataSetException(
                'If classValues is not a function, it must have the same length as dataList')
        if (ids is not None
                and not callable(ids)
                and len(dataList) != len(ids)):
            raise DataSetException(
                'If ids is not a function or None, it must have the same length as dataList')

        if callable(classValues):
            try:
                pickle.dumps(classValues)
            except pickle.PicklingError:
                raise DataSetException('classValues if a function must be pickleable. '
                                       + 'Lambda and some other functions are not.')

            classValues = [classValues] * len(dataList)

        if callable(ids):
            try:
                pickle.dumps(ids)
            except pickle.PicklingError:
                raise DataSetException('ids if a function must be pickleable. '
                                       + 'Lambda and some other functions are not.')

            ids = [ids] * len(dataList)
        elif ids is None:
            ids = [None] * len(dataList)

        for i in range(len(dataList)):
            d = dataList[i]
            cv = classValues[i]
            thisId = ids[i]
            self.addData(d, cv, thisId)

    # pylint: disable=redefined-builtin
    # noinspection PyShadowingBuiltins
    def addData(self, dataOrStreamOrPath, classValue=None, id=None):
        '''
        Add a Stream, DataInstance, MetadataEntry, or path (Posix or str)
        to a corpus or local file to this data set.

        The class value passed here is assumed to be the same as
        the classLabel assigned at startup.
        '''
        if self._classLabel is None:
            raise DataSetException(
                'cannot add data unless a class label for this DataSet has been set.')

        s = None
        if isinstance(dataOrStreamOrPath, DataInstance):
            di = dataOrStreamOrPath
            s = di.stream
            if s is None:
                s = di.streamPath
        else:
            # all else are stored directly
            s = dataOrStreamOrPath
            di = DataInstance(dataOrStreamOrPath, id=id)

        di.setClassLabel(self._classLabel, classValue)
        self.dataInstances.append(di)

    def process(self):
        '''
        Process all Data with all FeatureExtractors.
        Processed data is stored internally as numerous Feature objects.
        '''
        if self.runParallel:
            return self._processParallel()
        else:
            return self._processNonParallel()

    def _processParallel(self):
        '''
        Run a set of processes in parallel.
        '''
        for di in self.dataInstances:
            di.featureExtractorClassesForParallelRunning = self._featureExtractors

        shouldUpdate = not self.quiet

        # print('about to run parallel')
        outputData = common.runParallel([(di, self.failFast) for di in self.dataInstances],
                                           _dataSetParallelSubprocess,
                                           updateFunction=shouldUpdate,
                                           updateMultiply=1,
                                           unpackIterable=True
                                        )
        featureData, errors, classValues, ids = zip(*outputData)
        errors = common.flattenList(errors)
        for e in errors:
            if self.quiet is True:
                environLocal.printDebug(e)
            else:
                environLocal.warn(e)
        self.features = featureData

        for i, di in enumerate(self.dataInstances):
            if callable(di._classValue):
                di._classValue = classValues[i]
            if callable(di._id):
                di._id = ids[i]

    def _processNonParallel(self):
        '''
        The traditional way: run non-parallel
        '''
        # clear features
        self.features = []
        for data in self.dataInstances:
            row = []
            for fe in self._instantiatedFeatureExtractors:
                fe.setData(data)
                # in some cases there might be problem; to not fail
                try:
                    fReturned = fe.extract()
                except Exception as e:  # pylint: disable=broad-exception-caught
                    # for now take any error
                    fList = ['failed feature extractor:', fe, str(e)]
                    if self.quiet is True:
                        environLocal.printDebug(fList)
                    else:
                        environLocal.warn(fList)
                    if self.failFast is True:
                        raise e
                    # provide a blank feature extractor
                    fReturned = fe.getBlankFeature()

                row.append(fReturned)  # get feature and store
            # rows will align with data the order of DataInstances
            self.features.append(row)

    def getFeaturesAsList(self, includeClassLabel=True, includeId=True, concatenateLists=True):
        '''
        Get processed data as a list of lists, merging any sub-lists
        in multidimensional features.
        '''
        post = []
        for i, row in enumerate(self.features):
            v = []
            di = self.dataInstances[i]

            if includeId:
                v.append(di.getId())

            for f in row:
                if concatenateLists:
                    v += f.vector
                else:
                    v.append(f.vector)
            if includeClassLabel:
                v.append(di.getClassValue())
            post.append(v)
        if not includeClassLabel and not includeId:
            return post[0]
        else:
            return post

    def getUniqueClassValues(self):
        '''
        Return a list of unique class values.
        '''
        post = []
        for di in self.dataInstances:
            v = di.getClassValue()
            if v not in post:
                post.append(v)
        return post

    def _getOutputFormat(self, featureFormat):
        from music21.features import outputFormats
        if featureFormat.lower() in ['tab', 'orange', 'taborange', None]:
            outputFormat = outputFormats.OutputTabOrange(dataSet=self)
        elif featureFormat.lower() in ['csv', 'comma']:
            outputFormat = outputFormats.OutputCSV(dataSet=self)
        elif featureFormat.lower() in ['arff', 'attribute']:
            outputFormat = outputFormats.OutputARFF(dataSet=self)
        else:
            return None
        return outputFormat

    def _getOutputFormatFromFilePath(self, fp):
        '''
        Get an output format from a file path if possible, otherwise return None.

        >>> ds = features.DataSet()
        >>> ds._getOutputFormatFromFilePath('test.tab')
        <music21.features.outputFormats.OutputTabOrange object at ...>
        >>> ds._getOutputFormatFromFilePath('test.csv')
        <music21.features.outputFormats.OutputCSV object at ...>
        >>> ds._getOutputFormatFromFilePath('junk') is None
        True
        '''
        # get format from fp if possible
        of = None
        if '.' in fp:
            if self._getOutputFormat(fp.split('.')[-1]) is not None:
                of = self._getOutputFormat(fp.split('.')[-1])
        return of

    def getString(self, outputFmt='tab'):
        '''
        Get a string representation of the data set in a specific format.
        '''
        # pass reference to self to output
        outputFormat = self._getOutputFormat(outputFmt)
        return outputFormat.getString()

    # pylint: disable=redefined-builtin
    def write(self, fp=None, format=None, includeClassLabel=True):
        '''
        Set the output format object.
        '''
        if format is None and fp is not None:
            outputFormat = self._getOutputFormatFromFilePath(fp)
        else:
            outputFormat = self._getOutputFormat(format)
        if outputFormat is None:
            raise DataSetException('no output format could be defined from file path '
                                   + f'{fp} or format {format}')

        return outputFormat.write(fp=fp, includeClassLabel=includeClassLabel)

def _dataSetParallelSubprocess(dataInstance, failFast):
    row = []
    errors = []
    # howBigWeCopied = len(pickle.dumps(dataInstance))
    # print('Starting ', dataInstance, ' Size: ', howBigWeCopied)
    for feClass in dataInstance.featureExtractorClassesForParallelRunning:
        fe = feClass()
        fe.setData(dataInstance)
        # in some cases there might be problem; to not fail
        try:
            fReturned = fe.extract()
        except Exception as e:  # pylint: disable=broad-exception-caught
            # for now take any error
            errors.append('failed feature extractor:' + str(fe) + ': ' + str(e))
            if failFast:
                raise e
            # provide a blank feature extractor
            fReturned = fe.getBlankFeature()

        row.append(fReturned)  # get feature and store
    # rows will align with data the order of DataInstances
    return row, errors, dataInstance.getClassValue(), dataInstance.getId()

def allFeaturesAsList(streamInput):
    # noinspection PyShadowingNames
    '''
    returns a list containing ALL currently implemented feature extractors

    streamInput can be a Stream, DataInstance, or path to a corpus or local
    file to this data set.

    >>> s = converter.parse('tinynotation: 4/4 c4 d e2')
    >>> f = features.allFeaturesAsList(s)
    >>> f[2:5]
    [[2], [2], [1.0]]
    >>> len(f) > 85
    True
    '''
    from music21.features import jSymbolic, native
    ds = DataSet(classLabel='')
    f = list(jSymbolic.featureExtractors) + list(native.featureExtractors)
    ds.addFeatureExtractors(f)
    ds.addData(streamInput)
    ds.process()
    allData = ds.getFeaturesAsList(includeClassLabel=False,
                                   includeId=False,
                                   concatenateLists=False)

    return allData

# ------------------------------------------------------------------------------
def extractorsById(idOrList, library=('jSymbolic', 'native')):
    '''
    Given one or more :class:`~music21.features.FeatureExtractor` ids, return the
    appropriate  subclass. An optional `library` argument can be added to define which
    module is used. Current options are jSymbolic and native.

    >>> features.extractorsById('p20')
    [<class 'music21.features.jSymbolic.PitchClassDistributionFeature'>]

    >>> [x.id for x in features.extractorsById('p20')]
    ['P20']
    >>> [x.id for x in features.extractorsById(['p19', 'p20'])]
    ['P19', 'P20']

    Normalizes case:

    >>> [x.id for x in features.extractorsById(['r31', 'r32', 'r33', 'r34', 'r35', 'p1', 'p2'])]
    ['R31', 'R32', 'R33', 'R34', 'R35', 'P1', 'P2']

    Get all feature extractors from all libraries:

    >>> y = [x.id for x in features.extractorsById('all')]
    >>> y[0:3], y[-3:-1]
    (['M1', 'M2', 'M3'], ['CS12', 'MC1'])

    '''
    from music21.features import jSymbolic
    from music21.features import native

    if not common.isIterable(library):
        library = [library]

    featureExtractors = []
    for lib in library:
        if lib.lower() in ['jsymbolic', 'all']:
            featureExtractors += jSymbolic.featureExtractors
        elif lib.lower() in ['native', 'all']:
            featureExtractors += native.featureExtractors

    if not common.isIterable(idOrList):
        idOrList = [idOrList]

    flatIds = []
    for featureId in idOrList:
        featureId = featureId.strip().lower()
        featureId.replace('-', '')
        featureId.replace(' ', '')
        flatIds.append(featureId)

    post = []
    if not flatIds:
        return post

    for fe in featureExtractors:
        if fe.id.lower() in flatIds or flatIds[0].lower() == 'all':
            post.append(fe)
    return post

def extractorById(idOrList, library=('jSymbolic', 'native')):
    '''
    Get the first feature matched by extractorsById().

    >>> s = stream.Stream()
    >>> s.append(note.Note('A4'))
    >>> fe = features.extractorById('p20')(s)  # call class
    >>> fe.extract().vector
    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    '''
    ebi = extractorsById(idOrList=idOrList, library=library)
    if ebi:
        return ebi[0]
    return None  # no match

def vectorById(streamObj, vectorId, library=('jSymbolic', 'native')):
    '''
    Utility function to get a vector from an extractor

    >>> s = stream.Stream()
    >>> s.append(note.Note('A4'))
    >>> features.vectorById(s, 'p20')
    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    '''
    fe = extractorById(vectorId, library)(streamObj)  # call class with stream
    if fe is None:
        return None  # could raise exception
    return fe.extract().vector

def getIndex(featureString, extractorType=None):
    '''
    Returns the list index of the given feature extractor and the feature extractor
    category (jsymbolic or native). If feature extractor string is not in either
    jsymbolic or native feature extractors, returns None

    optionally include the extractorType ('jsymbolic' or 'native') if known
    and searching will be made more efficient

    >>> features.getIndex('Range')
    (61, 'jsymbolic')
    >>> features.getIndex('Ends With Landini Melodic Contour')
    (18, 'native')
    >>> features.getIndex('aBrandNewFeature!') is None
    True
    >>> features.getIndex('Fifths Pitch Histogram', 'jsymbolic')
    (70, 'jsymbolic')
    >>> features.getIndex('Tonal Certainty', 'native')
    (1, 'native')
    '''
    from music21.features import jSymbolic, native

    if extractorType is None or extractorType == 'jsymbolic':
        indexCount = 0
        for feature in jSymbolic.featureExtractors:

            if feature().name == featureString:
                return (indexCount, 'jsymbolic')
            indexCount += 1
    if extractorType is None or extractorType == 'native':
        indexCount = 0
        for feature in native.featureExtractors:
            if feature().name == featureString:
                return (indexCount, 'native')
            indexCount += 1

        return None

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER = [DataSet, Feature, FeatureExtractor]

# , runTest='testStreamFormsA')
