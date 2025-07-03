# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Name:         stream/mixins/__init__.py
# Purpose:      Stream mixin classes package
#
# Authors:      Michael Scott Asato Cuthbert
#               Claude Code Assistant
#
# Copyright:    Copyright © 2024 Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# -----------------------------------------------------------------------------
"""
Stream mixin classes for organizing Stream functionality.

This package contains mixin classes that provide specialized functionality
for Stream objects. These mixins were extracted from stream/base.py to
improve code organization and maintainability.
"""

from music21.stream.mixins.voice_operations import VoiceOperationsMixin

__all__ = [
    'VoiceOperationsMixin',
]