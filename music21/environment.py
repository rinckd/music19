# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         environment.py
# Purpose:      Storage for user environment settings and defaults
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-2017 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
'''
The environment module describes an object for accessing and setting
variables related to the user's music21 environment. Such variables include
the location of external applications such as MusicXML readers (e.g. MuseScore),
whether music21 is allowed to download files directly (via the virtual corpus),
and other settings.

Additional documentation for and examples of using this module are found in
:ref:`User's Guide, Chapter 24, Environment <usersGuide_24_environment>`.

# TODO: Update to user's guide -- showing each function
'''
from __future__ import annotations

import io
import os
import pathlib
import sys
import tempfile
import typing as t
from typing import overload

import xml.etree.ElementTree as ET
from xml.sax import saxutils

from music21 import exceptions21
from music21 import common

# used below
_MOD = 'environment'

def etIndent(elem, level=0, spaces=2):
    '''
    indent an elementTree element for printing
    '''
    i = '\n' + level * spaces * ' '
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + spaces * ' '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subEl in elem:
            etIndent(subEl, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# -----------------------------------------------------------------------------

class EnvironmentException(exceptions21.Music21Exception):
    pass

class UserSettingsException(EnvironmentException):
    pass

# -----------------------------------------------------------------------------
# this must be above EnvironmentSingleton
class LocalCorpusSettings(list):
    '''
    A lightweight object for storing the 'LocalCorpusSettings' tag in the
    .music21rc

    It is a subclass of list and has two additional attributes, name (which
    should be None for the unnamed localCorpus) and cacheFilePath
    for a full filepath (ending in .json) as a location
    to store the .metadataBundle (.json) cache for the
    LocalCorpus.  This can be None, in which case the (volatile) temp
    directory is used.

    >>> lcs = environment.LocalCorpusSettings(['/tmp', '/home'])
    >>> lcs
    LocalCorpusSettings(['/tmp', '/home'])

    >>> lcs.name = 'theWholeEnchilada'
    >>> lcs
    LocalCorpusSettings(['/tmp', '/home'], name='theWholeEnchilada')

    >>> lcs.cacheFilePath = '/home/enchilada.json'
    >>> lcs
    LocalCorpusSettings(['/tmp', '/home'],
                        name='theWholeEnchilada',
                        cacheFilePath='/home/enchilada.json')

    >>> list(lcs)
    ['/tmp', '/home']
    >>> lcs.name
    'theWholeEnchilada'
    >>> lcs.cacheFilePath
    '/home/enchilada.json'
    >>> '/home' in lcs
    True
    >>> '/root' in lcs
    False
    '''

    def __init__(self, paths=None, name=None, cacheFilePath=None):
        if paths is None:
            paths = []
        super().__init__(paths)
        self.name = name
        self.cacheFilePath = cacheFilePath

    def __repr__(self):
        listRepr = super().__repr__()
        namePart = ''
        mdbpPart = ''
        if self.name is not None:
            namePart = ', name=' + repr(self.name)
        if self.cacheFilePath is not None:
            mdbpPart = ', cacheFilePath=' + repr(self.cacheFilePath)
        return f'LocalCorpusSettings({listRepr}{namePart}{mdbpPart})'

# -----------------------------------------------------------------------------

class _EnvironmentCore:
    '''
    This private class should never be directly created; use the Environment
    object to access this object.

    Multiple Environment instances may exist, but all share access to the same
    _EnvironmentCore instance that is stored in this module.

    The only case in which a new _EnvironmentCore is created is if the
    forcePlatform argument is passed and is different from the stored
    forcePlatform argument. This is only used in testing--it allows authors to
    test what the settings on a different platform (win, Mac, etc.) would be.

    NOTE: this is a private class. All documentation for public methods should
    be placed in the Environment class.
    '''

    # INITIALIZER #

    def __init__(self, forcePlatform=None):
        # only create one
        # sys.stderr.write('creating singleton _EnvironmentCore\n')
        self._ref = {}
        # define all settings that are paths
        # store names of all values that are keys; check for validity
        self._keysToPaths = []
        for pathKey in [
            'graphicsPath',
            'localCorpusPath',
            'manualCoreCorpusPath',
            'midiPath',
            'musescoreDirectPNGPath',
            'musicxmlPath',
            'pdfPath',
            'vectorPath',
        ]:
            self._keysToPaths.append(pathKey)

        # defines all valid keys in ref
        self._loadDefaults(forcePlatform=forcePlatform)
        # read will only overwrite values if set in field
        if forcePlatform is None:  # only read if not forcing platform
            self.read()  # load a stored file if available
        self.defaultRootTempDir = None

    # SPECIAL METHODS #

    def __getitem__(self, key):
        # could read file here to update from disk
        # could store last update time and look if file is more recent
        # how, only doing read once is a bit more conservative
        # self.read()

        # note: this will not get 'localCorpusPath' as there may be more than
        # one value
        if key not in self._ref and key != 'localCorpusPath':
            raise EnvironmentException(f'no preference: {key}')

        if key != 'localCorpusPath':
            value = self._ref[key]
        else:
            paths = list(self._ref['localCorpusSettings'])
            if len(paths) > 0:
                value = paths[0]
            else:
                value = ''

        if isinstance(value, bytes):
            value = value.decode(encoding='utf-8', errors='replace')

        valueStr = str(value).lower()

        if key == 'debug':  # debug expects a number
            if valueStr == 'true':
                value = common.DEBUG_USER
            elif valueStr == 'false':
                value = common.DEBUG_OFF
            elif 'off' in valueStr:
                value = common.DEBUG_OFF
            elif 'user' in valueStr:
                value = common.DEBUG_USER
            elif 'devel' in valueStr:
                value = common.DEBUG_DEVEL
            elif 'all' in valueStr:
                value = common.DEBUG_ALL
            else:
                value = int(value)

        if value is not None and value != '':
            if key in self.getKeysToPaths():
                value = pathlib.Path(value)
        else:
            value = None  # return None for values not set
        return value

    def __repr__(self):
        return '<Environment>'

    def __setitem__(self, key, value):
        # saxutils.escape  # used for escaping strings going to xml
        # with unicode encoding
        # http://www.xml.com/pub/a/2002/11/13/py-xml.html?page=2
        # saxutils.escape(msg).encode('UTF-8')

        # add local corpus path as a key
        # if isinstance(value, bytes):
        #    value = value.decode(errors='replace')
        if 'path' in key.lower() and value is not None:
            value = common.cleanpath(value, returnPathlib=False)

        if key not in self._ref:
            if key != 'localCorpusPath':
                raise EnvironmentException(f'no preference: {key}')
        if value == '':
            value = None  # always replace '' with None

        valid = False
        if key == 'showFormat':
            value = value.lower()
            if value in common.VALID_SHOW_FORMATS:
                valid = True
        elif key == 'writeFormat':
            value = value.lower()
            if value in common.VALID_WRITE_FORMATS:
                valid = True
        elif key == 'autoDownload':
            value = value.lower()
            if value in common.VALID_AUTO_DOWNLOAD:
                valid = True
        elif key == 'localCorpusSettings':
            # needs to be a list of strings for now
            if isinstance(value, LocalCorpusSettings):
                valid = True
        else:  # temporarily not validating other preferences
            valid = True

        if not valid:
            raise EnvironmentException(
                f'{value} is not an acceptable value for preference: {key}')

        # need to escape problematic characters for xml storage
        if isinstance(value, str):
            value = saxutils.escape(value)  # .encode('UTF-8')
        # set value
        if key == 'localCorpusPath':
            # only add if unique
            if str(value) not in self._ref['localCorpusSettings']:
                # check for malicious values here
                self._ref['localCorpusSettings'].append(str(value))
        else:
            self._ref[key] = value

    def __str__(self):
        return repr(self._ref)

    # PRIVATE METHODS #
    def _fromSettings(self, settingsTree, ref=None):
        '''
        Takes in a ElementTree and possibly an already populated reference dictionary
        (or creates a new one) and populates it.
        '''
        if ref is None:
            ref = {}
        settings = settingsTree.getroot()
        for slot in settings:
            if slot.tag == 'localCorpusSettings':
                lcs = LocalCorpusSettings()
                for slotChild in slot:
                    if slotChild.tag == 'localCorpusPath':
                        fpCandidate = slotChild.text.strip()
                        lcs.append(fpCandidate)
                    elif slotChild.tag == 'cacheFilePath':
                        lcs.cacheFilePath = slotChild.text.strip()
                ref['localCorpusSettings'] = lcs

            elif slot.tag == 'localCorporaSettings':
                ref['localCorporaSettings'] = {}
                for localCorpusSettings in slot:
                    name = localCorpusSettings.get('name')
                    lcs = LocalCorpusSettings()
                    lcs.name = name
                    for slotChild in localCorpusSettings:
                        if slotChild.tag == 'localCorpusPath':
                            fpCandidate = slotChild.text.strip()
                            lcs.append(fpCandidate)
                        elif slotChild.tag == 'cacheFilePath':
                            lcs.cacheFilePath = slotChild.text.strip()
                    ref['localCorporaSettings'][name] = lcs

            else:
                name = slot.get('name')
                value = slot.get('value')
                if name not in ref:
                    continue
                    # do not set, ignore for now
                else:  # load up stored values, overwriting defaults
                    ref[name] = value

    def _loadDefaults(self, forcePlatform=None):
        '''
        Load defaults.

        All keys are derived from these defaults.
        '''
        # path to a directory for temporary files
        self._ref['directoryScratch'] = None

        # path to a MusicXML reader: default, will find 'MuseScore'
        self._ref['musicxmlPath'] = None

        # path to a midi reader
        self._ref['midiPath'] = None

        # path to a graphics viewer
        self._ref['graphicsPath'] = None

        # path to a vector graphics viewer
        self._ref['vectorPath'] = None

        # path to a pdf viewer
        self._ref['pdfPath'] = None

        # path to MuseScore (if not the musicxmlPath)
        # for direct creation of PNG from MusicXML
        self._ref['musescoreDirectPNGPath'] = None
        self._ref['showFormat'] = 'musicxml'
        self._ref['writeFormat'] = 'musicxml'
        self._ref['ipythonShowFormat'] = 'ipython.musicxml.png'

        self._ref['autoDownload'] = 'ask'
        self._ref['debug'] = 0

        # printing of missing import warnings
        # default/non-zero is on
        self._ref['warnings'] = 1

        # store a list of strings
        self._ref['localCorpusSettings'] = LocalCorpusSettings()
        self._ref['localCorporaSettings'] = {}

        self._ref['manualCoreCorpusPath'] = None

        if forcePlatform is None:
            platform = common.getPlatform()
        else:
            platform = forcePlatform

        if platform == 'win':
            for name, value in [
                ('musicxmlPath',
                 common.cleanpath(r'%PROGRAMFILES%\MuseScore 3\bin\MuseScore3.exe')
                 ),
                ('musescoreDirectPNGPath',
                 common.cleanpath(r'%PROGRAMFILES%\MuseScore 3\bin\MuseScore3.exe')
                 ),
            ]:
                self[name] = value  # use for key checking
        elif platform == 'nix':
            for name, value in [
                ('musicxmlPath', '/usr/bin/mscore3'),
                ('musescoreDirectPNGPath', '/usr/bin/mscore3'),
                ('graphicsPath', '/usr/bin/xdg-open'),
                ('pdfPath', '/usr/bin/xdg-open')
            ]:
                self[name] = value  # use for key checking
        elif platform == 'darwin':
            versionTuple = common.macOSVersion()
            if versionTuple[0] >= 11 or (versionTuple[0] == 10 and versionTuple[1] >= 15):
                previewLocation = '/System/Applications/Preview.app'
            else:
                previewLocation = '/Applications/Preview.app'

            for name, value in [
                ('musicxmlPath',
                 '/Applications/MuseScore 3.app/Contents/MacOS/mscore'),
                ('graphicsPath', previewLocation),
                ('vectorPath', previewLocation),
                ('pdfPath', previewLocation),
                ('midiPath', '/Applications/GarageBand.app'),
                ('musescoreDirectPNGPath',
                 '/Applications/MuseScore 3.app/Contents/MacOS/mscore'),
            ]:
                self[name] = value  # use for key checking

    def _checkAccessibility(self, path: str|pathlib.Path|None) -> bool:
        '''
        Return True if the path exists, is readable and writable.
        '''
        if isinstance(path, (pathlib.Path, str)):
            exists = os.path.exists(path)
            readable = os.access(path, os.R_OK)
            writable = os.access(path, os.W_OK)
            return exists and readable and writable
        else:
            return False

    def toSettingsXML(self, ref=None):
        '''
        Convert a ref dictionary to an xml.etree.ElementTree.Element object
        with root "<settings>" and return that object
        '''
        if ref is None:
            ref = self._ref

        settingsDict = {'encoding': 'utf-8'}
        settings = ET.Element('settings', settingsDict)

        settingsTree = ET.ElementTree(settings)
        for key, value in sorted(ref.items()):
            lcs = value
            # assert isinstance(lcs, LocalCorpusSettings)
            if key == 'localCorpusSettings':
                localCorpusSettings = ET.Element('localCorpusSettings')
                for filePath in sorted(lcs):
                    localCorpusPath = ET.Element('localCorpusPath')
                    if filePath is not None:
                        localCorpusPath.text = str(filePath)
                    localCorpusSettings.append(localCorpusPath)
                if lcs.cacheFilePath is not None:
                    mdbp = ET.Element('cacheFilePath')
                    mdbp.text = str(lcs.cacheFilePath)
                    localCorpusSettings.append(mdbp)

                settings.append(localCorpusSettings)
            elif key == 'localCorporaSettings':
                localCorporaSettings = ET.Element('localCorporaSettings')
                for name, lcs in sorted(value.items()):
                    localCorpusSettings = ET.Element('localCorpusSettings', name=name)
                    for filePath in sorted(lcs):
                        localCorpusPath = ET.Element('localCorpusPath')
                        if filePath is not None:
                            localCorpusPath.text = str(filePath)
                        localCorpusSettings.append(localCorpusPath)
                    if lcs.cacheFilePath is not None:
                        mdbp = ET.Element('cacheFilePath')
                        mdbp.text = str(lcs.cacheFilePath)
                        localCorpusSettings.append(mdbp)

                    localCorporaSettings.append(localCorpusSettings)
                settings.append(localCorporaSettings)
            else:
                # value = fixBytes(value)
                attribs = {'name': key}
                if value is not None:
                    attribs['value'] = str(value)
                slot = ET.Element('preference', attribs)
                settings.append(slot)
        return settingsTree

    # PUBLIC METHODS #

    def getDefaultRootTempDir(self):
        # noinspection SpellCheckingInspection
        '''
        returns whatever tempfile.gettempdir() returns plus 'music21'.

        Creates the subdirectory if it doesn't exist:

        >>> import tempfile
        >>> import pathlib
        >>> tempFile = tempfile.gettempdir()
        >>> #_DOCS_SHOW tempFile
        '/var/folders/x5/rymq2tx16lqbpytwb1n_cc4c0000gn/T'

        >>> import os
        >>> e = environment.Environment()
        >>> e.getDefaultRootTempDir() == pathlib.Path(tempFile) / 'music21'
        True

        If failed to create the subdirectory (OSError is raised), this function
        will return (1), for Linux and Mac platforms, a subdirectory under the
        system temp directory which is named with 'music21-userid-$UID' or (2),
        for other platforms, a temporary directory which is created by
        tempfile.mkdtemp(prefix="music21-"), which is named with 'music21-'
        plus 8 hashed codes, and (3) if failing for both above, it will return
        the directory from tempfile.gettempdir(). The location of this directory
        depends on OS.

        Note the temporary directory may be different in each python session.
        '''
        if self._checkAccessibility(self.defaultRootTempDir):
            return self.defaultRootTempDir

        # this returns the root temp dir; this does not create a new dir
        self.defaultRootTempDir = pathlib.Path(tempfile.gettempdir()) / 'music21'

        # if this path already exists, readable and writable, we have nothing more to do
        if self._checkAccessibility(self.defaultRootTempDir):
            return self.defaultRootTempDir
        else:
            # make this directory as a temp directory
            try:
                self.defaultRootTempDir.mkdir()
            except OSError:  # directory already exists or permission denied
                if common.getPlatform() in ['nix', 'darwin']:
                    uid = os.getuid()
                    dir_path = pathlib.Path(tempfile.gettempdir()) / f'music21-userid-{uid}'
                else:
                    dir_path = pathlib.Path(tempfile.mkdtemp(prefix='music21-'))

                if self._checkAccessibility(dir_path):
                    self.defaultRootTempDir = dir_path
                else:
                    try:
                        dir_path.mkdir()
                        self.defaultRootTempDir = dir_path
                    except OSError:  # pragma: no cover
                        # Give up and use /tmp
                        self.defaultRootTempDir = pathlib.Path(tempfile.gettempdir())

            return self.defaultRootTempDir

    def getKeysToPaths(self):
        '''
        Find all keys that refer to paths

        >>> e = environment.Environment()
        >>> for i in e.getKeysToPaths():
        ...     #_DOCS_SHOW print(i)
        ...     pass #_DOCS_HIDE

        graphicsPath
        lilypondPath
        ...
        '''
        return self._keysToPaths

    def getRefKeys(self):
        '''
        Find all keys (in any order)...

        >>> e = environment.Environment()
        >>> for i in e.getRefKeys():
        ...     #_DOCS_SHOW print(i)
        ...     pass #_DOCS_HIDE

        lilypondBackend
        pdfPath
        lilypondVersion
        graphicsPath
        ...
        '''
        # list() is for python3 compatibility
        return list(self._ref.keys())

    def getRootTempDir(self):
        '''
        gets either the directory in key 'directoryScratch' or self.getDefaultRootTempDir

        Returns an exception if directoryScratch is defined but does not exist.

        Returns a pathlib.Path
        '''
        if self._ref['directoryScratch'] is None:
            return self.getDefaultRootTempDir()
        # check that the user-specified directory exists

        refDir = pathlib.Path(self._ref['directoryScratch'])

        if not refDir.exists():
            raise EnvironmentException(
                'user-specified scratch directory ({!s}) does not exist; '
                'remove preference file or reset Environment'.format(
                    refDir))
        return refDir

    def getSettingsPath(self):
        '''
        Return a pathlib.Path object to the '.music21rc' object
        '''
        platform = common.getPlatform()
        if 'USERPROFILE' in os.environ:
            userProfilePath = pathlib.Path(os.environ['USERPROFILE']) / 'Application Data'
        else:
            userProfilePath = None

        if platform == 'win':
            # try to use defined app data directory for preference file
            # this is not available on all windows versions
            if 'APPDATA' in os.environ:
                directory = pathlib.Path(os.environ['APPDATA'])
            elif userProfilePath:
                directory = userProfilePath
            else:  # use home directory
                directory = pathlib.Path(os.path.expanduser('~'))
            return directory / 'music21-settings.xml'
        elif platform in ['nix', 'darwin']:
            # might not exist if running as nobody in a webserver
            if 'HOME' in os.environ and os.access(os.environ['HOME'], os.W_OK):
                directory = pathlib.Path(os.environ['HOME'])
            else:
                directory = pathlib.Path('/tmp/')
            return directory / '.music21rc'
        # darwin specific option
        # os.path.join(os.environ['HOME'], 'Library',)

    def getTempFile(self, suffix='', returnPathlib=True) -> str|pathlib.Path:
        '''
        Gets a temporary file with a suffix that will work for a bit.

        v5 -- added returnPathlib.
        v6 -- returnPathlib defaults to True

        OMIT_FROM_DOCS
        >>> e = environment.Environment()
        >>> tmp1 = e.getTempFile(returnPathlib=False)
        >>> isinstance(tmp1, str)
        True
        >>> import pathlib
        >>> tmp2 = e.getTempFile()
        >>> isinstance(tmp2, pathlib.Path)
        True
        >>> import os
        >>> os.remove(tmp1)
        >>> os.remove(tmp2)
        '''
        # get the root dir, which may be the user-specified dir
        rootDir = self.getRootTempDir()
        if suffix and not suffix.startswith('.'):
            suffix = '.' + suffix

        with tempfile.NamedTemporaryFile(dir=rootDir, suffix=suffix, delete=False) as ntf:
            ntf_name = ntf.name

        if returnPathlib:
            return pathlib.Path(ntf_name)
        else:
            return ntf_name

    def keys(self):
        return list(self._ref.keys()) + ['localCorpusPath']

    def formatToKey(self, m21Format):
        '''
        Finds the appropriate key to the file/app that can launch the given format:

        >>> e = environment.Environment()
        >>> e.formatToKey('png')
        'graphicsPath'
        >>> e.formatToKey('jpeg')
        'graphicsPath'
        >>> e.formatToKey('svg')
        'vectorPath'
        >>> e.formatToKey('pdf')
        'pdfPath'
        >>> e.formatToKey('musicxml')
        'musicxmlPath'
        >>> e.formatToKey('midi')
        'midiPath'

        returns None if there is no key for this format (whether the format exists or not)

        >>> e.formatToKey('ipython') is None  # actual format
        True
        >>> e.formatToKey('adobePhotoshop') is None  # not a music21 format
        True
        '''
        environmentKey = None
        if m21Format in ('png', 'jpeg'):
            environmentKey = 'graphicsPath'
        elif m21Format == 'svg':
            environmentKey = 'vectorPath'
        elif m21Format == 'pdf':
            environmentKey = 'pdfPath'
        elif m21Format in ('musicxml',):
            environmentKey = 'musicxmlPath'
        elif m21Format == 'midi':
            environmentKey = 'midiPath'
        return environmentKey

    def formatToApp(self, m21Format):
        '''
        Given a format, return the app that will launch it.
        '''
        environmentKey = self.formatToKey(m21Format)
        if environmentKey is not None:
            if environmentKey not in self._ref:
                raise EnvironmentException(environmentKey + ' is not set in UserSettings. ')
            return self._ref[environmentKey]
        return None

    def read(self, filePath=None):
        '''
        Read the environment file from .music21rc and call _fromSettings
        Called only once per music21 instance.
        '''
        if filePath is None:
            filePath = self.getSettingsPath()
        if not filePath.exists():
            return None  # do nothing if no file exists

        try:
            settingsTree = ET.parse(str(filePath))
        except ET.ParseError as pe:
            raise EnvironmentException(
                f'Cannot parse file {filePath}: {str(pe)}'
            ) from pe
        # load from XML into dictionary
        # updates self._ref in place
        self._fromSettings(settingsTree, self._ref)

    def restoreDefaults(self):
        '''
        Changes everything to default but does not write.
        '''
        self._ref = {}
        self._loadDefaults()  # defines all valid keys in ref

    def write(self, filePath=None):
        '''
        Write the .music21rc using `.getSettingsPath` and `.toSettingsXML`.
        '''
        if filePath is None:
            filePath = self.getSettingsPath()
        # need to use __getitem__ here b/c need to convert debug value
        # to an integer
        if filePath is None or not filePath.parent.exists():
            raise EnvironmentException(f'bad file path for .music21rc: {filePath}')
        settingsTree = self.toSettingsXML()
        etIndent(settingsTree.getroot())

        # uncomment to figure out where something in the test set is writing .music21rc
        # import traceback
        # traceback.print_stack()
        settingsTree.write(str(filePath), encoding='utf-8')

# -----------------------------------------------------------------------------

# store one singleton instance of _EnvironmentCore within this module
# this is a module-level implementation of the singleton pattern
# reloading the module will force a recreation of the module
# noinspection PyDictCreation
_environStorage = {'instance': _EnvironmentCore(), 'forcePlatform': None}

def envSingleton():
    '''
    returns the _environStorage['instance'], _EnvironmentCore singleton
    object
    '''
    return _environStorage['instance']

# -----------------------------------------------------------------------------

class Environment:
    '''
    The environment.Environment object stores user preferences as a
    dictionary-like object.  Additionally, the Environment object provides
    convenience methods to music21 modules for getting temporary files,
    launching files with external applications, and printing debug and warning
    messages.

    Generally, each module creates a single, module-level instance of
    Environment, passing the module's name during creation. (This is an
    efficient operation since the Environment module caches most information
    from module to module)

    For a more user-friendly interface for creating and editing settings, see
    the :class:`~music21.environment.UserSettings` object.

    >>> env = environment.Environment(forcePlatform='darwin')
    >>> env['musicxmlPath'] = '/Applications/Finale Reader.app'
    >>> env['musicxmlPath']
    PosixPath('/Applications/Finale Reader.app')
    '''

    # Defines the order of presenting names in the documentation; use strings
    _DOC_ORDER = ['read', 'write', 'getSettingsPath']

    # documentation for all attributes (not properties or methods)
    _DOC_ATTR: dict[str, str] = {
        'modNameParent': '''
            A string representation of the module that contains this
            Environment instance.
            ''',
    }

    # INITIALIZER #

    def __init__(self, modName=None, forcePlatform=None):
        '''
        Create an instance of this object, reading settings from disk.

        When created from a module, the `modName` parameter stores a string
        naming the module. This is used to identify the output of printDebug()
        calls.

        The `forcePlatform` argument can be used for testing what the
        environment settings would look like on another OS platform (e.g., win,
        nix, darwin).

        >>> myEnv = environment.Environment()
        >>> post = myEnv['writeFormat']
        >>> #_DOCS_SHOW post
        >>> print("\'musicxml\'") #_DOCS_HIDE
        'musicxml'
        '''
        self.modNameParent = modName
        # only re-create the instance if forcing a different platform
        # this only happens in testing
        # otherwise, delegate all calls to the module-level instance
        if forcePlatform != _environStorage['forcePlatform']:
            _environStorage['instance'] = _EnvironmentCore(forcePlatform=forcePlatform)

    # SPECIAL METHODS #

    def __getitem__(self, key):
        return envSingleton().__getitem__(key)

    def __repr__(self):
        return repr(envSingleton())

    def __setitem__(self, key, value):
        '''
        Dictionary-like setting. Changes are made only to local dictionary.

        Must call write() to make permanent:

        >>> from pathlib import Path
        >>> a = environment.Environment()
        >>> a['debug'] = 1
        >>> a['graphicsPath'] = '/test&Encode'
        >>> 'test&amp;Encode' in str(a['graphicsPath'])
        True
        >>> isinstance(a['graphicsPath'], Path)
        True

        >>> a['autoDownload'] = 'asdf'
        Traceback (most recent call last):
        music21.environment.EnvironmentException: asdf is not an acceptable
            value for preference: autoDownload

        >>> a['showFormat'] = 'asdf'
        Traceback (most recent call last):
        music21.environment.EnvironmentException: asdf is not an acceptable
            value for preference: showFormat

        >>> a['showFormat'] = 'musicxml'
        >>> a['localCorpusPath'] = '/path/to/local'
        '''
        envSingleton().__setitem__(key, value)

    def __str__(self):
        return str(envSingleton())

    # PUBLIC METHODS #

    def getDefaultRootTempDir(self):
        '''
        Use the Python tempfile.gettempdir() to get the system specified
        temporary directory, and try to add a new 'music21' directory, and then
        return this directory.

        This method is only called if the no scratch directory preference has
        been set.

        If not able to create a 'music21' directory, the standard default is
        returned.

        Returns a pathlib.Path
        '''
        dstDir = envSingleton().getDefaultRootTempDir()
        self.printDebug([_MOD, 'using temporary directory:', str(dstDir)])
        return dstDir

    def getKeysToPaths(self):
        '''
        Get the keys that refer to file paths.

        >>> a = environment.Environment()
        >>> for x in sorted(a.getKeysToPaths()):
        ...     x
        ...
        'graphicsPath'
        'lilypondPath'
        'localCorpusPath'
        'manualCoreCorpusPath'
        'midiPath'
        'musescoreDirectPNGPath'
        'musicxmlPath'
        'pdfPath'
        'vectorPath'

        '''
        return envSingleton().getKeysToPaths()

    def getRefKeys(self):
        '''
        Get the raw keys stored in the internal reference dictionary.

        These are different from the keys() method in that the
        'localCorpusPath' entry is not included.

        >>> a = environment.Environment()
        >>> for x in sorted(a.getRefKeys()):
        ...     x
        ...
        'autoDownload'
        'debug'
        'directoryScratch'
        'graphicsPath'
        'ipythonShowFormat'
        'lilypondBackend'
        'lilypondFormat'
        'lilypondPath'
        'lilypondVersion'
        'localCorporaSettings'
        'localCorpusSettings'
        'manualCoreCorpusPath'
        'midiPath'
        'musescoreDirectPNGPath'
        'musicxmlPath'
        'pdfPath'
        'showFormat'
        'vectorPath'
        'warnings'
        'writeFormat'
        '''
        return envSingleton().getRefKeys()

    def getRootTempDir(self):
        '''
        Return a directory for writing temporary files. This does not create a
        new directory for each use, but either uses the user-set preference or
        gets the system-provided directory (with a music21 subdirectory, if
        possible).
        '''
        return envSingleton().getRootTempDir()

    def getSettingsPath(self):
        '''
        Return the path to the platform specific settings file.
        '''
        return envSingleton().getSettingsPath()

    @overload
    def getTempFile(self, suffix: str, returnPathlib: t.Literal[False]) -> str:
        ...

    @overload
    def getTempFile(self, suffix: str = '', returnPathlib: t.Literal[True] = True) -> pathlib.Path:
        ...

    def getTempFile(self, suffix: str = '', returnPathlib=True) -> str|pathlib.Path:
        '''
        Return a file path to a temporary file with the specified suffix (file
        extension).

        v5 -- added returnPathlib.
        v6 -- returnPathlib defaults to True.
        '''
        filePath = envSingleton().getTempFile(suffix=suffix, returnPathlib=returnPathlib)
        self.printDebug([_MOD, 'temporary file:', filePath])
        return filePath

    def keys(self):
        '''
        Return valid keys to get and set values for the Environment instance.

        >>> e = environment.Environment()
        >>> for x in sorted(list(e.keys())):
        ...     x
        ...
        'autoDownload'
        'debug'
        'directoryScratch'
        'graphicsPath'
        'ipythonShowFormat'
        'lilypondBackend'
        'lilypondFormat'
        'lilypondPath'
        'lilypondVersion'
        'localCorporaSettings'
        'localCorpusPath'
        'localCorpusSettings'
        'manualCoreCorpusPath'
        'midiPath'
        'musescoreDirectPNGPath'
        'musicxmlPath'
        'pdfPath'
        'showFormat'
        'vectorPath'
        'warnings'
        'writeFormat'
        '''
        return envSingleton().keys()

    def formatToApp(self, m21Format):
        return envSingleton().formatToApp(m21Format)

    def formatToKey(self, m21Format):
        return envSingleton().formatToKey(m21Format)

    def printDebug(self, msg, statusLevel=common.DEBUG_USER):
        '''
        Format one or more data elements into string, and print it to stderr.
        The first arg can be a list of strings or a string; lists are
        concatenated with common.formatStr().
        '''
        if envSingleton()['debug'] >= statusLevel:
            if isinstance(msg, str):
                msg = [msg]  # make into a list
            if msg[0] != self.modNameParent and self.modNameParent is not None:
                msg = [self.modNameParent + ':'] + msg
            # pass list to common.formatStr
            msg = common.formatStr(*msg)
            sys.stderr.write(msg)

    def read(self, filePath=None):
        '''
        Load an XML preference file if and only if the file is available
        and has been written in the past. This means that no preference file
        will ever be written unless manually done so. If no preference file
        exists, the method returns None.
        '''
        return envSingleton().read(filePath=filePath)

    def restoreDefaults(self):
        '''
        Restore only defaults for all parameters. Useful for testing.

        >>> a = environment.Environment()
        >>> a['debug'] = 1
        >>> a.restoreDefaults()
        >>> a['debug']
        0

        And we can ``read()`` the environment settings back from our
        configuration file to restore our normal working environment.

        >>> a = environment.Environment().read()
        '''
        envSingleton().restoreDefaults()

    def warn(self, msg, header=None):
        '''
        To print a warning to the user, send a list of strings to this method.
        Similar to printDebug but even if debug is off.
        '''
        if isinstance(msg, str):
            msg = [msg]  # make into a list
        elif isinstance(msg, dict):
            msg = [repr(msg)]
        elif common.isNum(msg):
            msg = [str(msg)]
        elif isinstance(msg, Exception):
            msg = [str(msg)]

        if header is None:
            if msg[0] != self.modNameParent and self.modNameParent is not None:
                msg = [self.modNameParent + ': WARNING:'] + msg
        else:
            msg = [header] + msg
        msg = common.formatStr(*msg)
        sys.stderr.write(msg)

    def write(self, filePath=None):
        '''
        Write an XML preference file. This must be manually called to store
        any changes made to the object and access preferences later.
        If `filePath` is None, the default storage location will be used.
        '''
        return envSingleton().write(filePath=filePath)

    def xmlReaderType(self):
        r'''
        Returns an xmlReaderType depending on the 'musicxmlPath'

        >>> a = environment.Environment()
        >>> original = a['musicxmlPath']  #_DOCS_HIDE
        >>> a['musicxmlPath'] = '/Applications/Musescore.app'
        >>> a.xmlReaderType()
        'Musescore'
        >>> a['musicxmlPath'] = '/Applications/Sibelius 7.app'
        >>> a.xmlReaderType()
        'Sibelius'
        >>> a['musicxmlPath'] = r'C:\Program Files\Finale\Finale 2014.exe'
        >>> a.xmlReaderType()
        'Finale'

        Nostalgia is unknown...

        >>> a['musicxmlPath'] = r'C:\Program Files\Deluxe Music Construction Set.exe'
        >>> a.xmlReaderType()
        'unknown'

        >>> a['musicxmlPath'] = None
        >>> a.xmlReaderType() is None
        True

        >>> a['musicxmlPath'] = original  #_DOCS_HIDE
        '''
        xp = self['musicxmlPath']
        if common.runningInNotebook():
            xp = self['musescoreDirectPNGPath']

        if not xp:
            return None
        xp = str(xp).lower()
        if 'sibelius' in xp:
            return 'Sibelius'
        elif 'finale' in xp:
            return 'Finale'
        elif 'musescore' in xp:
            return 'Musescore'
        else:
            return 'unknown'

# -----------------------------------------------------------------------------

class UserSettings:
    '''
    The UserSettings object provides a simple interface for configuring the
    user preferences in the :class:`~music21.environment.Environment` object.

    It automatically writes all changes to disk.

    First, create an instance of UserSettings:

    >>> us = environment.UserSettings()

    Second, view the available settings keys.

    >>> for key in sorted(us.keys()):
    ...     key
    'autoDownload'
    'debug'
    'directoryScratch'
    'graphicsPath'
    'ipythonShowFormat'
    'lilypondBackend'
    'lilypondFormat'
    'lilypondPath'
    'lilypondVersion'
    'localCorporaSettings'
    'localCorpusPath'
    'localCorpusSettings'
    'manualCoreCorpusPath'
    'midiPath'
    'musescoreDirectPNGPath'
    'musicxmlPath'
    'pdfPath'
    'showFormat'
    'vectorPath'
    'warnings'
    'writeFormat'

    Third, after finding the desired setting, supply the new value as a Python
    dictionary key value pair. Setting this value updates the user's settings
    file. For example, to set the file path to the Application that will be
    used to open MusicXML files, use the 'musicxmlPath' key.

    >>> #_DOCS_SHOW us['musicxmlPath'] = '/Applications/Finale Reader.app'
    >>> #_DOCS_SHOW us['musicxmlPath']
    '/Applications/Finale Reader.app'

    Note that the 'localCorpusPath' setting operates in a slightly different
    manner than other settings. Each time the 'localCorpusPath' setting is set,
    an additional local corpus file path is added to the list of local corpus
    paths (unless that path is already defined in the list of local corpus
    paths). To view all local corpus paths, access the 'localCorpusSettings'
    settings. This setting can also be used to set a complete list of file
    paths.

    >>> #_DOCS_SHOW us['localCorpusPath'] = '~/Documents'
    >>> #_DOCS_SHOW list(us['localCorpusSettings'])
    ['~/Documents']

    Alternatively, the environment.py module provides convenience functions for
    setting these settings: :func:`~music21.environment.keys`,
    :func:`~music21.environment.get`, and :func:`~music21.environment.set`.
    '''

    # INITIALIZER #

    def __init__(self):
        # store environment as a private attribute
        self._environment = Environment()

    # SPECIAL METHODS #

    def __getitem__(self, key):
        # location specific, cannot test further
        return self._environment.__getitem__(key)

    def __repr__(self):
        '''
        Return a string representation.

        >>> us = environment.UserSettings()
        >>> post = repr(us)  # location specific, cannot test
        '''
        return repr(self._environment)

    def __str__(self):
        '''
        Return a string representation.

        >>> us = environment.UserSettings()
        >>> post = repr(us)  # location specific, cannot test
        '''
        return str(self._environment)

    def __setitem__(self, key, value):
        '''
        Dictionary-like setting. Changes are made and written to the user
        configuration file.

        >>> us = environment.UserSettings()
        >>> us['musicxmlPath'] = 'asdf/asdf/asdf'
        Traceback (most recent call last):
        music21.environment.UserSettingsException: attempting to set a value
            to a path that does not exist: ...asdf

        >>> us['localCorpusPath'] = '/path/to/local'
        Traceback (most recent call last):
        music21.environment.UserSettingsException: attempting to set a value
            to a path that does not exist: ...local
        '''
        # NOTE: testing setting of any UserSettings key will result
        # in a change in your local preferences files

        # before setting value, see if this is a path and test existence
        # this will accept localCorpusPath
        if key in self._environment.getKeysToPaths():
            # try to expand user if found; otherwise return unaltered
            if value is not None and not str(value).startswith('/skip'):
                value = common.cleanpath(value, returnPathlib=False)
                if not os.path.exists(value):
                    raise UserSettingsException(
                        f'attempting to set a value to a path that does not exist: {value}')
        # when setting a local corpus setting, if not a list, append
        elif key == 'localCorpusSettings':
            if not common.isListLike(value):
                raise UserSettingsException(
                    'localCorpusSettings must be provided as a list.')
        elif key == 'localCorporaSettings':
            if not isinstance(value, dict):
                raise UserSettingsException(
                    'localCorporaSettings must be provided as a dict.')
            if value:
                for innerKey, innerValue in value.values():
                    if not isinstance(innerKey, str):
                        raise UserSettingsException(
                            'Each key in localCorporaSettings must be a string.')
                    if not common.isListLike(innerValue):
                        raise UserSettingsException(
                            'Each entry in localCorporaSettings must point to a list.')

        # location specific, cannot test further
        self._environment.__setitem__(key, value)
        self._environment.write()
        # self._updateAllEnvironments()

    # PUBLIC METHODS #

    def create(self):
        '''
        If an environment configuration file does not exist, create one based on
        the default settings.
        '''
        if not self._environment.getSettingsPath().exists():
            self._environment.write()
        else:
            raise UserSettingsException(
                'An environment configuration file already exists; '
                'simply set values to modify.')

    def delete(self):
        '''
        Permanently remove the user configuration file.
        '''
        if self._environment.getSettingsPath().exists():
            self._environment.getSettingsPath().unlink()
        else:
            raise UserSettingsException(
                'An environment configuration file does not exist.')

    def getSettingsPath(self):
        '''
        Return the path to the platform specific settings file.
        '''
        return self._environment.getSettingsPath()

    def keys(self):
        '''
        Return the keys found in the user's
        :class:`~music21.environment.Environment` object.
        '''
        return self._environment.getRefKeys() + ['localCorpusPath']

    def restoreDefaults(self):
        '''
        Restore platform specific defaults.
        '''
        # location specific, cannot test further
        self._environment.restoreDefaults()
        self._environment.write()

# -----------------------------------------------------------------------------
# convenience routines for accessing UserSettings.

def keys():
    '''
    Return all valid UserSettings keys.
    '''
    us = UserSettings()
    return us.keys()

# pylint: disable=redefined-builtin
# noinspection PyShadowingBuiltins
def set(key, value):  # okay to override set here: @ReservedAssignment
    '''
    Directly set a single UserSettings key, by providing a key and the
    appropriate value. This will create a user settings file if necessary.

    >>> environment.set('wer', 'asdf')
    Traceback (most recent call last):
    music21.environment.EnvironmentException: no preference: wer

    >>> #_DOCS_SHOW environment.set('musicxmlPath', '/Applications/Finale Reader.app')
    '''
    us = UserSettings()
    try:
        us.create()  # no problem if this does not exist
    except UserSettingsException:
        pass  # this means it already exists
    us[key] = value  # this may raise an exception

def get(key):
    '''
    Return the current setting of a UserSettings key.

    This will create a user settings file if necessary:

    >>> #_DOCS_SHOW environment.get('musicxmlPath')
    '/Applications/Finale Reader.app'
    '''
    us = UserSettings()
    return us[key]

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------

_DOC_ORDER = [UserSettings, Environment, LocalCorpusSettings]
