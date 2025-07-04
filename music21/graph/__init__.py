# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         graph.py
# Purpose:      Classes for graphing in matplotlib and/or other graphing tools.
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#               Evan Lynch
#
# Copyright:    Copyright © 2009-2023 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Tools for graphing, plotting, or otherwise visualizing :class:`~music21.stream.Stream` objects.

The easiest and most common way of using plotting functions is to call
`.plot('typeOfGraph')` on a Stream.  See :meth:`~music21.stream.Stream.plot`.
That method uses tools from the `music21.graph.findPlot` module to map between
names of plots and classes that can show them.

The :class:`~music21.graph.plot.PlotStream`
subclasses in the `music21.graph.plot` module give easy to use
and configurable ways of graphing data and structures in
:class:`~music21.stream.Stream` objects.  These Plot objects use classes from
the `music21.graph.axis` module to automatically extract relevant data for you.

At a lower level, the :class:`~music21.graph.primitives.Graph` subclasses
in the `music21.graph.primitives` modules give abstract fundamental
graphing archetypes using the matplotlib library.  They are to be used when
you already have data extracted on your own but still want to take advantage
of musically-aware axes and scaling.

From highest level to lowest level usage, ways of graphing are as follows:

    1. `streamObj.plot('graphName')`
    2. `graph.plot.Class(streamObj).run()`
    3. `plotter = graph.primitives.Class(); plotter.data = ...; plotter.process()`
    4. Use `matplotlib` directly to create any graph, musical or non-musical.
'''
from __future__ import annotations

__all__ = [
    'axis', 'findPlot', 'plot', 'primitives', 'utilities',
    'plotStream',
]

import typing as t
from music21 import common
from music21 import environment

from music21.graph import axis
from music21.graph import findPlot
from music21.graph import plot
from music21.graph import primitives
from music21.graph import utilities

if t.TYPE_CHECKING:
    from music21 import stream

environLocal = environment.Environment('graph')

def plotStream(
    streamObj: stream.Stream,
    graphFormat: str|None = None,
    xValue=None,
    yValue=None,
    zValue=None,
    **keywords,
):
    '''
    Given a stream and any keyword configuration arguments, create and display a plot.

    Note: plots require matplotlib to be installed.

    Plot methods can be specified as additional arguments or by keyword.
    Two keyword arguments can be given: `format` and `values`.
    If positional arguments are given, the first is taken as `format`
    and the rest are collected as `values`. If `format` is the class
    name, that class is collected. Additionally, every
    :class:`~music21.graph.PlotStream` subclass defines one `format`
    string and a list of `values` strings. The `format` parameter
    defines the type of Graph (e.g. scatter, histogram, colorGrid). The
    `values` list defines what values are graphed
    (e.g. quarterLength, pitch, pitchClass).

    If a user provides a `format` and one or more `values` strings, a plot with
    the corresponding profile, if found, will be generated. If not, the first
    Plot to match any of the defined specifiers will be created.

    In the case of :class:`~music21.graph.PlotWindowedAnalysis` subclasses,
    the :class:`~music21.analysis.discrete.DiscreteAnalysis`
    subclass :attr:`~music21.analysis.discrete.DiscreteAnalysis.identifiers` list
    is added to the Plot's `values` list.

    Available plots include the following:

    * :class:`~music21.graph.plot.HistogramPitchSpace`
    * :class:`~music21.graph.plot.HistogramPitchClass`
    * :class:`~music21.graph.plot.HistogramQuarterLength`
    * :class:`~music21.graph.plot.ScatterPitchSpaceQuarterLength`
    * :class:`~music21.graph.plot.ScatterPitchClassQuarterLength`
    * :class:`~music21.graph.plot.ScatterPitchClassOffset`
    * :class:`~music21.graph.plot.ScatterPitchSpaceDynamicSymbol`
    * :class:`~music21.graph.plot.HorizontalBarPitchSpaceOffset`
    * :class:`~music21.graph.plot.HorizontalBarPitchClassOffset`
    * :class:`~music21.graph.plot.ScatterWeightedPitchSpaceQuarterLength`
    * :class:`~music21.graph.plot.ScatterWeightedPitchClassQuarterLength`
    * :class:`~music21.graph.plot.ScatterWeightedPitchSpaceDynamicSymbol`
    * :class:`~music21.graph.plot.Plot3DBarsPitchSpaceQuarterLength`
    * :class:`~music21.graph.plot.WindowedKey`
    * :class:`~music21.graph.plot.WindowedAmbitus`
    * :class:`~music21.graph.plot.Dolan`

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> thePlot = s.plot('histogram', 'pitch', doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW thePlot = s.plot('histogram', 'pitch')

    .. image:: images/HistogramPitchSpace.*
        :width: 600

    >>> s = corpus.parse('bach/bwv324.xml') #_DOCS_HIDE
    >>> thePlot = s.plot('pianoroll', doneAction=None) #_DOCS_HIDE
    >>> #_DOCS_SHOW s = corpus.parse('bach/bwv57.8')
    >>> #_DOCS_SHOW thePlot = s.plot('pianoroll')

    .. image:: images/HorizontalBarPitchSpaceOffset.*
        :width: 600

    '''
    plotMake = findPlot.getPlotsToMake(graphFormat, xValue, yValue, zValue)
    # environLocal.printDebug(['plotClassName found', plotMake])

    obj = None
    for plotInfo in plotMake:
        if not common.isIterable(plotInfo):
            plotClassName = plotInfo
            plotDict = None
        else:
            plotClassName, plotDict = plotInfo
        obj = plotClassName(streamObj, **keywords)
        if plotDict:
            for axisName, axisClass in plotDict.items():
                attrName = 'axis' + axisName.upper()
                setattr(obj, attrName, axisClass(obj, axisName))
        obj.run()

    return obj  # just last one

# ------------------------------------------------------------------------------

# -----------------------------------------------------------------------------
_DOC_ORDER = [plotStream]

# -----------------------------------------------------------------------------

# , runTest='testPlot3DPitchSpaceQuarterLengthCount')
