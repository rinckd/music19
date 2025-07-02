# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         midi.realtime.py
# Purpose:      music21 classes for playing midi data in realtime
#
# Authors:      Michael Scott Asato Cuthbert
#               (from an idea by Joe "Codeswell")
#
# Copyright:    Copyright © 2012 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Objects for realtime playback of Music21 Streams as MIDI.

From an idea of Joe "Codeswell":

https://joecodeswell.wordpress.com/2012/06/13/how-to-produce-python-controlled-audio-output-from-music-made-with-music21

https://stackoverflow.com/questions/10983462/how-can-i-produce-real-time-audio-output-from-music-made-with-music21

Requires pygame: pip3 install pygame
'''
from __future__ import annotations

from importlib.util import find_spec
from io import BytesIO
from music21 import defaults
from music21.exceptions21 import Music21Exception
from music21 import stream

from music21.midi import translate as midiTranslate

class StreamPlayerException(Music21Exception):
    pass

class StreamPlayer:  # pragma: no cover
    '''
    Create a player for a stream that plays its midi version in realtime using pygame.

    Set up a detuned piano (where each key has a random but
    consistent detuning from 30 cents flat to sharp)
    and play a Bach Chorale on it in real time.

    >>> import random
    >>> keyDetune = []
    >>> for i in range(127):
    ...    keyDetune.append(random.randint(-30, 30))

    >>> #_DOCS_SHOW b = corpus.parse('bwv66.6')
    >>> #_DOCS_SHOW for n in b.flatten().notes:
    >>> class PitchMock: midi = 20  #_DOCS_HIDE
    >>> class Mock: pitch = PitchMock()  #_DOCS_HIDE
    >>> #_DOCS_HIDE -- should not play back in doctests, see TestExternal
    >>> n = Mock()  #_DOCS_HIDE
    >>> for i in [1]:  #_DOCS_HIDE
    ...    n.pitch.microtone = keyDetune[n.pitch.midi]
    >>> #_DOCS_SHOW sp = midi.realtime.StreamPlayer(b)
    >>> #_DOCS_SHOW sp.play()

    The stream is stored (unaltered) in `StreamPlayer.streamIn`, and can be changed any time the
    midi file is not playing.

    A number of mixer controls can be passed in with keywords:

    *  mixerFreq (default 44100 -- CD quality)
    *  mixerBitSize (default -16 (=unsigned 16bit) --
         really, are you going to do 24bit audio with Python?? :-)  )
    *  mixerChannels (default 2 = stereo)
    *  mixerBuffer (default 1024 = number of samples)
    '''
    mixerInitialized = False

    def __init__(
        self,
        streamIn: stream.Stream,
        reinitMixer: bool = False,
        mixerFreq: int = 44100,
        mixerBitSize: int = -16,
        mixerChannels: int = 2,
        mixerBuffer: int = 1024,
    ):
        try:
            # noinspection PyPackageRequirements
            import pygame  # type: ignore
            self.pygame = pygame
            # noinspection PyPackageRequirements
            import pygame.exceptions    # type: ignore
            self.pygame_exceptions = pygame.exceptions  # type: ignore  # pylint: disable=no-member
        except ImportError:
            raise StreamPlayerException('StreamPlayer requires pygame.  Install first')
        if self.mixerInitialized is False or reinitMixer:
            pygame.mixer.init(mixerFreq, mixerBitSize, mixerChannels, mixerBuffer)

        self.streamIn = streamIn

    def play(self,
             busyFunction=None,
             busyArgs=None,
             endFunction=None,
             endArgs=None,
             busyWaitMilliseconds=50,
             *,
             playForMilliseconds=float('inf'),
             blocked=True):
        '''
        busyFunction is a function that is called with busyArgs when the music is busy every
        busyWaitMilliseconds.

        endFunction is a function that is called with endArgs when the music finishes playing.

        playForMilliseconds is the amount of time in milliseconds after which
        the playback will be automatically stopped.

        If blocked is False, the method will finish before ending the stream, allowing
        you to completely control whether to stop it. Ignore every other arguments
        '''
        streamStringIOFile = self.getStringOrBytesIOFile()
        self.playStringIOFile(streamStringIOFile,
                              busyFunction=busyFunction,
                              busyArgs=busyArgs,
                              endFunction=endFunction,
                              endArgs=endArgs,
                              busyWaitMilliseconds=busyWaitMilliseconds,
                              playForMilliseconds=playForMilliseconds,
                              blocked=blocked)

    def getStringOrBytesIOFile(self):
        streamMidiFile = midiTranslate.streamToMidiFile(self.streamIn)
        streamMidiWritten = streamMidiFile.writestr()
        return BytesIO(streamMidiWritten)

    def playStringIOFile(self, stringIOFile, busyFunction=None, busyArgs=None,
                         endFunction=None, endArgs=None, busyWaitMilliseconds=50,
                         *,
                         playForMilliseconds=float('inf'), blocked=True):
        '''
        busyFunction is a function that is called with busyArgs when the music is busy every
        busyWaitMilliseconds.

        endFunction is a function that is called with endArgs when the music finishes playing.

        playForMilliseconds is the amount of time in milliseconds after which the
        playback will be automatically stopped.

        If blocked is False, the method will finish before ending the stream, allowing you to
        completely control whether to stop it. Ignore every other arguments but for stringIOFile
        '''
        pygameClock = self.pygame.time.Clock()
        try:
            self.pygame.mixer.music.load(stringIOFile)
        except self.pygame_exceptions.PygameError as pge:
            raise StreamPlayerException(
                f'Could not play music file {stringIOFile} because: '
                + f'{self.pygame_exceptions.get_error()}'
            ) from pge
        self.pygame.mixer.music.play()
        if not blocked:
            return
        framerate = int(1000 / busyWaitMilliseconds)  # coerce into int even if given a float.
        start_time = self.pygame.time.get_ticks()
        while self.pygame.mixer.music.get_busy():
            if busyFunction is not None:
                busyFunction(busyArgs)
            if self.pygame.time.get_ticks() - start_time > playForMilliseconds:
                self.pygame.mixer.music.stop()
                break
            pygameClock.tick(framerate)

        if endFunction is not None:
            endFunction(endArgs)

    def stop(self):
        self.pygame.mixer.music.stop()
