# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         commonTest.py
# Purpose:      Things common to testing
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2009-15 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Things that are common to testing.
'''
from __future__ import annotations

import copy
import doctest
import importlib
import importlib.util
import os
import sys
import typing
import types
import unittest
import unittest.runner
from unittest.signals import registerResult
import warnings

import music21
from music21 import environment
from music21 import common

environLocal = environment.Environment('test.commonTest')

def testCopyAll(testInstance: unittest.TestCase, globals_: typing.Dict[str, typing.Any]):
    my_module = testInstance.__class__.__module__
    for part, obj in globals_.items():
        match = False
        for skip in ['_', 'Test', 'Exception']:
            if part.startswith(skip) or part.endswith(skip):
                match = True
        if match:
            continue
        # noinspection PyTypeChecker
        if not callable(obj) or isinstance(obj, types.FunctionType):
            continue
        if not hasattr(obj, '__module__') or obj.__module__ != my_module:
            continue

        try:  # see if obj can be made w/o args
            instance = obj()
        except TypeError:
            continue

        try:
            copy.copy(instance)
        except Exception as e:  # pylint: disable=broad-exception-caught
            testInstance.fail(f'Could not copy obj {part}: {e}')
        try:
            copy.deepcopy(instance)
        except Exception as e:  # pylint: disable=broad-exception-caught
            testInstance.fail(f'Could not deepcopy obj {part}: {e}')


def load_source(name: str, path: str) -> types.ModuleType:
    '''
    Replacement for deprecated imp.load_source()

    Thanks to:
    https://github.com/epfl-scitas/spack for pointing out the
    important missing "spec.loader.exec_module(module)" line.
    '''
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f'No such file or directory: {path!r}')
    if name in sys.modules:
        module = sys.modules[name]
    else:
        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise FileNotFoundError(f'No such file or directory: {path!r}')
        sys.modules[name] = module
    spec.loader.exec_module(module)

    return module

# noinspection PyPackageRequirements
def testImports():
    '''
    Test that all optional packages needed for test suites are installed
    '''
    # pylint: disable=unused-import
    try:
        import scipy  # type: ignore
    except ImportError as e:
        raise ImportError('pip install scipy : needed for running test suites') from e

    try:
        from Levenshtein import StringMatcher  # type: ignore
    except ImportError as e:
        raise ImportError('pip install python-Levenshtein : needed for running test suites') from e

    # Lilypond support removed - no longer required for test suites
    # from music21.lily.translate import LilypondConverter, LilyTranslateException
    # try:
    #     LilypondConverter()
    # except LilyTranslateException as e:
    #     raise ImportError('lilypond must be installed to run test suites') from e

def defaultDoctestSuite(name=None):
    globs = __import__('music21').__dict__.copy()
    docTestOptions = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    keywords = {
        'globs': globs,
        'optionflags': docTestOptions,
    }
    # in case there are any tests here, get a suite to load up later
    if name is not None:
        s1 = doctest.DocTestSuite(name, **keywords)
    else:
        s1 = doctest.DocTestSuite(**keywords)
    return s1

# from testRunner
# more silent type


class Music21TestRunner(unittest.runner.TextTestRunner):
    def run(self, test):
        '''
        Run the given test case or test suite.
        '''
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        with warnings.catch_warnings():
            if hasattr(self, 'warnings') and self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ('default', 'always'):
                    warnings.filterwarnings('module',
                                            category=DeprecationWarning,
                                            message=r'Please use assert\w+ instead.')
            # startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            # stopTime = time.time()
        # timeTaken = stopTime - startTime
        result.printErrors()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write('FAILED')
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append(f'failures={failed}')
            if errored:
                infos.append(f'errors={errored}')
        else:
            pass
        if skipped:
            infos.append(f'skipped={skipped}')
        if expectedFails:
            infos.append(f'expected failures={expectedFails}')
        if unexpectedSuccesses:
            infos.append(f'unexpected successes={unexpectedSuccesses}')
        if infos:
            joined = ', '.join(infos)
            self.stream.writeln(f' ({joined})')
        else:
            pass
        return result

# ------------------------------------------------------------------------------


class ModuleGather:
    r'''
    Utility class for gathering and importing all modules in the music21
    package. Puts them in self.modulePaths.

    >>> from music21.test import commonTest
    >>> mg = commonTest.ModuleGather(useExtended=True)
    >>> #_DOCS_SHOW print(mg.modulePaths[0])
    D:\Web\eclipse\music21base\music21\volume.py
    '''

    def __init__(self, useExtended=False, autoWalk=True):
        self.dirParent = str(common.getSourceFilePath())
        self.useExtended = useExtended
        self.modulePaths = []

        self.moduleSkip = [
            'testSingleCoreAll.py',
            'testExternal.py',
            'testDefault.py',
            'testInstallation.py',
            'testLint.py',
            'testPerformance.py',
            'timeGraphs.py',
            'timeGraphImportStar.py',
            'multiprocessTest.py',
            'setup.py',  # somehow got committed once and now screwing things up

            # 'corpus/virtual.py',  # offline for v.4+
            'figuredBass/examples.py',  # 40 seconds and runs fine

        ]

        self.moduleSkipExtended = self.moduleSkip + [
            'configure.py',  # runs oddly

            'testSerialization.py',
            'mptCurses.py',
            'memoryUsage.py',

            'test/treeYield.py',
            'test/toggleDebug.py',

            'musicxml/testPrimitive.py',
            'musicxml/testFiles.py',
            'musedata/testPrimitive/test01/__init__.py',
            'musedata/testPrimitive/__init__.py',
            'mei/test_base.py',
            'humdrum/questions.py',

            'documentation/upload.py',
            'documentation/source/conf.py',
            'documentation/extensions.py',

            'corpus/testCorpus.py',
            'audioSearch/scoreFollower.py',
            'audioSearch/repetitionGame.py',
            'abcFormat/testFiles.py',
        ]
        # run these first
        self.slowModules = ['metadata/bundles',
                            'metadata/caching',
                            'features',
                            'graph',
                            'graph/plot',
                            'graph/axis',
                            'graph/primitives',
                            'freezeThaw',
                            'figuredBass/realizer',
                            'features/jSymbolic',
                            'features/native',
                            'figuredBass/examples',
                            'stream/tests',
                            'analysis/windowed',
                            'converter/__init__',

                            'musicxml/test_m21ToXml',
                            'musicxml/test_xmlToM21',

                            'romanText/translate',
                            'corpus/testCorpus',
                            'corpus/corpora',
                            'audioSearch/transcriber',
                            'audioSearch/__init__',
                            'alpha/theoryAnalysis/theoryAnalyzer',
                            ]

        # skip any path that contains this string
        self.pathSkip = []  # 'music21/ext',  # not just 'ext' because of 'text!'
        self.pathSkipExtended = self.pathSkip + []

        self.moduleSkip = [x.replace('/', os.sep) for x in self.moduleSkip]
        self.moduleSkipExtended = [x.replace('/', os.sep) for x in self.moduleSkipExtended]
        self.pathSkip = [x.replace('/', os.sep) for x in self.pathSkip]
        self.pathSkipExtended = [x.replace('/', os.sep) for x in self.pathSkipExtended]
        self.slowModules = [x.replace('/', os.sep) for x in self.slowModules]

        # search on init
        if autoWalk:
            self.walk()

    def _visitFunc(self, args, dirname, names):
        '''
        append all module paths from _walk() to self.modulePaths.
        Utility function called from os.walk()
        '''
        for fileName in names:
            if fileName.endswith('py'):
                fp = os.path.join(dirname, fileName)
                if not os.path.isdir(fp):
                    self.modulePaths.append(fp)

    def walk(self):
        '''
        Get all the modules in reverse order, storing them in self.modulePaths
        '''
        def manyCoreSortFunc(name):
            '''
            for many core systems, like the MacPro, running slowest modules first
            helps there be fewer idle cores later
            '''
            name = name[len(self.dirParent) + 1:]
            name = name.replace('.py', '')
            return (name in self.slowModules, name)

        # the results of this are stored in self.curFiles, self.dirList
        for dirPath, unused_dirNames, filenames in os.walk(self.dirParent):
            self._visitFunc(None, dirPath, filenames)

        if common.cpus() > 4:
            self.modulePaths.sort(key=manyCoreSortFunc)
        else:
            self.modulePaths.sort()

        # I don't know why we do this, but it happened this way in an early m21 version,
        # and it's just tradition now. It'd wig me out
        # if I ever didn't see them in reverse alphabetical order.
        self.modulePaths.reverse()

    def _getName(self, fp):
        r'''
        Given full file pathlib.Path, find a name for the module with _ as the separator.

        >>> from music21.test import commonTest
        >>> mg = commonTest.ModuleGather()
        >>> #_DOCS_SHOW mg._getName(r'D:\Web\eclipse\music21base\music21\chord.py')
        'chord'
        '''
        fn = fp.replace(str(self.dirParent), '')  # remove parent
        if fn.startswith(os.sep):
            fn = fn[1:]
        fn = fn.replace(os.sep, '_')  # replace w/ _
        fn = fn.replace('.py', '')
        return fn

    def _getNamePeriod(self, fp, *, addM21=False):
        r'''
        Given full file path, find a name for the module with . as the separator.

        >>> from music21.test import commonTest
        >>> mg = commonTest.ModuleGather()
        >>> name = '/Users/cuthbert/git/music21base/music21/features/native.py'
        >>> #_DOCS_SHOW mg._getNamePeriod(name)
        'features.native'
        '''
        fn = fp.replace(self.dirParent, '')  # remove parent
        parts = [x for x in fn.split(os.sep) if x]
        if parts[-1] == '__init__.py':
            parts.pop()
        fn = '.'.join(parts)  # replace w/ period

        fn = fn.replace('.py', '')
        if addM21 and fn:
            fn = 'music21.' + fn
        elif addM21:
            fn = 'music21'

        return fn

    def load(self, restoreEnvironmentDefaults=False):
        '''
        Return a list of module objects that are not in the skip list.

        N.B. the list is a list of actual module objects not names,
        therefore cannot be pickled.
        '''
        modules = []
        for fp in self.modulePaths:
            moduleObject = self.getModule(fp, restoreEnvironmentDefaults)
            if moduleObject is not None:
                modules.append(moduleObject)
        return modules

    def getModule(self, fp, restoreEnvironmentDefaults=False):
        '''
        gets one module object from the file path
        '''
        skip = False
        ms = self.moduleSkip
        if self.useExtended:
            ms = self.moduleSkipExtended

        for fnSkip in ms:
            if fp.endswith(fnSkip):
                skip = True
                break
        if skip:
            return None

        ps = self.pathSkip
        if self.useExtended:
            ps = self.pathSkipExtended

        for dirSkip in ps:
            if dirSkip in fp:
                skip = True
                break
        if skip:
            return None

        name = self._getNamePeriod(fp, addM21=False)

        try:
            with warnings.catch_warnings():
                mod = load_source(name, fp)
        except Exception as excp:  # pylint: disable=broad-exception-caught
            environLocal.warn(['failed import:', name, '\t', fp, '\n',
                               '\tEXCEPTION:', str(excp).strip()])
            return None

        if restoreEnvironmentDefaults:
            if hasattr(mod, 'environLocal'):
                mod.environLocal.restoreDefaults()
        return mod

    def getModuleWithoutImp(self, fp, restoreEnvironmentDefaults=False):
        '''
        gets one module object from the file path without using Imp
        '''
        skip = False
        for fnSkip in self.moduleSkip:
            if fp.endswith(fnSkip):
                skip = True
                break
        if skip:
            return 'skip'
        for dirSkip in self.pathSkip:
            dirSkipSlash = os.sep + dirSkip + os.sep
            if dirSkipSlash in fp:
                skip = True
                break
        if skip:
            return 'skip'
        moduleName = self._getNamePeriod(fp)
        moduleNames = moduleName.split('.')
        currentModule = music21
        # print(currentModule, moduleName, fp)

        for thisName in moduleNames:
            if hasattr(currentModule, thisName):
                currentModule = object.__getattribute__(currentModule, thisName)
                if not isinstance(currentModule, types.ModuleType):
                    return 'notInTree'
            elif 'test' in thisName:
                # import '*test*' automatically.
                packageName = currentModule.__name__
                newMod = importlib.import_module('.' + thisName, packageName)
                setattr(currentModule, thisName, newMod)
                environLocal.printDebug(
                    f'Imported {thisName=} from {currentModule=}, {fp=}, {packageName=}'
                )
                currentModule = newMod
            else:
                return 'notInTree'
        mod = currentModule

        if restoreEnvironmentDefaults:
            if hasattr(mod, 'environLocal'):
                mod.environLocal.restoreDefaults()
        print('starting ' + moduleName)
        return mod


if __name__ == '__main__':
    music21.mainTest()
