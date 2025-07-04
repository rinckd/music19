# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         graph/findPlot.py
# Purpose:      Functions that find appropriate plots for graph.plot
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2017-22 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Functions that find appropriate plots for graph.plot.
'''
from __future__ import annotations

import collections
import types
import typing as t

from music21.graph import axis
from music21.graph import plot
from music21.graph import primitives

# shortcuts that get a PlotClass directly
PLOTCLASS_SHORTCUTS: dict[str, type[plot.PlotStreamMixin]] = {
    'ambitus': plot.WindowedAmbitus,
    'dolan': plot.Dolan,
    'instruments': plot.Dolan,
    'key': plot.WindowedKey,
    'pianoroll': plot.HorizontalBarPitchSpaceOffset,
}

# all formats need to be here, and first for each row must match a graphType.
FORMAT_SYNONYMS: list[tuple[str, ...]] = [
    ('horizontalbar', 'bar', 'horizontal', 'pianoroll', 'piano'),
    ('histogram', 'histo', 'count'),
    ('scatter', 'point'),
    ('scatterweighted', 'weightedscatter', 'weighted'),
    ('3dbars', '3d'),
    ('colorgrid', 'grid', 'window', 'windowed'),
    ('horizontalbarweighted', 'barweighted', 'weightedbar')
]

# define co format strings
FORMATS = [syn[0] for syn in FORMAT_SYNONYMS]

def getPlotClasses() -> list[type[plot.PlotStreamMixin]]:
    '''
    return a list of all PlotStreamMixin subclasses. Returns a list sorted by name

    >>> graph.findPlot.getPlotClasses()
    [<class 'music21.graph.plot.Dolan'>,
     <class 'music21.graph.plot.Features'>,
     <class 'music21.graph.plot.Histogram'>,
     <class 'music21.graph.plot.HistogramPitchClass'>,
     <class 'music21.graph.plot.HistogramPitchSpace'>,
     ...]
    '''
    allPlot: list[type[plot.PlotStreamMixin]] = []
    for i in sorted(plot.__dict__):
        name = getattr(plot, i)
        # noinspection PyTypeChecker
        if (callable(name)
                and not isinstance(name, types.FunctionType)
                and hasattr(name, '__mro__')
                and plot.PlotStreamMixin in name.__mro__
                and primitives.Graph in name.__mro__):
            allPlot.append(t.cast(type[plot.PlotStreamMixin], name))
    return allPlot

def getAxisClasses() -> list[type[axis.Axis]]:
    '''
    return a list of all Axis subclasses.  Returns a list sorted by name

    >>> graph.findPlot.getAxisClasses()
    [<class 'music21.graph.axis.Axis'>,
     <class 'music21.graph.axis.CountingAxis'>,
     <class 'music21.graph.axis.DynamicsAxis'>,
     <class 'music21.graph.axis.OffsetAxis'>,
     ...]
    '''
    allAxis: list[type[axis.Axis]] = []
    for i in sorted(axis.__dict__):
        name = getattr(axis, i)
        if (callable(name)
                and not isinstance(name, types.FunctionType)
                and issubclass(name, axis.Axis)):
            allAxis.append(name)
    return allAxis

def getAxisQuantities(synonyms=False, axesToCheck=None):
    '''
    >>> graph.findPlot.getAxisQuantities()
    ['generic', 'count', 'dynamic', 'offset', 'offsetEnd',
     'pitchGeneric', 'pitchClass', 'pitchSpace', 'octave', 'position', 'quarterLength']

    >>> graph.findPlot.getAxisQuantities(synonyms=True)
    ['generic', 'one', 'nothing', 'blank', 'count', 'quantity', 'frequency', ...]

    >>> theseAxes = [graph.axis.CountingAxis, graph.axis.OffsetAxis]
    >>> graph.findPlot.getAxisQuantities(axesToCheck=theseAxes)
    ['count', 'offset']

    >>> graph.findPlot.getAxisQuantities(True, axesToCheck=theseAxes)
    ['count', 'quantity', 'frequency', 'counting',
     'offset', 'measure', 'offsets', 'measures', 'time']

    '''
    if axesToCheck is None:
        axesToCheck = getAxisClasses()
    allQuantities = []
    for axClass in axesToCheck:
        if synonyms:
            allQuantities.extend(axClass.quantities)
        else:
            allQuantities.append(axClass.quantities[0])
    return allQuantities

def userFormatsToFormat(userFormat):
    '''
    Replace possible user format strings with defined format names as used herein.
    Returns string unaltered if no match.

    >>> graph.findPlot.userFormatsToFormat('horizontal')
    'horizontalbar'
    >>> graph.findPlot.userFormatsToFormat('Weighted Scatter')
    'scatterweighted'
    >>> graph.findPlot.userFormatsToFormat('3D')
    '3dbars'

    Unknown formats pass through unaltered.

    >>> graph.findPlot.userFormatsToFormat('4D super chart')
    '4dsuperchart'
    '''
    # environLocal.printDebug(['calling user userFormatsToFormat:', value])
    userFormat = userFormat.lower()
    userFormat = userFormat.replace(' ', '')

    for opt in FORMAT_SYNONYMS:
        if userFormat in opt:
            return opt[0]  # first one for each is the preferred

    # return unaltered if no match
    # environLocal.printDebug(['userFormatsToFormat(): could not match value', value])
    return userFormat

def getPlotClassesFromFormat(graphFormat, checkPlotClasses=None):
    '''
    Given a graphFormat, find a list of plots that match:

    >>> graph.findPlot.getPlotClassesFromFormat('scatterweighted')
    [<class 'music21.graph.plot.ScatterWeighted'>,
     <class 'music21.graph.plot.ScatterWeightedPitchClassQuarterLength'>,
     <class 'music21.graph.plot.ScatterWeightedPitchSpaceDynamicSymbol'>,
     <class 'music21.graph.plot.ScatterWeightedPitchSpaceQuarterLength'>]

    Or give a list of plot classes to check:

    >>> pcs = [graph.plot.ScatterWeighted, graph.plot.Dolan]
    >>> graph.findPlot.getPlotClassesFromFormat('scatterweighted', pcs)
    [<class 'music21.graph.plot.ScatterWeighted'>]

    '''
    graphFormat = userFormatsToFormat(graphFormat).lower()

    if checkPlotClasses is None:
        checkPlotClasses = getPlotClasses()
    filteredPlots = []
    for p in checkPlotClasses:
        if p.graphType.lower() == graphFormat:
            filteredPlots.append(p)
    return filteredPlots

def getAxisClassFromValue(axisValue: str) -> type[axis.Axis]|None:
    '''
    given an axis value return the single best axis for the value, or None

    uses Axis.quantities

    >>> getAxis = graph.findPlot.getAxisClassFromValue

    >>> getAxis('counting')
    <class 'music21.graph.axis.CountingAxis'>

    >>> getAxis('pc')
    <class 'music21.graph.axis.PitchClassAxis'>

    >>> print(getAxis('boogie'))
    None
    '''
    for thisAxis in getAxisClasses():
        if axisMatchesValue(thisAxis, axisValue):
            return thisAxis
    return None

def axisMatchesValue(axisClass: type[axis.Axis]|axis.Axis,
                     axisValue: str) -> bool:
    '''
    Returns Bool about whether axisValue.lower() is anywhere in axisClass.quantities

    >>> ax = graph.axis.CountingAxis
    >>> graph.findPlot.axisMatchesValue(ax, 'counting')
    True
    >>> graph.findPlot.axisMatchesValue(ax, 'count')
    True
    >>> graph.findPlot.axisMatchesValue(ax, 'offset')
    False

    Works on an instantiated object as well:

    >>> ax = graph.axis.CountingAxis()
    >>> graph.findPlot.axisMatchesValue(ax, 'counting')
    True
    >>> graph.findPlot.axisMatchesValue(ax, 'flute')
    False

    * Changed in v8: Must send a subclass of axis.Axis or an instance.
        `None` is no longer supported.
    '''
    axisValue = axisValue.lower()
    for v in axisClass.quantities:
        if v.lower() == axisValue:
            return True
    return False

def getPlotsToMake(graphFormat: str|None = None,
                   xValue=None,
                   yValue=None,
                   zValue=None):
    '''
    Returns either a list of plot classes to make if there is a predetermined class

    or a list of tuples where the first element of each tuple is the plot class
    and the second is a dict of {'x': axisXClass, 'y': axisYClass} etc.

    Default is pianoroll

    >>> graph.findPlot.getPlotsToMake()
    [<class 'music21.graph.plot.HorizontalBarPitchSpaceOffset'>]

    >>> graph.findPlot.getPlotsToMake('scatter')
    [<class 'music21.graph.plot.Scatter'>,
     <class 'music21.graph.plot.ScatterPitchClassOffset'>,
     <class 'music21.graph.plot.ScatterPitchClassQuarterLength'>,
     <class 'music21.graph.plot.ScatterPitchSpaceDynamicSymbol'>,
     <class 'music21.graph.plot.ScatterPitchSpaceQuarterLength'>]

    >>> graph.findPlot.getPlotsToMake('scatter', 'offset', 'pitchClass')
    [<class 'music21.graph.plot.ScatterPitchClassOffset'>]

    Try in wrong order:

    >>> graph.findPlot.getPlotsToMake('scatter', 'pitchClass', 'offset')
    [<class 'music21.graph.plot.ScatterPitchClassOffset'>]

    Try giving just one value:

    >>> graph.findPlot.getPlotsToMake('scatter', 'offset')
    [<class 'music21.graph.plot.ScatterPitchClassOffset'>]

    >>> graph.findPlot.getPlotsToMake('scatter', 'ql')  # abbreviation
    [<class 'music21.graph.plot.ScatterPitchClassQuarterLength'>,
     <class 'music21.graph.plot.ScatterPitchSpaceQuarterLength'>]

    Just one value, but it is in the wrong axis:

    >>> graph.findPlot.getPlotsToMake('scatter', 'pitchClass')
    [<class 'music21.graph.plot.ScatterPitchClassOffset'>,
     <class 'music21.graph.plot.ScatterPitchClassQuarterLength'>]

    Create a graph that does not exist:

    >>> graph.findPlot.getPlotsToMake('scatter', 'offset', 'dynamics')
    [(<class 'music21.graph.plot.Scatter'>,
      OrderedDict([('x', <class 'music21.graph.axis.OffsetAxis'>),
                   ('y', <class 'music21.graph.axis.DynamicsAxis'>)]))]

    Just a couple of values:

    >>> graph.findPlot.getPlotsToMake('offset', 'dynamics')
    [(<class 'music21.graph.plot.Scatter'>,
      OrderedDict([('x', <class 'music21.graph.axis.OffsetAxis'>),
                   ('y', <class 'music21.graph.axis.DynamicsAxis'>)]))]

    Just one value:

    >>> graph.findPlot.getPlotsToMake('octave')
    [(<class 'music21.graph.plot.Histogram'>,
      OrderedDict([('x', <class 'music21.graph.axis.PitchSpaceOctaveAxis'>)]))]

    Three values:

    >>> graph.findPlot.getPlotsToMake('offset', 'dynamics', 'count')
    [(<class 'music21.graph.plot.ScatterWeighted'>,
      OrderedDict([('x', <class 'music21.graph.axis.OffsetAxis'>),
                   ('y', <class 'music21.graph.axis.DynamicsAxis'>),
                   ('z', <class 'music21.graph.axis.CountingAxis'>)]))]

    '''
    def _bestPlotType(graphClassesToChooseFrom):
        # now get the best graph type from this possibly motley list
        numAxes = len([1 for val in (xValue, yValue, zValue) if val is not None])
        bestGraphType = ''

        if numAxes == 3:
            bestGraphType = 'scatterweighted'
        elif numAxes == 2:
            bestGraphType = 'scatter'
        elif numAxes == 1:
            bestGraphType = 'histogram'
        innerFilteredClasses = getPlotClassesFromFormat(bestGraphType, graphClassesToChooseFrom)
        if innerFilteredClasses:
            return innerFilteredClasses
        else:
            return graphClassesToChooseFrom

    if [graphFormat, xValue, yValue, zValue] == [None] * 4:
        graphFormat = 'pianoroll'

    graphClasses: list[type[plot.PlotStreamMixin]]
    if graphFormat in PLOTCLASS_SHORTCUTS:
        graphClasses = [PLOTCLASS_SHORTCUTS[graphFormat]]
    else:
        graphClasses = getPlotClassesFromFormat(graphFormat)

    # try as if the args are all values
    if not graphClasses and graphFormat:
        xValue, yValue, zValue = graphFormat, xValue, yValue
        graphFormat = None
        graphClasses = getPlotClasses()  # assume graphFormat is an axis and shift over
    # match values to axes

    graphRemove = []
    for axisLetter, axisValue in (('x', xValue), ('y', yValue), ('z', zValue)):
        for gc in graphClasses:
            if axisValue is None:
                continue
            if axisLetter not in gc.axesClasses:
                graphRemove.append(gc)
                continue
            axisObjClass = gc.axesClasses[axisLetter]
            if not axisMatchesValue(axisObjClass, axisValue):
                graphRemove.append(gc)

    graphClassesFiltered = [x for x in graphClasses if x not in graphRemove]
    if graphClassesFiltered:
        if graphFormat or len(graphClassesFiltered) == 1:
            return graphClassesFiltered
        else:
            return _bestPlotType(graphClassesFiltered)

    # no matches for values.  Try agnostic about X and Y
    graphRemove = []
    for axisLetter, axisValue in (('x', xValue), ('y', yValue), ('z', zValue)):
        for gc in graphClasses:
            if axisValue is None:
                continue
            found = False
            for unused_axisLetter, axisObjClass in gc.axesClasses.items():
                if axisMatchesValue(axisObjClass, axisValue):
                    found = True
                    break

            if not found:
                graphRemove.append(gc)

    graphClassesFiltered = [x for x in graphClasses if x not in graphRemove]
    if graphClassesFiltered:
        if graphFormat or len(graphClassesFiltered) == 1:
            return graphClassesFiltered
        else:
            return _bestPlotType(graphClassesFiltered)

    # if still not found, return a dict with the proper axes

    axisDict = collections.OrderedDict()
    for axisLetter, axisValue in (('x', xValue), ('y', yValue), ('z', zValue)):
        if axisValue is None:
            continue
        axisClass = getAxisClassFromValue(axisValue)
        if axisClass is None:
            continue
        axisDict[axisLetter] = axisClass

    if len(graphClasses) == 1:
        return [(graphClasses[0], axisDict)]
    else:
        filteredClasses = _bestPlotType(graphClasses)

        if filteredClasses:
            return [(filteredClasses[0], axisDict)]
        else:  # we have done our best
            return [(graphClasses[0], axisDict)]
