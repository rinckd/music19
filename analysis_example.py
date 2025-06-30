"""
Music21 Analysis Module Examples
================================

This demonstrates various analysis capabilities available in the music21.analysis package:

1. PITCH ANALYSIS - Analyzing pitch class distributions and patterns
2. KEY DETECTION - Algorithmic key detection using Krumhansl-Schmuckler
3. NEO-RIEMANNIAN THEORY - Chord transformations (L, P, R operations)
4. METRICAL ANALYSIS - Beat strength and rhythmic pattern analysis
5. WINDOWED ANALYSIS - Time-series analysis of musical features
6. CHORD REDUCTION - Simplifying harmonic progressions
7. DISCRETE ANALYSIS - Statistical analysis of musical elements

Each section includes practical examples and explanations.
"""

from music19 import stream, note, chord, key, meter, scale, corpus, duration
from music19.analysis import discrete, pitchAnalysis, neoRiemannian, metrical, windowed
import sys

print("=" * 60)
print("MUSIC21 ANALYSIS MODULE EXAMPLES")
print("=" * 60)

# =============================================================================
# 1. PITCH ANALYSIS - Analyzing pitch distributions
# =============================================================================
print("\n1. PITCH ANALYSIS")
print("-" * 40)

# Create a simple melody for analysis
melody = stream.Stream()
melody.append(note.Note('C4', quarterLength=1))
melody.append(note.Note('D4', quarterLength=1))
melody.append(note.Note('E4', quarterLength=1))
melody.append(note.Note('F4', quarterLength=1))
melody.append(note.Note('G4', quarterLength=1))
melody.append(note.Note('A4', quarterLength=1))
melody.append(note.Note('B4', quarterLength=1))
melody.append(note.Note('C5', quarterLength=1))
melody.append(note.Note('D4', quarterLength=1))  # Repeat some notes
melody.append(note.Note('F4', quarterLength=1))
melody.append(note.Note('A4', quarterLength=1))

print("Analyzing pitch class distribution in a C major scale melody:")

# Count pitch classes (0=C, 1=C#, 2=D, etc.)
pc_count = pitchAnalysis.pitchAttributeCount(melody, 'pitchClass')
print("\nPitch class counts:")
for pc in sorted(pc_count):
    print(f"  {pc:2d}: {pc_count[pc]:2d} occurrences")

# Count by note names
name_count = pitchAnalysis.pitchAttributeCount(melody, 'name')
print(f"\nMost common pitches:")
for name, count in name_count.most_common(3):
    print(f"  {name}: {count} occurrences")

# =============================================================================
# 2. KEY DETECTION - Krumhansl-Schmuckler Algorithm
# =============================================================================
print("\n\n2. KEY DETECTION - Krumhansl-Schmuckler Algorithm")
print("-" * 50)

# Create a melody in D minor
d_minor_melody = stream.Stream()
d_minor_scale = scale.MinorScale('D')
for degree in [1, 2, 3, 4, 5, 6, 7, 8, 3, 5, 1]:
    pitch = d_minor_scale.pitchFromDegree(degree)
    d_minor_melody.append(note.Note(pitch, quarterLength=1))

print("Analyzing key of a D minor melody using Krumhansl-Schmuckler:")

# Use discrete analysis for key detection
ks = discrete.KrumhanslSchmuckler()
key_result = ks.getSolution(d_minor_melody)

print(f"Detected key: {key_result}")
print(f"Key name: {key_result.name}")
print(f"Mode: {key_result.mode}")
print(f"Confidence: {key_result.correlationCoefficient:.3f}")

# Test with a major key melody
c_major_melody = stream.Stream()
c_major_scale = scale.MajorScale('C')
for degree in [1, 3, 5, 8, 5, 3, 1, 4, 2, 7, 1]:
    pitch = c_major_scale.pitchFromDegree(degree)
    c_major_melody.append(note.Note(pitch, quarterLength=1))

key_result2 = ks.getSolution(c_major_melody)
print(f"\nC major melody detected as: {key_result2}")
print(f"Confidence: {key_result2.correlationCoefficient:.3f}")

# =============================================================================
# 3. NEO-RIEMANNIAN TRANSFORMATIONS - Chord theory
# =============================================================================
print("\n\n3. NEO-RIEMANNIAN TRANSFORMATIONS")
print("-" * 40)

print("Neo-Riemannian theory: L (Leading-tone), P (Parallel), R (Relative) transformations")

# Start with C major triad
c_major = chord.Chord(['C4', 'E4', 'G4'])
print(f"\nStarting chord: {c_major.pitchedCommonName}")

# Apply L transformation (leading-tone exchange)
try:
    l_transform = neoRiemannian.L(c_major)
    print(f"L transformation: {c_major.pitchedCommonName} -> {l_transform.pitchedCommonName}")
except Exception as e:
    print(f"L transformation: {e}")

# Apply P transformation (parallel - major/minor switch)
try:
    p_transform = neoRiemannian.P(c_major)
    print(f"P transformation: {c_major.pitchedCommonName} -> {p_transform.pitchedCommonName}")
except Exception as e:
    print(f"P transformation: {e}")

# Apply R transformation (relative)
try:
    r_transform = neoRiemannian.R(c_major)
    print(f"R transformation: {c_major.pitchedCommonName} -> {r_transform.pitchedCommonName}")
except Exception as e:
    print(f"R transformation: {e}")

# Demonstrate chord progression using transformations
print(f"\nChord progression using Neo-Riemannian transformations:")
current_chord = c_major
print(f"1. {current_chord.pitchedCommonName}")

transformations = ['P', 'L', 'R']
for i, transform in enumerate(transformations, 2):
    try:
        if transform == 'P':
            current_chord = neoRiemannian.P(current_chord)
        elif transform == 'L':
            current_chord = neoRiemannian.L(current_chord)
        elif transform == 'R':
            current_chord = neoRiemannian.R(current_chord)
        print(f"{i}. {current_chord.pitchedCommonName} (via {transform} transformation)")
    except Exception as e:
        print(f"{i}. Error applying {transform}: {e}")

# =============================================================================
# 4. DISCRETE ANALYSIS - Ambitus and other analyses
# =============================================================================
print("\n\n4. DISCRETE ANALYSIS - Range and Statistical Analysis")
print("-" * 55)

# Create a melody with varying range
wide_melody = stream.Stream()
pitches = ['C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'C5', 'G4', 'E4', 'C4', 'G3', 'C3']
for p in pitches:
    wide_melody.append(note.Note(p, quarterLength=1))

print("Analyzing pitch range (ambitus) of a melody:")

# Analyze ambitus (pitch range)
ambitus_analyzer = discrete.Ambitus()
ambitus_result = ambitus_analyzer.getSolution(wide_melody)

print(f"Pitch range (as interval): {ambitus_result}")

# Get the actual lowest and highest pitches
pitch_span = ambitus_analyzer.getPitchSpan(wide_melody)
if pitch_span:
    lowest_pitch, highest_pitch = pitch_span
    print(f"Lowest note: {lowest_pitch}")
    print(f"Highest note: {highest_pitch}")
    print(f"Range in semitones: {ambitus_result.chromatic.semitones}")
else:
    print("No pitches found in the melody")

# =============================================================================
# 5. METRICAL ANALYSIS - Beat strength analysis
# =============================================================================
print("\n\n5. METRICAL ANALYSIS - Beat Strength")
print("-" * 40)

print("Analyzing metrical strength of beats in 4/4 time:")

# Create a stream with measures and time signature
metrical_example = stream.Stream()
ts = meter.TimeSignature('4/4')
metrical_example.insert(0, ts)

# Add eighth notes (create new note objects to avoid Stream conflicts)
for i in range(8):  # Two measures worth
    eighth_note = note.Note('C4', type='eighth')
    metrical_example.append(eighth_note)

# Create measures
metrical_example.makeMeasures(inPlace=True)

# Apply metrical analysis
try:
    metrical.labelBeatDepth(metrical_example)
    
    print("\nBeat positions and their metrical strength (more * = stronger):")
    for n in metrical_example.flatten().notes:
        if hasattr(n, 'lyrics') and n.lyrics:
            stars = "".join([l.text for l in n.lyrics])
            print(f"  Beat {n.beatStr:8s}: {stars}")
        else:
            print(f"  Beat {n.beatStr:8s}: (no metrical analysis)")
except Exception as e:
    print(f"Metrical analysis error: {e}")

# =============================================================================
# 6. WINDOWED ANALYSIS - Time-series analysis
# =============================================================================
print("\n\n6. WINDOWED ANALYSIS - Time-series Key Analysis")
print("-" * 50)

print("Analyzing key changes over time using windowed analysis:")

# Create a stream that modulates from C major to G major
modulating_stream = stream.Stream()

# C major section
c_major_scale = scale.MajorScale('C')
for degree in [1, 2, 3, 4, 5, 4, 3, 2, 1]:
    pitch = c_major_scale.pitchFromDegree(degree)
    modulating_stream.append(note.Note(pitch, quarterLength=1))

# Transitional notes
modulating_stream.append(note.Note('F#4', quarterLength=1))  # Leading tone to G

# G major section  
g_major_scale = scale.MajorScale('G')
for degree in [1, 2, 3, 4, 5, 4, 3, 2, 1]:
    pitch = g_major_scale.pitchFromDegree(degree)
    modulating_stream.append(note.Note(pitch, quarterLength=1))

try:
    # Set up windowed analysis
    wa = windowed.WindowedAnalysis(modulating_stream, discrete.KrumhanslSchmuckler())
    wa.windowSize = 6  # Analyze 6 notes at a time
    wa.windowStep = 3   # Step by 3 notes
    
    # Process the analysis
    results = wa.process()
    
    print("\nKey analysis over time windows:")
    print("(Analyzing how key signatures change as melody progresses)")
    
    for i, result in enumerate(results):
        window_start = i * wa.windowStep
        # Extract just the key information from the complex result
        if isinstance(result, list) and len(result) > 1:
            # The result contains solution data - extract key information
            if isinstance(result[1], list) and result[1]:
                key_info = result[1][0]  # Get first/best solution
                if isinstance(key_info, tuple) and len(key_info) >= 3:
                    pitch_obj, mode, confidence = key_info[:3]
                    print(f"  Window {i+1} (notes {window_start+1}-{window_start+wa.windowSize}): {pitch_obj} {mode} (confidence: {confidence:.3f})")
                else:
                    print(f"  Window {i+1}: Complex result - {type(result)}")
            else:
                print(f"  Window {i+1}: No clear key detected")
        else:
            print(f"  Window {i+1}: Unexpected result format")
        
except Exception as e:
    print(f"Windowed analysis error: {e}")
    print("Windowed analysis can be complex - this demonstrates the concept but may need")
    print("more sophisticated setup for practical use.")

# =============================================================================
# 7. PRACTICAL EXAMPLE - Complete harmonic analysis
# =============================================================================
print("\n\n7. PRACTICAL EXAMPLE - Chord Progression Analysis")
print("-" * 55)

print("Analyzing a ii-V-I progression in C major:")

# Create a ii-V-I progression
progression = stream.Stream()
progression.append(chord.Chord(['D4', 'F4', 'A4'], quarterLength=2))  # Dm
progression.append(chord.Chord(['G3', 'B3', 'D4', 'F4'], quarterLength=2))  # G7
progression.append(chord.Chord(['C4', 'E4', 'G4'], quarterLength=2))  # C

print("\nChord progression:")
for i, c in enumerate(progression.recurse().getElementsByClass(chord.Chord), 1):
    print(f"  {i}. {c.pitchedCommonName}")

# Analyze each chord's key implications
ks = discrete.KrumhanslSchmuckler()
print(f"\nKey analysis of entire progression:")
key_result = ks.getSolution(progression)
print(f"  Overall key: {key_result}")
print(f"  Confidence: {key_result.correlationCoefficient:.3f}")

# Analyze pitch class distribution
pc_count = pitchAnalysis.pitchAttributeCount(progression, 'pitchClass')
print(f"\nPitch class distribution:")
for pc in sorted(pc_count):
    pitch_name = note.Note(midi=60+pc).name  # Convert PC to note name
    print(f"  {pitch_name} ({pc:2d}): {pc_count[pc]:2d} occurrences")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
print("\nThe music21 analysis package provides powerful tools for:")
print("• Pitch and harmonic analysis")
print("• Algorithmic key detection") 
print("• Neo-Riemannian transformations")
print("• Metrical and rhythmic analysis")
print("• Statistical analysis of musical elements")
print("• Time-series analysis with windowed processing")

# Add explicit exit to avoid threading cleanup issues
sys.exit(0)