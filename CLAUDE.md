# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

music19 is a slim-downed version of music21: A Toolkit for Computer-Aided Musical Analysis and Computational Musicology. It's a sophisticated Python library for music analysis, notation, and computational musicology research.

## Development Commands

### Running Tests

```bash
# Run all tests
python -m music21.test.testSingleCoreAll

# Run tests for a specific module
python -c "import music21; music21.mainTest(music21.scale)"

# Run a single test method
python -m unittest music21.scale.test_scale_main.Test.testBasicLegacy

# Run tests with options (noDocTest, verbose, onlyDocTest)
python -c "import music21; music21.mainTest('noDocTest', 'verbose')"
```

### Running Tests in PyCharm

1. **Setup PyCharm for pytest**:
   - File → Settings → Tools → Python Integrated Tools
   - Set Default test runner to "pytest"

2. **Run tests using pytest**:
   - Right-click on `music21/scale/test_scale_main.py`
   - Select "Run pytest in test_scale_main.py"
   - Or click green arrows next to individual test methods

3. **Run tests using music21's test runner**:
   - Run `test_scale_in_pycharm.py` script
   - Or create custom run configuration with script content:
     ```python
     import music21; music21.mainTest(music21.scale)
     ```

4. **Debug tests**:
   - Set breakpoints in test methods or source code
   - Right-click → "Debug" instead of "Run"
   - Step through both test code and music21 implementation

### Linting and Code Quality

```bash
# Run pylint
pylint -j0 music21
pylint -j0 documentation

# Run flake8 for PEP8 compliance
flake8 music21
flake8 documentation

# Run type checking with mypy
mypy music21
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Install music21 in editable mode
pip install -e .
```

## Architecture Overview

### Core Structure
- **Main Package**: `/music21/` - Contains all library modules
- **Tests**: `/music21/test/` - Comprehensive test suite
- **Documentation**: `/documentation/` - Sphinx docs and Jupyter notebooks
- **Corpus**: Musical works for testing and examples

### Key Modules
- **Music Objects**: `note.py`, `pitch.py`, `chord.py`, `interval.py`, `stream/`
- **Analysis**: `analysis/`, `roman.py`, `key.py`, `harmony.py`
- **File I/O**: `converter/`, `musicxml/`, `midi/`, `abc/`, `lily/`
- **Visualization**: `graph/`, plotting utilities
- **Corpus Management**: `corpus/` - Access to musical works

### Important Design Patterns
1. **Stream Architecture**: Musical objects are organized in Stream containers (Score, Part, Measure, Voice)
2. **Music21Object Base Class**: Most objects inherit from `base.Music21Object`
3. **Converter Pattern**: Unified interface for importing/exporting various music formats
4. **Corpus Access**: Built-in corpus provides standardized access to musical works

## Development Guidelines

### Python Version
- Requires Python 3.10+
- Uses modern Python features including type hints

### Type Annotations
- Project is fully typed (includes `py.typed`)
- Always maintain type hints when modifying code
- Run `mypy music21` before committing

### Testing Philosophy
- Every public method should have doctests
- Complex functionality requires unit tests
- Use the corpus for real-world test cases

### Code Style
- Follow PEP8 (enforced by flake8)
- Use descriptive variable names
- Maintain existing code conventions in each module

### AI-Generated Code
- Must declare AI usage with "(AI)" in PR/issue titles
- Reviewers must also disclose AI usage

## Common Development Tasks

### Adding a New Music Object
1. Inherit from `base.Music21Object`
2. Implement required properties and methods
3. Add comprehensive doctests
4. Update relevant converters if needed

### Working with Streams
```python
from music21 import stream, note
s = stream.Stream()
s.append(note.Note('C4'))
```

### Running a Quick Test
```python
# In Python interpreter
import music21
music21.mainTest(music21.note.Test.testSpecificMethod)
```

### Debugging Import Issues
- Check circular imports (common in large codebase)
- Use late imports where necessary
- Follow existing import patterns in similar modules

## CI/CD Integration
GitHub Actions runs:
- Tests on Python 3.10, 3.11, 3.12, 3.13
- Pylint and flake8 checks
- MyPy type checking
- Coverage reporting (Python 3.12 only)

All checks must pass before merging PRs.