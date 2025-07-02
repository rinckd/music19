from binascii import a2b_hex
import copy
import io
import math
import random
from music21 import chord
from music21 import converter
from music21 import common
from music21 import corpus
from music21 import environment
from music21 import instrument
from music21 import interval
from music21 import key
from music21 import meter
from music21.midi.base import (
    ChannelVoiceMessages,
    DeltaTime,
    MetaEvents,
    MidiTrack,
    MidiEvent,
    MidiFile,
)
from music21.midi.translate import (
    TimedNoteEvent,
    TranslateWarning,
    channelInstrumentData,
    conductorStream,
    getMetaEvents,
    midiAsciiStringToBinaryString,
    midiEventsToInstrument,
    midiEventsToNote,
    midiFileToStream,
    noteToMidiEvents,
    packetStorageFromSubstreamList,
    prepareStreamForMidi,
    streamHierarchyToMidiTracks,
    streamToMidiFile,
    updatePacketStorageWithChannelInfo,
)
from music21.musicxml import testPrimitive
from music21 import note
from music21 import percussion
from music21 import scale
from music21 import stream
from music21 import tempo
from music21 import tie
from music21 import volume

environLocal = environment.Environment('midi.tests')

# ------------------------------------------------------------------------------
