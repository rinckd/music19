# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         corpus_bridge.py
# Purpose:      Bridge between music21 corpus and music19 objects
#
# Authors:      Claude Code
#
# Copyright:    Copyright © 2025 Music19 Project
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
"""
This module provides a bridge between music21's corpus and music19 objects.
It imports from music21.corpus but converts the results to music19 objects.
"""
from __future__ import annotations

try:
    import music21.corpus
    import music21.stream
    import music21.note
    import music21.pitch
    import music21.duration
    import music21.chord
    import music21.meter
    import music21.key
    import music21.clef
    import music21.bar
    import music21.metadata
    import music21.instrument
    import music21.layout
    import music21.expressions
    import music21.note
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False

from music19 import stream
from music19 import note
from music19 import pitch
from music19 import duration
from music19 import chord
from music19 import meter
from music19 import key
from music19 import clef
from music19 import bar
from music19 import metadata
from music19 import instrument
from music19 import layout
from music19 import expressions


def check_music21_availability():
    """Check if music21 is available for import."""
    if not MUSIC21_AVAILABLE:
        raise ImportError(
            "music21 is required for corpus functionality. "
            "Please install music21: pip install music21"
        )


def convert_music21_to_music19(obj):
    """
    Convert a music21 object to its music19 equivalent.
    This simplified converter focuses on preserving critical attributes.
    """
    check_music21_availability()
    
    if obj is None:
        return None
    
    # Handle basic types that don't need conversion
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # Handle Stream objects
    if isinstance(obj, music21.stream.Stream):
        return _convert_stream(obj)
    
    # Handle Note objects
    elif isinstance(obj, music21.note.Note):
        return _convert_note(obj)
    
    # Handle Rest objects
    elif isinstance(obj, music21.note.Rest):
        return _convert_rest(obj)
    
    # Handle Chord objects
    elif isinstance(obj, music21.chord.Chord):
        return _convert_chord(obj)
    
    # Handle Pitch objects
    elif isinstance(obj, music21.pitch.Pitch):
        return _convert_pitch(obj)
    
    # Handle Duration objects
    elif isinstance(obj, music21.duration.Duration):
        return _convert_duration(obj)
    
    # Handle Meter objects
    elif isinstance(obj, music21.meter.TimeSignature):
        return _convert_time_signature(obj)
    
    # Handle Key objects (Key must come before KeySignature since Key inherits from KeySignature)
    elif isinstance(obj, music21.key.Key):
        return _convert_key(obj)
    elif isinstance(obj, music21.key.KeySignature):
        return _convert_key_signature(obj)
    
    # Handle Clef objects
    elif isinstance(obj, music21.clef.Clef):
        return _convert_clef(obj)
    
    # Handle Bar objects
    elif isinstance(obj, music21.bar.Barline):
        return _convert_barline(obj)
    
    # Handle Metadata
    elif isinstance(obj, music21.metadata.Metadata):
        return _convert_metadata(obj)
    
    # Handle Instrument
    elif isinstance(obj, music21.instrument.Instrument):
        return _convert_instrument(obj)
    
    # Handle Layout objects
    elif isinstance(obj, music21.layout.LayoutBase):
        return _convert_layout(obj)
    
    # Handle Expression objects
    elif isinstance(obj, music21.expressions.Expression):
        return _convert_expression(obj)
    
    # Handle Lyric objects
    elif isinstance(obj, music21.note.Lyric):
        return _convert_lyric(obj)
    
    # For anything else, return None
    else:
        return None


def _convert_stream(m21_stream):
    """Convert a music21 Stream to a music19 Stream."""
    # Determine the correct stream type
    if isinstance(m21_stream, music21.stream.Score):
        m19_stream = stream.Score()
    elif isinstance(m21_stream, music21.stream.Part):
        m19_stream = stream.Part()
    elif isinstance(m21_stream, music21.stream.Measure):
        m19_stream = stream.Measure()
    elif isinstance(m21_stream, music21.stream.Voice):
        m19_stream = stream.Voice()
    else:
        m19_stream = stream.Stream()
    
    # Copy critical attributes
    if hasattr(m21_stream, 'id') and m21_stream.id:
        m19_stream.id = m21_stream.id
    
    # Copy measure-specific attributes for Measure streams
    if isinstance(m21_stream, music21.stream.Measure):
        if hasattr(m21_stream, 'number'):
            m19_stream.number = m21_stream.number
        if hasattr(m21_stream, 'paddingLeft'):
            m19_stream.paddingLeft = m21_stream.paddingLeft
        if hasattr(m21_stream, 'paddingRight'):
            m19_stream.paddingRight = m21_stream.paddingRight
    
    # Convert and add all elements while preserving their exact positions
    for element in m21_stream:
        converted_element = convert_music21_to_music19(element)
        if converted_element is not None:
            # Preserve the exact offset from the original
            original_offset = element.offset
            m19_stream.insert(original_offset, converted_element)
    
    # Handle metadata specially
    if hasattr(m21_stream, 'metadata') and m21_stream.metadata:
        m19_stream.metadata = _convert_metadata(m21_stream.metadata)
    
    # Stream is automatically finalized when elements are inserted
    
    return m19_stream


def _convert_note(m21_note):
    """Convert a music21 Note to a music19 Note."""
    # Convert pitch and duration
    m19_pitch = convert_music21_to_music19(m21_note.pitch)
    m19_duration = convert_music21_to_music19(m21_note.duration)
    
    # Create the note
    m19_note = note.Note(pitch=m19_pitch, quarterLength=m19_duration.quarterLength)
    
    # Copy critical attributes
    if hasattr(m21_note, 'offset'):
        m19_note.offset = m21_note.offset
    if hasattr(m21_note, 'id') and m21_note.id:
        m19_note.id = m21_note.id
    
    # Copy expressions
    if hasattr(m21_note, 'expressions') and m21_note.expressions:
        for expression in m21_note.expressions:
            converted_expression = convert_music21_to_music19(expression)
            if converted_expression is not None:
                m19_note.expressions.append(converted_expression)
    
    # Copy lyrics
    if hasattr(m21_note, 'lyrics') and m21_note.lyrics:
        for lyric in m21_note.lyrics:
            converted_lyric = _convert_lyric(lyric)
            if converted_lyric is not None:
                m19_note.lyrics.append(converted_lyric)
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_note, m19_note)
    
    return m19_note


def _convert_rest(m21_rest):
    """Convert a music21 Rest to a music19 Rest."""
    m19_duration = convert_music21_to_music19(m21_rest.duration)
    m19_rest = note.Rest(quarterLength=m19_duration.quarterLength)
    
    # Copy critical attributes
    if hasattr(m21_rest, 'offset'):
        m19_rest.offset = m21_rest.offset
    if hasattr(m21_rest, 'id') and m21_rest.id:
        m19_rest.id = m21_rest.id
    
    # Copy expressions
    if hasattr(m21_rest, 'expressions') and m21_rest.expressions:
        for expression in m21_rest.expressions:
            converted_expression = convert_music21_to_music19(expression)
            if converted_expression is not None:
                m19_rest.expressions.append(converted_expression)
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_rest, m19_rest)
    
    return m19_rest


def _convert_chord(m21_chord):
    """Convert a music21 Chord to a music19 Chord."""
    # Convert pitches
    m19_pitches = [convert_music21_to_music19(p) for p in m21_chord.pitches]
    m19_duration = convert_music21_to_music19(m21_chord.duration)
    
    m19_chord = chord.Chord(pitches=m19_pitches, quarterLength=m19_duration.quarterLength)
    
    # Copy critical attributes
    if hasattr(m21_chord, 'offset'):
        m19_chord.offset = m21_chord.offset
    if hasattr(m21_chord, 'id') and m21_chord.id:
        m19_chord.id = m21_chord.id
    
    # Copy expressions
    if hasattr(m21_chord, 'expressions') and m21_chord.expressions:
        for expression in m21_chord.expressions:
            converted_expression = convert_music21_to_music19(expression)
            if converted_expression is not None:
                m19_chord.expressions.append(converted_expression)
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_chord, m19_chord)
    
    return m19_chord


def _convert_pitch(m21_pitch):
    """Convert a music21 Pitch to a music19 Pitch."""
    return pitch.Pitch(
        step=m21_pitch.step,
        octave=m21_pitch.octave,
        accidental=m21_pitch.accidental.name if m21_pitch.accidental else None
    )


def _convert_duration(m21_duration):
    """Convert a music21 Duration to a music19 Duration."""
    return duration.Duration(quarterLength=m21_duration.quarterLength)


def _convert_time_signature(m21_ts):
    """Convert a music21 TimeSignature to a music19 TimeSignature."""
    m19_ts = meter.TimeSignature(f"{m21_ts.numerator}/{m21_ts.denominator}")
    
    # Copy critical attributes
    if hasattr(m21_ts, 'offset'):
        m19_ts.offset = m21_ts.offset
    if hasattr(m21_ts, 'id') and m21_ts.id:
        m19_ts.id = m21_ts.id
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_ts, m19_ts)
    
    return m19_ts


def _convert_key_signature(m21_ks):
    """Convert a music21 KeySignature to a music19 KeySignature."""
    m19_ks = key.KeySignature(m21_ks.sharps)
    
    # Copy critical attributes
    if hasattr(m21_ks, 'offset'):
        m19_ks.offset = m21_ks.offset
    if hasattr(m21_ks, 'id') and m21_ks.id:
        m19_ks.id = m21_ks.id
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_ks, m19_ks)
    
    return m19_ks


def _convert_key(m21_key):
    """Convert a music21 Key to a music19 Key."""
    m19_key = key.Key(m21_key.tonic.name, m21_key.mode)
    
    # Copy critical attributes
    if hasattr(m21_key, 'offset'):
        m19_key.offset = m21_key.offset
    if hasattr(m21_key, 'id') and m21_key.id:
        m19_key.id = m21_key.id
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_key, m19_key)
    
    return m19_key


def _convert_clef(m21_clef):
    """Convert a music21 Clef to a music19 Clef."""
    clef_name = m21_clef.__class__.__name__
    if hasattr(clef, clef_name):
        m19_clef = getattr(clef, clef_name)()
    else:
        # Fallback to generic clef
        m19_clef = clef.TrebleClef()
    
    # Copy critical attributes
    if hasattr(m21_clef, 'offset'):
        m19_clef.offset = m21_clef.offset
    if hasattr(m21_clef, 'id') and m21_clef.id:
        m19_clef.id = m21_clef.id
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_clef, m19_clef)
    
    return m19_clef


def _convert_barline(m21_barline):
    """Convert a music21 Barline to a music19 Barline."""
    m19_barline = bar.Barline(m21_barline.type)
    
    # Copy critical attributes
    if hasattr(m21_barline, 'offset'):
        m19_barline.offset = m21_barline.offset
    if hasattr(m21_barline, 'id') and m21_barline.id:
        m19_barline.id = m21_barline.id
    
    return m19_barline


def _convert_metadata(m21_metadata):
    """Convert a music21 Metadata to a music19 Metadata."""
    m19_metadata = metadata.Metadata()
    
    # Copy common metadata fields
    if hasattr(m21_metadata, 'title') and m21_metadata.title:
        m19_metadata.title = m21_metadata.title
    if hasattr(m21_metadata, 'composer') and m21_metadata.composer:
        m19_metadata.composer = m21_metadata.composer
    if hasattr(m21_metadata, 'date') and m21_metadata.date:
        m19_metadata.date = m21_metadata.date
    
    # Copy corpus file path if it exists
    if hasattr(m21_metadata, 'corpusFilepath') and m21_metadata.corpusFilepath:
        m19_metadata.corpusFilePath = m21_metadata.corpusFilepath
    
    return m19_metadata


def _convert_instrument(m21_instrument):
    """Convert a music21 Instrument to a music19 Instrument."""
    instrument_name = m21_instrument.__class__.__name__
    if hasattr(instrument, instrument_name):
        m19_instrument = getattr(instrument, instrument_name)()
    else:
        # Fallback to generic instrument
        m19_instrument = instrument.Instrument()
    
    # Copy critical attributes
    if hasattr(m21_instrument, 'offset'):
        m19_instrument.offset = m21_instrument.offset
    if hasattr(m21_instrument, 'id') and m21_instrument.id:
        m19_instrument.id = m21_instrument.id
    
    # Copy instrument-specific attributes
    if hasattr(m21_instrument, 'instrumentName') and hasattr(m19_instrument, 'instrumentName'):
        m19_instrument.instrumentName = m21_instrument.instrumentName
    if hasattr(m21_instrument, 'partName') and hasattr(m19_instrument, 'partName'):
        m19_instrument.partName = m21_instrument.partName
    if hasattr(m21_instrument, 'partId') and hasattr(m19_instrument, 'partId'):
        m19_instrument.partId = m21_instrument.partId
    
    return m19_instrument


def _convert_layout(m21_layout):
    """Convert a music21 Layout object to a music19 Layout object."""
    layout_name = m21_layout.__class__.__name__
    if hasattr(layout, layout_name):
        m19_layout = getattr(layout, layout_name)()
    else:
        # Fallback to generic LayoutBase
        m19_layout = layout.LayoutBase()
    
    # Copy critical attributes
    if hasattr(m21_layout, 'offset'):
        m19_layout.offset = m21_layout.offset
    if hasattr(m21_layout, 'id') and m21_layout.id:
        m19_layout.id = m21_layout.id
    
    # Copy layout-specific attributes
    if hasattr(m21_layout, 'isNew') and hasattr(m19_layout, 'isNew'):
        m19_layout.isNew = m21_layout.isNew
    
    # Copy common layout properties that might exist (but skip read-only ones)
    for attr in ['leftMargin', 'rightMargin', 'topDistance']:
        if hasattr(m21_layout, attr) and hasattr(m19_layout, attr):
            try:
                setattr(m19_layout, attr, getattr(m21_layout, attr))
            except (AttributeError, TypeError):
                # Skip read-only properties
                pass
    
    # Try to preserve beat-related information from the original context
    _copy_beat_context(m21_layout, m19_layout)
    
    return m19_layout


def _convert_expression(m21_expression):
    """Convert a music21 Expression to a music19 Expression."""
    expression_name = m21_expression.__class__.__name__
    if hasattr(expressions, expression_name):
        m19_expression = getattr(expressions, expression_name)()
    else:
        # Fallback to generic Expression
        m19_expression = expressions.Expression()
    
    # Copy critical attributes
    if hasattr(m21_expression, 'offset'):
        m19_expression.offset = m21_expression.offset
    if hasattr(m21_expression, 'id') and m21_expression.id:
        m19_expression.id = m21_expression.id
    
    # Copy expression-specific attributes that might exist
    for attr in ['name', 'content']:
        if hasattr(m21_expression, attr) and hasattr(m19_expression, attr):
            try:
                setattr(m19_expression, attr, getattr(m21_expression, attr))
            except (AttributeError, TypeError):
                # Skip read-only properties
                pass
    
    return m19_expression


def _copy_beat_context(m21_obj, m19_obj):
    """Copy beat-related context from music21 object to music19 object."""
    # Store cached values as instance attributes without modifying the class
    try:
        original_beat = m21_obj.beat
        if not (original_beat is None or (hasattr(original_beat, '__class__') and 
                original_beat.__class__.__name__ == 'float' and str(original_beat) == 'nan')):
            m19_obj._cached_beat = original_beat
    except:
        pass
    
    try:
        original_beat_strength = m21_obj.beatStrength  
        if not (original_beat_strength is None or (hasattr(original_beat_strength, '__class__') and 
                original_beat_strength.__class__.__name__ == 'float' and str(original_beat_strength) == 'nan')):
            m19_obj._cached_beatStrength = original_beat_strength
    except:
        pass
    
    try:
        original_beat_duration = m21_obj.beatDuration
        if original_beat_duration is not None and original_beat_duration.quarterLength > 0:
            m19_obj._cached_beatDuration = original_beat_duration.quarterLength
    except:
        pass
    
    try:
        original_measure_offset = m21_obj._getMeasureOffset()
        if original_measure_offset is not None:
            m19_obj._cached_measureOffset = original_measure_offset
    except:
        pass


def _convert_lyric(m21_lyric):
    """Convert a music21 Lyric to a music19 Lyric."""
    m19_lyric = note.Lyric(text=m21_lyric.text)
    
    # Copy critical attributes
    if hasattr(m21_lyric, 'number') and m21_lyric.number is not None:
        m19_lyric.number = m21_lyric.number
    if hasattr(m21_lyric, 'syllabic') and m21_lyric.syllabic is not None:
        m19_lyric.syllabic = m21_lyric.syllabic
    if hasattr(m21_lyric, 'identifier') and m21_lyric.identifier is not None:
        m19_lyric.identifier = m21_lyric.identifier
    
    return m19_lyric


# Bridge functions that use music21.corpus and convert results
def parse(*args, **kwargs):
    """Parse from music21.corpus and convert to music19 objects."""
    check_music21_availability()
    m21_result = music21.corpus.parse(*args, **kwargs)
    return convert_music21_to_music19(m21_result)


def search(*args, **kwargs):
    """Search music21.corpus (returns music21 metadata objects)."""
    check_music21_availability()
    return music21.corpus.search(*args, **kwargs)


def getWork(*args, **kwargs):
    """Get work from music21.corpus."""
    check_music21_availability()
    return music21.corpus.getWork(*args, **kwargs)


# Re-export other functions directly
def getCorePaths(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.getCorePaths(*args, **kwargs)


def getLocalPaths(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.getLocalPaths(*args, **kwargs)


def addPath(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.addPath(*args, **kwargs)


def getPaths(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.getPaths(*args, **kwargs)


def cacheMetadata(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.cacheMetadata(*args, **kwargs)


def getComposer(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.getComposer(*args, **kwargs)


def noCorpus(*args, **kwargs):
    check_music21_availability()
    return music21.corpus.noCorpus(*args, **kwargs)