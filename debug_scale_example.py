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