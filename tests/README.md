# Music21 Tests Migration - Consolidated Test Directory

This directory contains all tests for music21, organized into a structure that supports both PyCharm/Rider test discovery and the existing music21.mainTest() interface.

## Directory Structure

```
tests/
├── __init__.py                     # Main test package
├── conftest.py                     # PyCharm/pytest configuration
├── test_runner_compat.py          # Compatibility layer for music21.mainTest()
├── README.md                       # This file
├── unit/                           # Unit tests
│   ├── __init__.py
│   ├── test_note.py               # Tests for music21.note
│   ├── test_pitch.py              # Tests for music21.pitch  
│   ├── test_stream.py             # Tests for music21.stream
│   ├── test_chord.py              # Tests for music21.chord
│   ├── test_base.py               # Tests for music21.base
│   ├── test_interval.py           # Tests for music21.interval
│   ├── test_metadata.py           # Tests for music21.metadata
│   ├── test_clef.py               # Tests for music21.clef
│   ├── test_expressions.py        # Tests for music21.expressions
│   ├── test_meter.py              # Tests for music21.meter
│   ├── test_midi.py               # Tests for music21.midi
│   ├── test_scale.py              # Tests for music21.scale
│   ├── test_intervalNetwork.py    # Tests for music21.scale.intervalNetwork
│   ├── test_musicxml_m21ToXml.py  # Tests for music21.musicxml.m21ToXml
│   └── test_musicxml_xmlToM21.py  # Tests for music21.musicxml.xmlToM21
├── external/                       # External/integration tests
│   ├── __init__.py
│   └── test_external_note.py      # External tests for music21.note
├── integration/                    # End-to-end integration tests
│   └── __init__.py
├── framework/                      # Test framework and utilities (from music21.test)
│   ├── __init__.py
│   ├── commonTest.py              # Common test utilities
│   ├── coverageM21.py             # Coverage analysis
│   ├── multiprocessTest.py        # Multiprocess testing
│   ├── testDefault.py             # Default test configuration
│   ├── testExternal.py            # External test utilities
│   ├── testLint.py                # Linting tests
│   ├── testRunner.py              # Main test runner
│   ├── testSerialization.py       # Serialization tests
│   ├── testSingleCoreAll.py       # Single core test runner
│   ├── toggleDebug.py             # Debug utilities
│   ├── treeYield.py               # Tree yield utilities
│   └── warningMultiprocessTest.py # Warning multiprocess tests
└── performance/                    # Performance and timing tests
    ├── __init__.py
    ├── memory_usage.py            # Memory usage tests
    ├── test_performance.py        # Performance benchmarks
    ├── time_graph_import_star.py  # Import timing tests
    └── time_graphs.py             # Timing graph utilities
```

## Running Tests

### With PyCharm/Rider
1. Open the project in PyCharm/Rider
2. Right-click on any test file or directory
3. Select "Run tests" or "Debug tests"
4. Individual test methods can be run by clicking the green arrow next to them

### With pytest
```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run specific module tests
pytest tests/unit/test_note.py

# Run specific test method
pytest tests/unit/test_note.py::TestNote::testLyricRepr

# Run external tests (may require external software)
pytest tests/external/

# Run with verbose output
pytest tests/ -v
```

### With music21.mainTest() (backward compatibility)
```python
import music21
import tests.unit.test_note

# Run all tests in a test module
music21.mainTest(tests.unit.test_note.TestNote)

# This maintains compatibility with existing music21 test patterns
```

## Migration Status - COMPLETED! ✅

### ✅ ALL TESTS SUCCESSFULLY MIGRATED
- **✅ ALL test framework files**: Moved from `music21/test/` to `tests/framework/`
- **✅ ALL unit test files**: Moved from `music21/test/` to `tests/unit/`
- **✅ ALL performance tests**: Moved to `tests/performance/`
- **✅ ALL module-specific tests**: Moved from subdirectories to `tests/unit/`
- **✅ Embedded Test classes**: Extracted from modules (note.py, pitch.py)
- **✅ Clean directory structure**: Original `music21/test/` cleaned up
- **✅ Backward compatibility**: Maintained with compatibility layer

### Migration Summary
**FROM:** `music21/test/` (scattered test files)
**TO:** `tests/` (consolidated, organized structure)

**Files Migrated:**
- 8 unit test files → `tests/unit/`
- 12 framework files → `tests/framework/` 
- 4 performance files → `tests/performance/`
- Embedded tests from 2+ modules → `tests/unit/` and `tests/external/`

### Cleanup Completed
- ✅ **Original files removed** from `music21/test/`
- ✅ **Compatibility layer** created for backward compatibility
- ✅ **No duplicate files** remaining

### Test Discovery Compatibility
- ✅ **PyCharm/Rider**: Full test discovery and running support
- ✅ **pytest**: Native pytest compatibility  
- ✅ **music21.mainTest()**: Backward compatibility maintained
- ✅ **Doctests**: Still embedded in modules (PyCharm can run these)

### Framework Benefits
- **IDE Support**: Proper test discovery, debugging, and coverage analysis
- **Standard Structure**: Follows Python testing conventions
- **Separation of Concerns**: Unit tests, external tests, and integration tests separated
- **Backward Compatibility**: Existing music21.mainTest() interface preserved
- **Enhanced Development**: Better test organization and maintainability

## Further Migration

Additional modules with embedded Test classes can be migrated using the established pattern:

1. **Extract Test classes** from module files to tests/unit/test_MODULE.py
2. **Extract TestExternal classes** to tests/external/test_external_MODULE.py
3. **Update imports** to reference music21 modules properly
4. **Test compatibility** with both pytest and music21.mainTest()

### Modules Still Containing Embedded Tests
Large modules like `harmony.py` (29 test methods) can be migrated using the same pattern when needed.

## Test Configuration

The `conftest.py` file provides:
- Automatic music21 environment setup
- Custom pytest markers for test categorization
- Path configuration for proper module discovery

## Notes

- External tests are configured with `show = False` by default to prevent GUI popups during automated testing
- All imports have been updated to work with the new structure
- Doctests remain embedded in module docstrings and can be run by PyCharm
- The test runner compatibility layer maintains music21's custom test discovery