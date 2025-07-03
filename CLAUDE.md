# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

music19 is a slim-downed version of music21: A Toolkit for Computer-Aided Musical Analysis and Computational Musicology. It's a sophisticated Python library for music analysis, notation, and computational musicology research.

## Development Commands

### Running Tests

```bash
# Run all tests (preferred method)
python -m pytest tests/

# Run tests for a specific module
python -m pytest tests/unit/test_scale.py

# Run a single test method
python -m pytest tests/unit/test_scale.py::Test::testBasicLegacy

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=music21
```

### Running Tests in PyCharm

1. **Setup PyCharm for pytest**:
   - File → Settings → Tools → Python Integrated Tools
   - Set Default test runner to "pytest"

2. **Run tests using pytest**:
   - Right-click on `tests/unit/test_scale.py`
   - Select "Run pytest in test_scale.py"
   - Or click green arrows next to individual test methods

3. **Run all tests**:
   - Right-click on `tests/` directory
   - Select "Run pytest in tests"

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
- **Tests**: `/tests/` - Comprehensive test suite (migrated from embedded tests)
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
- Complex functionality requires unit tests in `tests/unit/`
- Use the corpus for real-world test cases
- Tests are organized by module: `test_[module_name].py`

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
```bash
# Run specific test class
python -m pytest tests/unit/test_note.py::Test

# Run specific test method
python -m pytest tests/unit/test_note.py::Test::testSpecificMethod
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

## Dependency Analysis & Refactor Plan

### Current Dependency Issues

The music21 codebase has several architectural challenges that are being addressed through a planned refactor:

#### Circular Dependencies
- **base.py ↔ higher-level modules**: `base.py` needs to import `note`, `chord`, `stream` for specific operations
- **stream ↔ core modules**: `stream` imports most core modules while they need stream for context
- **TYPE_CHECKING pattern**: Extensive use of `if t.TYPE_CHECKING:` blocks (58+ files)

#### Late Import Workarounds
- **Function-level imports**: 99+ instances of imports inside functions to avoid circular dependencies
- **Performance impact**: Late imports affect import performance and code clarity
- **Maintenance burden**: Makes dependency relationships unclear

#### Import Pattern Examples
```python
# Common late import pattern
def some_method(self):
    from music21 import chord  # Avoid circular dependency
    from music21 import note
    # ... function logic
```

### Planned Refactor Phases

#### Phase 1: Dependency Inversion & Interface Extraction
1. Extract protocol/interface classes from `base.py`
2. Create factory patterns for object creation
3. Move utility functions requiring high-level imports

#### Phase 2: Stream Module Restructuring
1. Split `stream/base.py` into focused modules:
   - `stream/core.py` (container logic)
   - `stream/operations.py` (operations requiring other modules)
   - `stream/context.py` (context-aware operations)
2. Reduce stream's import footprint

#### Phase 3: Late Import Consolidation
1. Replace function-level imports with dependency injection
2. Consolidate TYPE_CHECKING imports where runtime imports needed
3. Create import utilities for commonly late-imported modules

#### Phase 4: Module Responsibility Clarification
1. Define clear module boundaries with explicit APIs
2. Move cross-cutting concerns to dedicated utilities
3. Document and enforce dependency hierarchy

### Development Guidelines for Refactor

#### When Working with Dependencies
- **Avoid adding new circular dependencies**: Check import chains before adding imports
- **Use TYPE_CHECKING appropriately**: Only for static analysis, not runtime needs
- **Document late imports**: If you must use late imports, document why
- **Follow the hierarchy**: Lower-level modules should not import higher-level ones

#### Import Best Practices
```python
# Good: Use TYPE_CHECKING for static analysis
from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    from music21 import stream  # Only for type hints

# Good: Late import with documentation
def method_requiring_stream(self):
    """Method that needs stream - imported late to avoid circular dependency."""
    from music21 import stream
    # ... implementation

# Avoid: Direct import that creates circular dependency
# from music21 import stream  # This would create circular import
```

Go ahead, use the Google Style Guide: 
* Names should be: module_name, package_name, ClassName, method_name, ExceptionName, function_name, GLOBAL_CONSTANT_NAME, global_var_name, instance_var_name, function_parameter_name, local_var_name, query_proper_noun_for_thing, send_acronym_via_https.

See: https://google.github.io/styleguide/pyguide.html
