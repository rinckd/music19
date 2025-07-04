# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         volume.py
# Purpose:      Objects for representing volume, amplitude, and related
#               parameters
#
# Authors:      Christopher Ariza
#               Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2011-2012, 2015, 2017, 2024
#               Michael Scott Asato Cuthbert
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
'''
This module defines the object model of Volume, covering all representation of
amplitude, volume, velocity, and related parameters.
'''
from __future__ import annotations

from collections.abc import Iterable
import typing as t
from music21 import articulations
from music21 import exceptions21
from music21 import common
from music21.common.objects import SlottedObjectMixin
from music21 import dynamics
from music21 import environment
from music21 import prebase
from music21 import note  # circular but acceptable, because not used at highest level.

environLocal = environment.Environment('volume')

# ------------------------------------------------------------------------------
class VolumeException(exceptions21.Music21Exception):
    pass

# ------------------------------------------------------------------------------
class Volume(prebase.ProtoM21Object, SlottedObjectMixin):
    '''
    The Volume object lives on NotRest objects and subclasses. It is not a
    Music21Object subclass.

    Generally, just assume that a Note has a volume object and don't worry
    about creating this class directly:

    >>> n = note.Note('C5')
    >>> v = n.volume
    >>> v.velocity = 20
    >>> v.client is n
    True

    But if you want to create it yourself, you can specify the client, velocity,
    velocityScalar, and

    >>> v = volume.Volume(velocity=90)
    >>> v
    <music21.volume.Volume realized=0.71>
    >>> v.velocity
    90

    * Changed in v9: all constructor attributes are keyword only.
        (client as first attribute was confusing)
    '''
    # CLASS VARIABLES #
    __slots__ = (
        'client',
        '_velocityScalar',
        '_cachedRealized',
        'velocityIsRelative',
    )

    def __init__(
        self,
        *,
        client: note.NotRest|None = None,
        velocity: int|None = None,
        velocityScalar: float|None = None,
        velocityIsRelative: bool = True,
    ):
        # store a reference to the client, as we use this to do context
        # will use property; if None will leave as None
        self.client = client
        self._velocityScalar: float|None = None
        if velocity is not None:
            self.velocity = int(velocity)
        elif velocityScalar is not None:
            self.velocityScalar = float(velocityScalar)
        self._cachedRealized = None
        self.velocityIsRelative = velocityIsRelative

    # SPECIAL METHODS #
    def __deepcopy__(self, memo=None):
        '''
        Don't copy the client; set to current
        '''
        new = common.defaultDeepcopy(self, memo, ignoreAttributes={'client'})
        new.client = self.client
        return new

    def _reprInternal(self):
        return f'realized={round(self.realized, 2)}'

    # PUBLIC METHODS #
    def getDynamicContext(self):
        '''
        Return the dynamic context of this Volume, based on the position of the
        client of this object.

        >>> n = note.Note()
        >>> n.volume.velocityScalar = 0.9
        >>> s = stream.Measure([dynamics.Dynamic('ff'), n])
        >>> n.volume.getDynamicContext()
        <music21.dynamics.Dynamic ff>
        '''
        # TODO: find wedges and crescendi too and demo/test.
        return self.client.getContextByClass('Dynamic')

    def mergeAttributes(self, other):
        '''
        Given another Volume object, gather all attributes except client.
        Values are always copied, not passed by reference.

        >>> n1 = note.Note()
        >>> v1 = n1.volume
        >>> v1.velocity = 111

        >>> v2 = volume.Volume()
        >>> v2.mergeAttributes(v1)
        >>> v2.client is None
        True
        >>> v2.velocity
        111
        '''
        if other is not None:
            self._velocityScalar = other._velocityScalar
            self.velocityIsRelative = other.velocityIsRelative

    def getRealizedStr(self,
                       useDynamicContext: dynamics.Dynamic|bool = True,
                       useVelocity=True,
                       useArticulations: t.Union[bool,
                                                 articulations.Articulation,
                                                 Iterable[articulations.Articulation]
                                                 ] = True,
                       baseLevel=0.5,
                       clip=True):
        '''
        Return the realized as rounded and formatted string value. Useful for testing.

        >>> v = volume.Volume(velocity=64)
        >>> v.getRealizedStr()
        '0.5'
        '''
        val = self.getRealized(useDynamicContext=useDynamicContext,
                               useVelocity=useVelocity,
                               useArticulations=useArticulations,
                               baseLevel=baseLevel,
                               clip=clip)
        return str(round(val, 2))

    def getRealized(
        self,
        useDynamicContext: bool|dynamics.Dynamic = True,
        useVelocity=True,
        useArticulations: t.Union[
            bool, articulations.Articulation, Iterable[articulations.Articulation]
        ] = True,
        baseLevel=0.5,
        clip=True,
    ):
        '''
        Get a realized unit-interval scalar for this Volume. This scalar is to
        be applied to the dynamic range of whatever output is available,
        whatever that may be.

        The `baseLevel` value is a middle value between 0 and 1 that all
        scalars modify. This also becomes the default value for unspecified
        dynamics. When scalars (between 0 and 1) are used, their values are
        doubled, such that mid-values (around 0.5, which become 1) make no
        change.

        This can optionally take into account `dynamicContext`, `useVelocity`,
        and `useArticulation`.

        If `useDynamicContext` is True, a context search for a dynamic will be
        done, else dynamics are ignored. Alternatively, the useDynamicContext
        may supply a Dynamic object that will be used instead of a context
        search.

        If `useArticulations` is True and client is not None, any articulations
        found on that client will be used to adjust the volume. Alternatively,
        the `useArticulations` parameter may supply an iterable of articulations
        that will be used instead of that available on a client.

        The `velocityIsRelative` tag determines if the velocity value includes
        contextual values, such as dynamics and accents, or not.

        >>> s = stream.Stream()
        >>> s.repeatAppend(note.Note('d3', quarterLength=0.5), 8)
        >>> s.insert([0, dynamics.Dynamic('p'),
        ...           1, dynamics.Dynamic('mp'),
        ...           2, dynamics.Dynamic('mf'),
        ...           3, dynamics.Dynamic('f')])

        >>> s.notes[0].volume.getRealized()
        0.496...

        >>> s.notes[1].volume.getRealized()
        0.496...

        >>> s.notes[2].volume.getRealized()
        0.63779...

        >>> s.notes[7].volume.getRealized()
        0.99212...

        velocity, if set, will be scaled by dynamics:

        >>> s.notes[7].volume.velocity = 20
        >>> s.notes[7].volume.getRealized()
        0.22047...

        Unless we set the velocity to not be relative:

        >>> s.notes[7].volume.velocityIsRelative = False
        >>> s.notes[7].volume.getRealized()
        0.1574803...

        '''
        # velocityIsRelative might be best set at import. e.g., from MIDI,
        # velocityIsRelative is False, but in other applications, it may not
        # be
        val = baseLevel
        dm = None  # no dynamic mark
        # velocity is checked first; the range between 0 and 1 is doubled,
        # to 0 to 2. a velocityScalar of 0.7 thus scales the base value of
        # 0.5 by 1.4 to become 0.7
        if useVelocity:
            if self._velocityScalar is not None:
                if not self.velocityIsRelative:
                    # if velocity is not relative
                    # it should fully determine output independent of anything
                    # else
                    val = self._velocityScalar
                else:
                    val = val * (self._velocityScalar * 2.0)
            # this value provides a good default velocity, as 0.5 is low
            # this not a scalar application but a shift.
            else:  # target :0.70866
                val += 0.20866
        # only change the val from here if velocity is relative
        if self.velocityIsRelative:
            if useDynamicContext is not False:
                if isinstance(useDynamicContext, dynamics.Dynamic):
                    dm = useDynamicContext  # it is a dynamic
                elif self.client is not None:
                    dm = self.getDynamicContext()  # dm may be None
                else:
                    environLocal.printDebug([
                        'getRealized():',
                        'useDynamicContext is True but no dynamic supplied or found in context',
                    ])
                if dm is not None:
                    # double scalar (so range is between 0 and 1) and scale
                    # the current val (around the base)
                    val = val * (dm.volumeScalar * 2.0)
            # useArticulations can be a list of 1 or more articulation objects
            # as well as True/False
            if useArticulations is not False:
                am: Iterable[articulations.Articulation]
                if isinstance(useArticulations, articulations.Articulation):
                    am = [useArticulations]  # place in a list
                elif common.isIterable(useArticulations):
                    am = useArticulations  # type: ignore[assignment]
                elif self.client is not None:
                    am = self.client.articulations
                else:
                    am = []
                for a in am:
                    # add in volume shift for all articulations
                    val += a.volumeShift
        if clip:  # limit between 0 and 1
            if val > 1:
                val = 1.0
            elif val < 0:
                val = 0.0
        # might want to re-balance range after scaling
        # always update cached result each time this is called
        self._cachedRealized = val
        return val

    # PUBLIC PROPERTIES #
    @property
    def cachedRealized(self):
        '''
        Return the cached realized value of this volume. This will be the last
        realized value or, if that value has not been set, a newly realized
        value. If the caller knows that the realized values have all been
        recently set, using this property will add significant performance
        boost.

        >>> v = volume.Volume(velocity=128)
        >>> v.cachedRealized
        1.0
        '''
        if self._cachedRealized is None:
            self._cachedRealized = self.getRealized()
        return self._cachedRealized

    @property
    def cachedRealizedStr(self):
        '''
        Convenience property for testing.

        >>> v = volume.Volume(velocity=128)
        >>> v.cachedRealizedStr
        '1.0'
        '''
        return str(round(self.cachedRealized, 2))

    @property
    def realized(self):
        return self.getRealized()

    @property
    def velocity(self) -> int|None:
        '''
        Get or set the velocity value, a numerical value between 0 and 127 and
        available setting amplitude on each Note or Pitch in chord.

        >>> n = note.Note()
        >>> n.volume.velocity = 20
        >>> n.volume.client == n
        True

        >>> n.volume.velocity
        20
        '''
        vs = self._velocityScalar
        if vs is None:
            return None
        v = vs * 127
        if v > 127:
            v = 127
        elif v < 0:
            v = 0
        return round(v)

    @velocity.setter
    def velocity(self, value: int|float|None):
        if value is None:
            self._velocityScalar = None
        elif not common.isNum(value):
            raise VolumeException(f'value provided for velocity must be a number, not {value}')
        elif value <= 0:
            self._velocityScalar = 0.0
        elif value >= 127:
            self._velocityScalar = 1.0
        else:
            self._velocityScalar = value / 127.0

    @property
    def velocityScalar(self) -> float|None:
        '''
        Get or set the velocityScalar value, a numerical value between 0
        and 1 and available setting amplitude on each Note or Pitch in
        chord. This value is mapped to the range 0 to 127 on output.

        Note that this value is derived from the set velocity value.
        Floating point error seen here will not be found in the velocity
        value.

        When setting this value, an integer-based velocity value will be
        derived and stored.

        >>> n = note.Note()
        >>> n.volume.velocityScalar = 0.5
        >>> n.volume.velocity
        64

        >>> n.volume.velocity = 127
        >>> n.volume.velocityScalar
        1.0

        If velocity is not set, then this will return None

        >>> n = note.Note()
        >>> n.volume.velocityScalar is None
        True
        '''
        v = self._velocityScalar
        if v is None:
            return None
        else:
            return v

    @velocityScalar.setter
    def velocityScalar(self, value: int|float|None):
        if value is None:
            self._velocityScalar = None

        if not common.isNum(value):
            raise VolumeException('value provided for velocityScalar must be a number, '
                                  + f'not {value}')

        scalar: float
        if value < 0:
            scalar = 0.0
        elif value > 1:
            scalar = 1.0
        else:
            if t.TYPE_CHECKING:
                assert value is not None
            scalar = float(value)
        self._velocityScalar = scalar

# ------------------------------------------------------------------------------
# utility stream processing methods

def realizeVolume(srcStream,
                  setAbsoluteVelocity=False,
                  useDynamicContext=True,
                  useVelocity=True,
                  useArticulations=True):
    '''
    Given a Stream with one level of dynamics
    (e.g., a Part, or two Staffs that share Dynamics),
    destructively modify it to set all realized volume levels.
    These values will be stored in the Volume object as `cachedRealized` values.

    This is a top-down routine, as opposed to bottom-up values available with
    context searches on Volume. This thus offers a performance benefit.

    This is always done in place.

    If setAbsoluteVelocity is True, the realized values will overwrite all
    existing velocity values, and the Volume objects velocityIsRelative
    parameters will be set to False.
    '''
    bKeys = []
    boundaries = {}
    # get dynamic map
    flatSrc = srcStream.flatten()  # assuming sorted

    # check for any dynamics
    dynamicsAvailable = False
    if flatSrc.getElementsByClass(dynamics.Dynamic):
        dynamicsAvailable = True
    else:  # no dynamics available
        if useDynamicContext is True:  # only if True, and non avail, override
            useDynamicContext = False

    if dynamicsAvailable:
        # extend durations of all dynamics
        # doing this in place as this is a destructive operation
        flatSrc.extendDuration(dynamics.Dynamic, inPlace=True)
        elements = flatSrc.getElementsByClass(dynamics.Dynamic)
        for e in elements:
            start = flatSrc.elementOffset(e)
            end = start + e.duration.quarterLength
            boundaries[(start, end)] = e
        bKeys = list(boundaries.keys())
        bKeys.sort()  # sort

    # assuming stream is sorted
    # storing last relevant index lets us always start form the last-used
    # key, avoiding searching through entire list every time
    lastRelevantKeyIndex = 0
    for e in flatSrc:  # iterate over all elements
        if hasattr(e, 'volume') and isinstance(e, note.NotRest):
            # try to find a dynamic
            eStart = e.getOffsetBySite(flatSrc)

            # get the most recent dynamic
            if dynamicsAvailable and useDynamicContext is True:
                dm = False  # set to not search dynamic context
                for k in range(lastRelevantKeyIndex, len(bKeys)):
                    start, end = bKeys[k]
                    if end > eStart >= start:
                        # store to start in the same position
                        # for next element
                        lastRelevantKeyIndex = k
                        dm = boundaries[bKeys[k]]
                        break
            else:  # permit supplying a single dynamic context for all material
                dm = useDynamicContext
            # this returns a value, but all we need to do is to set the
            # cached values stored internally
            val = e.volume.getRealized(useDynamicContext=dm,
                                       useVelocity=useVelocity,
                                       useArticulations=useArticulations)
            if setAbsoluteVelocity:
                e.volume.velocityIsRelative = False
                # set to velocity scalar
                e.volume.velocityScalar = val

# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER: list[type] = []
