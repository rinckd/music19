# -*- coding: utf-8 -*-
# Migrated from embedded tests

import unittest

from music21.audioSearch.recording import *


class Test(unittest.TestCase):
    pass


class TestExternal(unittest.TestCase):  # pragma: no cover
    loader = find_spec('pyaudio')
    if loader is not None:  # pragma: no cover
        pyaudio_installed = True
    else:
        pyaudio_installed = False

    @unittest.skipUnless(pyaudio_installed, 'pyaudio must be installed')
    def testRecording(self):
        '''
        record one second of data and print 10 records
        '''
        sampleList = samplesFromRecording(seconds=1, storeFile=False)
        print(sampleList[30:40])


if __name__ == '__main__':
    import music21
    music21.mainTest(Test, TestExternal)
