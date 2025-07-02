# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         converter/__init__.py
# Purpose:      Provide a common way to create Streams from any data music21
#               handles
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2015 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
music21.converter contains tools for loading music from various file formats,
whether from disk, from the web, or from text, into
music21.stream.:class:`~music21.stream.Score` objects (or
other similar stream objects).

The most powerful and easy to use tool is the :func:`~music21.converter.parse`
function. Simply provide a filename, URL, or text string and, if the format
is supported, a :class:`~music21.stream.Score` will be returned.

This is the most general, public interface for all formats.  Programmers
adding their own formats to the system should provide an interface here to
their own parsers (such as humdrum, musicxml, etc.)

The second and subsequent times that a file is loaded it will likely be much
faster since we store a parsed version of each file as a "pickle" object in
the temp folder on the disk.

>>> #_DOCS_SHOW s = converter.parse('d:/myDocs/schubert.krn')
>>> s = converter.parse(humdrum.testFiles.schubert) #_DOCS_HIDE
>>> s
<music21.stream.Score ...>
'''
from __future__ import annotations

from collections import deque
import copy
from http.client import responses
import io
from math import isclose
import os
import re
import pathlib
import sys
import types
import typing as t
import unittest
import zipfile

import requests

from music21.converter import subConverters
from music21.converter import museScore

from music21 import _version
from music21 import common
from music21 import environment
from music21 import exceptions21
from music21 import metadata
from music21 import stream
from music21.metadata import bundles

if t.TYPE_CHECKING:
    from music21 import base

__all__ = [
    'subConverters', 'museScore',
    'ArchiveManagerException', 'PickleFilterException',
    'ConverterException', 'ConverterFileException',
    'ArchiveManager', 'PickleFilter', 'resetSubConverters',
    'registerSubConverter', 'unregisterSubConverter',
    'Converter', 'parseFile', 'parseData', 'parseURL',
    'parse', 'freeze', 'thaw', 'freezeStr', 'thawStr',

]

environLocal = environment.Environment('converter')

_StrOrBytes = t.TypeVar('_StrOrBytes', bound=str|bytes)

# ------------------------------------------------------------------------------
class ArchiveManagerException(exceptions21.Music21Exception):
    pass

class PickleFilterException(exceptions21.Music21Exception):
    pass

class ConverterException(exceptions21.Music21Exception):
    pass

class ConverterFileException(exceptions21.Music21Exception):
    pass

# ------------------------------------------------------------------------------
class ArchiveManager:
    r'''
    Before opening a file path, this class can check if this is an
    archived file collection, such as a .zip or .mxl file. This will return the
    data from the archive.

    >>> fnCorpus = corpus.getWork('bwv66.6', fileExtensions=('.xml',))

    This is likely a unicode string

    >>> #_DOCS_SHOW fnCorpus
    >>> '/Users/cuthbert/git/music21base/music21/corpus/bach/bwv66.6.mxl' #_DOCS_HIDE
    '/Users/cuthbert/git/music21base/music21/corpus/bach/bwv66.6.mxl'
    >>> am = converter.ArchiveManager(fnCorpus)
    >>> am.isArchive()
    True
    >>> am.getNames()
    ['bwv66.6.xml', 'META-INF/container.xml']
    >>> data = am.getData()
    >>> data[0:70]
    '<?xml version="1.0" encoding="UTF-8"?>\r<!DOCTYPE score-partwise PUBLIC'

    The only archive type supported now is zip. But .mxl is zip so that covers almost
    everything.
    '''
    # for info on mxl files, see
    # http://www.recordare.com/xml/compressed-mxl.html

    def __init__(self, fp: str|pathlib.Path, archiveType='zip'):
        self.fp: pathlib.Path = common.cleanpath(fp, returnPathlib=True)
        self.archiveType: str = archiveType

    def isArchive(self) -> bool:
        '''
        Return True or False if the filepath is an
        archive of the supplied archiveType.
        '''
        if self.archiveType == 'zip':
            # some .md files can be zipped
            if self.fp.suffix in ('.mxl', '.md'):
                # try to open it, as some mxl files are not zips
                try:
                    with zipfile.ZipFile(self.fp, 'r') as unused:
                        pass
                except zipfile.BadZipfile:
                    return False
                return True
            elif self.fp.suffix == '.zip':
                return True
        else:
            raise ArchiveManagerException(f'no support for archiveType: {self.archiveType}')
        return False

    def getNames(self) -> list[str]:
        '''
        Return a list of all names contained in this archive.
        '''
        post: list[str] = []
        if self.archiveType == 'zip':
            with zipfile.ZipFile(self.fp, 'r') as f:
                for subFp in f.namelist():
                    post.append(subFp)
        return post

    def getData(self, dataFormat='musicxml') -> t.Any:
        '''
        Return data from the archive.

        For 'musicxml' this will be a single string.

        * Changed in v8: name is not used.
        '''
        post = None
        if self.archiveType != 'zip':
            raise ArchiveManagerException(f'no support for extension: {self.archiveType}')

        with zipfile.ZipFile(self.fp, 'r') as f:
            post = self._extractContents(f, dataFormat)

        return post

    def _extractContents(self,
                         f: zipfile.ZipFile,
                         dataFormat: str = 'musicxml') -> t.Any:
        post: t.Any = None
        if dataFormat == 'musicxml':  # try to auto-harvest
            # will return data as a string
            # note that we need to read the META-INF/container.xml file
            # and get the root file full-path
            # a common presentation will be like this:
            # ['musicXML.xml', 'META-INF/', 'META-INF/container.xml']
            for subFp in f.namelist():
                # the name musicXML.xml is often used, or get top level
                # xml file
                if 'META-INF' in subFp:
                    continue
                # include .mxl to be kind to users who zipped up mislabeled files
                if pathlib.Path(subFp).suffix not in ['.musicxml', '.xml', '.mxl']:
                    continue

                post = f.read(subFp)
                if isinstance(post, bytes):
                    foundEncoding = re.match(br"encoding=[\'\"](\S*?)[\'\"]", post[:1000])
                    if foundEncoding:
                        defaultEncoding = foundEncoding.group(1).decode('ascii')
                        # print('FOUND ENCODING: ', defaultEncoding)
                    else:
                        defaultEncoding = 'UTF-8'
                    try:
                        post = post.decode(encoding=defaultEncoding)
                    except UnicodeDecodeError:  # sometimes windows written
                        post = post.decode(encoding='utf-16-le')
                        post = re.sub(r"encoding=([\'\"]\S*?[\'\"])",
                                      "encoding='UTF-8'", post)

                break

        return post

# ------------------------------------------------------------------------------
class PickleFilter:
    '''
    Before opening a file path, this class checks to see if there is an up-to-date
    version of the file pickled and stored in the scratch directory.

    If forceSource is True, then a pickle path will not be created.

    Provide a file path to check if there is pickled version.

    If forceSource is True, pickled files, if available, will not be
    returned.
    '''

    def __init__(self,
                 fp: str|pathlib.Path,
                 forceSource: bool = False,
                 number: int|None = None,
                 # quantizePost: bool = False,
                 # quarterLengthDivisors: Iterable[int]|None = None,
                 **keywords):
        self.fp: pathlib.Path = common.cleanpath(fp, returnPathlib=True)
        self.forceSource: bool = forceSource
        self.number: int|None = number
        self.keywords: dict[str, t.Any] = keywords
        # environLocal.printDebug(['creating pickle filter'])

    def getPickleFp(self,
                    directory: pathlib.Path|str|None = None,
                    zipType: str|None = None) -> pathlib.Path:
        '''
        Returns the file path of the pickle file for this file.

        Returns a pathlib.Path
        '''
        pathLibDirectory: pathlib.Path
        if directory is None:
            pathLibDirectory = environLocal.getRootTempDir()  # pathlibPath
        elif isinstance(directory, str):
            pathLibDirectory = pathlib.Path(directory)
        else:
            pathLibDirectory = directory

        if zipType is None:
            extension = '.p'
        else:
            extension = '.p.gz'

        pythonVersion = 'py' + str(sys.version_info.major) + '.' + str(sys.version_info.minor)

        pathNameToParse = str(self.fp)

        quantization: list[str] = []
        if 'quantizePost' in self.keywords and self.keywords['quantizePost'] is False:
            quantization.append('noQtz')
        elif 'quarterLengthDivisors' in self.keywords:
            for divisor in self.keywords['quarterLengthDivisors']:
                quantization.append('qld' + str(divisor))

        baseName = '-'.join(['m21', _version.__version__, pythonVersion, *quantization,
                             common.getMd5(pathNameToParse)])

        if self.number is not None:
            baseName += '-' + str(self.number)
        baseName += extension

        return pathLibDirectory / baseName

    def removePickle(self) -> None:
        '''
        If a compressed pickled file exists, remove it from disk.

        Generally not necessary to call, since we can just overwrite obsolete pickles,
        but useful elsewhere.
        '''
        pickleFp = self.getPickleFp(zipType='gz')  # pathlib
        if pickleFp.exists():
            os.remove(pickleFp)

    def status(self) -> tuple[pathlib.Path, bool, pathlib.Path|None]:
        '''
        Given a file path specified with __init__, look for an up-to-date pickled
        version of this file path. If it exists, return its fp, otherwise return the
        original file path.

        Return arguments are file path to load, boolean whether to write a pickle, and
        the file path of the pickle.  All file paths can be pathlib.Path objects or None

        Does not check that fp exists or create the pickle file.

        >>> fp = '/Users/Cuthbert/Desktop/musicFile.mxl'
        >>> pickFilter = converter.PickleFilter(fp)
        >>> #_DOCS_SHOW pickFilter.status()
        (PosixPath('/Users/Cuthbert/Desktop/musicFile.mxl'), True,
              PosixPath('/tmp/music21/m21-7.0.0-py3.9-18b8c5a5f07826bd67ea0f20462f0b8d.p.gz'))
        '''
        fpScratch = environLocal.getRootTempDir()
        m21Format = common.findFormatFile(self.fp)

        if m21Format == 'pickle':  # do not pickle a pickle
            if self.forceSource:
                raise PickleFilterException(
                    'cannot access source file when only given a file path to a pickled file.')
            writePickle = False  # cannot write pickle if no scratch dir
            fpLoad = self.fp
            fpPickle = None
        elif fpScratch is None or self.forceSource:
            writePickle = False  # cannot write pickle if no scratch dir
            fpLoad = self.fp
            fpPickle = None
        else:  # see which is more up to date
            fpPickle = self.getPickleFp(fpScratch, zipType='gz')  # pathlib Path
            if not fpPickle.exists():
                writePickle = True  # if pickled file does not exist
                fpLoad = self.fp
            else:
                if self.fp.stat().st_mtime < fpPickle.stat().st_mtime:
                    # pickle is most recent
                    writePickle = False
                    fpLoad = fpPickle
                else:  # file is most recent
                    writePickle = True
                    fpLoad = self.fp
        return fpLoad, writePickle, fpPickle

# ------------------------------------------------------------------------------
# a deque of additional subConverters to use (in addition to the default ones)
_registeredSubConverters: deque[type[subConverters.SubConverter]] = deque()

# default subConverters to skip
_deregisteredSubConverters: deque[
    type[subConverters.SubConverter]|t.Literal['all']
] = deque()

def resetSubConverters():
    '''
    Reset state to default (removing all registered and deregistered subConverters).
    '''
    _registeredSubConverters.clear()
    _deregisteredSubConverters.clear()

def registerSubConverter(newSubConverter: type[subConverters.SubConverter]) -> None:
    '''
    Add a SubConverter to the list of registered subConverters.

    Example, register a converter for the obsolete Amiga composition software Sonix (so fun!)

    >>> class ConverterSonix(converter.subConverters.SubConverter):
    ...    registerFormats = ('sonix',)
    ...    registerInputExtensions = ('mus',)

    >>> converter.registerSubConverter(ConverterSonix)
    >>> scf = converter.Converter().getSubConverterFormats()
    >>> for x in sorted(scf):
    ...     x, scf[x]
    ('abc', <class 'music21.converter.subConverters.ConverterABC'>)
    ...
    ('sonix', <class 'music21.ConverterSonix'>)
    ...

    See `converter.qmConverter` for an example of an extended subConverter.

    >>> converter.resetSubConverters() #_DOCS_HIDE

    Changed in v.9 -- custom subConverters are registered above default subConverters.
    '''
    _registeredSubConverters.appendleft(newSubConverter)

@common.deprecated('v9', 'v10', 'use unregisterSubconverter with capital C')
def registerSubconverter(
    newSubConverter: type[subConverters.SubConverter]
) -> None:  # pragma: no cover
    '''
    Deprecated: use registerSubConverter w/ capital "C" instead.
    '''
    registerSubConverter(newSubConverter)

def unregisterSubConverter(
    removeSubConverter: t.Literal['all']|type[subConverters.SubConverter]
) -> None:
    # noinspection PyShadowingNames
    '''
    Remove a SubConverter from the list of registered subConverters.

    >>> converter.resetSubConverters() #_DOCS_HIDE
    >>> mxlConverter = converter.subConverters.ConverterMusicXML

    >>> c = converter.Converter()
    >>> mxlConverter in c.subConvertersList()
    True
    >>> converter.unregisterSubConverter(mxlConverter)
    >>> mxlConverter in c.subConvertersList()
    False

    If there is no such subConverter registered, and it is not a default subConverter,
    then a converter.ConverterException is raised:

    >>> class ConverterSonix(converter.subConverters.SubConverter):
    ...    registerFormats = ('sonix',)
    ...    registerInputExtensions = ('mus',)
    >>> converter.unregisterSubConverter(ConverterSonix)
    Traceback (most recent call last):
    music21.converter.ConverterException: Could not remove <class 'music21.ConverterSonix'> from
                registered subConverters

    The special command "all" removes everything including the default converters:

    >>> converter.unregisterSubConverter('all')
    >>> c.subConvertersList()
    []

    >>> converter.resetSubConverters() #_DOCS_HIDE
    '''
    if removeSubConverter == 'all':
        _registeredSubConverters.clear()
        _deregisteredSubConverters.clear()
        _deregisteredSubConverters.append('all')
        return

    try:
        _registeredSubConverters.remove(removeSubConverter)
    except ValueError:
        c = Converter()
        dsc = c.defaultSubConverters()
        if removeSubConverter in dsc:
            _deregisteredSubConverters.append(removeSubConverter)
        else:
            raise ConverterException(
                f'Could not remove {removeSubConverter!r} from registered subConverters')

@common.deprecated('v9', 'v10', 'use unregisterSubConverter with capital C')
def unregisterSubconverter(
    newSubConverter: type[subConverters.SubConverter]
) -> None:  # pragma: no cover
    '''
    Deprecated: use unregisterSubConverter w/ capital "C" instead.
    '''
    unregisterSubConverter(newSubConverter)

# ------------------------------------------------------------------------------
class Converter:
    '''
    A class used for converting all supported data formats into music21 objects.

    Not a subclass, but a wrapper for different converter objects based on format.
    '''
    _DOC_ATTR: dict[str, str] = {
        'subConverter':
            '''
            a :class:`~music21.converter.subConverters.SubConverter` object
            that will do the actual converting.
            ''',
    }

    def __init__(self) -> None:
        self.subConverter: subConverters.SubConverter|None = None
        # a stream object unthawed
        self._thawedStream: stream.Score|stream.Part|stream.Opus|None = None

    def _getDownloadFp(
        self,
        directory: pathlib.Path|str,
        ext: str,
        url: str,
    ):
        directoryPathlib: pathlib.Path
        if isinstance(directory, str):
            directoryPathlib = pathlib.Path(directory)
        else:
            directoryPathlib = directory

        filename = 'm21-' + _version.__version__ + '-' + common.getMd5(url) + ext
        return directoryPathlib / filename

    # pylint: disable=redefined-builtin
    # noinspection PyShadowingBuiltins
    def parseFileNoPickle(
        self,
        fp: pathlib.Path|str,
        number: int|None = None,
        format: str|None = None,
        forceSource: bool = False,
        **keywords
    ):
        '''
        Given a file path, parse and store a music21 Stream.

        If format is None then look up the format from the file
        extension using `common.findFormatFile`.

        Does not use or store pickles in any circumstance.
        '''
        fpPathlib: pathlib.Path = common.cleanpath(fp, returnPathlib=True)
        # environLocal.printDebug(['attempting to parseFile', fp])
        if not fpPathlib.exists():
            raise ConverterFileException(f'no such file exists: {fp}')
        useFormat = format

        if useFormat is None:
            useFormat = self.getFormatFromFileExtension(fpPathlib)
        self.setSubConverterFromFormat(useFormat)
        if t.TYPE_CHECKING:
            assert isinstance(self.subConverter, subConverters.SubConverter)

        self.subConverter.keywords = keywords
        try:
            self.subConverter.parseFile(
                fp,
                number=number,
                **keywords
            )
        except NotImplementedError:
            raise ConverterFileException(f'File is not in a correct format: {fp}')

        if t.TYPE_CHECKING:
            assert isinstance(self.stream, stream.Stream)

        if not self.stream.metadata:
            self.stream.metadata = metadata.Metadata()
        self.stream.metadata.filePath = str(fpPathlib)
        self.stream.metadata.fileNumber = number
        self.stream.metadata.fileFormat = useFormat

    def getFormatFromFileExtension(self, fp):
        # noinspection PyShadowingNames
        '''
        gets the format from a file extension.

        >>> from music21 import corpus
        >>> fp = corpus.corpora.LocalCorpus().getWorkList()[0]  # pragma: no cover
        >>> c = converter.Converter()  # pragma: no cover
        >>> c.getFormatFromFileExtension(fp)  # pragma: no cover
        '''
        fp = common.cleanpath(fp, returnPathlib=True)
        # if the file path is to a directory, find format from contents
        useFormat = None
        if fp.is_dir():
            useFormat = None  # will be determined by file contents
        else:
            useFormat = common.findFormatFile(fp)
            if useFormat is None:
                raise ConverterFileException(f'cannot find a format extensions for: {fp}')
        return useFormat

    # noinspection PyShadowingBuiltins
    def parseFile(self, fp, number=None,
                  format=None, forceSource=False, storePickle=True, **keywords):
        '''
        Given a file path, parse and store a music21 Stream, set as self.stream.

        If format is None then look up the format from the file
        extension using `common.findFormatFile`.

        Will load from a pickle unless forceSource is True
        Will store as a pickle unless storePickle is False
        '''
        from music21 import freezeThaw
        fp = common.cleanpath(fp, returnPathlib=True)
        if not fp.exists():
            raise ConverterFileException(f'no such file exists: {fp}')
        useFormat = format

        if useFormat is None:
            useFormat = self.getFormatFromFileExtension(fp)

        pfObj = PickleFilter(fp, forceSource, number, **keywords)
        unused_fpDst, writePickle, fpPickle = pfObj.status()
        if writePickle is False and fpPickle is not None and forceSource is False:
            environLocal.printDebug('Loading Pickled version')
            try:
                self._thawedStream = thaw(fpPickle, zipType='zlib')
            except freezeThaw.FreezeThawException:
                environLocal.warn(f'Could not parse pickle, {fpPickle}.  Rewriting')
                os.remove(fpPickle)
                self.parseFileNoPickle(fp, number, format, forceSource, **keywords)

            if not self.stream.metadata:
                self.stream.metadata = metadata.Metadata()
            self.stream.metadata.filePath = fp
            self.stream.metadata.fileNumber = number
            self.stream.metadata.fileFormat = useFormat
        else:
            environLocal.printDebug('Loading original version')
            self.parseFileNoPickle(fp, number, format, forceSource, **keywords)
            if writePickle is True and fpPickle is not None and storePickle is True:
                # save the stream to disk
                environLocal.printDebug('Freezing Pickle')
                s = self.stream
                sf = freezeThaw.StreamFreezer(s, fastButUnsafe=True)
                sf.write(fp=fpPickle, zipType='zlib')

                environLocal.printDebug('Replacing self.stream')
                # get a new stream
                self._thawedStream = thaw(fpPickle, zipType='zlib')

                if not self.stream.metadata:
                    self.stream.metadata = metadata.Metadata()
                self.stream.metadata.filePath = fp
                self.stream.metadata.fileNumber = number
                self.stream.metadata.fileFormat = useFormat

    def parseData(
        self,
        dataStr: str|bytes,
        number=None,
        format=None,
        forceSource=False,
        **keywords,
    ) -> None:
        '''
        Given raw data, determine format and parse into a music21 Stream,
        set as self.stream.
        '''
        useFormat = format
        # get from data in string if not specified
        if useFormat is None:  # it's a string
            dataStr = dataStr.lstrip()
            useFormat, dataStr = self.formatFromHeader(dataStr)

            if isinstance(dataStr, bytes):
                dataStrMakeStr = dataStr.decode('utf-8', 'ignore')
            else:
                dataStrMakeStr = dataStr

            if useFormat is not None:
                pass
            elif dataStrMakeStr.startswith('<?xml'):
                useFormat = 'musicxml'
            elif dataStrMakeStr.lower().startswith('musicxml:'):
                useFormat = 'musicxml'
            elif dataStrMakeStr.startswith('MThd') or dataStrMakeStr.lower().startswith('midi:'):
                useFormat = 'midi'
            elif dataStrMakeStr.lower().startswith('tinynotation:'):
                useFormat = 'tinyNotation'

            # MuseData format has been removed
            elif 'M:' in dataStrMakeStr and 'K:' in dataStrMakeStr:
                useFormat = 'abc'
            else:
                raise ConverterException('File not found or no such format found for: %s' %
                                         dataStrMakeStr)

        self.setSubConverterFromFormat(useFormat)
        if t.TYPE_CHECKING:
            assert isinstance(self.subConverter, subConverters.SubConverter)
        self.subConverter.keywords = keywords
        self.subConverter.parseData(dataStr, number=number)

    def parseURL(
        self,
        url: str,
        *,
        format: str|None = None,
        number: int|None = None,
        forceSource: bool = False,
        **keywords,
    ) -> None:
        '''
        Given a url, download and parse the file
        into a music21 Stream stored in the `stream`
        property of the converter object.

        Note that this checks the user Environment
        `autoDownload` setting before downloading.

        Use `forceSource=True` to download every time rather than
        re-reading from a cached file.

        >>> joplinURL = ('https://github.com/cuthbertLab/music21/raw/master'
        ...              + '/music21/corpus/joplin/maple_leaf_rag.mxl')
        >>> c = converter.Converter()
        >>> #_DOCS_SHOW c.parseURL(joplinURL)
        >>> #_DOCS_SHOW joplinStream = c.stream

        * Changed in v7: made keyword-only and added `forceSource` option.
        '''
        autoDownload = environLocal['autoDownload']
        if autoDownload in ('deny', 'ask'):
            message = f'Automatic downloading of URLs is presently set to {autoDownload!r}; '
            message += 'configure your Environment "autoDownload" setting to '
            message += '"allow" to permit automatic downloading: '
            message += "environment.set('autoDownload', 'allow')"
            raise ConverterException(message)

        # this format check is here first to see if we can find the format
        # in the url; if forcing a format we do not need this
        # we do need the file extension to construct file path below
        if format is None:
            formatFromURL, ext = common.findFormatExtURL(url)
            if formatFromURL is None:  # cannot figure out what it is
                raise ConverterException(f'cannot determine file format of url: {url}')
        else:
            unused_formatType, ext = common.findFormat(format)
            if ext is None:
                ext = '.txt'

        directory = environLocal.getRootTempDir()
        fp = self._getDownloadFp(directory, ext, url)  # returns pathlib.Path

        if forceSource is True or not fp.exists():
            environLocal.printDebug([f'downloading to: {fp}'])
            r = requests.get(url, allow_redirects=True, timeout=20)
            if r.status_code != 200:
                raise ConverterException(
                    f'Could not download {url}, error: {r.status_code} {responses[r.status_code]}')
            fp.write_bytes(r.content)
        else:
            environLocal.printDebug([f'using already downloaded file: {fp}'])

        # update format based on downloaded fp
        if format is None:  # if not provided as an argument
            useFormat = common.findFormatFile(fp)
        else:
            useFormat = format
        if useFormat is None:
            raise ConverterException(f'Cannot automatically find a format for {fp!r}')

        self.setSubConverterFromFormat(useFormat)
        if t.TYPE_CHECKING:
            assert isinstance(self.subConverter, subConverters.SubConverter)

        self.subConverter.keywords = keywords
        self.subConverter.parseFile(fp, number=number)

        if self.stream is None:
            raise ConverterException('Could not create a Stream via a subConverter.')
        self.stream.metadata.filePath = fp
        self.stream.metadata.fileNumber = number
        self.stream.metadata.fileFormat = useFormat

    # -----------------------------------------------------------------------#
    # SubConverters
    @common.deprecated('v9', 'v10', 'use subConvertersList with capital C')
    def subconvertersList(
        self,
        converterType: t.Literal['any', 'input', 'output'] = 'any'
    ) -> list[type[subConverters.SubConverter]]:  # pragma: no cover
        return self.subConvertersList(converterType)

    @staticmethod
    def subConvertersList(
        converterType: t.Literal['any', 'input', 'output'] = 'any'
    ) -> list[type[subConverters.SubConverter]]:
        # noinspection PyAttributeOutsideInit
        '''
        Gives a list of all the subConverter classes that are registered.

        If converterType is 'any' (true), then input or output
        subConverters are listed.

        Otherwise, 'input', or 'output' can be used to filter.

        >>> converter.resetSubConverters() #_DOCS_HIDE
        >>> c = converter.Converter()
        >>> scl = c.subConvertersList()
        >>> defaultScl = c.defaultSubConverters()
        >>> tuple(scl) == tuple(defaultScl)
        True

        >>> sclInput = c.subConvertersList('input')
        >>> sclInput
        [<class 'music21.converter.subConverters.ConverterABC'>,
         <class 'music21.converter.subConverters.ConverterCapella'>,
         <class 'music21.converter.subConverters.ConverterClercqTemperley'>,
         <class 'music21.converter.subConverters.ConverterHumdrum'>,
         <class 'music21.converter.subConverters.ConverterMEI'>,
         <class 'music21.converter.subConverters.ConverterMidi'>,
         <class 'music21.converter.subConverters.ConverterMuseData'>,
         <class 'music21.converter.subConverters.ConverterMusicXML'>,
         <class 'music21.converter.subConverters.ConverterNoteworthy'>,
         <class 'music21.converter.subConverters.ConverterNoteworthyBinary'>,
         <class 'music21.converter.subConverters.ConverterRomanText'>,
         <class 'music21.converter.subConverters.ConverterScala'>,
         <class 'music21.converter.subConverters.ConverterTinyNotation'>,
         <class 'music21.converter.subConverters.ConverterVolpiano'>]

        Get those that can output (note that this is also a static method
        on converter)

        >>> sclOutput = converter.Converter.subConvertersList('output')
        >>> sclOutput
        [
         <class 'music21.converter.subConverters.ConverterLilypond'>,
         <class 'music21.converter.subConverters.ConverterMidi'>,
         <class 'music21.converter.subConverters.ConverterMusicXML'>,
         <class 'music21.converter.subConverters.ConverterRomanText'>,
         <class 'music21.converter.subConverters.ConverterScala'>,
         <class 'music21.converter.subConverters.ConverterText'>,
         <class 'music21.converter.subConverters.ConverterTextLine'>,
         <class 'music21.converter.subConverters.ConverterVexflow'>,
         <class 'music21.converter.subConverters.ConverterVolpiano'>]

        >>> class ConverterSonix(converter.subConverters.SubConverter):
        ...    registerFormats = ('sonix',)
        ...    registerInputExtensions = ('mus',)
        >>> converter.registerSubConverter(ConverterSonix)
        >>> ConverterSonix in c.subConvertersList()
        True

        Newly registered subConveters appear first, so they will be used instead
        of any default subConverters that work on the same format or extension.

        >>> class BadMusicXMLConverter(converter.subConverters.SubConverter):
        ...    registerFormats = ('musicxml',)
        ...    registerInputExtensions = ('xml', 'mxl', 'musicxml')
        ...    def parseData(self, strData, number=None):
        ...        self.stream = stream.Score(id='empty')

        >>> converter.registerSubConverter(BadMusicXMLConverter)
        >>> c.subConvertersList()
        [<class 'music21.BadMusicXMLConverter'>,
         ...
         <class 'music21.converter.subConverters.ConverterMusicXML'>,
         ...]

        Show that this musicxml file by Amy Beach is now parsed by BadMusicXMLConverter:

        >>> #_DOCS_SHOW s = corpus.parse('beach/prayer_of_a_tired_child')
        >>> #_DOCS_HIDE -- we cannot know if the piece is already parsed or not.
        >>> s = corpus.parse('beach/prayer_of_a_tired_child', forceSource=True)  #_DOCS_HIDE
        >>> s.id
        'empty'
        >>> len(s.parts)
        0

        Note that if the file has already been parsed by another subConverter format
        the parameter `forceSource` is required to force the file to be parsed by the
        newly registered subConverter:

        >>> converter.unregisterSubConverter(BadMusicXMLConverter)
        >>> #_DOCS_HIDE -- the forceSource will not have created a pickle.
        >>> #_DOCS_SHOW s = corpus.parse('beach/prayer_of_a_tired_child')
        >>> s.id
        'empty'
        >>> s = corpus.parse('beach/prayer_of_a_tired_child', forceSource=True)
        >>> len(s.parts)
        6

        >>> converter.resetSubConverters() #_DOCS_HIDE
        '''
        subConverterList = []
        for reg in _registeredSubConverters:
            # print(reg)
            subConverterList.append(reg)

        if _deregisteredSubConverters and _deregisteredSubConverters[0] == 'all':
            pass
        else:
            subConverterList.extend(Converter.defaultSubConverters())
            for unregistered in _deregisteredSubConverters:
                if unregistered == 'all':
                    continue
                try:
                    subConverterList.remove(unregistered)
                except ValueError:
                    pass

        if converterType == 'any':
            return subConverterList

        filteredSubConvertersList = []
        for sc in subConverterList:
            if converterType == 'input' and not sc.registerInputExtensions:
                continue
            if converterType == 'output' and not sc.registerOutputExtensions:
                continue
            filteredSubConvertersList.append(sc)

        return filteredSubConvertersList

    @common.deprecated('v9', 'v10', 'use defaultSubConverters with capital C')
    def defaultSubconverters(self) -> list[type[subConverters.SubConverter]]:  # pragma: no cover
        return self.defaultSubConverters()

    @staticmethod
    def defaultSubConverters() -> list[type[subConverters.SubConverter]]:
        '''
        return an alphabetical list of the default subConverters: those in converter.subConverters
        with the class SubConverter.

        Do not use generally.  Use Converter.subConvertersList()

        >>> c = converter.Converter()
        >>> for sc in c.defaultSubConverters():
        ...     print(sc)
        <class 'music21.converter.subConverters.ConverterABC'>
        <class 'music21.converter.subConverters.ConverterCapella'>
        <class 'music21.converter.subConverters.ConverterClercqTemperley'>
        <class 'music21.converter.subConverters.ConverterHumdrum'>
        <class 'music21.converter.subConverters.ConverterIPython'>
        <class 'music21.converter.subConverters.ConverterLilypond'>
        <class 'music21.converter.subConverters.ConverterMEI'>
        <class 'music21.converter.subConverters.ConverterMidi'>
        <class 'music21.converter.subConverters.ConverterMuseData'>
        <class 'music21.converter.subConverters.ConverterMusicXML'>
        <class 'music21.converter.subConverters.ConverterNoteworthy'>
        <class 'music21.converter.subConverters.ConverterNoteworthyBinary'>
        <class 'music21.converter.subConverters.ConverterRomanText'>
        <class 'music21.converter.subConverters.ConverterScala'>
        <class 'music21.converter.subConverters.ConverterText'>
        <class 'music21.converter.subConverters.ConverterTextLine'>
        <class 'music21.converter.subConverters.ConverterTinyNotation'>
        <class 'music21.converter.subConverters.ConverterVexflow'>
        <class 'music21.converter.subConverters.ConverterVolpiano'>
        <class 'music21.converter.subConverters.SubConverter'>
        '''
        defaultSubConverters: list[type[subConverters.SubConverter]] = []
        for i in sorted(subConverters.__dict__):
            possibleSubConverter = getattr(subConverters, i)
            # noinspection PyTypeChecker
            if (callable(possibleSubConverter)
                    and not isinstance(possibleSubConverter, types.FunctionType)
                    and hasattr(possibleSubConverter, '__mro__')
                    and issubclass(possibleSubConverter, subConverters.SubConverter)):
                defaultSubConverters.append(possibleSubConverter)
        return defaultSubConverters

    @common.deprecated('v9', 'v10', 'use getSubConverterFormats with capital C')
    def getSubconverterFormats(
        self
    ) -> dict[str, type[subConverters.SubConverter]]:  # pragma: no cover
        return self.getSubConverterFormats()

    @staticmethod
    def getSubConverterFormats() -> dict[str, type[subConverters.SubConverter]]:
        '''
        Get a dictionary of subConverters for various formats.

        (staticmethod: call on an instance or the class itself)

        >>> scf = converter.Converter.getSubConverterFormats()
        >>> scf['abc']
        <class 'music21.converter.subConverters.ConverterABC'>
        >>> for x in sorted(scf):
        ...     x, scf[x]
        ('abc', <class 'music21.converter.subConverters.ConverterABC'>)
        ('clercqtemperley', <class 'music21.converter.subConverters.ConverterClercqTemperley'>)
        ('cttxt', <class 'music21.converter.subConverters.ConverterClercqTemperley'>)
        ('har', <class 'music21.converter.subConverters.ConverterClercqTemperley'>)
        ('humdrum', <class 'music21.converter.subConverters.ConverterHumdrum'>)
        ('ipython', <class 'music21.converter.subConverters.ConverterIPython'>)
        ('jupyter', <class 'music21.converter.subConverters.ConverterIPython'>)
        ('lily', <class 'music21.converter.subConverters.ConverterLilypond'>)
        ('lilypond', <class 'music21.converter.subConverters.ConverterLilypond'>)
        ('mei', <class 'music21.converter.subConverters.ConverterMEI'>)
        ('midi', <class 'music21.converter.subConverters.ConverterMidi'>)
        ('musicxml', <class 'music21.converter.subConverters.ConverterMusicXML'>)
        ('rntext', <class 'music21.converter.subConverters.ConverterRomanText'>)
        ('romantext', <class 'music21.converter.subConverters.ConverterRomanText'>)
        ('scala', <class 'music21.converter.subConverters.ConverterScala'>)
        ('t', <class 'music21.converter.subConverters.ConverterText'>)
        ('text', <class 'music21.converter.subConverters.ConverterText'>)
        ('textline', <class 'music21.converter.subConverters.ConverterTextLine'>)
        ('tinynotation', <class 'music21.converter.subConverters.ConverterTinyNotation'>)
        ('txt', <class 'music21.converter.subConverters.ConverterText'>)
        ('volpiano', <class 'music21.converter.subConverters.ConverterVolpiano'>)
        ('xml', <class 'music21.converter.subConverters.ConverterMusicXML'>)
        '''
        converterFormats = {}
        for name in Converter.subConvertersList():
            if hasattr(name, 'registerFormats'):
                formatsTuple = name.registerFormats
                for f in formatsTuple:
                    f = f.lower()
                    if f not in converterFormats:
                        converterFormats[f] = name
        return converterFormats

    @staticmethod
    def getSubConverterFromFormat(
        converterFormat: str
    ) -> subConverters.SubConverter:
        '''
        Return a particular subConverter class based on the format
        of the converterFormat string.

        Static method: call on the class itself or an instance:

        >>> converter.Converter.getSubConverterFromFormat('musicxml')
        <music21.converter.subConverters.ConverterMusicXML object at 0x...>
        '''
        if converterFormat is None:
            raise ConverterException('Did not find a format from the source file')
        converterFormat = converterFormat.lower()
        scf = Converter.getSubConverterFormats()
        if converterFormat not in scf:
            raise ConverterException(f'no converter available for format: {converterFormat}')
        subConverterClass = scf[converterFormat]
        return subConverterClass()

    @common.deprecated('v9', 'v10', 'use setSubConverterFromFormat with capital C')
    def setSubconverterFromFormat(self, converterFormat: str):  # pragma: no cover
        self.setSubConverterFromFormat(converterFormat)

    def setSubConverterFromFormat(self, converterFormat: str):
        '''
        sets the .subConverter according to the format of `converterFormat`:

        >>> convObj = converter.Converter()
        >>> convObj.setSubConverterFromFormat('humdrum')
        >>> convObj.subConverter
        <music21.converter.subConverters.ConverterHumdrum object at 0x...>
        '''
        self.subConverter = Converter.getSubConverterFromFormat(converterFormat)

    def formatFromHeader(
        self,
        dataStr: _StrOrBytes
    ) -> tuple[str|None, _StrOrBytes]:
        '''
        if dataStr begins with a text header such as  "tinyNotation:" then
        return that format plus the dataStr with the head removed.

        Else, return (None, dataStr) where dataStr is the original untouched.

        The header is not detected case-sensitive.

        >>> c = converter.Converter()
        >>> c.formatFromHeader('tinynotation: C4 E2')
        ('tinynotation', 'C4 E2')

        Note that the format is always returned in lower case:

        >>> c.formatFromHeader('romanText: m1: a: I b2 V')
        ('romantext', 'm1: a: I b2 V')

        If there is no header then the format is None and the original is
        returned unchanged:

        >>> c.formatFromHeader('C4 E2')
        (None, 'C4 E2')
        >>> c.formatFromHeader(b'binary-data')
        (None, b'binary-data')

        New formats can register new headers, like this old Amiga format:

        >>> class ConverterSonix(converter.subConverters.SubConverter):
        ...    registerFormats = ('sonix',)
        ...    registerInputExtensions = ('mus',)
        >>> converter.registerSubConverter(ConverterSonix)
        >>> c.formatFromHeader('sonix: AIFF data')
        ('sonix', 'AIFF data')
        >>> converter.resetSubConverters() #_DOCS_HIDE

        If bytes are passed in, the data is returned as bytes, but the
        header format is still converted to a string:

        >>> c.formatFromHeader(b'romanText: m1: a: I b2 V')
        ('romantext', b'm1: a: I b2 V')

        Anything except string or bytes raises a ValueError:

        >>> c.formatFromHeader(23)
        Traceback (most recent call last):
        ValueError: Cannot parse a format from <class 'int'>.
        '''
        dataStrStartLower: str
        if isinstance(dataStr, bytes):
            dataStrStartLower = dataStr[:20].decode('utf-8', 'ignore').lower()
        elif isinstance(dataStr, str):
            dataStrStartLower = dataStr[:20].lower()
        else:
            raise ValueError(f'Cannot parse a format from {type(dataStr)}.')

        foundFormat = None
        subConverterList = self.subConvertersList()
        for sc in subConverterList:
            for possibleFormat in sc.registerFormats:
                if dataStrStartLower.startswith(possibleFormat.lower() + ':'):
                    foundFormat = possibleFormat
                    dataStr = t.cast(_StrOrBytes,
                                     dataStr[len(foundFormat) + 1:].lstrip()
                                     )
                    break
        return (foundFormat, dataStr)

    def regularizeFormat(self, fmt: str) -> str|None:
        '''
        Take in a string representing a format, a file extension (w/ or without leading dot)
        etc. and find the format string that best represents the format that should be used.

        Searches SubConverter.registerFormats first, then SubConverter.registerInputExtensions,
        then SubConverter.registerOutputExtensions

        Returns None if no format applies:

        >>> c = converter.Converter()
        >>> c.regularizeFormat('mxl')
        'musicxml'
        >>> c.regularizeFormat('t')
        'text'
        >>> c.regularizeFormat('abc')
        'abc'
        >>> c.regularizeFormat('lily.png')
        'lilypond'
        >>> c.regularizeFormat('blah') is None
        True
        '''
        # make lower case, as some lilypond processing used upper case
        fmt = fmt.lower().strip()
        if fmt.startswith('.'):
            fmt = fmt[1:]  # strip .
        foundSc = None

        formatList = fmt.split('.')
        fmt = formatList[0]
        if len(formatList) > 1:
            unused_subformats = formatList[1:]
        else:
            unused_subformats = []
        scl = self.subConvertersList()

        for sc in scl:
            formats = sc.registerFormats
            for scFormat in formats:
                if fmt == scFormat:
                    foundSc = sc
                    break
            if foundSc is not None:
                break

        if foundSc is None:
            for sc in scl:
                extensions = sc.registerInputExtensions
                for ext in extensions:
                    if fmt == ext:
                        foundSc = sc
                        break
                if foundSc is not None:
                    break
        if foundSc is None:
            for sc in scl:
                extensions = sc.registerInputExtensions
                for ext in extensions:
                    if fmt == ext:
                        foundSc = sc
                        break
                if foundSc is not None:
                    break

        if foundSc and foundSc.registerFormats:
            return foundSc.registerFormats[0]
        else:
            return None

    # --------------------------------------------------------------------------
    # properties
    @property
    def stream(self) -> stream.Score|stream.Part|stream.Opus|None:
        '''
        Returns the .subConverter.stream object.
        '''
        if self._thawedStream is not None:
            return self._thawedStream
        elif self.subConverter is not None:
            return self.subConverter.stream
        else:
            return None
        # not _stream: please don't look in other objects' private variables;
        #              humdrum worked differently.

# ------------------------------------------------------------------------------
# module level convenience methods

# pylint: disable=redefined-builtin
# noinspection PyShadowingBuiltins
def parseFile(fp,
              number=None,
              format=None,
              forceSource=False,
              **keywords) -> stream.Score|stream.Part|stream.Opus:
    '''
    Given a file path, attempt to parse the file into a Stream.
    '''
    v = Converter()
    fp = common.cleanpath(fp, returnPathlib=True)
    v.parseFile(fp, number=number, format=format, forceSource=forceSource, **keywords)
    if t.TYPE_CHECKING:
        assert isinstance(v.stream, (stream.Score, stream.Part, stream.Opus))
    return v.stream

# pylint: disable=redefined-builtin
# noinspection PyShadowingBuiltins
def parseData(dataStr,
              number=None,
              format=None,
              **keywords) -> stream.Score|stream.Part|stream.Opus:
    '''
    Given musical data represented within a Python string, attempt to parse the
    data into a Stream.
    '''
    v = Converter()
    v.parseData(dataStr, number=number, format=format, **keywords)
    if t.TYPE_CHECKING:
        assert isinstance(v.stream, (stream.Score, stream.Part, stream.Opus))
    return v.stream

# pylint: disable=redefined-builtin
# noinspection PyShadowingBuiltins
def parseURL(url,
             *,
             format=None,
             number=None,
             forceSource=False,
             **keywords) -> stream.Score|stream.Part|stream.Opus:
    '''
    Given a URL, attempt to download and parse the file into a Stream. Note:
    URL downloading will not happen automatically unless the user has set their
    Environment "autoDownload" preference to "allow".

    * Changed in v7: made keyword-only.
    '''
    v = Converter()
    v.parseURL(url, format=format, forceSource=forceSource, **keywords)
    if t.TYPE_CHECKING:
        assert isinstance(v.stream, (stream.Score, stream.Part, stream.Opus))
    return v.stream

def parse(value: bundles.MetadataEntry|bytes|str|pathlib.Path|list|tuple,
          *,
          forceSource: bool = False,
          number: int|None = None,
          format: str|None = None,  # pylint: disable=redefined-builtin
          **keywords) -> stream.Score|stream.Part|stream.Opus:
    r'''
    Given a file path, encoded data in a Python string, or a URL, attempt to
    parse the item into a Stream.  Note: URL downloading will not happen
    automatically unless the user has set their Environment "autoDownload"
    preference to "allow".

    Keywords can include `number` which specifies a piece number in a file of
    multi-piece file. (Otherwise, a particular score from an
    :class:`~music21.stream.Opus` can also be extracted by providing a
    two-element list or tuple of the form (path, number) to the `value` argument.)

    `format` specifies the format to parse the line of text or the file as.

    `quantizePost` specifies whether to quantize a stream resulting from MIDI conversion.
    By default, MIDI streams are quantized to the nearest sixteenth or triplet-eighth
    (i.e. smaller durations will not be preserved).
    `quarterLengthDivisors` sets the quantization units explicitly.

    A string of text is first checked to see if it is a filename that exists on
    disk.  If not it is searched to see if it looks like a URL.  If not it is
    processed as data.

    PC File:

    >>> #_DOCS_SHOW s = converter.parse(r'c:\users\myke\desktop\myFile.xml')

    Mac File:

    >>> #_DOCS_SHOW s = converter.parse('/Users/cuthbert/Desktop/myFile.xml')

    URL:

    >>> #_DOCS_SHOW s = converter.parse('https://midirepository.org/file220/file.mid')

    Data is preceded by an identifier such as "tinynotation:"

    >>> s = converter.parse("tinyNotation: 3/4 E4 r f# g=lastG trip{b-8 a g} c", makeNotation=False)
    >>> s[meter.TimeSignature].first()
    <music21.meter.TimeSignature 3/4>

    or the format can be passed directly:

    >>> s = converter.parse("2/16 E4 r f# g=lastG trip{b-8 a g} c", format='tinyNotation')
    >>> s[meter.TimeSignature].first()
    <music21.meter.TimeSignature 2/16>

    * Changed in v8: passing a list of tinyNotation strings was never documented as a
        possibility and has been removed.
    '''
    # environLocal.printDebug(['attempting to parse()', value])
    # see if a work number is defined; for multi-work collections
    valueStr: str
    if isinstance(value, bytes):
        valueStr = value.decode('utf-8', 'ignore')
    if isinstance(value, pathlib.Path):
        valueStr = str(value)
    elif isinstance(value, bundles.MetadataEntry):
        if value.sourcePath.is_absolute():
            valueStr = str(value.sourcePath)
        else:
            valueStr = str(common.getCorpusFilePath() / value.sourcePath)
    elif isinstance(value, str):
        valueStr = value
    else:
        valueStr = ''

    if (common.isListLike(value)
            and len(value) == 2
            and value[1] is None
            and _osCanLoad(str(value[0]))):
        # comes from corpus.search
        return parseFile(value[0], format=format, **keywords)
    elif (common.isListLike(value)
          and len(value) == 2
          and _osCanLoad(str(value[0]))):
        # corpus or other file with movement number
        if not isinstance(value[0], str):
            raise ConverterException(
                f'If using a two-element list, the first value must be a string, not {value[0]!r}'
            )
        if not isinstance(value[1], int):
            raise ConverterException(
                'If using a two-element list, the second value must be an integer number, '
                f'not {value[1]!r}'
            )
        sc = parseFile(value[0], format=format, **keywords)
        if isinstance(sc, stream.Opus):
            return sc.getScoreByNumber(value[1])
        else:
            return sc
    # a midi string, must come before os.path.exists test
    elif not isinstance(value, bytes) and valueStr.startswith('MThd'):
        return parseData(value, number=number, format=format, **keywords)
    elif (not isinstance(value, bytes)
          and _osCanLoad(valueStr)):
        return parseFile(valueStr, number=number, format=format,
                         forceSource=forceSource, **keywords)
    elif (not isinstance(value, bytes)
          and _osCanLoad(common.cleanpath(valueStr))):
        return parseFile(common.cleanpath(valueStr), number=number, format=format,
                         forceSource=forceSource, **keywords)
    elif not isinstance(valueStr, bytes) and (valueStr.startswith('http://')
                                              or valueStr.startswith('https://')):
        # it's a url; may need to broaden these criteria
        return parseURL(value, number=number, format=format,
                        forceSource=forceSource, **keywords)
    elif isinstance(value, pathlib.Path):
        raise FileNotFoundError(f'Cannot find file in {str(value)}')
    elif isinstance(value, str) and common.findFormatFile(value) is not None:
        # assume mistyped file path
        raise FileNotFoundError(f'Cannot find file in {str(value)}')
    else:
        # all else, including MidiBytes
        return parseData(value, number=number, format=format, **keywords)

def toData(obj: base.Music21Object, fmt: str, **keywords) -> str|bytes:
    '''
    Convert `obj` to the given format `fmt` and return the information retrieved.

    Currently, this is somewhat inefficient: it calls SubConverter.toData which
    calls `write()` on the object and reads back the value of the file.

    >>> tiny = converter.parse('tinyNotation: 4/4 C4 D E F G1')
    >>> data = converter.toData(tiny, 'text')
    >>> type(data)
    <class 'str'>
    '''
    if fmt.startswith('.'):
        fmt = fmt[1:]
    regularizedConverterFormat, unused_ext = common.findFormat(fmt)
    if regularizedConverterFormat is None:
        raise ConverterException(f'cannot support output in this format yet: {fmt}')

    formatSubs = fmt.split('.')
    fmt = formatSubs[0]
    subformats = formatSubs[1:]

    scClass = common.findSubConverterForFormat(regularizedConverterFormat)
    if scClass is None:  # pragma: no cover
        raise ConverterException(f'cannot support output in this format yet: {fmt}')
    formatWriter = scClass()
    return formatWriter.toData(
        obj,
        fmt=regularizedConverterFormat,
        subformats=subformats,
        **keywords)

def freeze(streamObj, fmt=None, fp=None, fastButUnsafe=False, zipType='zlib') -> pathlib.Path:
    # noinspection PyShadowingNames
    '''
    Given a StreamObject and a file path, serialize and store the Stream to a file.

    This function is based on the :class:`~music21.converter.StreamFreezer` object.

    The serialization format is defined by the `fmt` argument; 'pickle' (the default) is only one
    presently supported.  'json' or 'jsonnative' will be used once jsonpickle is good enough.

    If no file path is given, a temporary file is used.

    The file path is returned.

    >>> c = converter.parse('tinynotation: 4/4 c4 d e f')
    >>> c.show('text')
    {0.0} <music21.stream.Measure 1 offset=0.0>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.meter.TimeSignature 4/4>
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Note D>
        {2.0} <music21.note.Note E>
        {3.0} <music21.note.Note F>
        {4.0} <music21.bar.Barline type=final>
    >>> fp = converter.freeze(c, fmt='pickle')
    >>> #_DOCS_SHOW fp
    PosixPath('/tmp/music21/sjiwoe.p.gz')

    The file can then be "thawed" back into a Stream using the
    :func:`~music21.converter.thaw` method.

    >>> d = converter.thaw(fp)
    >>> d.show('text')
    {0.0} <music21.stream.Measure 1 offset=0.0>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.meter.TimeSignature 4/4>
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Note D>
        {2.0} <music21.note.Note E>
        {3.0} <music21.note.Note F>
        {4.0} <music21.bar.Barline type=final>

    OMIT_FROM_DOCS

    >>> import os
    >>> os.remove(fp)
    '''
    from music21 import freezeThaw
    v = freezeThaw.StreamFreezer(streamObj, fastButUnsafe=fastButUnsafe)
    return v.write(fmt=fmt, fp=fp, zipType=zipType)  # returns fp

def thaw(fp, zipType='zlib'):
    '''
    Given a file path of a serialized Stream, defrost the file into a Stream.

    This function is based on the :class:`~music21.converter.StreamFreezer` object.

    See the documentation for :meth:`~music21.converter.freeze` for demos.
    '''
    from music21 import freezeThaw
    v = freezeThaw.StreamThawer()
    v.open(fp, zipType=zipType)
    return v.stream

def freezeStr(streamObj, fmt=None):
    '''
    Given a StreamObject
    serialize and return a serialization string.

    This function is based on the
    :class:`~music21.converter.StreamFreezer` object.

    The serialization format is defined by
    the `fmt` argument; 'pickle' (the default),
    is the only one presently supported.

    >>> c = converter.parse('tinyNotation: 4/4 c4 d e f', makeNotation=False)
    >>> c.show('text')
    {0.0} <music21.meter.TimeSignature 4/4>
    {0.0} <music21.note.Note C>
    {1.0} <music21.note.Note D>
    {2.0} <music21.note.Note E>
    {3.0} <music21.note.Note F>
    >>> data = converter.freezeStr(c, fmt='pickle')
    >>> len(data) > 20  # pickle implementation dependent
    True
    >>> d = converter.thawStr(data)
    >>> d.show('text')
    {0.0} <music21.meter.TimeSignature 4/4>
    {0.0} <music21.note.Note C>
    {1.0} <music21.note.Note D>
    {2.0} <music21.note.Note E>
    {3.0} <music21.note.Note F>

    '''
    from music21 import freezeThaw
    v = freezeThaw.StreamFreezer(streamObj)
    return v.writeStr(fmt=fmt)  # returns a string

def thawStr(strData):
    '''
    Given a serialization string, defrost into a Stream.

    This function is based on the :class:`~music21.converter.StreamFreezer` object.
    '''
    from music21 import freezeThaw
    v = freezeThaw.StreamThawer()
    v.openStr(strData)
    return v.stream

def _osCanLoad(fp: str) -> bool:
    '''
    Return os.path.exists, but catch `ValueError` and return False.

    os.path.exists raises ValueError for paths over 260 chars
    on all versions of Windows lacking the `LongPathsEnabled` setting,
    which is absent below Windows 10.1607 and opt-in on higher versions.
    '''
    try:
        return os.path.exists(fp)
    except ValueError:  # pragma: no cover
        return False

# ------------------------------------------------------------------------------
# tests moved to tests/unit/test_converter.py

# define presented order in documentation
_DOC_ORDER = [parse, parseFile, parseData, parseURL, freeze, thaw, freezeStr, thawStr,
              Converter, registerSubConverter, unregisterSubConverter]
