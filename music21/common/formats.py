# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         common/formats.py
# Purpose:      Utilities for formats
#
# Authors:      Michael Scott Asato Cuthbert
#               Christopher Ariza
#
# Copyright:    Copyright © 2009-2015 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
Utilities for working with file formats.

almost everything here is deprecated.
'''
from __future__ import annotations

__all__ = [
    'findSubConverterForFormat',
    'findFormat',
    'findInputExtension',
    'findFormatFile',
    'findFormatExtFile',
    'findFormatExtURL',
    'VALID_SHOW_FORMATS',
    'VALID_WRITE_FORMATS',
    'VALID_AUTO_DOWNLOAD',
]

from functools import cache
import pathlib
import typing as t


if t.TYPE_CHECKING:
    from music21.converter.subConverters import SubConverter


# used for checking preferences, and for setting environment variables
# TODO: only check top-level.  Let subConverters check sub formats.
VALID_SHOW_FORMATS = ['musicxml', 'text', 'textline', 'midi',
                      'png', 'pdf', 'svg',
                      'ipython', 'ipython.png', 'ipython.midi',
                      'musicxml.png', 'musicxml.pdf']
VALID_WRITE_FORMATS = ['musicxml', 'text', 'textline', 'midi',
                       'png', 'pdf', 'svg',
                       'ipython', 'ipython.png', 'ipython.midi',
                       'musicxml.png', 'musicxml.pdf']
VALID_AUTO_DOWNLOAD = ['ask', 'deny', 'allow']

# ------------------------------------------------------------------------------


def findSubConverterForFormat(fmt: str) -> type[SubConverter]|None:
    '''
    return a converter.subConverter.SubConverter subclass
    for a given format -- this is a music21 format name,
    not a file extension. Or returns None

    >>> common.findSubConverterForFormat('musicxml')
    <class 'music21.converter.subConverters.ConverterMusicXML'>

    >>> common.findSubConverterForFormat('text')
    <class 'music21.converter.subConverters.ConverterText'>


    Some subConverters have format aliases

    >>> common.findSubConverterForFormat('t')
    <class 'music21.converter.subConverters.ConverterText'>

    '''
    fmt = fmt.lower().strip()
    from music21 import converter
    scl = converter.Converter().subConvertersList()
    for sc in scl:
        formats = sc.registerFormats
        if fmt in formats:
            return sc
    return None


# @deprecated('May 2014', '[soonest possible]', 'Moved to converter')
def findFormat(fmt):
    '''
    Given a format defined either by a format name, abbreviation, or
    an extension, return the regularized format name as well as
    the output extensions.

    DEPRECATED May 2014 -- moving to converter


    All but the first element of the tuple are deprecated for use, since
    the extension can vary by subConverter (e.g., lily.png)

    >>> common.findFormat('.mxl')
    ('musicxml', '.musicxml')
    >>> common.findFormat('musicxml')
    ('musicxml', '.musicxml')
    >>> common.findFormat('txt')
    ('text', '.txt')
    >>> common.findFormat('textline')
    ('textline', '.txt')
    >>> common.findFormat('midi')
    ('midi', '.mid')
    >>> common.findFormat('scl')
    ('scala', '.scl')
    >>> common.findFormat('vexflow')
    ('vexflow', '.html')
    >>> common.findFormat('capx')
    ('capella', '.capx')


    Works the same whether you have a leading dot or not:


    >>> common.findFormat('md')
    ('musedata', '.md')
    >>> common.findFormat('.md')
    ('musedata', '.md')


    If you give something we can't deal with, returns a Tuple of None, None:

    >>> common.findFormat('wpd')
    (None, None)


    These don't work but should eventually:

    # >>> common.findFormat('png')
    # ('musicxml.png', '.png')

    # >>> common.findFormat('ipython')
    # ('ipython', '.png')
    # >>> common.findFormat('ipython.png')
    # ('ipython', '.png')

    # >>> common.findFormat('musicxml.png')
    # ('musicxml.png', '.png')
    '''
    from music21 import converter
    c = converter.Converter()
    fileFormat = c.regularizeFormat(fmt)
    if fileFormat is None:
        return (None, None)
    scf = c.getSubConverterFormats()
    sc = scf[fileFormat]

    if sc.registerOutputExtensions:
        firstOutput = '.' + sc.registerOutputExtensions[0]
    elif sc.registerInputExtensions:
        firstOutput = '.' + sc.registerInputExtensions[0]
    else:
        firstOutput = None

    return fileFormat, firstOutput


# @deprecated('May 2014', '[soonest possible]', 'Moved to converter')
@cache
def findInputExtension(fmt: str) -> tuple[str, ...]:
    '''
    Will be fully deprecated when there's an exact equivalent in converter.

    Given an input format or music21 format, find and return all possible
    input extensions.

    >>> a = common.findInputExtension('musicxml')
    >>> a
    ('.xml', '.mxl', '.musicxml')
    >>> common.findInputExtension('musedata')
    ('.md', '.musedata', '.zip')

    Leading dots don't matter:

    >>> common.findInputExtension('.mxl')
    ('.xml', '.mxl', '.musicxml')

    Blah is not a format

    >>> common.findInputExtension('blah')
    ()
    '''
    from music21 import converter
    fmt = fmt.lower().strip()
    if fmt.startswith('.'):
        fmt = fmt[1:]  # strip .

    sc = findSubConverterForFormat(fmt)
    if sc is None:
        # file extension
        post: list[str] = []
        for sc in converter.Converter().subConvertersList():
            if fmt not in sc.registerInputExtensions:
                continue
            for ext in sc.registerInputExtensions:
                if not ext.startswith('.'):
                    ext = '.' + ext
                post.append(ext)
            if post:
                return tuple(post)
        return tuple(post)  # empty
    else:
        # music21 format
        post = []
        for ext in sc.registerInputExtensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            post.append(ext)
        return tuple(post)

# @deprecated('May 2014', '[soonest possible]', 'Moved to converter')


def findFormatFile(fp):
    r'''
    Given a file path (relative or absolute) return the format

    DEPRECATED May 2014 -- moving to converter


    >>> common.findFormatFile('test.xml')
    'musicxml'
    >>> common.findFormatFile('long/file/path/test-2009.03.02.xml')
    'musicxml'
    >>> common.findFormatFile('long/file/path.intermediate.png/test-2009.03.xml')
    'musicxml'

    On a windows networked filesystem
    '''
    if not isinstance(fp, pathlib.Path):
        fp = pathlib.Path(fp)
    fmt, unused_ext = findFormat(fp.suffix)
    return fmt  # may be None if no match

# @deprecated('May 2014', '[soonest possible]', 'Moved to converter')


def findFormatExtFile(fp):
    r'''
    Given a file path (relative or absolute)
    find format and extension used (not the output extension)

    DEPRECATED May 2014 -- moving to converter

    >>> common.findFormatExtFile('test.mxl')
    ('musicxml', '.mxl')
    >>> common.findFormatExtFile('long/file/path/test-2009.03.02.xml')
    ('musicxml', '.xml')
    >>> common.findFormatExtFile('long/file/path.intermediate.png/test-2009.03.xml')
    ('musicxml', '.xml')

    >>> common.findFormatExtFile('test')
    (None, None)

    Windows drive
    >>> common.findFormatExtFile('d:/long/file/path/test.xml')
    ('musicxml', '.xml')

    On a windows networked filesystem
    '''
    if not isinstance(fp, pathlib.Path):
        fp = pathlib.Path(fp)

    fileFormat, unused_extOut = findFormat(fp.suffix)
    if fileFormat is None:
        return (None, None)
    else:
        return (fileFormat, fp.suffix)  # may be None if no match

# @deprecated('May 2014', '[soonest possible]', 'Moved to converter')


def findFormatExtURL(url):
    '''
    Given a URL, attempt to find the extension.
    This may scrub arguments in a URL, or simply look at the last characters.

    DEPRECATED May 2014 -- moving to converter


    >>> urlF = 'https://junk'
    >>> urlM = 'http://somesite.com/files/mid001.mid'

    >>> common.findFormatExtURL(urlF)
    (None, None)
    >>> common.findFormatExtURL(urlM)
    ('midi', '.mid')
    '''
    from music21 import converter
    ext = None
    # first, look for cgi arguments
    if '=xml' in url:
        ext = '.xml'
    elif '=kern' in url:
        ext = '.krn'
    # specific tag used on musedata.org
    elif 'format=stage2' in url or 'format=stage1' in url:
        ext = '.md'
    else:  # check for file that ends in all known input extensions
        for sc in converter.Converter().subConvertersList():
            inputTypes = sc.registerInputExtensions
            for extSample in inputTypes:
                if url.endswith('.' + extSample):
                    ext = '.' + extSample
                    break
    # presently, not keeping the extension returned from this function
    # reason: mxl is converted to xml; need to handle mxl files first
    if ext is not None:
        fileFormat, unused_junk = findFormat(ext)
        return fileFormat, ext
    else:
        return None, None


if __name__ == '__main__':
    import music21
    music21.mainTest()

