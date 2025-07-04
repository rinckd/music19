# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         audioSearch.transcriber.py
# Purpose:      Automatically transcribe melodies from a microphone or
#               wave file and output them as a score
#
# Authors:      Jordi Bartolome
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from __future__ import annotations

import unittest

from music21 import environment
from music21 import scale

environLocal = environment.Environment('audioSearch.transcriber')


def runTranscribe(show=True, plot=True, useMic=True,
                  seconds=20.0, useScale=None, saveFile=True):  # pragma: no cover
    '''
    runs all the methods to record from audio for `seconds` length (default 10.0)
    and transcribe the resulting melody returning a music21.Score object

    if `show` is True, show the stream.

    if `plot` is True, then a Tk graph of the frequencies will be displayed.

    if `useMic` is True then use the microphone.  If False it will load the file of `saveFile`
    or the default temp file to run transcriptions from.

    a different scale than the chromatic scale can be specified by setting `useScale`.
    See :ref:`moduleScale` for a list of allowable scales. (or a custom one can be given).
    Microtonal scales are totally accepted, as are retuned scales where A != 440hz.

    if `saveFile` is False, then the recorded audio is saved to disk.  If
    set to `True` then `environLocal.getRootTempDir() / 'ex.wav'` is
    used as the filename.  If set to anything else then it will use that as the
    filename.
    '''
    from music21 import audioSearch as audioSearchBase

    if useScale is None:
        useScale = scale.ChromaticScale('C4')
    # beginning - recording or not
    if saveFile is True:
        waveFilename = environLocal.getRootTempDir() / 'ex.wav'
    elif saveFile is False:
        waveFilename = False
    else:
        waveFilename = saveFile

    # the rest of the score
    if useMic is True:
        freqFromAQList = audioSearchBase.getFrequenciesFromMicrophone(
            length=seconds,
            storeWaveFilename=str(waveFilename))
    else:
        freqFromAQList = audioSearchBase.getFrequenciesFromAudioFile(
            waveFilename=str(waveFilename))

    detectedPitchesFreq = audioSearchBase.detectPitchFrequencies(freqFromAQList, useScale)
    detectedPitchesFreq = audioSearchBase.smoothFrequencies(detectedPitchesFreq)
    (detectedPitchObjects,
        listplot) = audioSearchBase.pitchFrequenciesToObjects(detectedPitchesFreq, useScale)
    (notesList,
        durationList) = audioSearchBase.joinConsecutiveIdenticalPitches(detectedPitchObjects)
    myScore, unused_length_part = audioSearchBase.notesAndDurationsToStream(
        notesList,
        durationList,
        removeRestsAtBeginning=True)

    if show:
        myScore.show()

    if plot:
        try:
            # for finding
            import matplotlib.pyplot  # type: ignore
        except ImportError:
            raise audioSearchBase.AudioSearchException(
                'Cannot plot without matplotlib installed.')
        matplotlib.pyplot.plot(listplot)
        matplotlib.pyplot.show()
    environLocal.printDebug('* END')

    return myScore


def monophonicStreamFromFile(fileName, useScale=None):
    '''
    Reads in a .wav file and returns a stream representing the transcribed, monophonic audio.

    `fileName` should be the complete path to a file on the disk.

    A different scale than the chromatic scale can be specified by setting `useScale`.
    See :ref:`moduleScale` for a list of allowable scales. (or a custom one can be given).
    Microtonal scales are totally accepted, as are retuned scales where A != 440hz.

    We demonstrate with an audio file beginning with an ascending scale.

    >>> import os #_DOCS_HIDE
    >>> taw = 'test_audio.wav' #_DOCS_HIDE
    >>> waveFile = str(common.getSourceFilePath() / 'audioSearch' / taw) #_DOCS_HIDE
    >>> #_DOCS_SHOW waveFile = 'test_audio.wav'
    >>> p = audioSearch.transcriber.monophonicStreamFromFile(waveFile)
    >>> p
    <music21.stream.Part ...>
    >>> p.show('text')
    {0.0} <music21.note.Note C>
    {0.25} <music21.note.Note C>
    {0.75} <music21.note.Note D>
    {1.75} <music21.note.Note E>
    {2.75} <music21.note.Note F>
    {4.25} <music21.note.Note G>
    {5.25} <music21.note.Note A>
    {6.25} <music21.note.Note B>
    {7.25} <music21.note.Note C>
    ...
    '''
    from music21 import audioSearch as audioSearchBase

    freqFromAQList = audioSearchBase.getFrequenciesFromAudioFile(waveFilename=fileName)

    detectedPitchesFreq = audioSearchBase.detectPitchFrequencies(freqFromAQList, useScale)
    detectedPitchesFreq = audioSearchBase.smoothFrequencies(detectedPitchesFreq)
    (detectedPitchObjects,
        unused_listplot) = audioSearchBase.pitchFrequenciesToObjects(detectedPitchesFreq, useScale)
    (notesList,
        durationList) = audioSearchBase.joinConsecutiveIdenticalPitches(detectedPitchObjects)
    myScore, unused_length_part = audioSearchBase.notesAndDurationsToStream(
        notesList, durationList, removeRestsAtBeginning=True)
    return myScore.parts.first()


if __name__ == '__main__':
    import music21
    music21.mainTest(TestExternal)


