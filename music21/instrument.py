# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         instrument.py
# Purpose:      Class for basic instrument information
#
# Authors:      Michael Scott Asato Cuthbert
#               Neena Parikh
#               Christopher Ariza
#               Jose Cabal-Ugaz
#               Ben Houge
#               Mark Gotham
#
# Copyright:    Copyright © 2009-2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
This module represents instruments through objects that contain general information
such as Metadata for instrument names, classifications, transpositions and default
MIDI program numbers.  It also contains information specific to each instrument
or instrument family, such as string pitches, etc.  Information about instrumental
ensembles is also included here though it may later be separated out into its own
ensemble.py module.
'''
from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
import importlib
import typing as t

from music21 import base
from music21 import common
from music21 import environment
from music21.exceptions21 import InstrumentException
from music21 import interval
from music21 import note
from music21 import pitch
from music21.tree.trees import OffsetTree

if t.TYPE_CHECKING:
    from music21 import stream

environLocal = environment.Environment('instrument')

def unbundleInstruments(streamIn: stream.Stream,
                        *,
                        inPlace=False) -> stream.Stream|None:
    # noinspection PyShadowingNames
    '''
    takes a :class:`~music21.stream.Stream` that has :class:`~music21.note.NotRest` objects
    and moves their `.storedInstrument` attributes to a new Stream (unless inPlace=True)

    >>> up1 = note.Unpitched()
    >>> up1.storedInstrument = instrument.BassDrum()
    >>> up2 = note.Unpitched()
    >>> up2.storedInstrument = instrument.Cowbell()
    >>> s = stream.Stream()
    >>> s.append(up1)
    >>> s.append(up2)
    >>> s2 = instrument.unbundleInstruments(s)
    >>> s2.show('text')
    {0.0} <music21.instrument.BassDrum 'Bass Drum'>
    {0.0} <music21.note.Unpitched 'Bass Drum'>
    {1.0} <music21.instrument.Cowbell 'Cowbell'>
    {1.0} <music21.note.Unpitched 'Cowbell'>
    '''
    if inPlace is True:
        s = streamIn
    else:
        s = streamIn.coreCopyAsDerivation('unbundleInstruments')

    for thisObj in s:
        if isinstance(thisObj, note.NotRest):
            # eventually also unbundle each note of chord, but need new voices
            i = thisObj.storedInstrument
            if i is not None:
                off = thisObj.offset
                s.insert(off, i)

    if inPlace is False:
        return s

def bundleInstruments(streamIn: stream.Stream,
                      *,
                      inPlace=False) -> stream.Stream|None:
    # noinspection PyShadowingNames
    '''
    >>> up1 = note.Unpitched()
    >>> up1.storedInstrument = instrument.BassDrum()
    >>> upUnknownInstrument = note.Unpitched()

    >>> up2 = note.Unpitched()
    >>> up2.storedInstrument = instrument.Cowbell()
    >>> s = stream.Stream()
    >>> s.append(up1)
    >>> s.append(upUnknownInstrument)
    >>> s.append(up2)
    >>> s2 = instrument.unbundleInstruments(s)
    >>> s3 = instrument.bundleInstruments(s2)
    >>> for test in s3:
    ...     print(test.storedInstrument)
    Bass Drum
    Bass Drum
    Cowbell

    '''
    if inPlace is True:
        s = streamIn
    else:
        s = streamIn.coreCopyAsDerivation('bundleInstruments')

    lastInstrument = None

    for thisObj in s:
        if 'Instrument' in thisObj.classes:
            lastInstrument = thisObj
            s.remove(thisObj)
        elif isinstance(thisObj, note.NotRest):
            thisObj.storedInstrument = lastInstrument

    if inPlace is False:
        return s

class Instrument(base.Music21Object):
    '''
    Base class for all musical instruments.  Designed
    for subclassing, though usually a more specific
    instrument class (such as StringInstrument) would
    be better to subclass.

    Some defined attributes for instruments include:

    * partId
    * partName
    * partAbbreviation
    * instrumentId
    * instrumentName
    * instrumentAbbreviation
    * midiProgram (0-indexed)
    * midiChannel (0-indexed)
    * lowestNote (a note object or a string for _written_ pitch)
    * highestNote (a note object or a string for _written_ pitch)
    * transposition (an interval object)
    * inGMPercMap (bool -- if it uses the GM percussion map)
    * soundfontFn (filepath to a sound font, optional)
    '''
    classSortOrder = -25

    def __init__(self, instrumentName: str|None = None, **keywords):
        super().__init__(**keywords)

        self.partId: str|None = None
        self._partIdIsRandom = False

        self.partName: str|None = None
        self.partAbbreviation: str|None = None

        self.printPartName: bool|None = None  # True = yes, False = no, None = let others decide
        self.printPartAbbreviation: bool|None = None

        self.instrumentId: str|None = None  # apply to midi and instrument
        self._instrumentIdIsRandom = False

        self.instrumentName: str|None = instrumentName
        self.instrumentAbbreviation: str|None = None
        self.midiProgram: int|None = None  # 0-indexed
        self.midiChannel: int|None = None  # 0-indexed
        self.instrumentSound: str|None = None

        self.lowestNote: pitch.Pitch|None = None
        self.highestNote: pitch.Pitch|None = None

        # define interval to go from written to sounding
        self.transposition: interval.Interval|None = None

        self.inGMPercMap = False
        self.soundfontFn = None  # if defined

    def __str__(self):
        msg = []
        if self.partId is not None:
            msg.append(f'{self.partId}: ')
        if self.partName is not None:
            msg.append(f'{self.partName}: ')
        if self.instrumentName is not None:
            msg.append(self.instrumentName)
        return ''.join(msg)

    def _reprInternal(self):
        return repr(str(self))

    def __deepcopy__(self, memo=None):
        new = common.defaultDeepcopy(self, memo)
        if self._partIdIsRandom:
            new.partIdRandomize()
        if self._instrumentIdIsRandom:
            new.instrumentIdRandomize()
        return new

    def bestName(self):
        '''
        Find a viable name, looking first at instrument, then part, then
        abbreviations.
        '''
        if self.partName is not None:
            return self.partName
        elif self.partAbbreviation is not None:
            return self.partAbbreviation
        elif self.instrumentName is not None:
            return self.instrumentName
        elif self.instrumentAbbreviation is not None:
            return self.instrumentAbbreviation
        else:
            return None

    def partIdRandomize(self):
        '''
        Force a unique id by using an MD5
        '''
        idNew = f'P{common.getMd5()}'
        # environLocal.printDebug(['incrementing instrument from',
        #                         self.partId, 'to', idNew])
        self.partId = idNew
        self._partIdIsRandom = True

    def instrumentIdRandomize(self):
        '''
        Force a unique id by using an MD5
        '''
        idNew = f'I{common.getMd5()}'
        # environLocal.printDebug(['incrementing instrument from',
        #                         self.partId, 'to', idNew])
        self.instrumentId = idNew
        self._instrumentIdIsRandom = True

    def autoAssignMidiChannel(self, usedChannels: list[int], maxMidi=16):
        '''
        Assign an unused midi channel given a list of
        used channels.  Music21 uses 0-indexed MIDI channels.

        assigns the number to self.midiChannel and returns
        it as an int.

        Note that the Percussion MIDI channel (9 in music21, 10 in 1-16 numbering) is special,
        and thus is skipped.

        >>> used = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]
        >>> i = instrument.Violin()
        >>> i.autoAssignMidiChannel(used)
        12
        >>> i.midiChannel
        12

        Note that used is unchanged after calling this and would need to be updated manually

        >>> used
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11]

        Unpitched percussion will be set to 9, so long as it's not in the filter list:

        >>> used = [0]
        >>> i = instrument.Maracas()
        >>> i.autoAssignMidiChannel(used)
        9
        >>> i.midiChannel
        9

        >>> used = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> i = instrument.Woodblock()
        >>> i.autoAssignMidiChannel(used)
        11
        >>> i.midiChannel
        11

        If all 16 channels are used, an exception is raised:

        >>> used2 = range(16)
        >>> i = instrument.Instrument()
        >>> i.autoAssignMidiChannel(used2)
        Traceback (most recent call last):
        music21.exceptions21.InstrumentException: we are out of midi channels! help!

        Get around this by assinging higher channels:

        >>> i.autoAssignMidiChannel(used2, maxMidi=32)
        16
        >>> i.midiChannel
        16

        * Changed in v.9 -- usedChannelList is required, add maxMidi as an optional parameter.
            various small tweaks for corner cases.
        '''
        # NOTE: this is used in musicxml output, not in midi output
        channelFilter = frozenset(usedChannels)

        if 'UnpitchedPercussion' in self.classes and 9 not in channelFilter:
            self.midiChannel = 9
            return self.midiChannel
        elif not channelFilter:
            self.midiChannel = 0
            return self.midiChannel
        elif len(channelFilter) >= maxMidi - 1:
            # subtract one, since we are not using percussion channel (=9)
            raise InstrumentException('we are out of midi channels! help!')
        else:
            for ch in range(maxMidi):
                if ch in channelFilter:
                    continue
                elif ch % 16 == 9:
                    continue  # skip 10 / percussion for now
                else:
                    self.midiChannel = ch
                    return self.midiChannel
            return 0
            # raise InstrumentException('we are out of midi channels and this ' +
            #            'was not already detected PROGRAM BUG!')

# ------------------------------------------------------------------------------

class KeyboardInstrument(Instrument):

    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.instrumentName = 'Keyboard'
        self.instrumentAbbreviation = 'Kb'
        self.instrumentSound = 'keyboard.piano'

class Piano(KeyboardInstrument):
    '''

    >>> p = instrument.Piano()
    >>> p.instrumentName
    'Piano'
    >>> p.midiProgram
    0
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Piano'
        self.instrumentAbbreviation = 'Pno'
        self.midiProgram = 0

        self.lowestNote = pitch.Pitch('A0')
        self.highestNote = pitch.Pitch('C8')

class Harpsichord(KeyboardInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Harpsichord'
        self.instrumentAbbreviation = 'Hpschd'
        self.midiProgram = 6
        self.instrumentSound = 'keyboard.harpsichord'

        self.lowestNote = pitch.Pitch('F1')
        self.highestNote = pitch.Pitch('F6')

class Clavichord(KeyboardInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Clavichord'
        self.instrumentAbbreviation = 'Clv'
        self.midiProgram = 7
        self.instrumentSound = 'keyboard.clavichord'

        # TODO: self.lowestNote = pitch.Pitch('')
        # TODO: self.highestNote = pitch.Pitch('')

class Celesta(KeyboardInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Celesta'
        self.instrumentAbbreviation = 'Clst'
        self.midiProgram = 8
        self.instrumentSound = 'keyboard.celesta'

class Sampler(KeyboardInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Sampler'
        self.instrumentAbbreviation = 'Samp'
        self.midiProgram = 55

class ElectricPiano(Piano):
    '''

    >>> p = instrument.ElectricPiano()
    >>> p.instrumentName
    'Electric Piano'
    >>> p.midiProgram
    2
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Electric Piano'
        self.instrumentAbbreviation = 'E.Pno'
        self.midiProgram = 2

# ------------------------------------------------------------------------------

class Organ(Instrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.instrumentName = 'Organ'
        self.midiProgram = 19
        self.instrumentSound = 'keyboard.organ'

class PipeOrgan(Organ):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Pipe Organ'
        self.instrumentAbbreviation = 'P Org'
        self.midiProgram = 19
        self.instrumentSound = 'keyboard.organ.pipe'
        self.lowestNote = pitch.Pitch('C2')
        self.highestNote = pitch.Pitch('C6')

class ElectricOrgan(Organ):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Electric Organ'
        self.instrumentAbbreviation = 'Elec Org'
        self.midiProgram = 16

        self.lowestNote = pitch.Pitch('C2')
        self.highestNote = pitch.Pitch('C6')

class ReedOrgan(Organ):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Reed Organ'
        # TODO self.instrumentAbbreviation = ''
        self.midiProgram = 20
        self.instrumentSound = 'keyboard.organ.reed'

        self.lowestNote = pitch.Pitch('C2')
        self.highestNote = pitch.Pitch('C6')

class Accordion(Organ):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Accordion'
        self.instrumentAbbreviation = 'Acc'
        self.midiProgram = 21
        self.instrumentSound = 'keyboard.accordion'

        self.lowestNote = pitch.Pitch('F3')
        self.highestNote = pitch.Pitch('A6')

class Harmonica(Instrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Harmonica'
        self.instrumentAbbreviation = 'Hmca'
        self.midiProgram = 22
        self.instrumentSound = 'wind.reed.harmonica'

        self.lowestNote = pitch.Pitch('C3')
        self.highestNote = pitch.Pitch('C6')

# -----------------------------------------------------
class StringInstrument(Instrument):

    def __init__(self, **keywords):
        super().__init__(**keywords)
        self._stringPitches = None
        self._cachedPitches = None
        self.instrumentName = 'StringInstrument'
        self.instrumentAbbreviation = 'Str'

        self.midiProgram = 48

    def _getStringPitches(self):
        if hasattr(self, '_cachedPitches') and self._cachedPitches is not None:
            return self._cachedPitches
        elif not hasattr(self, '_stringPitches'):
            raise InstrumentException('cannot get stringPitches for these instruments')
        else:
            self._cachedPitches = [pitch.Pitch(x) for x in self._stringPitches]
            return self._cachedPitches

    def _setStringPitches(self, newPitches):
        if newPitches and (hasattr(newPitches[0], 'step') or newPitches[0] is None):
            # newPitches is pitchObjects or something
            self._stringPitches = newPitches
            self._cachedPitches = newPitches
        else:
            self._cachedPitches = None
            self._stringPitches = newPitches

    stringPitches = property(_getStringPitches, _setStringPitches, doc='''
            stringPitches is a property that stores a list of Pitches (or pitch names,
            such as "C4") that represent the pitch of the open strings from lowest to
            highest.[*]

            >>> vln1 = instrument.Violin()
            >>> [str(p) for p in vln1.stringPitches]
            ['G3', 'D4', 'A4', 'E5']

            instrument.stringPitches are full pitch objects, not just names:

            >>> [x.octave for x in vln1.stringPitches]
            [3, 4, 4, 5]

            Scordatura for Scelsi's violin concerto *Anahit*.
            (N.B. that string to pitch conversion is happening automatically)

            >>> vln1.stringPitches = ['G3', 'G4', 'B4', 'D4']

            (`[*]In some tuning methods such as reentrant tuning on the ukulele,
            lute, or five-string banjo the order might not strictly be from lowest to
            highest.  The same would hold true for certain violin scordatura pieces, such
            as some of Biber's *Mystery Sonatas*`)
            ''')

class Violin(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Violin'
        self.instrumentAbbreviation = 'Vln'
        self.midiProgram = 40
        self.instrumentSound = 'strings.violin'

        self.lowestNote = pitch.Pitch('G3')
        self._stringPitches = ['G3', 'D4', 'A4', 'E5']

class Viola(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Viola'
        self.instrumentAbbreviation = 'Vla'
        self.midiProgram = 41
        self.instrumentSound = 'strings.viola'

        self.lowestNote = pitch.Pitch('C3')
        self._stringPitches = ['C3', 'G3', 'D4', 'A4']

class Violoncello(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Violoncello'
        self.instrumentAbbreviation = 'Vc'
        self.midiProgram = 42
        self.instrumentSound = 'strings.cello'

        self.lowestNote = pitch.Pitch('C2')
        self._stringPitches = ['C2', 'G2', 'D3', 'A3']

class Contrabass(StringInstrument):
    '''
    For the Contrabass (or double bass), the stringPitches attribute refers to the sounding pitches
    of each string; whereas the lowestNote attribute refers to the lowest written note.
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Contrabass'
        self.instrumentAbbreviation = 'Cb'
        self.midiProgram = 43
        self.instrumentSound = 'strings.contrabass'

        self.lowestNote = pitch.Pitch('E2')
        self._stringPitches = ['E1', 'A1', 'D2', 'G2']
        self.transposition = interval.Interval('P-8')

class Harp(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Harp'
        self.instrumentAbbreviation = 'Hp'
        self.midiProgram = 46
        self.instrumentSound = 'pluck.harp'

        self.lowestNote = pitch.Pitch('C1')
        self.highestNote = pitch.Pitch('G#7')

class Guitar(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Guitar'
        self.instrumentAbbreviation = 'Gtr'
        self.midiProgram = 24  # default -- Acoustic
        self.instrumentSound = 'pluck.guitar'

        self.lowestNote = pitch.Pitch('E2')
        self._stringPitches = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']

class AcousticGuitar(Guitar):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Acoustic Guitar'
        self.instrumentAbbreviation = 'Ac Gtr'
        self.midiProgram = 24
        self.instrumentSound = 'pluck.guitar.acoustic'

class ElectricGuitar(Guitar):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Electric Guitar'
        self.instrumentAbbreviation = 'Elec Gtr'
        self.midiProgram = 26
        self.instrumentSound = 'pluck.guitar.electric'

class AcousticBass(Guitar):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Acoustic Bass'
        self.instrumentAbbreviation = 'Ac b'
        self.midiProgram = 32
        self.instrumentSound = 'pluck.bass.acoustic'

        self.lowestNote = pitch.Pitch('E1')
        self._stringPitches = ['E1', 'A1', 'D2', 'G2']

class ElectricBass(Guitar):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Electric Bass'
        self.instrumentAbbreviation = 'Elec b'
        self.midiProgram = 33
        self.instrumentSound = 'pluck.bass.electric'

        self.lowestNote = pitch.Pitch('E1')
        self._stringPitches = ['E1', 'A1', 'D2', 'G2']

class FretlessBass(Guitar):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Fretless Bass'
        # TODO: self.instrumentAbbreviation = ''
        self.midiProgram = 35
        self.instrumentSound = 'pluck.bass.fretless'

        self.lowestNote = pitch.Pitch('E1')
        self._stringPitches = ['E1', 'A1', 'D2', 'G2']

class Mandolin(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Mandolin'
        self.instrumentAbbreviation = 'Mdln'
        self.instrumentSound = 'pluck.mandolin'

        self.lowestNote = pitch.Pitch('G3')
        self._stringPitches = ['G3', 'D4', 'A4', 'E5']

class Ukulele(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Ukulele'
        self.instrumentAbbreviation = 'Uke'
        self.instrumentSound = 'pluck.ukulele'

        self.lowestNote = pitch.Pitch('C4')
        self._stringPitches = ['G4', 'C4', 'E4', 'A4']

class Banjo(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Banjo'
        self.instrumentAbbreviation = 'Bjo'
        self.instrumentSound = 'pluck.banjo'
        self.midiProgram = 105

        self.lowestNote = pitch.Pitch('C3')
        self._stringPitches = ['C3', 'G3', 'D4', 'A4']
        self.transposition = interval.Interval('P-8')

class Lute(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Lute'
        self.instrumentAbbreviation = 'Lte'
        self.instrumentSound = 'pluck.lute'
        self.midiProgram = 24

class Sitar(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Sitar'
        self.instrumentAbbreviation = 'Sit'
        self.instrumentSound = 'pluck.sitar'
        self.midiProgram = 104

class Shamisen(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Shamisen'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'pluck.shamisen'
        self.midiProgram = 106

class Koto(StringInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Koto'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'pluck.koto'
        self.midiProgram = 107

# ------------------------------------------------------------------------------

class WoodwindInstrument(Instrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.instrumentName = 'Woodwind'
        self.instrumentAbbreviation = 'Ww'

class Flute(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Flute'
        self.instrumentAbbreviation = 'Fl'
        self.instrumentSound = 'wind.flutes.flute'
        self.midiProgram = 73

        self.lowestNote = pitch.Pitch('C4')  # Occasionally (rarely) B3

class Piccolo(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Piccolo'
        self.instrumentAbbreviation = 'Picc'
        self.instrumentSound = 'wind.flutes.piccolo'
        self.midiProgram = 72

        self.lowestNote = pitch.Pitch('D4')  # Occasionally (rarely) C4
        self.transposition = interval.Interval('P8')

class Recorder(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Recorder'
        self.instrumentAbbreviation = 'Rec'
        self.instrumentSound = 'wind.flutes.recorder'
        self.midiProgram = 74

        self.lowestNote = pitch.Pitch('F4')

class PanFlute(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Pan Flute'
        self.instrumentAbbreviation = 'P Fl'
        self.instrumentSound = 'wind.flutes.panpipes'
        self.midiProgram = 75

class Shakuhachi(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Shakuhachi'
        self.instrumentAbbreviation = 'Shk Fl'
        self.instrumentSound = 'wind.flutes.shakuhachi'
        self.midiProgram = 77

class Whistle(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Whistle'
        self.instrumentAbbreviation = 'Whs'
        self.instrumentSound = 'wind.flutes.whistle'
        self.inGMPercMap = True
        # TODO: why is this not inheriting from UnpitchedPercussion if we're giving it percMapPitch?
        self.percMapPitch = 71
        self.midiProgram = 78

class Ocarina(Flute):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Ocarina'
        self.instrumentAbbreviation = 'Oc'
        self.instrumentSound = 'wind.flutes.ocarina'
        self.midiProgram = 79

class Oboe(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Oboe'
        self.instrumentAbbreviation = 'Ob'
        self.instrumentSound = 'wind.reed.oboe'
        self.midiProgram = 68

        self.lowestNote = pitch.Pitch('B-3')

class EnglishHorn(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'English Horn'
        self.instrumentAbbreviation = 'Eng Hn'
        self.instrumentSound = 'wind.reed.english-horn'
        self.midiProgram = 69

        self.lowestNote = pitch.Pitch('B3')
        self.transposition = interval.Interval('P-5')

class Clarinet(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Clarinet'
        self.instrumentAbbreviation = 'Cl'
        self.instrumentSound = 'wind.reed.clarinet'
        self.midiProgram = 71

        self.lowestNote = pitch.Pitch('E3')
        self.transposition = interval.Interval('M-2')

class BassClarinet(Clarinet):
    '''
    >>> bcl = instrument.BassClarinet()
    >>> bcl.instrumentName
    'Bass clarinet'
    >>> bcl.midiProgram
    71
    >>> 'WoodwindInstrument' in bcl.classes
    True
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bass clarinet'
        self.instrumentAbbreviation = 'Bs Cl'
        self.instrumentSound = 'wind.reed.clarinet.bass'

        self.lowestNote = pitch.Pitch('E-3')
        self.transposition = interval.Interval('M-9')

class Bassoon(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bassoon'
        self.instrumentAbbreviation = 'Bsn'
        self.instrumentSound = 'wind.reed.bassoon'
        self.midiProgram = 70

        self.lowestNote = pitch.Pitch('B-1')

class Contrabassoon(Bassoon):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Contrabassoon'
        self.instrumentAbbreviation = 'C Bsn'
        self.instrumentSound = 'wind.reed.bassoon'
        self.midiProgram = 70

        self.lowestNote = pitch.Pitch('B-1')

class Saxophone(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Saxophone'
        self.instrumentAbbreviation = 'Sax'
        self.instrumentSound = 'wind.reed.saxophone'
        self.midiProgram = 65

        self.lowestNote = pitch.Pitch('B-3')

class SopranoSaxophone(Saxophone):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Soprano Saxophone'
        self.instrumentAbbreviation = 'S Sax'
        self.instrumentSound = 'wind.reed.saxophone.soprano'
        self.midiProgram = 64

        self.transposition = interval.Interval('M-2')

class AltoSaxophone(Saxophone):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Alto Saxophone'
        self.instrumentAbbreviation = 'A Sax'
        self.instrumentSound = 'wind.reed.saxophone.alto'
        self.midiProgram = 65

        self.transposition = interval.Interval('M-6')

class TenorSaxophone(Saxophone):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tenor Saxophone'
        self.instrumentAbbreviation = 'T Sax'
        self.instrumentSound = 'wind.reed.saxophone.tenor'
        self.midiProgram = 66

        self.transposition = interval.Interval('M-9')

class BaritoneSaxophone(Saxophone):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Baritone Saxophone'
        self.instrumentAbbreviation = 'Bar Sax'
        self.instrumentSound = 'wind.reed.saxophone.baritone'
        self.midiProgram = 67

        self.transposition = interval.Interval('M-13')

class Bagpipes(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bagpipes'
        self.instrumentAbbreviation = 'Bag'
        self.instrumentSound = 'wind.pipes.bagpipes'
        self.midiProgram = 109

class Shehnai(WoodwindInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Shehnai'
        self.instrumentAbbreviation = 'Shn'
        # another spelling is 'Shehnai'
        self.instrumentSound = 'wind.reed.shenai'
        self.midiProgram = 111

# ------------------------------------------------------------------------------

class BrassInstrument(Instrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.instrumentName = 'Brass'
        self.instrumentAbbreviation = 'Brs'
        self.midiProgram = 61

class Horn(BrassInstrument):
    '''
    >>> hn = instrument.Horn()
    >>> hn.instrumentName
    'Horn'
    >>> hn.midiProgram
    60
    >>> 'BrassInstrument' in hn.classes
    True
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Horn'
        self.instrumentAbbreviation = 'Hn'
        self.instrumentSound = 'brass.french-horn'
        self.midiProgram = 60

        self.lowestNote = pitch.Pitch('C2')
        self.transposition = interval.Interval('P-5')

class Trumpet(BrassInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Trumpet'
        self.instrumentAbbreviation = 'Tpt'
        self.instrumentSound = 'brass.trumpet'
        self.midiProgram = 56

        self.lowestNote = pitch.Pitch('F#3')
        self.transposition = interval.Interval('M-2')

class Trombone(BrassInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Trombone'
        self.instrumentAbbreviation = 'Trb'
        self.instrumentSound = 'brass.trombone'
        self.midiProgram = 57

        self.lowestNote = pitch.Pitch('E2')

class BassTrombone(Trombone):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bass Trombone'
        self.instrumentAbbreviation = 'BTrb'
        self.instrumentSound = 'brass.trombone.bass'

        self.lowestNote = pitch.Pitch('B-1')

class Tuba(BrassInstrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tuba'
        self.instrumentAbbreviation = 'Tba'
        self.instrumentSound = 'brass.tuba'
        self.midiProgram = 58

        self.lowestNote = pitch.Pitch('D1')

# ------------

class Percussion(Instrument):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.inGMPercMap = False
        self.percMapPitch = None
        self.instrumentName = 'Percussion'
        self.instrumentAbbreviation = 'Perc'

class PitchedPercussion(Percussion):
    pass

class UnpitchedPercussion(Percussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self._modifier = None
        self._modifierToPercMapPitch = {}
        self._percMapPitchToModifier = {}
        self.midiChannel = 9  # 0-indexed, i.e. MIDI channel 10

    def _getModifier(self):
        return self._modifier

    def _setModifier(self, modifier):
        modifier = modifier.lower().strip()
        # BEN: to-do, pull out hyphens, spaces, etc.

        if self.inGMPercMap is True and modifier.lower() in self._modifierToPercMapPitch:
            self.percMapPitch = self._modifierToPercMapPitch[modifier.lower()]

            # normalize modifiers
            if self.percMapPitch in self._percMapPitchToModifier:
                modifier = self._percMapPitchToModifier[self.percMapPitch]

        self._modifier = modifier

    modifier = property(_getModifier, _setModifier, doc='''
    Returns or sets the modifier for this instrument.  A modifier could
    be something like "low-floor" for a TomTom or "rimshot" for a SnareDrum.

    If the modifier is in the object's ._modifierToPercMapPitch dictionary
    then changing the modifier also changes the .percMapPitch for the object

    >>> bd = instrument.BongoDrums()
    >>> bd.modifier
    'high'

    >>> bd.percMapPitch
    60
    >>> bd.modifier = 'low'
    >>> bd.percMapPitch
    61

    Variations on modifiers can also be used and they get normalized:

    >>> wb1 = instrument.Woodblock()
    >>> wb1.percMapPitch
    76
    >>> wb1.modifier = 'LO'
    >>> wb1.percMapPitch
    77
    >>> wb1.modifier  # n.b. -- not LO
    'low'
    ''')

class Vibraphone(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Vibraphone'
        self.instrumentAbbreviation = 'Vbp'
        self.instrumentSound = 'pitched-percussion.vibraphone'
        self.midiProgram = 11

class Marimba(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Marimba'
        self.instrumentAbbreviation = 'Mar'
        self.instrumentSound = 'pitched-percussion.marimba'
        self.midiProgram = 12

class Xylophone(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Xylophone'
        self.instrumentAbbreviation = 'Xyl.'
        self.instrumentSound = 'pitched-percussion.xylophone'
        self.midiProgram = 13

class Glockenspiel(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Glockenspiel'
        self.instrumentAbbreviation = 'Gsp'
        self.instrumentSound = 'pitched-percussion.glockenspiel'
        self.midiProgram = 9

class ChurchBells(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Church Bells'
        self.instrumentAbbreviation = 'Bells'
        self.instrumentSound = 'metal.bells.church'
        self.midiProgram = 14

class TubularBells(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tubular Bells'
        self.instrumentAbbreviation = 'Tbells'
        self.instrumentSound = 'pitched-percussion.tubular-bells'
        self.midiProgram = 14

class Gong(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Gong'
        self.instrumentAbbreviation = 'Gng'
        self.instrumentSound = 'metal.gong'

class Handbells(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Handbells'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'pitched-percussion.handbells'

class Dulcimer(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Dulcimer'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'pluck.dulcimer'
        self.midiProgram = 15

class SteelDrum(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Steel Drum'
        self.instrumentAbbreviation = 'St Dr'
        self.instrumentSound = 'metal.steel-drums'
        self.midiProgram = 114

class Timpani(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Timpani'
        self.instrumentAbbreviation = 'Timp'
        self.instrumentSound = 'drum.timpani'
        self.midiProgram = 47

class Kalimba(PitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Kalimba'
        self.instrumentAbbreviation = 'Kal'
        self.instrumentSound = 'pitched-percussion.kalimba'
        self.midiProgram = 108

class Woodblock(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Woodblock'
        self.instrumentAbbreviation = 'Wd Bl'
        self.instrumentSound = 'wood.wood-block'
        self.inGMPercMap = True
        self.midiProgram = 115

        self._modifier = 'high'
        self._modifierToPercMapPitch = {'high': 76, 'low': 77, 'hi': 76, 'lo': 77}
        self._percMapPitchToModifier = {76: 'high', 77: 'low'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class TempleBlock(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Temple Block'
        self.instrumentAbbreviation = 'Temp Bl'
        self.instrumentSound = 'wood.temple-block'

class Castanets(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Castanets'
        self.instrumentAbbreviation = 'Cas'
        self.instrumentSound = 'wood.castanets'

class Maracas(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Maracas'
        self.inGMPercMap = True
        self.percMapPitch = 70
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'rattle.maraca'

class Vibraslap(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Vibraslap'
        self.instrumentAbbreviation = 'Vbslp'
        self.instrumentSound = 'rattle.vibraslap'
        self.inGMPercMap = True
        self.percMapPitch = 58

# BEN: Standardize Cymbals as plural

class Cymbals(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)
        self.instrumentName = 'Cymbals'
        self.instrumentAbbreviation = 'Cym'

class FingerCymbals(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Finger Cymbals'
        self.instrumentAbbreviation = 'Fing Cym'
        self.instrumentSound = 'metal.cymbal.finger'

class CrashCymbals(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Crash Cymbals'
        self.instrumentAbbreviation = 'Cym'
        self.instrumentSound = 'metal.cymbal.crash'
        self.inGMPercMap = True
        self._modifier = '1'

        self._modifierToPercMapPitch = {'1': 49,
                                        '2': 57,
                                        }
        self._percMapPitchToModifier = {49: '1',
                                        57: '2',
                                        }
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class SuspendedCymbal(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Suspended Cymbal'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.cymbal.suspended'

class SizzleCymbal(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Sizzle Cymbal'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.cymbal.sizzle'

class SplashCymbals(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Splash Cymbals'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.cymbal.splash'

class RideCymbals(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Ride Cymbals'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.cymbal.ride'

class HiHatCymbal(Cymbals):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Hi-Hat Cymbal'
        self.instrumentSound = 'metal.hi-hat'
        self.inGMPercMap = True

        self._modifier = 'pedal'

        self._modifierToPercMapPitch = {'pedal': 44,
                                        'open': 46,
                                        'closed': 42,
                                        }
        self._percMapPitchToModifier = {44: 'pedal',
                                        46: 'open',
                                        42: 'closed',
                                        }
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

        # TODO: self.instrumentAbbreviation = ''

class Triangle(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Triangle'
        self.instrumentAbbreviation = 'Tri'
        self.instrumentSound = 'metal.triangle'
        self.inGMPercMap = True
        self._modifier = 'open'

        self._modifierToPercMapPitch = {'open': 81,
                                        'mute': 80,
                                        }
        self._percMapPitchToModifier = {80: 'mute',
                                        81: 'open',
                                        }
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class Cowbell(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Cowbell'
        self.instrumentAbbreviation = 'Cwb'
        self.instrumentSound = 'metal.bells.cowbell'
        self.inGMPercMap = True
        self.percMapPitch = 56

class Agogo(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Agogo'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.bells.agogo'
        self.inGMPercMap = True
        self.percMapPitch = 67
        self.midiProgram = 113

class TamTam(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tam-Tam'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.tamtam'

class SleighBells(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Sleigh Bells'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'metal.bells.sleigh-bells'

class SnareDrum(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Snare Drum'
        self.instrumentAbbreviation = 'Sn Dr'
        self.instrumentSound = 'drum.snare-drum'
        self.inGMPercMap = True
        self._modifier = 'acoustic'
        self._modifierToPercMapPitch = {'acoustic': 38,
                                        'side': 37,
                                        'electric': 40,
                                        }
        self._percMapPitchToModifier = {38: 'acoustic',
                                        37: 'side',
                                        40: 'electric',
                                        }
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class TenorDrum(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tenor Drum'
        self.instrumentAbbreviation = 'Ten Dr'
        self.instrumentSound = 'drum.tenor-drum'

class BongoDrums(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bongo Drums'
        self.instrumentAbbreviation = 'Bgo Dr'
        self.instrumentSound = 'drum.bongo'

        self.inGMPercMap = True
        self._modifier = 'high'
        self._modifierToPercMapPitch = {'high': 60, 'low': 61}
        self._percMapPitchToModifier = {60: 'high', 61: 'low'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class TomTom(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tom-Tom'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'drum.tom-tom'
        self.inGMPercMap = True
        self._modifier = 'low floor'
        self._modifierToPercMapPitch = {'low floor': 41, 'high floor': 43, 'low': 45,
                                        'low-mid': 47, 'high-mid': 48, 'high': 50}
        self._percMapPitchToModifier = {41: 'low floor', 43: 'high floor', 45: 'low',
                                        47: 'low-mid', 48: 'high-mid', 50: 'high'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class Timbales(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Timbales'
        self.instrumentAbbreviation = 'Tim'
        self.instrumentSound = 'drum.timbale'
        self.inGMPercMap = True
        self._modifier = 'high'
        self._modifierToPercMapPitch = {'high': 65, 'low': 66}
        self._percMapPitchToModifier = {65: 'high', 66: 'low'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class CongaDrum(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Conga Drum'
        self.instrumentAbbreviation = 'Cga Dr'
        self.instrumentSound = 'drum.conga'
        self.inGMPercMap = True
        self._modifier = 'low'
        self._modifierToPercMapPitch = {'low': 64, 'mute high': 62, 'open high': 63}
        self._percMapPitchToModifier = {64: 'low', 62: 'mute high', 63: 'open high'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class BassDrum(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bass Drum'
        self.instrumentAbbreviation = 'B Dr'
        self.instrumentSound = 'drum.bass-drum'
        self.inGMPercMap = True
        self._modifier = 'acoustic'
        self._modifierToPercMapPitch = {'acoustic': 35, '1': 36}
        self._percMapPitchToModifier = {35: 'acoustic', 36: '1'}
        self.percMapPitch = self._modifierToPercMapPitch[self._modifier]

class Taiko(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Taiko'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'drum.taiko'
        self.midiProgram = 116

class Tambourine(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tambourine'
        self.instrumentAbbreviation = 'Tmbn'
        self.instrumentSound = 'drum.tambourine'
        self.inGMPercMap = True
        self.percMapPitch = 54

class Whip(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Whip'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'effect.whip'

class Ratchet(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Ratchet'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'rattle.ratchet'

class Siren(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Siren'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'effect.siren'

class SandpaperBlocks(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Sandpaper Blocks'
        self.instrumentAbbreviation = 'Sand Bl'
        self.instrumentSound = 'wood.sand-block'

class WindMachine(UnpitchedPercussion):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Wind Machine'
        # TODO: self.instrumentAbbreviation = ''
        self.instrumentSound = 'effect.wind'

# -----------------------------------------------------

class Vocalist(Instrument):
    '''
    n.b. called Vocalist to not be confused with stream.Voice
    '''

    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Voice'
        self.instrumentAbbreviation = 'V'
        self.midiProgram = 53

class Soprano(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Soprano'
        self.instrumentAbbreviation = 'S'
        self.instrumentSound = 'voice.soprano'

class MezzoSoprano(Soprano):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Mezzo-Soprano'
        self.instrumentAbbreviation = 'Mez'
        self.instrumentSound = 'voice.mezzo-soprano'

class Alto(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Alto'
        self.instrumentAbbreviation = 'A'
        self.instrumentSound = 'voice.alto'

class Tenor(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Tenor'
        self.instrumentAbbreviation = 'T'
        self.instrumentSound = 'voice.tenor'

class Baritone(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Baritone'
        self.instrumentAbbreviation = 'Bar'
        self.instrumentSound = 'voice.baritone'

class Bass(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Bass'
        self.instrumentAbbreviation = 'B'
        self.instrumentSound = 'voice.bass'

class Choir(Vocalist):
    def __init__(self, **keywords):
        super().__init__(**keywords)

        self.instrumentName = 'Choir'
        self.instrumentAbbreviation = 'Ch'
        self.instrumentSound = 'voice.choir'
        self.midiProgram = 52

# -----------------------------------------------------

class Conductor(Instrument):
    '''
    Presently used only for tracking the MIDI track containing tempo,
    key signature, and related metadata.
    '''

    def __init__(self, **keywords):
        super().__init__(instrumentName='Conductor', **keywords)

# -----------------------------------------------------------------------------

# noinspection SpellCheckingInspection
ensembleNamesBySize = ['no performers', 'solo', 'duet', 'trio', 'quartet',
                       'quintet', 'sextet', 'septet', 'octet', 'nonet', 'dectet',
                       'undectet', 'duodectet', 'tredectet', 'quattuordectet',
                       'quindectet', 'sexdectet', 'septendectet', 'octodectet',
                       'novemdectet', 'vigetet', 'unvigetet', 'duovigetet',
                       'trevigetet', 'quattuorvigetet', 'quinvigetet', 'sexvigetet',
                       'septenvigetet', 'octovigetet', 'novemvigetet',
                       'trigetet', 'untrigetet', 'duotrigetet', 'tretrigetet',
                       'quottuortrigetet', 'quintrigetet', 'sextrigetet',
                       'septentrigetet', 'octotrigetet', 'novemtrigetet',
                       'quadragetet', 'unquadragetet', 'duoquadragetet',
                       'trequadragetet', 'quattuorquadragetet', 'quinquadragetet',
                       'sexquadragetet', 'octoquadragetet', 'octoquadragetet',
                       'novemquadragetet', 'quinquagetet', 'unquinquagetet',
                       'duoquinquagetet', 'trequinguagetet', 'quattuorquinquagetet',
                       'quinquinquagetet', 'sexquinquagetet', 'septenquinquagetet',
                       'octoquinquagetet', 'novemquinquagetet', 'sexagetet',
                       'undexagetet', 'duosexagetet', 'tresexagetet',
                       'quoattuorsexagetet', 'quinsexagetet', 'sexsexagetet',
                       'septensexagetet', 'octosexagetet', 'novemsexagetet',
                       'septuagetet', 'unseptuagetet', 'duoseptuagetet', 'treseptuagetet',
                       'quattuorseptuagetet', 'quinseptuagetet', 'sexseptuagetet',
                       'septenseptuagetet', 'octoseptuagetet', 'novemseptuagetet',
                       'octogetet', 'unoctogetet', 'duooctogetet',
                       'treoctogetet', 'quattuoroctogetet', 'quinoctogetet',
                       'sexoctogetet', 'septoctogetet', 'octooctogetet',
                       'novemoctogetet', 'nonagetet', 'unnonagetet', 'duononagetet',
                       'trenonagetet', 'quattuornonagetet', 'quinnonagetet',
                       'sexnonagetet', 'septennonagetet', 'octononagetet',
                       'novemnonagetet', 'centet']

def ensembleNameBySize(number):
    '''
    return the name of a generic ensemble with "number" players:

    >>> instrument.ensembleNameBySize(4)
    'quartet'
    >>> instrument.ensembleNameBySize(1)
    'solo'
    >>> instrument.ensembleNameBySize(83)
    'treoctogetet'
    '''
    if number > 100:
        return 'large ensemble'
    elif number < 0:
        raise InstrumentException('okay, you are on your own for this one buddy')
    else:
        return ensembleNamesBySize[int(number)]

def deduplicate(s: stream.Stream, inPlace: bool = False) -> stream.Stream:
    '''
    Check every offset in `s` for multiple instrument instances.
    If the `.partName` can be standardized across instances,
    i.e. if each instance has the same value or `None`,
    and likewise for `.instrumentName`, standardize the attributes.
    Further, and only if the above conditions are met,
    if there are two instances of the same class, remove all but one;
    if at least one generic `Instrument` instance is found at the same
    offset as one or more specific instruments, remove the generic `Instrument` instances.

    Two `Instrument` instances:

    >>> i1 = instrument.Instrument(instrumentName='Semi-Hollow Body')
    >>> i2 = instrument.Instrument()
    >>> i2.partName = 'Electric Guitar'
    >>> s1 = stream.Stream()
    >>> s1.insert(4, i1)
    >>> s1.insert(4, i2)
    >>> list(s1.getInstruments())
    [<music21.instrument.Instrument 'Semi-Hollow Body'>,
        <music21.instrument.Instrument 'Electric Guitar: '>]
    >>> post = instrument.deduplicate(s1)
    >>> list(post.getInstruments())
    [<music21.instrument.Instrument 'Electric Guitar: Semi-Hollow Body'>]

    One `Instrument` instance and one subclass instance, with `inPlace` and parts:

    >>> from music21.stream import Score, Part
    >>> i3 = instrument.Instrument()
    >>> i3.partName = 'Piccolo'
    >>> i4 = instrument.Piccolo()
    >>> s2 = stream.Score()
    >>> p1 = stream.Part()
    >>> p1.append([i3, i4])
    >>> p2 = stream.Part()
    >>> p2.append([instrument.Flute(), instrument.Flute()])
    >>> s2.insert(0, p1)
    >>> s2.insert(0, p2)
    >>> list(p1.getInstruments())
    [<music21.instrument.Instrument 'Piccolo: '>, <music21.instrument.Piccolo 'Piccolo'>]
    >>> list(p2.getInstruments())
    [<music21.instrument.Flute 'Flute'>, <music21.instrument.Flute 'Flute'>]
    >>> s2 = instrument.deduplicate(s2, inPlace=True)
    >>> list(p1.getInstruments())
    [<music21.instrument.Piccolo 'Piccolo: Piccolo'>]
    >>> list(p2.getInstruments())
    [<music21.instrument.Flute 'Flute'>]
    '''
    from music21 import stream

    if inPlace:
        returnObj = s
    else:
        returnObj = s.coreCopyAsDerivation('instrument.deduplicate')

    if not returnObj.hasPartLikeStreams():
        substreams: Iterable[stream.Stream] = [returnObj]
    else:
        substreams = returnObj.getElementsByClass(stream.Stream)

    for sub in substreams:
        oTree = OffsetTree(sub[Instrument].stream())
        for o in oTree:
            if len(o) == 1:
                continue
            notNonePartNames = {i.partName for i in o if i.partName is not None}
            notNoneInstNames = {i.instrumentName for i in o if i.instrumentName is not None}

            # Proceed only if 0-1 part name AND 0-1 instrument name candidates
            if len(notNonePartNames) > 1 or len(notNoneInstNames) > 1:
                continue

            partName = None
            for pName in notNonePartNames:
                partName = pName
            instrumentName = None
            for iName in notNoneInstNames:
                instrumentName = iName

            classes = {inst.__class__ for inst in o}
            # Case: 2+ instances of the same class
            if len(classes) == 1:
                surviving = None
                # Treat first as the surviving instance and standardize name
                for inst in o:
                    inst.partName = partName
                    inst.instrumentName = instrumentName
                    surviving = inst
                    break
                # Remove remaining instruments
                for inst in o:
                    if inst is surviving:
                        continue
                    sub.remove(inst, recurse=True)
            # Case: mixed classes: standardize names
            # Remove instances of generic `Instrument` if found
            else:
                for inst in o:
                    if inst.__class__ == Instrument:
                        sub.remove(inst, recurse=True)
                    else:
                        inst.partName = partName
                        inst.instrumentName = instrumentName

    return returnObj

# For lookup by MIDI Program
# TODOs should be resolved with another mapping from MIDI program
# to .instrumentSound
MIDI_PROGRAM_TO_INSTRUMENT = {
    0: Piano,
    1: Piano,
    2: ElectricPiano,
    3: Piano,
    4: ElectricPiano,
    5: ElectricPiano,
    6: Harpsichord,
    7: Clavichord,
    8: Celesta,
    9: Glockenspiel,
    10: Glockenspiel,  # TODO: MusicBox
    11: Vibraphone,
    12: Marimba,
    13: Xylophone,
    14: TubularBells,
    15: Dulcimer,
    16: ElectricOrgan,  # TODO: instrumentSound
    17: ElectricOrgan,  # TODO: instrumentSound
    18: ElectricOrgan,  # TODO: instrumentSound
    19: PipeOrgan,
    20: ReedOrgan,
    21: Accordion,
    22: Harmonica,
    23: Accordion,  # TODO: instrumentSound
    24: AcousticGuitar,  # TODO: instrumentSound
    25: AcousticGuitar,  # TODO: instrumentSound
    26: ElectricGuitar,  # TODO: instrumentSound
    27: ElectricGuitar,  # TODO: instrumentSound
    28: ElectricGuitar,  # TODO: instrumentSound
    29: ElectricGuitar,  # TODO: instrumentSound
    30: ElectricGuitar,  # TODO: instrumentSound
    31: ElectricGuitar,  # TODO: instrumentSound
    32: AcousticBass,
    33: ElectricBass,
    34: ElectricBass,  # TODO: instrumentSound
    35: FretlessBass,
    36: ElectricBass,  # TODO: instrumentSound
    37: ElectricBass,  # TODO: instrumentSound
    38: ElectricBass,  # TODO: instrumentSound
    39: ElectricBass,  # TODO: instrumentSound
    40: Violin,
    41: Viola,
    42: Violoncello,
    43: Contrabass,
    44: StringInstrument,  # TODO: instrumentSound
    45: StringInstrument,  # TODO: instrumentSound
    46: Harp,
    47: Timpani,
    48: StringInstrument,  # TODO: instrumentSound
    49: StringInstrument,  # TODO: instrumentSound
    50: StringInstrument,  # TODO: instrumentSound
    51: StringInstrument,  # TODO: instrumentSound
    52: Choir,  # TODO: instrumentSound
    53: Vocalist,  # TODO: instrumentSound
    54: Vocalist,  # TODO: instrumentSound
    55: Sampler,
    56: Trumpet,
    57: Trombone,
    58: Tuba,
    59: Trumpet,  # TODO: instrumentSound
    60: Horn,
    61: BrassInstrument,  # TODO: instrumentSound
    62: BrassInstrument,  # TODO: instrumentSound
    63: BrassInstrument,  # TODO: instrumentSound
    64: SopranoSaxophone,
    65: AltoSaxophone,
    66: TenorSaxophone,
    67: BaritoneSaxophone,
    68: Oboe,
    69: EnglishHorn,
    70: Bassoon,
    71: Clarinet,
    72: Piccolo,
    73: Flute,
    74: Recorder,
    75: PanFlute,
    76: PanFlute,  # TODO 76: Bottle
    77: Shakuhachi,
    78: Whistle,
    79: Ocarina,
    80: Sampler,  # TODO: all Sampler here and below: instrumentSound
    81: Sampler,
    82: Sampler,
    83: Sampler,
    84: Sampler,
    85: Sampler,
    86: Sampler,
    87: Sampler,
    88: Sampler,
    89: Sampler,
    90: Sampler,
    91: Sampler,
    92: Sampler,
    93: Sampler,
    94: Sampler,
    95: Sampler,
    96: Sampler,
    97: Sampler,
    98: Sampler,
    99: Sampler,
    100: Sampler,
    101: Sampler,
    102: Sampler,
    103: Sampler,
    104: Sitar,
    105: Banjo,
    106: Shamisen,
    107: Koto,
    108: Kalimba,
    109: Bagpipes,
    110: Violin,  # TODO: instrumentSound
    111: Shehnai,
    112: Glockenspiel,  # TODO 112: Tinkle Bell
    113: Agogo,
    114: SteelDrum,
    115: Woodblock,
    116: Taiko,
    117: TomTom,
    118: Sampler,  # TODO: instrumentSound  # debatable if this should be drum?
    119: Sampler,
    120: Sampler,
    121: Sampler,
    122: Sampler,
    123: Sampler,
    124: Sampler,
    125: Sampler,
    126: Sampler,
    127: Sampler
}

def instrumentFromMidiProgram(number: int) -> Instrument:
    '''
    Return the instrument with "number" as its assigned MIDI program.
    Notice any of the values 0-5 will return Piano.

    Lookups are performed against `instrument.MIDI_PROGRAM_TO_INSTRUMENT`.

    >>> instrument.instrumentFromMidiProgram(4)
    <music21.instrument.ElectricPiano 'Electric Piano'>
    >>> instrument.instrumentFromMidiProgram(21)
    <music21.instrument.Accordion 'Accordion'>
    >>> instrument.instrumentFromMidiProgram(500)
    Traceback (most recent call last):
    music21.exceptions21.InstrumentException: No instrument found for MIDI program 500
    >>> instrument.instrumentFromMidiProgram('43')
    Traceback (most recent call last):
    TypeError: Expected int, got <class 'str'>
    '''

    try:
        class_ = MIDI_PROGRAM_TO_INSTRUMENT[number]
        inst = class_()
        inst.midiProgram = number
        # TODO: if midiProgram in MIDI_PROGRAM_SOUND_MAP:
        #            inst.instrumentSound = MIDI_PROGRAM_SOUND_MAP[midiProgram]
    except KeyError as e:
        if not isinstance(number, int):
            raise TypeError(f'Expected int, got {type(number)}') from e
        raise InstrumentException(f'No instrument found for MIDI program {number}') from e
    return inst

def partitionByInstrument(streamObj: stream.Stream) -> stream.Stream:
    # noinspection PyShadowingNames
    '''
    Given a single Stream, or a Score or similar multi-part structure,
    partition into a Part for each unique Instrument, joining events
    possibly from different parts.

    >>> p1 = converter.parse("tinynotation: 4/4 c4  d  e  f  g  a  b  c'  c1")
    >>> p2 = converter.parse("tinynotation: 4/4 C#4 D# E# F# G# A# B# c#  C#1")

    >>> p1.getElementsByClass(stream.Measure)[0].insert(0.0, instrument.Piccolo())
    >>> p1.getElementsByClass(stream.Measure)[0].insert(2.0, instrument.AltoSaxophone())
    >>> p1.getElementsByClass(stream.Measure)[1].insert(3.0, instrument.Piccolo())

    >>> p2.getElementsByClass(stream.Measure)[0].insert(0.0, instrument.Trombone())
    >>> p2.getElementsByClass(stream.Measure)[0].insert(3.0, instrument.Piccolo())  # not likely
    >>> p2.getElementsByClass(stream.Measure)[1].insert(1.0, instrument.Trombone())

    >>> s = stream.Score()
    >>> s.insert(0, p1)
    >>> s.insert(0, p2)
    >>> s.show('text')
    {0.0} <music21.stream.Part ...>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.instrument.Piccolo 'Piccolo'>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note D>
            {2.0} <music21.instrument.AltoSaxophone 'Alto Saxophone'>
            {2.0} <music21.note.Note E>
            {3.0} <music21.note.Note F>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {2.0} <music21.note.Note B>
            {3.0} <music21.instrument.Piccolo 'Piccolo'>
            {3.0} <music21.note.Note C>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note C>
            {4.0} <music21.bar.Barline type=final>
    {0.0} <music21.stream.Part ...>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.instrument.Trombone 'Trombone'>
            {0.0} <music21.clef.BassClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note C#>
            {1.0} <music21.note.Note D#>
            {2.0} <music21.note.Note E#>
            {3.0} <music21.instrument.Piccolo 'Piccolo'>
            {3.0} <music21.note.Note F#>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note G#>
            {1.0} <music21.instrument.Trombone 'Trombone'>
            {1.0} <music21.note.Note A#>
            {2.0} <music21.note.Note B#>
            {3.0} <music21.note.Note C#>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note C#>
            {4.0} <music21.bar.Barline type=final>

    >>> s2 = instrument.partitionByInstrument(s)
    >>> len(s2.parts)
    3

    # TODO: this step might not be necessary:

    >>> for p in s2.parts:
    ...     p.makeRests(fillGaps=True, inPlace=True)

    # TODO: this step SHOULD not be necessary (.template()):

    >>> for p in s2.parts:
    ...     p.makeMeasures(inPlace=True)
    ...     p.makeTies(inPlace=True)

    >>> s2.show('text')
    {0.0} <music21.stream.Part Piccolo>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.instrument.Piccolo 'Piccolo'>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note C>
            {1.0} <music21.note.Note D>
            {2.0} <music21.note.Rest quarter>
            {3.0} <music21.note.Note F#>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note G#>
            {1.0} <music21.note.Rest half>
            {3.0} <music21.note.Note C>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note C>
            {4.0} <music21.bar.Barline type=final>
    {0.0} <music21.stream.Part Alto Saxophone>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.instrument.AltoSaxophone 'Alto Saxophone'>
            {0.0} <music21.clef.TrebleClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Rest half>
            {2.0} <music21.note.Note E>
            {3.0} <music21.note.Note F>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Note G>
            {1.0} <music21.note.Note A>
            {2.0} <music21.note.Note B>
            {3.0} <music21.bar.Barline type=final>
    {0.0} <music21.stream.Part Trombone>
        {0.0} <music21.stream.Measure 1 offset=0.0>
            {0.0} <music21.instrument.Trombone 'Trombone'>
            {0.0} <music21.clef.BassClef>
            {0.0} <music21.meter.TimeSignature 4/4>
            {0.0} <music21.note.Note C#>
            {1.0} <music21.note.Note D#>
            {2.0} <music21.note.Note E#>
            {3.0} <music21.note.Rest quarter>
        {4.0} <music21.stream.Measure 2 offset=4.0>
            {0.0} <music21.note.Rest quarter>
            {1.0} <music21.note.Note A#>
            {2.0} <music21.note.Note B#>
            {3.0} <music21.note.Note C#>
        {8.0} <music21.stream.Measure 3 offset=8.0>
            {0.0} <music21.note.Note C#>
            {4.0} <music21.bar.Barline type=final>

    * Changed in v8: returns the original stream if there are no instruments.

    TODO: parts should be in Score Order. Coincidence that this almost works.
    TODO: use proper recursion to make a copy of the stream.
    TODO: final barlines should be aligned.
    '''
    from music21 import stream
    if not streamObj.hasPartLikeStreams():
        # place in a score for uniform operations
        s = stream.Score()
        s.insert(0, streamObj.flatten())
    else:
        s = stream.Score()
        # append flat parts
        for sub in streamObj.getElementsByClass(stream.Stream):
            s.insert(0, sub.flatten())

    # first, let's extend the duration of each instrument to match stream
    for sub in s.getElementsByClass(stream.Stream):
        sub.extendDuration('Instrument', inPlace=True)

    # first, find all unique instruments
    instrumentIterator = s[Instrument]
    if not instrumentIterator:
        return s  # no partition is available

    names: OrderedDict[str, dict[str, t.Any]] = OrderedDict()  # store unique names
    for instrumentObj in instrumentIterator:
        # matching here by instrument name
        if instrumentObj.instrumentName not in names:
            names[instrumentObj.instrumentName or ''] = {'Instrument': instrumentObj}
            # just store one instance

    # create a return object that has a part for each instrument
    post = stream.Score()
    for iName in names:
        p = stream.Part()
        p.id = iName
        # add the instrument instance
        p.insert(0, names[iName]['Instrument'])
        # store a handle to this part
        names[iName]['Part'] = p
        post.insert(0, p)

    # iterate over flat sources; get events within each defined instrument
    # add to corresponding part
    for el in s:
        if not el.isStream:
            post.insert(el.offset, el)

        subStream = el
        for i in subStream.getElementsByClass(Instrument):
            start = i.offset
            # duration will have been set with sub.extendDuration above
            end = i.offset + i.duration.quarterLength
            # get destination Part
            p = names[i.instrumentName or '']['Part']

            coll = subStream.getElementsByOffset(
                start,
                end,
                # do not include elements that start at the end
                includeEndBoundary=False,
                mustFinishInSpan=False,
                mustBeginInSpan=True
            )
            # add to part at original offset
            # do not gather instrument
            for e in coll.getElementsNotOfClass(Instrument):
                try:
                    p.insert(subStream.elementOffset(e), e)
                except stream.StreamException:
                    pass
                    # it is possible to enter an element twice because the getElementsByOffset
                    # might return something twice if it's at the same offset as the
                    # instrument switch

    for inst in post.recurse().getElementsByClass(Instrument):
        inst.duration.quarterLength = 0
    return post

def _combinations(instrumentString):
    '''
    find all combinations of instrumentString.  Remove all punctuation.
    '''
    sampleList = instrumentString.split()
    allComb = []
    for size in range(1, len(sampleList) + 1):
        for i in range(len(sampleList) - size + 1):
            allComb.append(' '.join(sampleList[i:i + size]))
    return allComb

class SearchLanguage(common.enums.StrEnum):
    ALL = 'all'
    ENGLISH = 'english'
    FRENCH = 'french'
    GERMAN = 'german'
    ITALIAN = 'italian'
    RUSSIAN = 'russian'
    SPANISH = 'spanish'
    ABBREVIATION = 'abbreviation'

def fromString(instrumentString: str,
               language: SearchLanguage = SearchLanguage.ALL):
    '''
    Given a string with instrument content (from an orchestral score
    for example), attempts to return an appropriate
    :class:`~music21.instrument.Instrument`.

    >>> t1 = instrument.fromString('Clarinet 2 in A')
    >>> t1
    <music21.instrument.Clarinet 'Clarinet 2 in A'>
    >>> t1.transposition
    <music21.interval.Interval m-3>

    >>> t2 = instrument.fromString('Clarinetto 3')
    >>> t2
    <music21.instrument.Clarinet 'Clarinetto 3'>

    >>> t3 = instrument.fromString('flauto 2')
    >>> t3
    <music21.instrument.Flute 'flauto 2'>

    Excess information is ignored, and the useful information can be extracted
    correctly as long as it's sequential.

    >>> t4 = instrument.fromString('I <3 music saxofono tenore go beavers')
    >>> t4
    <music21.instrument.TenorSaxophone 'I <3 music saxofono tenore go beavers'>

    Some more demos:

    >>> t5 = instrument.fromString('Bb Clarinet')
    >>> t5
    <music21.instrument.Clarinet 'Bb Clarinet'>
    >>> t5.transposition
    <music21.interval.Interval M-2>

    >>> t6 = instrument.fromString('Clarinet in B-flat')
    >>> t5.__class__ == t6.__class__
    True

    >>> t5.transposition == t6.transposition
    True

    >>> t7 = instrument.fromString('B-flat Clarinet.')
    >>> t5.__class__ == t7.__class__ and t5.transposition == t7.transposition
    True

    >>> t8 = instrument.fromString('Eb Clarinet')
    >>> t5.__class__ == t8.__class__
    True
    >>> t8.transposition
    <music21.interval.Interval m3>

    Note that because of the ubiquity of B-flat clarinets and trumpets, and the
    rareness of B-natural forms of those instruments, this gives a B-flat, not
    B-natural clarinet, using the German form:

    >>> t9 = instrument.fromString('Klarinette in B.')
    >>> t9
    <music21.instrument.Clarinet 'Klarinette in B.'>
    >>> t9.transposition
    <music21.interval.Interval M-2>

    Use "H" or "b-natural" to get an instrument in B-major.  Or donate one to me,
    and I'll change this back!

    Standard abbreviations are acceptable:

    >>> t10 = instrument.fromString('Cl in B-flat')
    >>> t10
    <music21.instrument.Clarinet 'Cl in B-flat'>
    >>> t10.transposition
    <music21.interval.Interval M-2>

    This should work with or without a terminal period (for both 'Cl' and 'Cl.'):

    >>> t11 = instrument.fromString('Cl. in B-flat')
    >>> t11.__class__ == t10.__class__
    True

    Previously an exact instrument name was not always working:

    >>> instrument.fromString('Flute')
    <music21.instrument.Flute 'Flute'>

    This common MIDI instrument was not previously working:

    >>> instrument.fromString('Choir (Aahs)')
    <music21.instrument.Choir 'Choir (Aahs)'>

    By default, this function searches over all stored instrument names.
    This includes multiple languages as well as the abbreviations
    (an honorary 'language' for these purposes).

    Alternatively, you can specify the language to search using the `language`
    argument. (New in v7.3.)

    >>> t12 = instrument.fromString('Klarinette', language=instrument.SearchLanguage.GERMAN)
    >>> t12
    <music21.instrument.Clarinet 'Klarinette'>

    This case works because the name 'Klarinette' is a recognised instrument name in German
    and appears in the German language list.
    If you search for a German name like 'Klarinette' on the French list (language='french'),
    then it won't be found and an InstrumentException will be raised.
    An InstrumentException is also raised if the specified language is not
    one of those currently supported:
    'english', 'french', 'german', 'italian', 'russian', 'spanish', and 'abbreviation'.

    Note that the language string is not case-sensitive, so 'French' is also fine.
    '''
    from music21.languageExcerpts import instrumentLookup

    language = language.lower()
    if language not in SearchLanguage:
        raise InstrumentException(f'Chosen language {language} not currently supported.')
    sourceDict = getattr(instrumentLookup, language + 'ToClassName')

    instrumentStringOrig = instrumentString
    instrumentString = instrumentString.replace('.', ' ')  # sic, before removePunctuation
    instrumentString = instrumentString.lower()  # previously run on each substring separately
    instrumentString = common.removePunctuation(instrumentString)
    allCombinations = _combinations(instrumentString)
    # First task: Find the best instrument.
    bestInstrument = None
    bestName: str = ''

    this_module = importlib.import_module('music21.instrument')
    for substring in allCombinations:
        try:
            className = sourceDict[substring]
            thisInstClass = getattr(this_module, className)
            # In case users have overridden the module and imported more things
            if base.Music21Object not in thisInstClass.__mro__:  # pragma: no cover
                raise KeyError
            thisInstrument = thisInstClass()
            thisBestName = thisInstrument.bestName().lower()
            if (bestInstrument is None
                    or len(thisBestName.split()) >= len(bestName.split())
                    and not isinstance(bestInstrument, thisInstClass)):
                # priority is also given to same length instruments which fall later
                # on in the string (i.e. Bb Piccolo Trumpet)
                bestInstrument = thisInstrument
                bestInstrument.instrumentName = instrumentStringOrig
                bestName = thisBestName
        except KeyError:
            pass
    if bestInstrument is None:
        raise InstrumentException(
            f'Could not match string with instrument: {instrumentStringOrig}')
    if bestName not in instrumentLookup.transposition:
        return bestInstrument

    # A transposition table is defined for the instrument.
    # Second task: Determine appropriate transposition (if any)
    for substring in allCombinations:
        try:
            bestPitch = instrumentLookup.pitchFullNameToName[substring.lower()]
            bestInterval = instrumentLookup.transposition[bestName][bestPitch]
            bestInstrument.transposition = interval.Interval(bestInterval)
            break
        except KeyError:
            pass
    return bestInstrument

def _getKeys(classNameString: str,
             language: SearchLanguage = SearchLanguage.ALL):
    '''
    Retrieve the key or keys (variant instrument names)
    from an instrumentLookup dict, given
    the language (which instrumentLookup dict) and
    value (classNameString).

    Returns all relevant keys as a list of strings (empty if no matches).
    '''

    from music21.languageExcerpts import instrumentLookup
    sourceDict = getattr(instrumentLookup, language + 'ToClassName')

    returns = []
    for key, value in sourceDict.items():
        if classNameString == value:
            returns.append(key)
    return returns

def getAllNamesForInstrument(instrumentClass: Instrument,
                             language: SearchLanguage = SearchLanguage.ALL):
    '''
    Retrieves all currently stored names for a given instrument.

    The instrumentClass should be a valid music21
    :class:`~music21.instrument.Instrument`.

    By default, this function searches over all supported languages
    including instrument name abbreviations (an honorary 'language' for these purposes),
    and returns a dict with keys for the language tested and values as a list of
    strings for any names in that language.

    >>> instrument.getAllNamesForInstrument(instrument.Flute())
    {'english': ['flute', 'flutes', 'transverse flute'],
    'french': ['flûte', 'flûte traversière', 'flûtes', 'grande flûte'],
    'german': ['flöte', 'flöten', 'querflöte'],
    'italian': ['flauti', 'flauto', 'flauto traverso'],
    'russian': ['fleita'],
    'spanish': ['flauta', 'flauta de boehm', 'flauta de concierto',
                'flauta traversa', 'flauta travesera', 'flautas'],
    'abbreviation': ['fl']}

    Alternatively, you can specify the language to search using the `language`
    argument.

    >>> instrument.getAllNamesForInstrument(instrument.Flute(), language='german')
    {'german': ['flöte', 'flöten', 'querflöte']}

    An InstrumentException is raised if the specified language is not
    one of those currently supported:
    'english', 'french', 'german', 'italian', 'russian', 'spanish', and 'abbreviation'.

    Note that the language string is not case-sensitive, so 'German' is also fine.

    '''

    language = language.lower()
    instrumentNameDict = {}

    instrumentClassName = instrumentClass.instrumentName or ''

    if language == SearchLanguage.ALL:
        for lang in SearchLanguage:
            if lang is SearchLanguage.ALL:
                continue  # skip the 'all' combination, handle the languages separately.
            instrumentNameDict[str(lang)] = _getKeys(instrumentClassName, lang)
    elif language not in SearchLanguage:
        raise InstrumentException(f'Chosen language {language} not currently supported.')
    else:  # one, valid language
        instrumentNameDict[language] = _getKeys(instrumentClassName, SearchLanguage(language))

    return instrumentNameDict

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER = [Instrument]

if __name__ == '__main__':
    # sys.arg test options will be used in mainTest()
    import music21

    music21.mainTest(Test)
