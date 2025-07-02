# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         converter/__init__.py
# Purpose:      Specific subConverters for formats music21 should handle
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2015 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
SubConverters parse or display a single format.

Each subConverter should inherit from the base SubConverter object and have at least a
parseData method that sets self.stream.
'''
from __future__ import annotations

# ------------------------------------------------------------------------------
# Converters are associated classes; they are not subclasses,
# but most define a parseData() method,
# a parseFile() method, and a .stream attribute or property.
from io import IOBase
import os
import pathlib
import subprocess
import typing as t
from music21 import common
from music21 import defaults
from music21 import environment
from music21.exceptions21 import SubConverterException
from music21 import stream

if t.TYPE_CHECKING:
    from collections.abc import Iterable

environLocal = environment.Environment('converter.subConverters')

# pylint complains when abstract methods are not overwritten, but that's okay.
# pylint: disable=abstract-method

class SubConverter:
    '''
    Class wrapper for parsing data or outputting data.

    All other Converter types should inherit from this and
    have ways of dealing with various data formats.

    Attributes that should be set::

        readBinary = True or False (default False)
        registerFormats = tuple of formats that can be handled; eg: ('musicxml',)
        registerShowFormats = tuple of format calls that can be handled in .show() and .write()
        registerInputExtensions = tuple of input extensions that should be handled in converter
        registerOutputExtensions = tuple of output extensions that can be written. Order matters:
            the first will be used in calls to .write()
        canBePickled = True or False (default True; does not do anything yet)
        codecWrite = True or False (default False) if encodings need to be used to write
        stringEncoding = string (default 'utf-8'). If codecWrite is True, this specifies what
            encoding to use

    '''
    readBinary: bool = False
    canBePickled: bool = True
    registerFormats: tuple[str, ...] = ()
    registerShowFormats: tuple[str, ...] = ()
    registerInputExtensions: tuple[str, ...] = ()  # if converter supports input
    registerOutputExtensions: tuple[str, ...] = ()  # if converter supports output
    registerOutputSubformatExtensions: dict[str, str] = {}
    launchKey: str|pathlib.Path|None = None

    codecWrite: bool = False
    stringEncoding: str = 'utf-8'

    def __init__(self, **keywords) -> None:
        self._stream: stream.Score|stream.Part|stream.Opus = stream.Score()
        # TODO: unify keywords so that they are used by both parseFile and parseData
        self.keywords: dict[str, t.Any] = keywords

    def parseData(self, dataString, number: int|None = None):
        '''
        Called when a string (or binary) data is encountered.

        This method MUST be implemented to do anything in parsing.

        Return self.stream in the end
        '''
        raise NotImplementedError
        # return self.stream

    def parseFile(self,
                  filePath: str|pathlib.Path,
                  number: int|None = None,
                  **keywords):
        '''
        Called when a file is encountered. If all that needs to be done is
        loading the file and putting the data into parseData then there is no need
        to implement this method.  Just set self.readBinary to True | False.
        '''
        if self.readBinary is False:
            import locale
            with open(filePath, encoding=locale.getpreferredencoding()) as f:
                dataStream = f.read()
        else:
            with open(filePath, 'rb') as f:
                dataStream = f.read()  # type: ignore

        # might raise NotImplementedError
        self.parseData(dataStream, number)

        return self.stream

    def _getStream(self):
        return self._stream

    def _setStream(self, newStream):
        self._stream = newStream

    stream = property(_getStream, _setStream, doc='''
        Returns or sets the stream in the converter.  Must be defined for subConverter to work.
        ''')

    def checkShowAbility(self, **keywords) -> bool:
        '''
        return bool on whether the *system* is
        equipped to show in this format.

        Default True. Might be False if, say
        a Lilypond converter is used and Lilypond
        is not installed.
        '''
        return True

    def launch(self,
               filePath: pathlib.Path,
               fmt=None,
               options: str = '',
               app: str|None = None,
               launchKey=None):  # pragma: no cover
        '''
        Opens the appropriate viewer for the file generated by .write()

        app is the path to an application to launch.  Specify it and/or a launchKey.
        launchKey is the specific key in .music21rc (such as graphicsPath), etc.
        to search for the application.  If it's not specified then there might be
        a default one for the converter in self.launchKey.  If it can't find it
        there then environLocal.formatToApp(fmt) will be used.

        Not needed for formats for which .show() just prints to the console.
        '''
        if fmt is None and self.registerShowFormats:
            fmt = self.registerShowFormats[0]
        elif fmt is None:  # pragma: no cover
            raise ValueError('launch: fmt can only be None if there is a registered show format.')

        if app is None:
            if launchKey is not None:
                app = environLocal[launchKey]
            elif self.launchKey is not None:
                launchKey = self.launchKey
                app = environLocal[launchKey]
            else:
                launchKey = environLocal.formatToKey(fmt)
                app = environLocal.formatToApp(fmt)
            # app may still be None

        platform: str = common.getPlatform()
        shell: bool = False
        cmd: tuple[str, ...]
        if app is None:
            if platform == 'win':
                # no need to specify application here:
                # windows starts the program based on the file extension
                # Q: should options be here?
                cmd = ('start', str(filePath))
                shell = True
            elif platform == 'darwin':
                if options:
                    cmd = ('open', options, str(filePath))
                else:
                    cmd = ('open', str(filePath))
            else:
                raise SubConverterException(
                    f'Cannot find a valid application path for format {fmt}. '
                    + 'Specify this in your Environment by calling '
                    + f"environment.set({launchKey!r}, '/path/to/application')"
                )
        elif platform in ('win', 'nix'):
            if options:
                cmd = (app, options, str(filePath))
            else:
                cmd = (app, str(filePath))
        elif platform == 'darwin':
            if options:
                cmd = ('open', '-a', str(app), options, str(filePath))
            else:
                cmd = ('open', '-a', str(app), str(filePath))
        else:
            raise SubConverterException(f'Cannot launch files on {platform}')
        try:
            subprocess.run(cmd, check=False, shell=shell)
        except FileNotFoundError as e:
            # musicXML path misconfigured
            raise SubConverterException(
                'Most issues with show() can be resolved by calling configure.run()'
            ) from e

    def show(
        self,
        obj,
        fmt: str|None,
        app=None,
        subformats=(),
        **keywords
    ) -> None:
        '''
        Write the data, then show the generated data, using `.launch()` or printing
        to a console.

        Some simple formats that do not need launching, may skip .launch() and
        simply return the output.
        '''
        returnedFilePath = self.write(obj, fmt, subformats=subformats, **keywords)
        self.launch(returnedFilePath, fmt=fmt, app=app)

    def getExtensionForSubformats(self, subformats: Iterable[str] = ()) -> str:
        '''
        Given a default format or subformats, give the file extension it should have:

        >>> c = converter.subConverters.ConverterMidi()
        >>> c.getExtensionForSubformats()
        '.mid'
        '''
        extensions = self.registerOutputExtensions
        if not extensions:
            raise SubConverterException(
                'This subConverter cannot show or write: '
                + 'no output extensions are registered for it')
        # start by trying the first one.
        ext = extensions[0]
        if self.registerOutputSubformatExtensions and subformats:
            joinedSubformats = '.'.join(subformats)
            if joinedSubformats in self.registerOutputSubformatExtensions:
                ext = self.registerOutputSubformatExtensions[joinedSubformats]
        return '.' + ext

    def getTemporaryFile(self, subformats: Iterable[str] = ()) -> pathlib.Path:
        '''
        Return a temporary file with an extension appropriate for the format.

        >>> c = corpus.parse('bwv66.6')
        >>> mxConverter = converter.subConverters.ConverterMusicXML()
        >>> tf = str(mxConverter.getTemporaryFile(subformats=['png']))
        >>> tf.endswith('.png')
        True
        >>> import os  #_DOCS_HIDE
        >>> os.remove(tf)  #_DOCS_HIDE

        * Changed in v6: returns pathlib.Path
        '''
        ext = self.getExtensionForSubformats(subformats)
        fp = environLocal.getTempFile(ext, returnPathlib=True)
        return fp

    def write(self,
              obj: music21.base.Music21Object,
              fmt: str|None,
              fp: str|pathlib.Path|IOBase|None = None,
              subformats: Iterable[str] = (),
              **keywords):  # pragma: no cover
        '''
        Calls .writeDataStream on the repr of obj, and returns the fp returned by it.
        '''
        dataStr = repr(obj)
        fp = self.writeDataStream(fp, dataStr, **keywords)
        return fp

    def writeDataStream(self,
                        fp: str|pathlib.Path|IOBase|None,
                        dataStr: str|bytes,
                        **keywords) -> pathlib.Path:  # pragma: no cover
        '''
        Writes the data stream to `fp` or to a temporary file and returns the
        Path object of the filename written.
        '''
        if fp is None:
            fp = self.getTemporaryFile()

        if self.readBinary is False:
            writeFlags = 'w'
        else:
            writeFlags = 'wb'

        if self.codecWrite is False and isinstance(dataStr, bytes):
            try:
                dataStr = dataStr.decode('utf-8')
            except UnicodeDecodeError:
                # Reattempt below with self.stringEncoding
                self.codecWrite = True
                # Close file if already open, because we need to reopen with encoding
                if isinstance(fp, IOBase):
                    fp.close()

        if isinstance(fp, (str, pathlib.Path)):
            fp = common.cleanpath(fp, returnPathlib=True)
            with open(fp,
                      mode=writeFlags,
                      encoding=self.stringEncoding if self.codecWrite else None
                      ) as f:
                f.write(dataStr)
            return fp
        else:
            # file-like object
            fp.write(dataStr)
            fp.close()
            return pathlib.Path('')

    def toData(
        self,
        obj,
        fmt: str|None,
        subformats: Iterable[str] = (),
        **keywords,
    ) -> str|bytes:
        '''
        Write the object out in the given format and then read it back in
        and return the object (str or bytes) returned.
        '''
        fp = self.write(obj, fmt=fmt, subformats=subformats, **keywords)
        if self.readBinary is False:
            readFlags = 'r'
        else:
            readFlags = 'rb'
        with open(fp,
                  mode=readFlags,
                  encoding=self.stringEncoding if self.codecWrite else None
                  ) as f:
            out = f.read()
        fp.unlink(missing_ok=True)
        return out

class ConverterIPython(SubConverter):
    '''
    Meta-subConverter for displaying image data in a Notebook
    using either png (via MuseScore) or directly via
    Vexflow/music21j, or MIDI using music21j.
    '''
    registerFormats = ('ipython', 'jupyter')
    registerOutputExtensions = ()
    registerOutputSubformatExtensions = {}

    def show(self, obj, fmt, app=None, subformats=(),
             **keywords):  # pragma: no cover
        '''
        show a specialized for Jupyter Notebook using the appropriate subformat.

        For MusicXML runs it through MuseScore and returns the PNG data.
        (use multipageWidget to get an experimental interactive page display).

        For MIDI: loads a music21j-powered MIDI player in to the Notebook.
        '''
        from music21.converter import Converter
        from music21.ipython21 import converters as ip21_converters

        if subformats:
            helperFormat = subformats[0]
            helperSubformats = subformats[1:]
        else:
            helperFormat = 'musicxml'
            helperSubformats = []

        if not helperSubformats:
            helperSubformats = ['png']

        helperSubConverter = Converter.getSubConverterFromFormat(helperFormat)

        if helperFormat in ('musicxml', 'xml'):
            ip21_converters.showImageThroughMuseScore(
                obj,
                subConverter=helperSubConverter,
                fmt=helperFormat,
                subformats=helperSubformats,
                **keywords,
            )
        elif helperFormat == 'midi':
            if t.TYPE_CHECKING:
                assert isinstance(helperSubConverter, ConverterMidi)
            ip21_converters.displayMusic21jMIDI(
                obj,
                subConverter=helperSubConverter,
                fmt=helperFormat,
                subformats=helperSubformats,
                **keywords,
            )

class ConverterText(SubConverter):
    '''
    standard text presentation has line breaks, is printed.

    Two keyword options are allowed: addEndTimes=Boolean and useMixedNumerals=Boolean
    '''

    registerFormats = ('text', 'txt', 't')
    registerOutputExtensions = ('txt',)

    def write(self, obj, fmt, fp=None, subformats=(), **keywords):  # pragma: no cover
        dataStr = obj._reprText(**keywords)
        self.writeDataStream(fp, dataStr)
        return fp

    def show(self, obj, fmt, app=None, subformats=(), **keywords):
        print(obj._reprText(**keywords))

class ConverterTextLine(SubConverter):
    '''
    a text line compacts the complete recursive representation into a
    single line of text; most for debugging. returned, not printed

    >>> s = corpus.parse('bwv66.6')
    >>> s.measures(1, 4).show('textline')
    "{0.0} <music21.stream.Part Soprano> / {0.0} <music21.instrument.Instrument '... 1'>..."
    '''
    registerFormats = ('textline',)
    registerOutputExtensions = ('txt',)

    def write(self, obj, fmt, fp=None, subformats=(), **keywords):  # pragma: no cover
        dataStr = obj._reprTextLine()
        self.writeDataStream(fp, dataStr)
        return fp

    def show(self, obj, fmt, app=None, subformats=(), **keywords):
        return obj._reprTextLine()

class ConverterVolpiano(SubConverter):
    '''
    Reads or writes volpiano (Chant encoding).

    Normally, just use 'converter' and .show()/.write()

    >>> p = converter.parse('volpiano: 1---c-d-ef----4')
    >>> p.show('text')
    {0.0} <music21.stream.Measure 0 offset=0.0>
        {0.0} <music21.clef.TrebleClef>
        {0.0} <music21.note.Note C>
        {1.0} <music21.note.Note D>
        {2.0} <music21.note.Note E>
        {3.0} <music21.note.Note F>
        {4.0} <music21.volpiano.Neume <music21.note.Note E><music21.note.Note F>>
        {4.0} <music21.bar.Barline type=double>
    >>> p.show('volpiano')
    1---c-d-ef----4
    '''
    registerFormats = ('volpiano',)
    registerInputExtensions = ('volpiano', 'vp')
    registerOutputExtensions = ('txt', 'vp')

    def parseData(
        self,
        dataString,
        number: int|None = None,
        *,
        breaksToLayout: bool = False,
        **keywords,
    ):
        from music21 import volpiano
        self.stream = volpiano.toPart(dataString, breaksToLayout=breaksToLayout)

    def getDataStr(self, obj, **keywords):
        '''
        Get the raw data, for storing as a variable.
        '''
        from music21 import volpiano
        if obj.isStream:
            s = obj
        else:
            s = stream.Stream()
            s.append(obj)

        return volpiano.fromStream(s)

    def write(self, obj, fmt, fp=None, subformats=(), **keywords):  # pragma: no cover
        dataStr = self.getDataStr(obj, **keywords)
        self.writeDataStream(fp, dataStr)
        return fp

    def show(self, obj, fmt, app=None, subformats=(), **keywords):
        print(self.getDataStr(obj, **keywords))

class ConverterScala(SubConverter):
    registerFormats = ('scala',)
    registerInputExtensions = ('scl',)
    registerOutputExtensions = ('scl',)

# ------------------------------------------------------------------------------

class ConverterTinyNotation(SubConverter):
    '''
    Simple class wrapper for parsing TinyNotation data provided in a file or
    in a string.

    Input only for now.
    '''
    registerFormats = ('tinynotation',)
    registerInputExtensions = ('tntxt', 'tinynotation')

    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.data = None

    # --------------------------------------------------------------------------
    def parseData(self, tnData, number=None):
        # noinspection PyShadowingNames
        '''
        Open TinyNotation data from a string

        >>> tnData = "3/4 E4 r f# g=lastG trip{b-8 a g} c"
        >>> c = converter.subConverters.ConverterTinyNotation()
        >>> s = c.parseData(tnData)
        >>> c.stream.show('text')
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 3/4>
            {0.0} <music21.note.Note E>
            {1.0} <music21.note.Rest quarter>
            {2.0} <music21.note.Note F#>
        {3.0} <music21.stream.Measure 2 offset=3.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note B->
            {1.3333} <music21.note.Note A>
            {1.6667} <music21.note.Note G>
            {2.0} <music21.note.Note C>
            {2.5} <music21.bar.Barline type=final>
        '''
        if isinstance(tnData, str):
            tnStr = tnData
        else:  # assume a 2 element sequence  # pragma: no cover
            raise SubConverterException(
                'TinyNotation no longer supports two-element calls; put the time signature '
                + 'in the stream')
        from music21 import tinyNotation
        self.stream = tinyNotation.Converter(tnStr, **self.keywords).parse().stream

# ------------------------------------------------------------------------------
class ConverterMusicXML(SubConverter):
    '''
    Converter for MusicXML using the 2015 ElementTree system.

    Users should not need this Object.  Call converter.parse directly
    '''
    registerFormats = ('musicxml', 'xml')
    registerInputExtensions = ('xml', 'mxl', 'musicxml')
    registerOutputExtensions = ('musicxml', 'xml', 'mxl')
    registerOutputSubformatExtensions = {'png': 'png',
                                         'pdf': 'pdf',
                                         }

    def parseData(self, xmlString: str, number=None):
        '''
        Open MusicXML data from a string.
        '''
        from music21.musicxml import xmlToM21

        c = xmlToM21.MusicXMLImporter()
        c.xmlText = xmlString
        c.parseXMLText()
        self.stream = c.stream

    def parseFile(self,
                  filePath: str|pathlib.Path,
                  number: int|None = None,
                  **keywords):
        '''
        Open from a file path; check to see if there is a pickled
        version available and up to date; if so, open that, otherwise
        open source.
        '''
        # return fp to load, if pickle needs to be written, fp pickle
        # this should be able to work on a .mxl file, as all we are doing
        # here is seeing which is more recent
        from music21 import converter
        from music21.musicxml import xmlToM21

        c = xmlToM21.MusicXMLImporter()

        # here, we can see if this is a mxl or similar archive
        arch = converter.ArchiveManager(filePath)
        if arch.isArchive():
            archData = arch.getData()
            c.xmlText = archData
            c.parseXMLText()
        else:  # it is a file path or a raw musicxml string
            c.readFile(filePath)

        # movement titles can be stored in more than one place in musicxml
        # manually insert file name as a movementName title if no titles are defined
        if c.stream.metadata.movementName is None:
            junk, fn = os.path.split(filePath)
            c.stream.metadata.movementName = fn  # this should become a Path
        self.stream = c.stream

    def writeDataStream(self,
                        fp,
                        dataStr: str|bytes,
                        **keywords) -> pathlib.Path:  # pragma: no cover
        # noinspection PyShadowingNames
        '''
        Writes `dataStr` which must be bytes to `fp`.
        Adds `.musicxml` suffix to `fp` if it does not already contain some suffix.

        * Changed in v7: returns a pathlib.Path

        OMIT_FROM_DOCS

        >>> import os
        >>> from music21.converter.subConverters import ConverterMusicXML
        >>> fp = 'noSuffix'
        >>> sub = ConverterMusicXML()
        >>> outFp = sub.writeDataStream(fp, b'')
        >>> str(outFp).endswith('.musicxml')
        True

        >>> os.remove(outFp)
        >>> fp = 'other.suffix'
        >>> outFp = sub.writeDataStream(fp, b'')
        >>> str(outFp).endswith('.suffix')
        True
        >>> os.remove(outFp)
        '''
        if not isinstance(dataStr, bytes):
            raise ValueError(f'{dataStr} must be bytes to write to this format')
        dataBytes = dataStr

        fpPath: pathlib.Path
        if fp is None:
            fpPath = self.getTemporaryFile()
        else:
            fpPath = common.cleanpath(fp, returnPathlib=True)

        if not fpPath.suffix or fpPath.suffix == '.mxl':
            fpPath = fpPath.with_suffix('.musicxml')

        writeFlags = 'wb'

        with open(fpPath, writeFlags) as f:
            f.write(dataBytes)  # type: ignore

        return fpPath

    def write(self,
              obj: music21.Music21Object,
              fmt,
              fp=None,
              subformats=(),
              *,
              makeNotation=True,
              compress: bool|None = None,
              **keywords):
        '''
        Write to a .musicxml file.

        Set `makeNotation=False` to prevent fixing up the notation, and where possible,
        to prevent making additional deepcopies. (This option cannot be used if `obj` is not a
        :class:`~music21.stream.Score`.) `makeNotation=True` generally solves common notation
        issues, whereas `makeNotation=False` is intended for advanced users facing
        special cases where speed is a priority or making notation reverses user choices.

        Set `compress=True` to immediately compress the output to a .mxl file.  Set
        to True automatically if format='mxl' or if `fp` is given and ends with `.mxl`
        '''
        from music21.musicxml import archiveTools, m21ToXml

        savedDefaultTitle = defaults.title
        savedDefaultAuthor = defaults.author

        if compress is None:
            if fp and str(fp).endswith('.mxl'):
                compress = True
            elif fmt.startswith('mxl'):
                # currently unreachable from Music21Object.write()
                compress = True
            else:
                compress = False

        # hack to make MuseScore excerpts -- fix with a converter class in MusicXML
        if 'png' in subformats:
            # do not print a title or author -- to make the PNG smaller.
            defaults.title = ''
            defaults.author = ''

        dataBytes: bytes = b''
        generalExporter = m21ToXml.GeneralObjectExporter(obj)
        generalExporter.makeNotation = makeNotation
        dataBytes = generalExporter.parse()

        writeDataStreamFp = fp
        if fp is not None and subformats:  # could be empty list
            fpStr = str(fp)
            noExtFpStr = os.path.splitext(fpStr)[0]
            writeDataStreamFp = noExtFpStr + '.musicxml'

        xmlFp: pathlib.Path = self.writeDataStream(writeDataStreamFp, dataBytes)

        if 'png' in subformats:
            defaults.title = savedDefaultTitle
            defaults.author = savedDefaultAuthor

        if (('png' in subformats or 'pdf' in subformats)
                and not str(environLocal['musescoreDirectPNGPath']).startswith('/skip')):
            from music21.converter.museScore import runThroughMuseScore
            outFp = runThroughMuseScore(xmlFp, subformats, **keywords)
        elif compress:
            archiveTools.compressXML(xmlFp,
                                     deleteOriginal=True,
                                     silent=True,
                                     strictMxlCheck=False)
            filenameOut = xmlFp.with_suffix('.mxl')
            outFp = common.pathTools.cleanpath(filenameOut, returnPathlib=True)
        else:
            outFp = xmlFp

        return outFp

    def show(self, obj, fmt, app=None, subformats=(), **keywords):  # pragma: no cover
        '''
        Override to do something with png
        '''
        returnedFilePath = self.write(obj, fmt, subformats=subformats, **keywords)
        if 'png' in subformats:
            fmt = 'png'
        elif 'pdf' in subformats:
            fmt = 'pdf'
        self.launch(returnedFilePath, fmt=fmt, app=app)

# ------------------------------------------------------------------------------
class ConverterMidi(SubConverter):
    '''
    Simple class wrapper for parsing MIDI and sending MIDI data out.
    '''
    readBinary = True
    registerFormats = ('midi',)
    registerInputExtensions = ('mid', 'midi')
    registerOutputExtensions = ('mid',)

    @property
    def encoding(self) -> str:
        if 'encoding' in self.keywords and self.keywords['encoding']:
            # if the encoding is set to None or '', it will be ignored
            return self.keywords['encoding']
        return 'utf-8'

    def parseData(self, strData, number=None, *, encoding: str = ''):
        '''
        Get MIDI data from a binary string representation.

        Calls midi.translate.midiStringToStream.

        Keywords to control quantization:
        `quantizePost` controls whether to quantize the output. (Default: True)
        `quarterLengthDivisors` allows for overriding the default quantization units
        in defaults.quantizationQuarterLengthDivisors. (Default: (4, 3)).

        If encoding is not provided use the encoding of the Converter
        (default "utf-8")
        '''
        from music21.midi import translate as midiTranslate
        keywords = {k: v for k, v in self.keywords.items()
                    if k not in ('encoding',)}
        self.stream = midiTranslate.midiStringToStream(
            strData,
            encoding=encoding or self.encoding,
            **keywords
        )

    def parseFile(self,
                  filePath: pathlib.Path|str,
                  number: int|None = None,
                  *,
                  encoding: str = '',
                  **keywords):
        '''
        Get MIDI data from a file path.

        Calls midi.translate.midiFilePathToStream.

        Keywords to control quantization:
        `quantizePost` controls whether to quantize the output. (Default: True)
        `quarterLengthDivisors` allows for overriding the default quantization units
        in defaults.quantizationQuarterLengthDivisors. (Default: (4, 3)).

        If encoding is not provided use the encoding of the Converter
        (default "utf-8")
        '''
        from music21.midi import translate as midiTranslate
        keywords = {k: v for k, v in self.keywords.items()
                    if k not in ('encoding',)}
        midiTranslate.midiFilePathToStream(
            filePath,
            inputM21=self.stream,
            encoding=encoding or self.encoding,
            **keywords
        )

    def write(self,
              obj,
              fmt,
              fp=None,
              subformats=(),
              *,
              addStartDelay: bool = False,
              encoding: str = '',
              **keywords):  # pragma: no cover
        from music21.midi import translate as midiTranslate
        if fp is None:
            fp = self.getTemporaryFile()

        mf = midiTranslate.music21ObjectToMidiFile(obj, addStartDelay=addStartDelay,
                                                   encoding=encoding or self.encoding)
        mf.open(fp, 'wb')  # write binary
        mf.write()
        mf.close()
        return fp

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------

# run command below to test commands that open museScore, etc.
    # music21.mainTest(TestExternal)
