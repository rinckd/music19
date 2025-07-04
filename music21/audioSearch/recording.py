# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         audioSearch.recording.py
# Purpose:      routines for making recordings from microphone input
#
# Authors:      Jordi Bartolome
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011-25 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
modules for audio searching that directly record from the microphone.

Requires PyAudio and portaudio to be installed (https://www.portaudio.com/download.html)

Windows users will get pyaudio and portaudio with `pip install pyaudio`

macOS users should have Homebrew installed and run `brew install portaudio`
before running `pip install pyaudio`

There is no official support for Linux/BSD etc. in music21, but package managers like `apt`
tend to have libraries like `portaudio19` and `python3-pyaudio`.
'''
from __future__ import annotations

from importlib.util import find_spec
import wave

from music21.common.types import DocOrder
from music21 import environment
from music21 import exceptions21

environLocal = environment.Environment('audioSearch.recording')

default_recordChannels = 1
default_recordSampleRate = 44100
default_recordChunkLength = 1024

def samplesFromRecording(seconds=10.0, storeFile=True,
                         recordFormat=None,
                         recordChannels=default_recordChannels,
                         recordSampleRate=default_recordSampleRate,
                         recordChunkLength=default_recordChunkLength):  # pragma: no cover
    '''
    records `seconds` length of sound in the given format (default Wave)
    and optionally stores it to disk using the filename of `storeFile`

    Returns a list of samples.
    '''
    # noinspection PyPackageRequirements
    import pyaudio  # type: ignore  # pylint: disable=import-error
    recordFormatDefault = pyaudio.paInt16

    if recordFormat is None:
        recordFormat = recordFormatDefault

    if recordFormat == pyaudio.paInt8:
        raise RecordingException('cannot perform samplesFromRecording on 8-bit samples')

    p_audio = pyaudio.PyAudio()
    st = p_audio.open(format=recordFormat,
                      channels=recordChannels,
                      rate=recordSampleRate,
                      input=True,
                      frames_per_buffer=recordChunkLength)

    recordingLength = int(recordSampleRate * float(seconds) / recordChunkLength)

    storedWaveSampleList = []

    # time_start = time.time()
    for i in range(recordingLength):
        data = st.read(recordChunkLength)
        storedWaveSampleList.append(data)
    # print('Time elapsed: %.3f s\n' % (time.time() - time_start))
    st.close()
    p_audio.terminate()

    if storeFile is not False:
        if isinstance(storeFile, str):
            waveFilename = storeFile
        else:
            waveFilename = str(environLocal.getRootTempDir() / 'recordingTemp.wav')
        # write recording to disk
        data = b''.join(storedWaveSampleList)
        try:
            # wave.open does not take a path-like object as of 3.12
            wf = wave.open(waveFilename, 'wb')
            wf.setnchannels(recordChannels)
            wf.setsampwidth(p_audio.get_sample_size(recordFormat))
            wf.setframerate(recordSampleRate)
            wf.writeframes(data)
            wf.close()
        except IOError:
            raise RecordingException(f'Cannot open {waveFilename} for writing.')
    return storedWaveSampleList

class RecordingException(exceptions21.Music21Exception):
    pass

# -----------------------------------------

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER: DocOrder = []
