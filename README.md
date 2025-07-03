# music19 #

`music19` -- Slim-downed version of music 21: A Toolkit for Computer-Aided Musical Analysis and 
Computational Musicology

Copyright © 2006-2025 [Michael Scott Asato Cuthbert](http://www.trecento.com)

`Music19` runs on Python 3.10+.

Released under the BSD (3-clause) license. See LICENSE.
Externally provided software (including the MIT-licensed Lilypond/MusicXML test Suite) and
music encoding in the corpus may have different licenses and/or copyrights. 
A no-corpus version of `music21` is available also on GitHub for those needing strict
BSD-license of all parts of the system.


### Testing 
  For everyday development testing:
  * Run specific test files in parallel (fastest for development)
  python -m pytest tests/unit/test_base.py tests/unit/test_stream.py -n auto -x

  * Run all unit tests in parallel with short traceback
  python -m pytest tests/unit/ -n auto --tb=short -x

  For comprehensive testing:
  * Run all tests with full output
  python -m pytest tests/unit/ -n auto -v

  * Run with coverage if needed
  python -m pytest tests/unit/ -n auto --cov=music21

  Key options:
  - -n auto: Auto-detect CPU cores
  - -n 8: Use 8 workers specifically
  - -x: Stop on first failure
  - --tb=short: Shorter tracebacks
  - -v: Verbose output
  - -q: Quiet output

## Acknowledgements ##

The early development of `music19` was supported by
the generosity of the Seaver Institute and the
National Endowment for the Humanities, along with MIT's Music and Theater Arts Section
and the School of Humanities, Arts, and Social Sciences.
