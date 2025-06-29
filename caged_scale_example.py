"""
CAGED Scale System Example using music21 tablature

The CAGED system shows 5 different patterns to play a major scale on guitar,
based on the open chord shapes of C, A, G, E, and D.

For C major scale (C D E F G A B C), we'll show all 5 positions.
Each position connects to the next, covering the entire fretboard.
"""

from music21 import tablature, scale, stream, note

# Create C major scale for reference
c_major_scale = scale.MajorScale('C')
print("C Major Scale notes:", [str(p) for p in c_major_scale.pitches])
print("\n" + "="*60)

# Define the 5 CAGED shapes for C major scale
# Each shape shows the scale pattern starting from different positions

# SHAPE 1: C Shape (open position/1st position)
print("\nSHAPE 1: C Shape (Open Position)")
print("-" * 40)
print("Pattern: Uses open strings, based on open C chord")
print("Root notes: C on 3rd fret of 5th string, C on 1st fret of 2nd string")

c_shape_notes = [
    # Low E string
    tablature.FretNote(string=6, fret=0),  # E
    tablature.FretNote(string=6, fret=1),  # F
    tablature.FretNote(string=6, fret=3),  # G
    # A string
    tablature.FretNote(string=5, fret=0),  # A
    tablature.FretNote(string=5, fret=2),  # B
    tablature.FretNote(string=5, fret=3),  # C (root)
    # D string
    tablature.FretNote(string=4, fret=0),  # D
    tablature.FretNote(string=4, fret=2),  # E
    tablature.FretNote(string=4, fret=3),  # F
    # G string
    tablature.FretNote(string=3, fret=0),  # G
    tablature.FretNote(string=3, fret=2),  # A
    # B string
    tablature.FretNote(string=2, fret=0),  # B
    tablature.FretNote(string=2, fret=1),  # C (root)
    tablature.FretNote(string=2, fret=3),  # D
    # High E string
    tablature.FretNote(string=1, fret=0),  # E
    tablature.FretNote(string=1, fret=1),  # F
    tablature.FretNote(string=1, fret=3),  # G
]

# Display C shape scale notes
guitar = tablature.GuitarFretBoard()
print("\nC Shape - Scale notes per string:")
for string_num in range(6, 0, -1):
    notes_on_string = [fn for fn in c_shape_notes if fn.string == string_num]
    if notes_on_string:
        frets = [fn.fret for fn in notes_on_string]
        print(f"  String {string_num}: frets {frets}")

# SHAPE 2: A Shape (3rd position)
print("\n\nSHAPE 2: A Shape (3rd Position)")
print("-" * 40)
print("Pattern: Based on open A chord shape, shifted up")
print("Root notes: C on 3rd fret of 5th string, C on 5th fret of 3rd string")

a_shape_notes = [
    # Low E string
    tablature.FretNote(string=6, fret=3),  # G
    tablature.FretNote(string=6, fret=5),  # A
    # A string
    tablature.FretNote(string=5, fret=2),  # B
    tablature.FretNote(string=5, fret=3),  # C (root)
    tablature.FretNote(string=5, fret=5),  # D
    # D string
    tablature.FretNote(string=4, fret=2),  # E
    tablature.FretNote(string=4, fret=3),  # F
    tablature.FretNote(string=4, fret=5),  # G
    # G string
    tablature.FretNote(string=3, fret=2),  # A
    tablature.FretNote(string=3, fret=4),  # B
    tablature.FretNote(string=3, fret=5),  # C (root)
    # B string
    tablature.FretNote(string=2, fret=3),  # D
    tablature.FretNote(string=2, fret=5),  # E
    tablature.FretNote(string=2, fret=6),  # F
    # High E string
    tablature.FretNote(string=1, fret=3),  # G
    tablature.FretNote(string=1, fret=5),  # A
]

print("\nA Shape - Scale notes per string:")
for string_num in range(6, 0, -1):
    notes_on_string = [fn for fn in a_shape_notes if fn.string == string_num]
    if notes_on_string:
        frets = [fn.fret for fn in notes_on_string]
        print(f"  String {string_num}: frets {frets}")

# SHAPE 3: G Shape (5th position)
print("\n\nSHAPE 3: G Shape (5th Position)")
print("-" * 40)
print("Pattern: Based on open G chord shape, shifted up")
print("Root notes: C on 8th fret of 6th string, C on 5th fret of 3rd string")

g_shape_notes = [
    # Low E string
    tablature.FretNote(string=6, fret=5),  # A
    tablature.FretNote(string=6, fret=7),  # B
    tablature.FretNote(string=6, fret=8),  # C (root)
    # A string
    tablature.FretNote(string=5, fret=5),  # D
    tablature.FretNote(string=5, fret=7),  # E
    tablature.FretNote(string=5, fret=8),  # F
    # D string
    tablature.FretNote(string=4, fret=5),  # G
    tablature.FretNote(string=4, fret=7),  # A
    # G string
    tablature.FretNote(string=3, fret=4),  # B
    tablature.FretNote(string=3, fret=5),  # C (root)
    tablature.FretNote(string=3, fret=7),  # D
    # B string
    tablature.FretNote(string=2, fret=5),  # E
    tablature.FretNote(string=2, fret=6),  # F
    tablature.FretNote(string=2, fret=8),  # G
    # High E string
    tablature.FretNote(string=1, fret=5),  # A
    tablature.FretNote(string=1, fret=7),  # B
    tablature.FretNote(string=1, fret=8),  # C (root)
]

print("\nG Shape - Scale notes per string:")
for string_num in range(6, 0, -1):
    notes_on_string = [fn for fn in g_shape_notes if fn.string == string_num]
    if notes_on_string:
        frets = [fn.fret for fn in notes_on_string]
        print(f"  String {string_num}: frets {frets}")

# SHAPE 4: E Shape (7th/8th position)
print("\n\nSHAPE 4: E Shape (7th/8th Position)")
print("-" * 40)
print("Pattern: Based on open E chord shape, shifted up")
print("Root notes: C on 8th fret of 6th string, C on 10th fret of 4th string")

e_shape_notes = [
    # Low E string
    tablature.FretNote(string=6, fret=7),  # B
    tablature.FretNote(string=6, fret=8),  # C (root)
    tablature.FretNote(string=6, fret=10), # D
    # A string
    tablature.FretNote(string=5, fret=7),  # E
    tablature.FretNote(string=5, fret=8),  # F
    tablature.FretNote(string=5, fret=10), # G
    # D string
    tablature.FretNote(string=4, fret=7),  # A
    tablature.FretNote(string=4, fret=9),  # B
    tablature.FretNote(string=4, fret=10), # C (root)
    # G string
    tablature.FretNote(string=3, fret=7),  # D
    tablature.FretNote(string=3, fret=9),  # E
    tablature.FretNote(string=3, fret=10), # F
    # B string
    tablature.FretNote(string=2, fret=8),  # G
    tablature.FretNote(string=2, fret=10), # A
    # High E string
    tablature.FretNote(string=1, fret=7),  # B
    tablature.FretNote(string=1, fret=8),  # C (root)
    tablature.FretNote(string=1, fret=10), # D
]

print("\nE Shape - Scale notes per string:")
for string_num in range(6, 0, -1):
    notes_on_string = [fn for fn in e_shape_notes if fn.string == string_num]
    if notes_on_string:
        frets = [fn.fret for fn in notes_on_string]
        print(f"  String {string_num}: frets {frets}")

# SHAPE 5: D Shape (10th position)
print("\n\nSHAPE 5: D Shape (10th Position)")
print("-" * 40)
print("Pattern: Based on open D chord shape, shifted up")
print("Root notes: C on 10th fret of 4th string, C on 13th fret of 2nd string")

d_shape_notes = [
    # Low E string
    tablature.FretNote(string=6, fret=10), # D
    tablature.FretNote(string=6, fret=12), # E
    tablature.FretNote(string=6, fret=13), # F
    # A string
    tablature.FretNote(string=5, fret=10), # G
    tablature.FretNote(string=5, fret=12), # A
    # D string
    tablature.FretNote(string=4, fret=9),  # B
    tablature.FretNote(string=4, fret=10), # C (root)
    tablature.FretNote(string=4, fret=12), # D
    # G string
    tablature.FretNote(string=3, fret=9),  # E
    tablature.FretNote(string=3, fret=10), # F
    tablature.FretNote(string=3, fret=12), # G
    # B string
    tablature.FretNote(string=2, fret=10), # A
    tablature.FretNote(string=2, fret=12), # B
    tablature.FretNote(string=2, fret=13), # C (root)
    # High E string
    tablature.FretNote(string=1, fret=10), # D
    tablature.FretNote(string=1, fret=12), # E
    tablature.FretNote(string=1, fret=13), # F
]

print("\nD Shape - Scale notes per string:")
for string_num in range(6, 0, -1):
    notes_on_string = [fn for fn in d_shape_notes if fn.string == string_num]
    if notes_on_string:
        frets = [fn.fret for fn in notes_on_string]
        print(f"  String {string_num}: frets {frets}")

# Demonstrate pitch verification for one shape
print("\n" + "="*60)
print("PITCH VERIFICATION - C Shape (with guitar tuning)")
print("="*60)

# Create a guitar fretboard with just the C shape notes
c_shape_fb = tablature.GuitarFretBoard(fretNotes=c_shape_notes[:6])  # Just first 6 notes for demo
guitar_pitches = c_shape_fb.getPitches()

print("\nFirst few notes of C shape with actual pitches:")
for i, fn in enumerate(c_shape_notes[:6]):
    # Calculate the actual pitch
    guitar_fb_single = tablature.GuitarFretBoard(fretNotes=[fn])
    pitches = guitar_fb_single.getPitches()
    actual_pitch = [p for p in pitches if p is not None][0]
    
    # Get the scale degree
    scale_degree = c_major_scale.getScaleDegreeFromPitch(actual_pitch)
    
    print(f"  {fn} -> {actual_pitch} (scale degree {scale_degree})")

# Show how shapes connect
print("\n" + "="*60)
print("HOW CAGED SHAPES CONNECT")
print("="*60)
print("\nThe 5 shapes connect in order: C -> A -> G -> E -> D -> C (octave)")
print("Each shape overlaps with the next, creating a continuous pattern")
print("that covers the entire fretboard.")
print("\nKey root note positions for C:")
print("  - C shape: 3rd fret of 5th string")
print("  - A shape: 3rd fret of 5th string (same position, different pattern)")
print("  - G shape: 8th fret of 6th string")
print("  - E shape: 8th fret of 6th string (same position, different pattern)")
print("  - D shape: 10th fret of 4th string")
print("  - Back to C shape: 15th fret of 5th string (octave)")

# Practice suggestion
print("\n" + "="*60)
print("PRACTICE TIPS")
print("="*60)
print("\n1. Learn each shape individually")
print("2. Practice connecting adjacent shapes")
print("3. Find all C notes within each shape")
print("4. Practice playing the scale ascending and descending")
print("5. Try the same patterns in different keys (just shift the patterns!)")

import sys
sys.exit(0)