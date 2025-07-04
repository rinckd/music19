# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         scala/__init__.py
# Purpose:      Interface and representation of Scala scale files
#
# Authors:      Christopher Ariza
#
# Copyright:    Copyright © 2010-22 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
# noinspection SpellCheckingInspection
'''
This module defines classes for representing Scala scale data,
including Scala pitch representations, storage, and files.

The Scala format is defined at the following URL:
https://www.huygens-fokker.org/scala/scl_format.html

We thank Manuel Op de Coul for allowing us to include
the repository (as of May 11, 2011) with music21

Scala files are encoded as latin-1 (ISO-8859) text

Utility functions are also provided to search and find
scales in the Scala scale archive. File names can be found
with the :func:`~music21.scala.search` function.

To create a :class:`~music21.scale.ScalaScale` instance, simply
provide a root pitch and the name of the scale. Scale names are given as
the scala .scl filename.

>>> mbiraScales = scale.scala.search('mbira')
>>> mbiraScales
['mbira_banda.scl', 'mbira_banda2.scl', 'mbira_gondo.scl', 'mbira_kunaka.scl',
 'mbira_kunaka2.scl', 'mbira_mude.scl', 'mbira_mujuru.scl', 'mbira_zimb.scl']

For most people you'll want to do something like this:

>>> sc = scale.ScalaScale('a4', 'mbira_banda.scl')
>>> [str(p) for p in sc.pitches]
['A4', 'B4(-15c)', 'C#5(-11c)', 'E-5(-7c)', 'E~5(+6c)', 'F#5(+14c)', 'G~5(+1c)', 'B-5(+2c)']
'''
from __future__ import annotations

import io
import math
import os
import pathlib
import typing as t
from music21 import common
from music21 import environment
from music21 import interval

# scl is the library of scala files
from music21.scale.scala import scl

environLocal = environment.Environment('scale.scala')

# ------------------------------------------------------------------------------
# global variable to cache the paths returned from getPaths()
SCALA_PATHS: dict[str, dict[str, list[str]]|None] = {'allPaths': None}

def getPaths():
    '''
    Get all scala scale paths. This is called once or the module and
    cached as SCALA_PATHS, which should be used instead of calls to this function.

    >>> a = scale.scala.getPaths()
    >>> len(a) >= 3800
    True
    '''
    if SCALA_PATHS['allPaths'] is not None:
        return SCALA_PATHS['allPaths']
    moduleName = scl
    if not hasattr(moduleName, '__path__'):
        # when importing a package name (a directory) the moduleName
        # may be a list of all paths contained within the package
        # this seems to be dependent on the context of the call:
        # from the command line is different from calling from the interpreter
        dirListing = moduleName
    else:
        # returns a list with one or more paths
        # the first is the path to the directory that contains xml files
        directory = moduleName.__path__[0]
        dirListing = [os.path.join(directory, x) for x in sorted(os.listdir(directory))]

    paths = {}  # return a dictionary with keys and list of alternate names
    for fp in dirListing:
        if fp.endswith('.scl'):
            paths[fp] = []
            # store alternative name representations
            # store version with no extension
            directory, fn = os.path.split(fp)
            fn = fn.replace('.scl', '')
            paths[fp].append(fn)
            # store version with removed underscores
            directory, fn = os.path.split(fp)
            fn = fn.lower()
            fn = fn.replace('.scl', '')
            fn = fn.replace('_', '')
            fn = fn.replace('-', '')
            paths[fp].append(fn)
    SCALA_PATHS['allPaths'] = paths
    return paths

# ------------------------------------------------------------------------------
class ScalaPitch:
    '''
    Representation of a scala pitch notation

    >>> sp = scale.scala.ScalaPitch(' 1066.667 cents')
    >>> print(sp.parse())
    1066.667

    >>> sp = scale.scala.ScalaPitch(' 2/1')
    >>> sp.parse()
    1200.0
    >>> sp.parse('100.0 C#')
    100.0
    >>> [sp.parse(x) for x in ['89/84', '55/49', '44/37', '63/50', '4/3', '99/70', '442/295',
    ...     '27/17', '37/22', '98/55', '15/8', '2/1']]
    [100.0992..., 199.9798..., 299.9739..., 400.10848..., 498.04499...,
     600.0883..., 699.9976..., 800.9095..., 900.0260...,
     1000.0201..., 1088.2687..., 1200.0]
    '''
    # pitch values; if it has a period, it is cents.  Otherwise, it is a ratio
    # above the implied base ratio
    # integer values w/ no period or slash: 2 is 2/1
    def __init__(self, sourceString=None):

        self.src = None
        if sourceString is not None:
            self._setSrc(sourceString)

        # resole all values into cents shifts
        self.cents = None

    def _setSrc(self, raw):
        raw = raw.strip()
        # get decimals and fractions
        raw, junk = common.getNumFromStr(raw, numbers='0123456789./')
        self.src = raw.strip()

    def parse(self, sourceString=None):
        '''
        Parse the source string and set self.cents.
        '''
        if sourceString is not None:
            self._setSrc(sourceString)

        if '.' in self.src:  # cents
            self.cents = float(self.src)
        else:  # it is a ratio
            if '/' in self.src:
                n, d = self.src.split('/')
                n, d = float(n), float(d)
            else:
                n = float(self.src)
                d = 1.0
            # http://www.sengpielaudio.com/calculator-centsratio.htm
            self.cents = 1200.0 * math.log((n / d), 2)
        return self.cents

class ScalaData:
    # noinspection SpellCheckingInspection
    '''
    Object representation of data stored in a Scala scale file. This object is used to
    access Scala information stored in a file. To create a music21 scale with a Scala file,
    use :class:`~music21.scale.ScalaScale`.

    This is not called ScalaScale, as this name clashes with the
    :class:`~music21.scale.ScalaScale` that uses this object.

    >>> import os
    >>> sf = scale.scala.ScalaFile()
    >>> fp = common.getSourceFilePath() / 'scale' / 'scala' / 'scl' / 'tanaka.scl'
    >>> sf.open(fp)
    >>> sd = sf.read()

    ScaleFile descriptions are converted to unicode.

    >>> print(sd.description)
    26-note choice system of Shohé Tanaka, Studien i.G.d. reinen Stimmung (1890)
    >>> sd.pitchCount
    26

    Distances from the tonic:

    >>> cat = sd.getCentsAboveTonic()
    >>> len(cat)
    26
    >>> list(int(round(x)) for x in cat[0:4])
    [71, 92, 112, 182]
    >>> sd.pitchValues[0]
    <music21.scale.scala.ScalaPitch object at 0x10b16fac8>
    >>> sd.pitchValues[0].cents
    70.6724...

    This will not add up with centsAboveTonic above, due to rounding

    >>> adj = sd.getAdjacentCents()
    >>> list(int(round(x)) for x in adj[0:4])
    [71, 22, 20, 71]

    Interval Sequences

    >>> intSeq = sd.getIntervalSequence()
    >>> intSeq[0:4]
    [<music21.interval.Interval m2 (-29c)>,
     <music21.interval.Interval P1 (+22c)>,
     <music21.interval.Interval P1 (+20c)>,
     <music21.interval.Interval m2 (-29c)>]

    Tweak the file and be ready to write it back out:

    >>> sd.pitchValues[0].cents = 73.25
    >>> sd.fileName = 'tanaka2.scl'
    >>> sd.description = 'Tweaked version of tanaka.scl'
    >>> fs = sd.getFileString()
    >>> print(fs)
    ! tanaka2.scl
    !
    Tweaked version of tanaka.scl
    26
    !
    73.25
    92.17...
    111.73...
    182.40...

    Be sure to reencode `fs` as `latin-1` before writing to disk.

    >>> sf.close()
    '''
    def __init__(self, sourceString=None, fileName=None):
        self.src = sourceString
        self.fileName = fileName  # store source file name

        # added in parsing:
        self.description = None

        # lower limit is 0, as degree 0, or the 1/1 ratio, is implied
        # assumes octave equivalence?
        self.pitchCount = None  # number of lines w/ pitch values will follow
        self.pitchValues = []

    def parse(self):
        '''
        Parse a scala file delivered as a long string with line breaks
        '''
        lines = self.src.split('\n')
        count = 0  # count non-comment lines
        for i, line in enumerate(lines):
            line = line.strip()
            # environLocal.printDebug(['line', line, self.fileName, i])
            if line.startswith('!'):
                if i == 0 and self.fileName is None:
                    # try to get from first line
                    if '.scl' in line:  # it has got the file name
                        self.fileName = line[1:].strip()  # remove leading !
                continue  # comment
            else:
                count += 1
            if count == 1:
                if line != '':  # may be empty
                    self.description = line
            elif count == 2:
                if line != '':
                    self.pitchCount = int(line)
            else:  # remaining counts are pitches
                if line != '':
                    sp = ScalaPitch(line)
                    sp.parse()
                    self.pitchValues.append(sp)

    def getCentsAboveTonic(self):
        '''
        Return a list of cent values above the implied tonic.
        '''
        return [sp.cents for sp in self.pitchValues]

    def getAdjacentCents(self):
        '''
        Get cents values between adjacent intervals.
        '''
        post = []
        location = 0
        for c in self.getCentsAboveTonic():
            dif = c - location
            # environLocal.printDebug(['getAdjacentCents', 'c',
            #                           c, 'location', location, 'dif', dif])
            post.append(dif)
            location = c  # set new location
        return post

    def setAdjacentCents(self, centList):
        '''
        Given a list of adjacent cent values, create the necessary ScalaPitch
        objects and update them
        '''
        self.pitchValues = []
        location = 0
        for c in centList:
            sp = ScalaPitch()
            sp.cents = location + c
            location = sp.cents
            self.pitchValues.append(sp)
        self.pitchCount = len(self.pitchValues)

    def getIntervalSequence(self):
        '''
        Get the scale as a list of Interval objects.
        '''
        post = []
        for c in self.getAdjacentCents():
            # convert cent values to semitone values to create intervals
            post.append(interval.Interval(c * 0.01))
        return post

    def setIntervalSequence(self, iList):
        '''
        Set the scale from a list of Interval objects.
        '''
        self.pitchValues = []
        location = 0
        for i in iList:
            # convert cent values to semitone values to create intervals
            sp = ScalaPitch()
            sp.cents = location + i.cents
            location = sp.cents
            self.pitchValues.append(sp)
        self.pitchCount = len(self.pitchValues)

    def getFileString(self):
        '''
        Return a unicode-string suitable for writing a Scala file

        The unicode string should be encoded in Latin-1 for maximum
        Scala compatibility.
        '''
        msg = []
        if self.fileName is not None:
            msg.append(f'! {self.fileName}')
        # conventional to add a comment space
        msg.append('!')

        if self.description is not None:
            msg.append(self.description)
        else:  # must supply empty line
            msg.append('')

        if self.pitchCount is not None:
            msg.append(str(self.pitchCount))
        else:  # must supply empty line
            msg.append('')

        # conventional to add a comment space
        msg.append('!')
        for sp in self.pitchValues:
            msg.append(str(sp.cents))
        # add space
        msg.append('')

        return '\n'.join(msg)

# ------------------------------------------------------------------------------
class ScalaFile:
    '''
    Interface for reading and writing scala files.
    On reading, returns a :class:`~music21.scala.ScalaData` object.

    >>> import os
    >>> sf = scale.scala.ScalaFile()
    >>> fp = common.getSourceFilePath() / 'scale' / 'scala' / 'scl' / 'tanaka.scl'
    >>> sf.open(fp)
    >>> sd = sf.read()
    >>> sd
    <music21.scale.scala.ScalaData object at 0x10b170e10>
    >>> sd is sf.data
    True
    >>> sf.fileName.endswith('tanaka.scl')
    True
    >>> sd.pitchCount
    26
    >>> sf.close()
    '''

    def __init__(self, data=None):
        self.fileName = None
        self.file = None
        # store data source if provided
        self.data = data

    def open(self, fp, mode='r'):
        '''
        Open a file for reading
        '''
        self.file = io.open(fp, mode, encoding='latin-1')  # pylint: disable=consider-using-with
        self.fileName = os.path.basename(fp)

    def openFileLike(self, fileLike):
        '''
        Assign a file-like object, such as those provided by StringIO, as an open file object.
        '''
        self.file = fileLike  # already 'open'

    def __repr__(self):
        r = '<ScalaFile>'
        return r

    def close(self):
        self.file.close()

    def read(self):
        '''
        Read a file. Note that this calls readstr, which processes all tokens.

        If `number` is given, a work number will be extracted if possible.
        '''
        return self.readstr(self.file.read())

    def readstr(self, strSrc):
        '''
        Read a string and process all Tokens. Returns a ABCHandler instance.
        '''
        ss = ScalaData(strSrc, self.fileName)
        ss.parse()
        self.data = ss
        return ss

    def write(self):
        ws = self.writestr()
        self.file.write(ws)

    def writestr(self):
        if isinstance(self.data, ScalaData):
            return self.data.getFileString()
        # handle Scale or other objects

# ------------------------------------------------------------------------------
def parse(target):
    # noinspection SpellCheckingInspection, PyShadowingNames
    '''
    Get a :class:`~music21.scala.ScalaData` object from
    the bundled SCL archive or a file path.

    >>> ss = scale.scala.parse('balafon6')
    >>> ss.description
    'Observed balafon tuning from Burma, Helmholtz/Ellis p. 518, nr.84'
    >>> [str(i) for i in ss.getIntervalSequence()]
    ['<music21.interval.Interval m2 (+14c)>', '<music21.interval.Interval M2 (+36c)>',
    '<music21.interval.Interval M2>', '<music21.interval.Interval m2 (+37c)>',
    '<music21.interval.Interval M2 (-49c)>', '<music21.interval.Interval M2 (-6c)>',
    '<music21.interval.Interval M2 (-36c)>']

    >>> scale.scala.parse('incorrectFileName.scl') is None
    True

    >>> ss = scale.scala.parse('barbourChrom1')
    >>> print(ss.description)
    Barbour's #1 Chromatic
    >>> ss.fileName
    'barbour_chrom1.scl'

    >>> ss = scale.scala.parse('blackj_gws.scl')
    >>> ss.description
    'Detempered Blackjack in 1/4 kleismic marvel tuning'
    '''
    match = None

    if isinstance(target, pathlib.Path):
        target = str(target)
    # this may be a file path to a scala file
    if os.path.exists(target) and target.endswith('.scl'):
        match = target

    # try from stored collections
    # remove any spaces
    target = target.replace(' ', '')
    if match is None:
        for fp in getPaths():
            unused_directory, fn = os.path.split(fp)
            # try exact match
            if target.lower() == fn.lower():
                match = fp
                break

    # try again, from cached reduced expressions
    if match is None:
        for fp in getPaths():
            # look at alternative names
            for alt in getPaths()[fp]:
                if target.lower() == alt:
                    match = fp
                    break
    if match is None:
        # accept partial matches
        for fp in getPaths():
            # look at alternative names
            for alt in getPaths()[fp]:
                if target.lower() in alt:
                    match = fp
                    break

    # might put this in a try block
    if match is not None:
        sf = ScalaFile()
        sf.open(match)
        ss = sf.read()
        sf.close()
        return ss

def search(target):
    # noinspection SpellCheckingInspection
    '''
    Search the scala archive for matches based on a string

    >>> mbiraScales = scale.scala.search('mbira')
    >>> mbiraScales
    ['mbira_banda.scl', 'mbira_banda2.scl', 'mbira_gondo.scl', 'mbira_kunaka.scl',
     'mbira_kunaka2.scl', 'mbira_mude.scl', 'mbira_mujuru.scl', 'mbira_zimb.scl']
    '''
    match = []
    # try from stored collections
    # remove any spaces
    target = target.replace(' ', '')
    for fp in getPaths():
        unused_directory, fn = os.path.split(fp)
        # try exact match
        if target.lower() == fn.lower():
            if fp not in match:
                match.append(fp)

    # accept partial matches
    for fp in getPaths():
        # look at alternative names
        for alt in getPaths()[fp]:
            if target.lower() in alt:
                if fp not in match:
                    match.append(fp)
    names = []
    for fp in match:
        names.append(os.path.basename(fp))
    names.sort()
    return names

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER: list[type] = []

if __name__ == '__main__':
    # sys.arg test options will be used in mainTest()
    import music21
    music21.mainTest(Test)
