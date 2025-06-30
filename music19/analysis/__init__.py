# -*- coding: utf-8 -*-
from __future__ import annotations

__all__ = [
    'correlate', 'discrete', 'elements', 'enharmonics',
    'floatingKey', 'harmonicFunction', 'metrical', 'neoRiemannian',
    'patel', 'pitchAnalysis',
    'reduceChords', 'reduceChordsOld', 'reduction', 'segmentByRests',
    'transposition', 'windowed',
    'AnalysisException',
]

# this is necessary to get these names available with a
# from music19 import * import statement
from music19.analysis import correlate
from music19.analysis import discrete
from music19.analysis import elements
from music19.analysis import enharmonics
from music19.analysis import floatingKey
from music19.analysis import harmonicFunction
from music19.analysis import metrical
from music19.analysis import neoRiemannian
from music19.analysis import patel
from music19.analysis import pitchAnalysis
from music19.analysis import reduceChords
from music19.analysis import reduceChordsOld
from music19.analysis import reduction
from music19.analysis import segmentByRests
from music19.analysis import transposition
from music19.analysis import windowed

from music19.exceptions21 import AnalysisException

