# Interactive debugging script for PyCharm
# Set breakpoints and run in debug mode

from music19 import scale, note

def debug_scale_example():
    # Create B-flat major scale
    bb_scale = scale.MajorScale('B-')  # Set breakpoint here
    
    # Examine scale pitches
    for pitch in bb_scale.pitches:
        scale_degree = bb_scale.getScaleDegreeFromPitch(pitch)
        print(f"{pitch}: pitchClass={pitch.pitchClass}, scaleDegree={scale_degree}")
    
    return bb_scale

def debug_note_analysis():
    bb_scale = scale.MajorScale('B-')
    bb_note = note.Note("B-4")  # Set breakpoint here
    c_note = note.Note("C5")
    
    # Analyze notes in context of scale
    bb_degree = bb_scale.getScaleDegreeFromPitch(bb_note.pitch)
    c_degree = bb_scale.getScaleDegreeFromPitch(c_note.pitch)
    
    return {
        'scale': bb_scale,
        'notes': {'B-flat': bb_note, 'C': c_note},
        'degrees': {'B-flat': bb_degree, 'C': c_degree}
    }

if __name__ == '__main__':
    # Run both examples
    print("=== Scale Example ===")
    scale_obj = debug_scale_example()
    
    print("\n=== Note Analysis ===")
    analysis = debug_note_analysis()
    
    print(f"\nB-flat is degree {analysis['degrees']['B-flat']}")
    print(f"C is degree {analysis['degrees']['C']}")