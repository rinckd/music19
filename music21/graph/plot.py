# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         graph/plots.py
# Purpose:      Classes for plotting music21 graphs based on Streams.
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#               Evan Lynch
#
# Copyright:    Copyright © 2009-2023 Michael Scott Asato Cuthbert,
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Object definitions for plotting :class:`~music21.stream.Stream` objects.

The :class:`~music21.graph.plot.PlotStream`
object subclasses combine a Graph object with the PlotStreamMixin to give
reusable approaches to graphing data and structures in
:class:`~music21.stream.Stream` objects.
'''
from __future__ import annotations

import collections
import numbers
import os
import pathlib
import typing as t

from music21.analysis import correlate
from music21.analysis import discrete
from music21.analysis import reduction
from music21.analysis import windowed
from music21 import base
from music21 import chord
from music21 import common
from music21 import corpus
from music21 import converter
from music21 import dynamics
from music21 import environment
from music21 import features
from music21 import note
from music21 import prebase
from music21 import stream  # circular, but okay, because not used at top level.

from music21.graph import axis
from music21.graph import primitives
from music21.graph.utilities import (GraphException, PlotStreamException)

environLocal = environment.Environment('graph.plot')

# Graph uses setattr, which PyLint can't infer from currently
# https://github.com/PyCQA/pylint/issues/2878
# pylint: disable=no-member

# ------------------------------------------------------------------------------
# graphing utilities that operate on streams

class PlotStreamMixin(prebase.ProtoM21Object):
    '''
    This Mixin adds Stream extracting and Axis holding features to any
    class derived from Graph.
    '''
    axesClasses: dict[str, type[axis.Axis]] = {'x': axis.Axis, 'y': axis.Axis}

    def __init__(self, streamObj=None, recurse=True, **keywords):
        # if not isinstance(streamObj, music21.stream.Stream):
        if streamObj is not None and not hasattr(streamObj, 'elements'):  # pragma: no cover
            raise PlotStreamException(f'non-stream provided as argument: {streamObj}')
        self.streamObj = streamObj
        self.recurse = recurse
        self.classFilterList = ['Note', 'Chord']
        self.matchPitchCountForChords = True

        self.data = None  # store native data representation, useful for testing

        for axisName, axisClass in self.axesClasses.items():
            if axisClass is not None:
                axisObj = axisClass(self, axisName)
                setattr(self, 'axis' + axisName.upper(), axisObj)

        self.savedKeywords = keywords

    def _reprInternal(self) -> str:
        # noinspection PyShadowingNames
        '''
        The representation of the Plot shows the stream repr
        in addition to the class name.

        >>> st = stream.Stream()
        >>> st.id = 'empty'
        >>> plot = graph.plot.ScatterPitchClassQuarterLength(st)
        >>> plot
        <music21.graph.plot.ScatterPitchClassQuarterLength for <music21.stream.Stream empty>>

        >>> plot = graph.plot.ScatterPitchClassQuarterLength(None)
        >>> plot
        <music21.graph.plot.ScatterPitchClassQuarterLength for (no stream)>

        >>> plot.axisX
        <music21.graph.axis.QuarterLengthAxis: x axis for ScatterPitchClassQuarterLength>

        >>> plot.axisY
        <music21.graph.axis.PitchClassAxis: y axis for ScatterPitchClassQuarterLength>

        >>> axIsolated = graph.axis.DynamicsAxis(axisName='z')
        >>> axIsolated
        <music21.graph.axis.DynamicsAxis: z axis for (no client)>
        '''
        s = self.streamObj
        if s is not None:  # not "if s" because could be empty
            streamName = repr(s)
        else:
            streamName = '(no stream)'

        return f'for {streamName}'

    @property
    def allAxes(self):
        '''
        return a list of axisX, axisY, axisZ if any are defined in the class.

        Some might be None.

        >>> s = stream.Stream()
        >>> p = graph.plot.ScatterPitchClassOffset(s)
        >>> p.allAxes
        [<music21.graph.axis.OffsetAxis: x axis for ScatterPitchClassOffset>,
         <music21.graph.axis.PitchClassAxis: y axis for ScatterPitchClassOffset>]
        '''
        allAxesList = []
        for axisName in ('axisX', 'axisY', 'axisZ'):
            if hasattr(self, axisName):
                allAxesList.append(getattr(self, axisName))
        return allAxesList

    def run(self, *, callProcess: bool = True, **keywords):
        '''
        main routine to extract data, set axis labels, run process() on the underlying
        Graph object, and if self.doneAction is not None, either write or show the graph.
        '''
        if t.TYPE_CHECKING:
            from music21.graph.primitives import Graph
            assert isinstance(self, Graph) and isinstance(self, PlotStreamMixin)

        self.setAxisKeywords()
        self.extractData()
        if hasattr(self, 'axisY') and self.axisY:
            self.setTicks('y', self.axisY.ticks())
            self.setAxisLabel('y', self.axisY.label)
        if hasattr(self, 'axisX') and self.axisX:
            self.setTicks('x', self.axisX.ticks())
            self.setAxisLabel('x', self.axisX.label)

        if callProcess:
            self.process()

    # --------------------------------------------------------------------------
    def setAxisKeywords(self):
        '''
        Configure axis parameters based on keywords given when creating the Plot.

        Looks in self.savedKeywords, in case any post creation manipulation needs
        to happen.

        Finds keywords that begin with x, y, z and sets the remainder of the
        keyword (lowercasing the first letter) as an attribute.  Does not
        set any new attributes, only existing ones.

        >>> b = corpus.parse('bwv66.6')
        >>> hist = graph.plot.HistogramPitchSpace(b, xHideUnused=False)
        >>> hist.axisX.hideUnused
        True
        >>> hist.setAxisKeywords()
        >>> hist.axisX.hideUnused
        False
        '''
        for thisAxis in self.allAxes:
            if thisAxis is None:
                continue
            thisAxisLetter = thisAxis.axisName
            for kw in self.savedKeywords:
                if not kw.startswith(thisAxisLetter):
                    continue
                if len(kw) < 3:
                    continue
                shortKw = kw[1].lower() + kw[2:]

                if not hasattr(thisAxis, shortKw):
                    continue
                setattr(thisAxis, shortKw, self.savedKeywords[kw])

    # --------------------------------------------------------------------------

    def extractData(self):
        if None in self.allAxes:
            raise PlotStreamException('Set all axes before calling extractData() via run()')

        if self.recurse:
            sIter = self.streamObj.recurse()
        else:
            sIter = self.streamObj.iter()

        if self.classFilterList:
            sIter = sIter.getElementsByClass(self.classFilterList)

        self.data = []

        for el in sIter:
            dataList = self.processOneElement(el)
            if dataList is not None:
                self.data.extend(dataList)

        self.postProcessData()

        for i, thisAxis in enumerate(self.allAxes):
            thisAxis.setBoundariesFromData([d[i] for d in self.data])

    def processOneElement(self, el: base.Music21Object):
        '''
        Get a list of data from a single element (generally a Note or chord):

        >>> n = note.Note('C#4')
        >>> n.offset = 10.25
        >>> s = stream.Stream([n])
        >>> pl = graph.plot.ScatterPitchClassOffset(s)
        >>> pl.processOneElement(n)
        [(10.25, 1, {})]

        >>> c = chord.Chord(['D4', 'E5'])
        >>> s.insert(5.0, c)
        >>> pl.processOneElement(c)
        [(5.0, 2, {}), (5.0, 4, {})]
        '''
        elementValues: list[list[t.Any]] = [[] for _ in range(len(self.allAxes))]
        formatDict: dict[t.Any, t.Any] = {}
        # should be two for most things

        if not isinstance(el, chord.Chord):
            for i, thisAxis in enumerate(self.allAxes):
                axisValue = thisAxis.extractOneElement(el, formatDict)
                # use isinstance(List) not isiterable, since
                # extractOneElement can distinguish between a tuple which
                # represents a single value, or a list of values (or list of tuples)
                # which represent multiple values
                if not isinstance(axisValue, list) and axisValue is not None:
                    axisValue = [axisValue]
                elementValues[i] = axisValue
        else:
            elementValues = self.extractChordDataMultiAxis(el, formatDict)

        self.postProcessElement(el, formatDict, *elementValues)
        if None in elementValues:
            return None

        elementValueLength = max([len(ev) for ev in elementValues])
        formatDictList = [formatDict.copy() for _ in range(elementValueLength)]
        elementValues.append(formatDictList)
        returnList = list(zip(*elementValues))
        return returnList

    def postProcessElement(self,
                           el: base.Music21Object,
                           formatDict: dict[t.Any, t.Any],
                           *values: list[numbers.Real]) -> None:
        '''
        Any processing that needs to take place for each element, independent
        of what the axis is finding can go here.  For chords, a single
        formatDict applies to all pitches/notes in the chord.
        '''
        pass

    def postProcessData(self):
        '''
        Call any post data processing routines here and on any axes.
        '''
        for thisAxis in self.allAxes:
            thisAxis.postProcessData()

    # --------------------------------------------------------------------------
    @staticmethod
    def extractChordDataOneAxis(ax, c, formatDict):
        '''
        Look for Note-like attributes in a Chord. This is done by first
        looking at the Chord, and then, if attributes are not found, looking at each pitch.

        Returns a list of values.
        '''
        values = []
        value = None
        try:
            value = ax.extractOneElement(c, formatDict)
        except AttributeError:
            pass  # do not try others

        if value is not None:
            values.append(value)

        if not values:  # still not set, get form chord
            for n in c:
                # try to get values from note inside chords
                value = None
                try:
                    value = ax.extractOneElement(n, formatDict)
                except AttributeError:  # pragma: no cover
                    break  # do not try others

                if value is not None:
                    values.append(value)
        return values

    def extractChordDataMultiAxis(self, c, formatDict):
        '''
        Returns a list of lists of values for each axis.
        '''
        elementValues = [self.extractChordDataOneAxis(ax, c, formatDict) for ax in self.allAxes]

        lookIntoChordForNotesGroups = []
        for thisAxis, values in zip(self.allAxes, elementValues):
            if not values:
                lookIntoChordForNotesGroups.append((thisAxis, values))

        for thisAxis, destValues in lookIntoChordForNotesGroups:
            for n in c:
                try:
                    target = thisAxis.extractOneElement(n, formatDict)
                except AttributeError:  # pragma: no cover
                    continue  # must try others
                if target is not None:
                    destValues.append(target)

        # environLocal.printDebug(['after looking at Pitch:',
        #    'xValues', xValues, 'yValues', yValues])

        # if we only have one attribute from the Chord, and many from the
        # Pitches, need to make the number of data points equal by
        # duplicating data
        if self.matchPitchCountForChords:
            self.fillValueLists(elementValues)
        return elementValues

    @staticmethod
    def fillValueLists(elementValues, nullFillValue=0):
        '''
        pads a list of lists so that each list has the same length.
        Pads with the first element of the list or nullFillValue if
        the list has no elements.   Modifies in place so returns None

        Used by extractChordDataMultiAxis

        >>> l0 = [2, 3, 4]
        >>> l1 = [10, 20, 30, 40, 50]
        >>> l2 = []
        >>> listOfLists = [l0, l1, l2]
        >>> graph.plot.PlotStream.fillValueLists(listOfLists)
        >>> listOfLists
        [[2,   3,  4,  2,  2],
         [10, 20, 30, 40, 50],
         [0,   0,  0,  0,  0]]
        '''
        maxLength = max([len(val) for val in elementValues])
        for val in elementValues:
            shortAmount = maxLength - len(val)
            if val:
                fillVal = val[0]
            else:
                fillVal = nullFillValue
            if shortAmount:
                val += [fillVal] * shortAmount

    # --------------------------------------------------------------------------
    @property
    def id(self):
        '''
        Each PlotStream has a unique id that consists of its class name and
        the class names of the axes:

        >>> s = stream.Stream()
        >>> pScatter = graph.plot.ScatterPitchClassQuarterLength(s)
        >>> pScatter.id
        'scatter-quarterLength-pitchClass'
        '''
        idName = self.graphType

        for axisObj in self.allAxes:
            if axisObj is None:
                continue
            axisName = axisObj.quantities[0]
            idName += '-' + axisName

        return idName

# ------------------------------------------------------------------------------
class PlotStream(primitives.Graph, PlotStreamMixin):
    '''
    A generic stream plotter.
    '''
    def __init__(self, streamObj=None, **keywords):
        primitives.Graph.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        self.axisX = axis.OffsetAxis(self, 'x')

# ------------------------------------------------------------------------------
# scatter plots

class Scatter(primitives.GraphScatter, PlotStreamMixin):
    '''
    Base class for 2D scatter plots.
    '''

    def __init__(self, streamObj=None, **keywords):
        primitives.GraphScatter.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

class ScatterPitchSpaceQuarterLength(Scatter):
    r'''
    A scatter plot of pitch space and quarter length

    >>> s = corpus.parse('bach/bwv324.xml')
    >>> p = graph.plot.ScatterPitchSpaceQuarterLength(s)
    >>> p.doneAction = None #_DOCS_HIDE
    >>> p.id
    'scatter-quarterLength-pitchSpace'
    >>> p.run()

    .. image:: images/ScatterPitchSpaceQuarterLength.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.QuarterLengthAxis,
        'y': axis.PitchSpaceAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)
        self.axisX.useLogScale = True
        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (6, 6)
        if 'title' not in keywords:
            self.title = 'Pitch by Quarter Length Scatter'
#         if 'alpha' not in keywords:
#             self.alpha = 0.7

class ScatterPitchClassQuarterLength(ScatterPitchSpaceQuarterLength):
    '''
    A scatter plot of pitch class and quarter length

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.ScatterPitchClassQuarterLength(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.ScatterPitchClassQuarterLength(s)
    >>> p.id
    'scatter-quarterLength-pitchClass'
    >>> p.run()

    .. image:: images/ScatterPitchClassQuarterLength.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.QuarterLengthAxis,
        'y': axis.PitchClassAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)
        if 'title' not in keywords:
            self.title = 'Pitch Class by Quarter Length Scatter'

class ScatterPitchClassOffset(Scatter):
    '''
    A scatter plot of pitch class and offset

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.ScatterPitchClassOffset(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.ScatterPitchClassOffset(s)
    >>> p.id
    'scatter-offset-pitchClass'
    >>> p.run()

    .. image:: images/ScatterPitchClassOffset.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.OffsetAxis,
        'y': axis.PitchClassAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 5)
        if 'title' not in keywords:
            self.title = 'Pitch Class by Offset Scatter'
        if 'alpha' not in keywords:  # will not restrike, so make less transparent
            self.alpha = 0.7

class ScatterPitchSpaceDynamicSymbol(Scatter):
    '''
    A graph of dynamics used by pitch space.

    >>> s = converter.parse('tinynotation: 4/4 C4 d E f', makeNotation=False) #_DOCS_HIDE
    >>> s.insert(0.0, dynamics.Dynamic('pp')) #_DOCS_HIDE
    >>> s.insert(2.0, dynamics.Dynamic('ff')) #_DOCS_HIDE
    >>> p = graph.plot.ScatterPitchSpaceDynamicSymbol(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('schumann_robert/opus41no1/movement2.xml')
    >>> #_DOCS_SHOW p = graph.plot.ScatterPitchSpaceDynamicSymbol(s)
    >>> p.run()

    .. image:: images/ScatterPitchSpaceDynamicSymbol.*
        :width: 600
    '''
    # string name used to access this class
    figureSizeDefault = (12, 6)
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.PitchSpaceAxis,
        'y': axis.DynamicsAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)

        self.axisX.showEnharmonic = False
        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = self.figureSizeDefault
        if 'title' not in keywords:
            self.title = 'Dynamics by Pitch Scatter'
        if 'alpha' not in keywords:
            self.alpha = 0.7

    def extractData(self):
        # get data from correlate object
        am = correlate.ActivityMatch(self.streamObj)
        amData = am.pitchToDynamic(dataPoints=True)
        self.data = []
        for x, y in amData:
            self.data.append((x, y, {}))

        xVals = [d[0] for d in self.data]
        yVals = [d[1] for d in self.data]

        self.axisX.setBoundariesFromData(xVals)
        self.axisY.setBoundariesFromData(yVals)
        self.postProcessData()

# ------------------------------------------------------------------------------
# histograms
class Histogram(primitives.GraphHistogram, PlotStreamMixin):
    '''
    Base class for histograms that plot one axis against its count
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.Axis,
        'y': axis.CountingAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        primitives.GraphHistogram.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        if 'alpha' not in keywords:
            self.alpha = 1.0

    def run(self, *, callProcess: bool = True, **keywords):
        '''
        Override run method to remap X data into individual bins.
        '''
        if t.TYPE_CHECKING:
            assert hasattr(self, 'axisX') and hasattr(self, 'axisY')

        self.setAxisKeywords()
        self.extractData()
        self.setTicks('y', self.axisY.ticks())
        xTicksNew = self.remapXTicksData()
        self.setTicks('x', xTicksNew)
        self.setAxisLabel('y', self.axisY.label)
        self.setAxisLabel('x', self.axisX.label)

        if callProcess:
            self.process()

    def remapXTicksData(self):
        '''
        Changes the ticks and data so that they both run
        1, 2, 3, 4, etc.
        '''

        xTicksOrig = self.axisX.ticks()
        xTickDict = {v[0]: v[1] for v in xTicksOrig}
        xTicksNew = []
        # self.data is already sorted.
        if ((not hasattr(self.axisX, 'hideUnused') or self.axisX.hideUnused is True)
                or self.axisX.minValue is None
                or self.axisX.maxValue is None):
            for i in range(len(self.data)):
                dataVal = self.data[i]
                xDataVal = dataVal[0]
                self.data[i] = (i + 1,) + dataVal[1:]
                if xDataVal in xTickDict:  # should be there:
                    newTick = (i + 1, xTickDict[xDataVal])
                    xTicksNew.append(newTick)
        else:
            from music21 import pitch
            for i in range(int(self.axisX.minValue), int(self.axisX.maxValue) + 1):
                if i in xTickDict:
                    label = xTickDict[i]
                elif hasattr(self.axisX, 'blankLabelUnused') and not self.axisX.blankLabelUnused:
                    label = pitch.Pitch(i).name
                else:
                    label = ''
                newTick = (i, label)
                xTicksNew.append(newTick)

        return xTicksNew

class HistogramPitchSpace(Histogram):
    '''
    A histogram of pitch space.

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.HistogramPitchSpace(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.HistogramPitchSpace(s)
    >>> p.id
    'histogram-pitchSpace-count'
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/HistogramPitchSpace.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **Histogram.axesClasses,
        'x': axis.PitchSpaceAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)
        self.axisX.showEnharmonic = False
        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 6)
        if 'title' not in keywords:
            self.title = 'Pitch Histogram'

class HistogramPitchClass(Histogram):
    '''
    A histogram of pitch class

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.HistogramPitchClass(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.HistogramPitchClass(s)
    >>> p.id
    'histogram-pitchClass-count'
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/HistogramPitchClass.*
        :width: 600

    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **Histogram.axesClasses,
        'x': axis.PitchClassAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)
        self.axisX.showEnharmonic = False
        if 'title' not in keywords:
            self.title = 'Pitch Class Histogram'

class HistogramQuarterLength(Histogram):
    '''
    A histogram of pitch class.

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.HistogramQuarterLength(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.HistogramQuarterLength(s)
    >>> p.id
    'histogram-quarterLength-count'
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/HistogramQuarterLength.*
        :width: 600

    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **Histogram.axesClasses,
        'x': axis.QuarterLengthAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)
        self.axisX = axis.QuarterLengthAxis(self, 'x')
        self.axisX.useLogScale = False
        if 'title' not in keywords:
            self.title = 'Quarter Length Histogram'

# ------------------------------------------------------------------------------
# weighted scatter

class ScatterWeighted(primitives.GraphScatterWeighted, PlotStreamMixin):
    '''
    Base class for histograms that plot one axis against its count.

    The count is stored as the Z axis, though it is represented as size.
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.Axis,
        'y': axis.Axis,
        'z': axis.CountingAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        primitives.GraphScatterWeighted.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        self.axisZ.countAxes = ('x', 'y')

class ScatterWeightedPitchSpaceQuarterLength(ScatterWeighted):
    '''
    A graph of event, sorted by pitch, over time.

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.ScatterWeightedPitchSpaceQuarterLength(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.ScatterWeightedPitchSpaceQuarterLength(s)
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/ScatterWeightedPitchSpaceQuarterLength.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **ScatterWeighted.axesClasses,
        'x': axis.QuarterLengthAxis,
        'y': axis.PitchSpaceAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(
            streamObj, **keywords)
        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (7, 7)
        if 'title' not in keywords:
            self.title = 'Count of Pitch and Quarter Length'
        if 'alpha' not in keywords:
            self.alpha = 0.8

class ScatterWeightedPitchClassQuarterLength(ScatterWeighted):
    '''
    A graph of event, sorted by pitch class, over time.

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.ScatterWeightedPitchClassQuarterLength(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.ScatterWeightedPitchClassQuarterLength(s)
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/ScatterWeightedPitchClassQuarterLength.*
        :width: 600

    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **ScatterWeighted.axesClasses,
        'x': axis.QuarterLengthAxis,
        'y': axis.PitchClassAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(
            streamObj, **keywords)

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (7, 7)
        if 'title' not in keywords:
            self.title = 'Count of Pitch Class and Quarter Length'
        if 'alpha' not in keywords:
            self.alpha = 0.8

class ScatterWeightedPitchSpaceDynamicSymbol(ScatterWeighted):
    '''
    A graph of dynamics used by pitch space.

    >>> #_DOCS_SHOW s = corpus.parse('schumann_robert/opus41no1/movement2.xml')
    >>> s = converter.parse('tinynotation: 4/4 C4 d E f', makeNotation=False) #_DOCS_HIDE
    >>> s.insert(0.0, dynamics.Dynamic('pp')) #_DOCS_HIDE
    >>> s.insert(2.0, dynamics.Dynamic('ff')) #_DOCS_HIDE
    >>> p = graph.plot.ScatterWeightedPitchSpaceDynamicSymbol(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW p = graph.plot.ScatterWeightedPitchSpaceDynamicSymbol(s)
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/ScatterWeightedPitchSpaceDynamicSymbol.*
        :width: 600

    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **ScatterWeighted.axesClasses,
        'x': axis.PitchSpaceAxis,
        'y': axis.DynamicsAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(
            streamObj, **keywords)

        self.axisX.showEnharmonic = False

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 10)
        if 'title' not in keywords:
            self.title = 'Count of Pitch Class and Quarter Length'
        if 'alpha' not in keywords:
            self.alpha = 0.8
        # make smaller for axis display
        if 'tickFontSize' not in keywords:
            self.tickFontSize = 7

    def extractData(self):
        # get data from correlate object
        am = correlate.ActivityMatch(self.streamObj)
        self.data = am.pitchToDynamic(dataPoints=True)
        xVals = [x for x, unused_y in self.data]
        yVals = [y for unused_x, y in self.data]
        self.data = [[x, y, 1] for x, y in self.data]

        self.axisX.setBoundariesFromData(xVals)
        self.axisY.setBoundariesFromData(yVals)
        self.postProcessData()

# ------------------------------------------------------------------------------
# color grids

class WindowedAnalysis(primitives.GraphColorGrid, PlotStreamMixin):
    '''
    Base Plot for windowed analysis routines such as Key Analysis or Ambitus.
    '''
    format = 'colorGrid'

    keywordConfigurables = primitives.GraphColorGrid.keywordConfigurables + (
        'minWindow', 'maxWindow', 'windowStep', 'windowType', 'compressLegend',
        'processorClass', 'graphLegend')

    axesClasses: dict[str, type[axis.Axis]] = {'x': axis.OffsetAxis}
    processorClassDefault: type[discrete.DiscreteAnalysis] = discrete.KrumhanslSchmuckler

    def __init__(self, streamObj=None, **keywords):
        self.processorClass = self.processorClassDefault  # a discrete processor class.
        self._processor = None

        self.graphLegend = None
        self.minWindow = 1
        self.maxWindow = None
        self.windowStep = 'pow2'
        self.windowType = 'overlap'
        self.compressLegend = True

        primitives.GraphColorGrid.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        self.axisX = axis.OffsetAxis(self, 'x')

    @property
    def processor(self):
        if not self.processorClass:
            return None
        if not self._processor:
            self._processor = self.processorClass(self.streamObj)
        return self._processor

    def run(self, *, callProcess: bool = True, **keywords):
        '''
        Actually creates the graph.
        '''
        if self.title == 'Music21 Graph' and self.processor:
            self.title = (self.processor.name
                          + f' ({self.processor.solutionUnitString()})')

        data, yTicks = self.extractData()
        self.data = data
        self.setTicks('y', yTicks)

        self.axisX.setBoundariesFromData()
        xTicks = self.axisX.ticks()
        # replace offset values with 0 and 1, as proportional here
        if len(xTicks) >= 2:
            xTicks = [(0, xTicks[0][1]), (1, xTicks[-1][1])]
        environLocal.printDebug(['xTicks', xTicks])
        self.setTicks('x', xTicks)
        self.setAxisLabel('y', 'Window Size\n(Quarter Lengths)')
        self.setAxisLabel('x', f'Windows ({self.axisX.label} Span)')

        self.graphLegend = self._getLegend()
        if callProcess:
            self.process()

        # uses self.processor

    def extractData(self):
        '''
        Extract data actually calls the processing routine.

        Returns two element tuple of the data (colorMatrix) and the yTicks list
        '''
        wa = windowed.WindowedAnalysis(self.streamObj, self.processor)
        unused_solutionMatrix, colorMatrix, metaMatrix = wa.process(self.minWindow,
                                                                    self.maxWindow,
                                                                    self.windowStep,
                                                                    windowType=self.windowType)

        # if more than 12 bars, reduce the number of ticks
        if len(metaMatrix) > 12:
            tickRange = range(0, len(metaMatrix), len(metaMatrix) // 12)
        else:
            tickRange = range(len(metaMatrix))

        environLocal.printDebug(['tickRange', tickRange])
        # environLocal.printDebug(['last start color', colorMatrix[-1][0]])

        # get dictionaries of metadata for each row
        pos = 0
        yTicks = []

        for y in tickRange:
            thisWindowSize = metaMatrix[y]['windowSize']
            # pad three ticks for each needed
            yTicks.append([pos, ''])  # pad first
            yTicks.append([pos + 1, str(thisWindowSize)])
            yTicks.append([pos + 2, ''])  # pad last
            pos += 3

        return colorMatrix, yTicks

    def _getLegend(self):
        '''
        Returns a solution legend for a WindowedAnalysis
        '''
        graphLegend = primitives.GraphColorGridLegend(doneAction=None,
                                                      title=self.title)
        graphData = self.processor.solutionLegend(compress=self.compressLegend)
        graphLegend.data = graphData
        return graphLegend

    def write(self, fp=None):  # pragma: no cover
        '''
        Overrides the normal write method here to add a legend.
        '''
        # call the process routine in the base graph
        super().write(fp)

        if fp is None:
            fp = environLocal.getTempFile('.png', returnPathlib=True)
        else:
            fp = common.cleanpath(fp, returnPathlib=True)

        directory, fn = os.path.split(fp)
        fpLegend = os.path.join(directory, 'legend-' + fn)
        # create a new graph of the legend
        self.graphLegend.process()
        self.graphLegend.write(fpLegend)

class WindowedKey(WindowedAnalysis):
    '''
    Stream plotting of windowed version of Krumhansl-Schmuckler analysis routine.
    See :class:`~music21.analysis.discrete.KrumhanslSchmuckler` for more details.

    >>> s = corpus.parse('bach/bwv66.6')
    >>> p = graph.plot.WindowedKey(s.parts[0])
    >>> p.doneAction = None #_DOCS_HIDE
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/WindowedKrumhanslSchmuckler.*
        :width: 600

    .. image:: images/legend-WindowedKrumhanslSchmuckler.*

    Set the processor class to one of the following for different uses:

    >>> p = graph.plot.WindowedKey(s.parts.first())
    >>> p.processorClass = analysis.discrete.AardenEssen
    >>> p.processorClass = analysis.discrete.SimpleWeights
    >>> p.processorClass = analysis.discrete.BellmanBudge
    >>> p.processorClass = analysis.discrete.TemperleyKostkaPayne
    >>> p.doneAction = None #_DOCS_HIDE
    >>> p.run()

    '''
    processorClassDefault = discrete.KrumhanslSchmuckler

class WindowedAmbitus(WindowedAnalysis):
    '''
    Stream plotting of basic pitch span.

    >>> s = corpus.parse('bach/bwv66.6')
    >>> p = graph.plot.WindowedAmbitus(s.parts.first())
    >>> p.doneAction = None #_DOCS_HIDE
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/WindowedAmbitus.*
        :width: 600

    .. image:: images/legend-WindowedAmbitus.*

    '''
    processorClassDefault = discrete.Ambitus

# ------------------------------------------------------------------------------
# horizontal bar graphs

class HorizontalBar(primitives.GraphHorizontalBar, PlotStreamMixin):
    '''
    A graph of events, sorted by pitch, over time.

    If colorByPart is True, then each part will get its own color from
    `self.colors` (unless there are more parts than colors).
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.OffsetEndAxis,
        'y': axis.PitchSpaceAxis,
    }

    def __init__(
        self,
        streamObj: stream.Stream|None = None,
        *,
        colorByPart=False,
        **keywords
    ) -> None:
        self.colorByPart = colorByPart
        self._partsToColor: dict[stream.Part, str] = {}

        self.axisY: axis.PitchSpaceAxis

        primitives.GraphHorizontalBar.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        self.axisY.hideUnused = False

    def run(self, *, callProcess: bool = True, **keywords):
        '''
        Optionally assign colors to Part objects and then do the normal run.
        '''
        if self.colorByPart:
            self.assignColorsToParts()
        super().run(callProcess=callProcess, **keywords)

    def assignColorsToParts(self) -> dict[stream.Part, str]:
        '''
        Give a different color for each part, if self.colorByPart is True.

        Returns the assignment for any further manipulation.

        Currently, two piano hands (PartStaff objects) get different colors.

        >>> bach = corpus.parse('bwv66.6')
        >>> plot = graph.plot.HorizontalBar(bach, colorByPart=True)
        >>> plot.assignColorsToParts()
        {<music21.stream.Part Soprano>: '#605c7f',
         <music21.stream.Part Alto>: '#5c7f60',
         <music21.stream.Part Tenor>: '#988969',
         <music21.stream.Part Bass>: '#628297'}
        '''
        s = self.streamObj
        numColors = len(self.colors)
        for i, p in enumerate(s[stream.Part]):
            self._partsToColor[p] = self.colors[i % numColors]
        return self._partsToColor

    def postProcessElement(self,
                           el: base.Music21Object,
                           formatDict: dict[t.Any, t.Any],
                           *values: list[numbers.Real]):
        '''
        Assign colors to each element if colorByPart is True.
        '''
        super().postProcessElement(el, formatDict, *values)
        if self.colorByPart:
            part = el.getContextByClass(stream.Part)
            if part is not None:
                formatDict['color'] = self._partsToColor.get(part,
                                                             self.colors[0])

    def postProcessData(self):
        '''
        Call any post data processing routines here and on any axes.
        '''
        super().postProcessData()
        self.axisY.setBoundariesFromData([d[1] for d in self.data])
        yTicks = self.axisY.ticks()

        pitchSpanDict = {}
        newData = []
        dictOfFormatDicts = {}

        for positionData, pitchData, formatDict in self.data:
            if pitchData not in pitchSpanDict:
                pitchSpanDict[pitchData] = []
                dictOfFormatDicts[pitchData] = {}

            positionDataWithFormatDict = (*positionData, formatDict)
            pitchSpanDict[pitchData].append(positionDataWithFormatDict)

            # this was a mergeDict not in place operation and thus did nothing
            # {**dictOfFormatDicts[pitchData], **formatDict}

        for unused_k, v in pitchSpanDict.items():
            # sort these tuples, ignoring unhashable dict.
            v.sort(key=lambda point: (point[0], point[1]))

        # seen_numericValues = set()
        for numericValue, label in yTicks:
            # make sure there is an entry for each yTick, regardless
            # of whether we have any data for it or not.
            if numericValue in pitchSpanDict:
                newData.append([label,
                                pitchSpanDict[numericValue],
                                dictOfFormatDicts[numericValue]])
            else:
                newData.append([label, [], {}])
            # seen_numericValues.add(numericValue)

        # # now find anything in pitchSpanDict that wasn't in the yTicks, for
        # # instance, microtones!
        # for numericValue, data_triplet in pitchSpanDict.items():
        #     if numericValue not in seen_numericValues:
        #         newData.append([
        #             '',  # no label
        #             data_triplet,
        #             dictOfFormatDicts[numericValue],
        #         ])

        self.data = newData

class HorizontalBarPitchClassOffset(HorizontalBar):
    '''
    A graph of events, sorted by pitch class, over time.

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.HorizontalBarPitchClassOffset(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.HorizontalBarPitchClassOffset(s)
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/HorizontalBarPitchClassOffset.*
        :width: 600

    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **HorizontalBar.axesClasses,
        'y': axis.PitchClassAxis,
    }

    def __init__(self, streamObj=None, *, colorByPart=False, **keywords):
        super().__init__(streamObj, colorByPart=colorByPart, **keywords)
        self.axisY = axis.PitchClassAxis(self, 'y')
        self.axisY.hideUnused = False

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 4)
        if 'title' not in keywords:
            self.title = 'Note Quarter Length and Offset by Pitch Class'

class HorizontalBarPitchSpaceOffset(HorizontalBar):
    '''
    A graph of events, sorted by pitch space, over time, generally called
    a "piano roll".

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.HorizontalBarPitchSpaceOffset(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW p = graph.plot.HorizontalBarPitchSpaceOffset(s)
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/HorizontalBarPitchSpaceOffset.*
        :width: 600
    '''

    def __init__(self, streamObj=None, *, colorByPart=False, **keywords):
        super().__init__(streamObj, colorByPart=colorByPart, **keywords)

        if 'figureSize' not in keywords:
            self.figureSize = (10, 6)
        if 'title' not in keywords:
            self.title = 'Note Quarter Length by Pitch'

# ------------------------------------------------------------------------------
class HorizontalBarWeighted(primitives.GraphHorizontalBarWeighted, PlotStreamMixin):
    '''
    A base class for plots of Scores with weighted (by height) horizontal bars.
    Many weighted segments represent a dynamic parameter of a Part.
    '''
    axesClasses: dict[str, type[axis.Axis]] = {'x': axis.OffsetAxis}
    keywordConfigurables = primitives.GraphHorizontalBarWeighted.keywordConfigurables + (
        'fillByMeasure',
        'normalizeByPart',
        'partGroups',
        'segmentByTarget',
    )

    def __init__(self, streamObj=None, **keywords):
        self.fillByMeasure = False
        self.segmentByTarget = True
        self.normalizeByPart = False
        self.partGroups = None

        primitives.GraphHorizontalBarWeighted.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

    def extractData(self):
        '''
        Extract the data from the Stream.
        '''
        if not isinstance(self.streamObj, stream.Score):
            raise GraphException('provided Stream must be Score')
        # parameters: x, span, heightScalar, color, alpha, yShift
        pr = reduction.PartReduction(
            self.streamObj,
            partGroups=self.partGroups,
            fillByMeasure=self.fillByMeasure,
            segmentByTarget=self.segmentByTarget,
            normalizeByPart=self.normalizeByPart)
        pr.process()
        data = pr.getGraphHorizontalBarWeightedData()
        # environLocal.printDebug(['data', data])
        uniqueOffsets = []
        for unused_key, value in data:
            for dataList in value:
                start = dataList[0]
                dur = dataList[1]
                if start not in uniqueOffsets:
                    uniqueOffsets.append(start)
                if start + dur not in uniqueOffsets:
                    uniqueOffsets.append(start + dur)
        # use default args for now
        self.axisX.minValue = min(uniqueOffsets)
        self.axisX.maxValue = max(uniqueOffsets)
        self.data = data

class Dolan(HorizontalBarWeighted):
    '''
    A graph of the activity of a parameter of a part (or a group of parts) over time.
    The default parameter graphed is Dynamics. Dynamics are assumed to extend activity
    to the next change in dynamics.

    Numerous parameters can be configured based on functionality encoded in
    the :class:`~music21.analysis.reduction.PartReduction` object.

    If the `fillByMeasure` parameter is True, and if measures are available, each part
    will segment by Measure divisions, and look for the target activity only once per
    Measure. If more than one target is found in the Measure, values will be averaged.
    If `fillByMeasure` is False, the part will be segmented by each Note.

    The `segmentByTarget` parameter is True, segments, which may be Notes or Measures,
    will be divided if necessary to show changes that occur over the duration of the
    segment by a target object.

    If the `normalizeByPart` parameter is True, each part will be normalized within the
    range only of that part. If False, all parts will be normalized by the max of all parts.
    The default is True.

    >>> s = corpus.parse('bwv66.6')
    >>> dyn = ['p', 'mf', 'f', 'ff', 'mp', 'fff', 'ppp']
    >>> i = 0
    >>> for p in s.parts:
    ...     for m in p.getElementsByClass(stream.Measure):
    ...         m.insert(0, dynamics.Dynamic(dyn[i % len(dyn)]))
    ...         i += 1
    ...
    >>> #_DOCS_SHOW s.plot('dolan', fillByMeasure=True, segmentByTarget=True)

    .. image:: images/Dolan.*
        :width: 600

    '''

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)

        # self.fy = lambda n: n.pitch.pitchClass
        # self.fyTicks = self.ticksPitchClassUsage
        # must set part groups if not defined here
        if streamObj is not None:
            self._getPartGroups()
        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 4)

        if 'title' not in keywords:
            self.title = 'Instrumentation'
            if self.streamObj and self.streamObj.metadata is not None:
                if self.streamObj.metadata.title is not None:
                    self.title = self.streamObj.metadata.title
        if 'hideYGrid' not in keywords:
            self.hideYGrid = True

    def _getPartGroups(self):
        '''
        Examine the instruments in the Score and determine if there
        is a good match for a default configuration of parts.
        '''
        from music21 import instrument

        if self.partGroups:
            return  # keep what the user set
        if self.streamObj:
            return None
        instStream = self.streamObj.flatten().getElementsByClass(instrument.Instrument)
        if not instStream:
            return  # do not set anything

        if len(instStream) == 4 and self.streamObj.getElementById('Soprano') is not None:
            pgOrc = [
                {'name': 'Soprano', 'color': 'purple', 'match': ['soprano', '0']},
                {'name': 'Alto', 'color': 'orange', 'match': ['alto', '1']},
                {'name': 'Tenor', 'color': 'lightgreen', 'match': ['tenor']},
                {'name': 'Bass', 'color': 'mediumblue', 'match': ['bass']},
            ]
            self.partGroups = pgOrc

        elif len(instStream) == 4 and self.streamObj.getElementById('Viola') is not None:
            pgOrc = [
                {'name': '1st Violin', 'color': 'purple',
                    'match': ['1st violin', '0', 'violin 1', 'violin i']},
                {'name': '2nd Violin', 'color': 'orange',
                    'match': ['2nd violin', '1', 'violin 2', 'violin ii']},
                {'name': 'Viola', 'color': 'lightgreen', 'match': ['viola']},
                {'name': 'Cello', 'color': 'mediumblue',
                    'match': ['cello', 'violoncello', "'cello"]},
            ]
            self.partGroups = pgOrc

        elif len(instStream) > 10:
            pgOrc = [
                {'name': 'Flute', 'color': '#C154C1', 'match': ['flauto', r'flute \d']},
                {'name': 'Oboe', 'color': 'blue', 'match': ['oboe', r'oboe \d']},
                {'name': 'Clarinet', 'color': 'mediumblue',
                 'match': ['clarinetto', r'clarinet in \w* \d']},
                {'name': 'Bassoon', 'color': 'purple', 'match': ['fagotto', r'bassoon \d']},

                {'name': 'Horns', 'color': 'orange', 'match': ['corno', r'horn in \w* \d']},
                {'name': 'Trumpet', 'color': 'red',
                 'match': ['tromba', r'trumpet \d', r'trumpet in \w* \d']},
                {'name': 'Trombone', 'color': 'red', 'match': [r'trombone \d']},
                {'name': 'Timpani', 'color': '#5C3317', 'match': None},

                {'name': 'Violin I', 'color': 'lightgreen', 'match': ['violino i', 'violin i']},
                {'name': 'Violin II', 'color': 'green', 'match': ['violino ii', 'violin ii']},
                {'name': 'Viola', 'color': 'forestgreen', 'match': None},
                {'name': 'Violoncello & CB', 'color': 'dark green',
                 'match': ['violoncello', 'contrabasso']},
                #            {'name':'CB', 'color':'#003000', 'match':['contrabasso']},
            ]
            self.partGroups = pgOrc

# ------------------------------------------------------------------------------------------
# 3D plots

class Plot3DBars(primitives.Graph3DBars, PlotStreamMixin):
    '''
    Base class for Stream plotting classes.
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        'x': axis.QuarterLengthAxis,
        'y': axis.PitchClassAxis,
        'z': axis.CountingAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        primitives.Graph3DBars.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, streamObj, **keywords)

        self.axisZ.countAxes = ('x', 'y')

class Plot3DBarsPitchSpaceQuarterLength(Plot3DBars):
    '''
    A scatter plot of pitch and quarter length

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> p = graph.plot.Plot3DBarsPitchSpaceQuarterLength(s, doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW from music21.musicxml import testFiles
    >>> #_DOCS_SHOW s = converter.parse(testFiles.mozartTrioK581Excerpt)
    >>> #_DOCS_SHOW p = graph.plot.Plot3DBarsPitchSpaceQuarterLength(s)
    >>> p.id
    '3DBars-quarterLength-pitchSpace-count'
    >>> p.run()  # with defaults and proper configuration, will open graph

    .. image:: images/Plot3DBarsPitchSpaceQuarterLength.*
        :width: 600
    '''
    axesClasses: dict[str, type[axis.Axis]] = {
        **Plot3DBars.axesClasses,
        'y': axis.PitchSpaceAxis,
    }

    def __init__(self, streamObj=None, **keywords):
        super().__init__(streamObj, **keywords)

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (6, 6)
        if 'title' not in keywords:
            self.title = 'Pitch by Quarter Length Count'

# ------------------------------------------------------------------------------
# base class for multi-stream displays

class MultiStream(primitives.GraphGroupedVerticalBar, PlotStreamMixin):
    '''
    Approaches to plotting and graphing multiple Streams.
    A base class from which Stream plotting Classes inherit.

    Not yet integrated into the 2017 system, unfortunately.

    Provide a list of Streams as an argument. Optionally
    provide an additional list of labels for each list.
    '''
    axesClasses: dict[str, type[axis.Axis]] = {}

    def __init__(self, streamList, labelList=None, **keywords):
        primitives.GraphGroupedVerticalBar.__init__(self, **keywords)
        PlotStreamMixin.__init__(self, None)

        if labelList is None:
            labelList = []
        self.streamList = None
        foundPaths = self.parseStreams(streamList)

        # use found paths if no labels are provided
        if not labelList and len(foundPaths) == len(streamList):
            self.labelList = foundPaths
        else:
            self.labelList = labelList

        self.data = None  # store native data representation, useful for testing

    def parseStreams(self, streamList):
        self.streamList = []
        foundPaths = []
        for s in streamList:
            # could be corpus or file path
            if isinstance(s, str):
                foundPaths.append(os.path.basename(s))
                if os.path.exists(s):
                    s = converter.parse(s)
                else:  # assume corpus
                    s = corpus.parse(s)
            elif isinstance(s, pathlib.Path):
                foundPaths.append(s.name)
                if s.exists():
                    s = converter.parse(s)
                else:  # assume corpus
                    s = corpus.parse(s)
            # otherwise assume a parsed stream
            self.streamList.append(s)
        return foundPaths

class Features(MultiStream):
    '''
    Plots the output of a set of feature extractors.

    FeatureExtractors can be ids or classes.
    '''
    format = 'features'

    def __init__(self, streamList, featureExtractors, labelList=None, **keywords):
        if labelList is None:
            labelList = []

        super().__init__(streamList, labelList, **keywords)

        self.featureExtractors = featureExtractors

        self.xTickLabelRotation = 90
        self.xTickLabelHorizontalAlignment = 'left'
        self.xTickLabelVerticalAlignment = 'top'

        # self.graph.setAxisLabel('y', 'Count')
        # self.graph.setAxisLabel('x', 'Streams')

        # need more space for pitch axis labels
        if 'figureSize' not in keywords:
            self.figureSize = (10, 6)
        if 'title' not in keywords:
            self.title = None

    def run(self, *, callProcess: bool = True, **keywords):
        # will use self.fx and self.fxTick to extract data
        self.setAxisKeywords()

        self.data, xTicks, yTicks = self.extractData()

        self.grid = False

        self.setTicks('x', xTicks)
        self.setTicks('y', yTicks)

        if callProcess:
            self.process()

    def extractData(self):
        if len(self.labelList) != len(self.streamList):
            labelList = [x + 1 for x in range(len(self.streamList))]
        else:
            labelList = self.labelList

        feList = []
        for fe in self.featureExtractors:
            if isinstance(fe, str):
                post = features.extractorsById(fe)
                for sub in post:
                    feList.append(sub())
            else:  # assume a class
                feList.append(fe())

        # store each stream in a data instance
        diList = []
        for s in self.streamList:
            di = features.DataInstance(s)
            diList.append(di)

        data = []
        for i, di in enumerate(diList):
            sub = collections.OrderedDict()
            for fe in feList:
                fe.data = di
                v = fe.extract().vector
                if len(v) == 1:
                    sub[fe.name] = v[0]
                # average all values?
                else:
                    sub[fe.name] = sum(v) / len(v)
            dataPoint = [labelList[i], sub]
            data.append(dataPoint)

        # environLocal.printDebug(['data', data])

        xTicks = []
        for x, label in enumerate(labelList):
            # first value needs to be center of bar
            # value of tick is the string entry
            xTicks.append([x + 0.5, f'{label}'])
        # always have min and max
        yTicks = []
        return data, xTicks, yTicks

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER = [
    HistogramPitchSpace,
    HistogramPitchClass,
    HistogramQuarterLength,
    # windowed
    WindowedKey,
    WindowedAmbitus,
    # scatters
    ScatterPitchSpaceQuarterLength,
    ScatterPitchClassQuarterLength,
    ScatterPitchClassOffset,
    ScatterPitchSpaceDynamicSymbol,
    # offset based horizontal
    HorizontalBarPitchSpaceOffset,
    HorizontalBarPitchClassOffset,
    Dolan,
    # weighted scatter
    ScatterWeightedPitchSpaceQuarterLength,
    ScatterWeightedPitchClassQuarterLength,
    ScatterWeightedPitchSpaceDynamicSymbol,
    # 3d graphs
    Plot3DBarsPitchSpaceQuarterLength,
]

# , TestExternalManual)
