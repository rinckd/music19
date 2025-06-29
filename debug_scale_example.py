"""
This file demonstrates two music21 features:

1. SCALES - Creating and working with musical scales
   - Shows how to create a B-flat major scale
   - Demonstrates scale degrees and pitch classes

2. TABLATURE - Working with guitar/string instrument tablature
   - FretNote: Represents a single note on a fretboard (string, fret, fingering)
   - FretBoard: Represents a full fretboard with multiple notes
   - Instrument-specific fretboards: Guitar, Ukulele, Bass, Mandolin
   - ChordWithFretBoard: Combines chord symbols with tablature notation
   
The tablature module is useful for:
- Converting between tablature notation and pitches
- Representing guitar chord diagrams
- Working with different string instrument tunings
- Analyzing fretboard positions
"""

# Creating a B-flat major scale
from music21 import scale, note

# Create B-flat major scale
bb_scale = scale.MajorScale('B-')
print("B-flat major scale:")
for pitch in bb_scale.pitches:
    print(f"  {pitch}: pitchClass={pitch.pitchClass}, scaleDegree={bb_scale.getScaleDegreeFromPitch(pitch)}")

# You can also get scale degrees
bb_note = note.Note("B-4")
c_note = note.Note("C5")
print(f"\nIn B-flat major:")
print(f"  B-flat is scale degree: {bb_scale.getScaleDegreeFromPitch(bb_note.pitch)}")
print(f"  C is scale degree: {bb_scale.getScaleDegreeFromPitch(c_note.pitch)}")

# The pitch classes remain the same
print(f"\nPitch classes (chromatic, C=0):")
print(f"  B-flat: {bb_note.pitch.pitchClass}")
print(f"  C: {c_note.pitch.pitchClass}")

# =====================================================
# TABLATURE EXAMPLE
# =====================================================
print("\n" + "="*50)
print("TABLATURE EXAMPLE")
print("="*50 + "\n")

from music21 import tablature, stream, chord

# Example 1: Basic FretNote creation
print("Example 1: Creating individual FretNotes")
print("-" * 40)
fn1 = tablature.FretNote(string=1, fret=3, fingering=3)  # 1st string, 3rd fret, 3rd finger
fn2 = tablature.FretNote(string=2, fret=1, fingering=1)  # 2nd string, 1st fret, 1st finger
fn3 = tablature.FretNote(string=3, fret=0, fingering=0)  # 3rd string, open (0th fret)
fn4 = tablature.FretNote(string=4, fret=2, fingering=2)  # 4th string, 2nd fret, 2nd finger

print(f"FretNote 1: {fn1}")
print(f"FretNote 2: {fn2}")
print(f"FretNote 3: {fn3}")
print(f"FretNote 4: {fn4}")

# Example 2: Creating a Guitar FretBoard (standard tuning: E A D G B E)
print("\nExample 2: Guitar FretBoard - D minor chord")
print("-" * 40)
# D minor chord shape: xx0231 (strings 6 to 1)
dm_notes = [
    tablature.FretNote(string=4, fret=0),        # D (open 4th string)
    tablature.FretNote(string=3, fret=2, fingering=2),  # A 
    tablature.FretNote(string=2, fret=3, fingering=3),  # D
    tablature.FretNote(string=1, fret=1, fingering=1),  # F
]

guitar_fb = tablature.GuitarFretBoard(fretNotes=dm_notes)
print(f"Guitar FretBoard: {guitar_fb}")
print(f"Number of strings: {guitar_fb.numStrings}")
print(f"Tuning: {[str(p) for p in guitar_fb.tuning]}")

# Get the actual pitches from the fretboard
pitches = guitar_fb.getPitches()
print("\nPitches on each string (6 to 1):")
for i, p in enumerate(pitches):
    string_num = 6 - i
    if p is not None:
        print(f"  String {string_num}: {p} (MIDI: {p.midi})")
    else:
        print(f"  String {string_num}: not played")

# Example 3: Creating a Ukulele FretBoard (tuning: G C E A)
print("\nExample 3: Ukulele FretBoard - C major chord")
print("-" * 40)
# C major on ukulele: 0003 (strings 4 to 1)
c_major_uke = [
    tablature.FretNote(string=1, fret=3, fingering=3),  # C on 1st string
    # Other strings are open (0 fret) - we can leave them out or explicitly add them
    tablature.FretNote(string=2, fret=0),  # E (open)
    tablature.FretNote(string=3, fret=0),  # C (open)
    tablature.FretNote(string=4, fret=0),  # G (open)
]

uke_fb = tablature.UkeleleFretBoard(fretNotes=c_major_uke)
print(f"Ukulele FretBoard: {uke_fb}")
print(f"Tuning: {[str(p) for p in uke_fb.tuning]}")

uke_pitches = uke_fb.getPitches()
print("\nPitches on each string (4 to 1):")
for i, p in enumerate(uke_pitches):
    string_num = 4 - i
    if p is not None:
        print(f"  String {string_num}: {p}")

# Example 4: ChordWithFretBoard - combining chord symbols with tablature
print("\nExample 4: ChordWithFretBoard")
print("-" * 40)
# Create a chord symbol with fretboard diagram
am_notes = [
    tablature.FretNote(string=5, fret=0),        # A (open 5th string)
    tablature.FretNote(string=4, fret=2, fingering=2),  # E
    tablature.FretNote(string=3, fret=2, fingering=3),  # A
    tablature.FretNote(string=2, fret=1, fingering=1),  # C
    tablature.FretNote(string=1, fret=0),        # E (open 1st string)
]

# Note: ChordWithFretBoard needs tuning to be set
chord_with_fb = tablature.ChordWithFretBoard('Am', fretNotes=am_notes)
# Set the tuning manually (it doesn't inherit from GuitarFretBoard)
chord_with_fb.tuning = [tablature.pitch.Pitch('E2'), tablature.pitch.Pitch('A2'), 
                        tablature.pitch.Pitch('D3'), tablature.pitch.Pitch('G3'), 
                        tablature.pitch.Pitch('B3'), tablature.pitch.Pitch('E4')]

print(f"Chord symbol: {chord_with_fb.figure}")
print(f"Root: {chord_with_fb.root()}")
print(f"Chord pitches from symbol: {[str(p) for p in chord_with_fb.pitches]}")

# Example 5: Bass Guitar (4 strings: E A D G)
print("\nExample 5: Bass Guitar - Walking bass line")
print("-" * 40)
# Simple walking bass pattern
bass_positions = [
    tablature.FretNote(string=4, fret=3),  # G on E string
    tablature.FretNote(string=3, fret=0),  # A (open)
    tablature.FretNote(string=3, fret=2),  # B
    tablature.FretNote(string=2, fret=0),  # D (open)
]

for i, fn in enumerate(bass_positions):
    bass_fb = tablature.BassGuitarFretBoard(fretNotes=[fn])
    pitches = bass_fb.getPitches()
    played_pitch = [p for p in pitches if p is not None][0]
    print(f"  Position {i+1}: {fn} -> {played_pitch}")

# Example 6: Getting specific fret notes from a fretboard
print("\nExample 6: Querying FretBoard")
print("-" * 40)
print(f"D minor guitar chord - what's on string 3?")
note_on_string_3 = guitar_fb.getFretNoteByString(3)
if note_on_string_3:
    print(f"  {note_on_string_3}")
else:
    print("  Nothing played on string 3")

print(f"\nD minor notes from lowest to highest string:")
for fn in guitar_fb.fretNotesLowestFirst():
    print(f"  {fn}")

# Add explicit exit to avoid threading cleanup issues in Python 3.13
import sys
sys.exit(0)