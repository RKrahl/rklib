"""Human readable quantities of some units.

This modules provides subclasses of :class:`int` or :class:`float` to
denote particular quantities such as time intervalls or amounts of
memory.  The classes provide string representations in a more human
readable form and constructors that accept these string
representations as input.
"""

import re


class Time(float):
    """Human readable time intervals.

    The value is a :class:`float` that denotes the time in seconds.

    >>> t1 = Time(4500)
    >>> str(t1)
    '1.250 h'
    >>> t2 = Time("1.5 d")
    >>> t2
    129600.0
    >>> t3 = Time("36 h")
    >>> t3 == t2
    True
    >>> t4 = Time(1/200)
    >>> str(t4)
    '5.000 ms'
    >>> t5 = 0.5*Time("1 h") + 5*Time("15 min")
    >>> str(t5)
    '1.750 h'
    """
    second = 1
    minute = 60*second
    hour = 60*minute
    day = 24*hour
    millisecond = (1/1000)*second
    units = { 'ms':millisecond, 's':second, 'min':minute, 'h':hour, 'd':day, }
    regexp = re.compile(r'^(\d+(?:\.\d+)?)\s*(ms|s|min|h|d)$')

    def __new__(cls, value):
        if isinstance(value, str):
            m = cls.regexp.match(value)
            if not m:
                raise ValueError("Invalid Time string '%s'" % value)
            v = float(m.group(1)) * cls.units[m.group(2)]
            return super().__new__(cls, v)
        else:
            v = float(value)
            if v < 0:
                raise ValueError("Invalid time value %f" % v)
            return super().__new__(cls, v)

    def __str__(self):
        for u in ['d', 'h', 'min', 's']:
            if self >= self.units[u]:
                return "%.3f %s" % (self / self.units[u], u)
        else:
            return "%.3f ms" % (self / self.units['ms'])

    def __add__(self, other):
        v = super().__add__(other)
        if isinstance(other, Time):
            return Time(v)
        else:
            return v

    def __sub__(self, other):
        v = super().__sub__(other)
        if isinstance(other, Time) and v >= 0:
            return Time(v)
        else:
            return v

    def __rmul__(self, other):
        if type(other) in { float, int }:
            return Time(other*float(self))
        else:
            return super().__rmul__(other)


class MemorySize(int):
    """Human readable amounts of memory.

    The value is an :class:`int` that denotes the number of bytes.

    >>> s1 = MemorySize(2)
    >>> str(s1)
    '2 B'
    >>> s2 = MemorySize("2.0 B")
    >>> s2
    2
    >>> s2 == s1
    True
    >>> s3 = MemorySize(33117290228613)
    >>> str(s3)
    '30.12 TiB'
    >>> s4 = MemorySize("1 PiB") + 3*MemorySize("128 TiB")
    >>> str(s4)
    '1.38 PiB'
    >>> s5 = s4 - MemorySize("512 TiB")
    >>> str(s5)
    '896.00 TiB'
    >>> s5
    985162418487296
    """
    sizeB = 1
    sizeKiB = 1024*sizeB
    sizeMiB = 1024*sizeKiB
    sizeGiB = 1024*sizeMiB
    sizeTiB = 1024*sizeGiB
    sizePiB = 1024*sizeTiB
    sizeEiB = 1024*sizePiB
    units = { 'B':sizeB, 'KiB':sizeKiB, 'MiB':sizeMiB, 'GiB':sizeGiB,
              'TiB':sizeTiB, 'PiB':sizePiB, 'EiB':sizeEiB, }
    regexp = re.compile(r'^(\d+(?:\.\d+)?)\s*(B|KiB|MiB|GiB|TiB|PiB|EiB)$')

    def __new__(cls, value):
        if isinstance(value, str):
            m = cls.regexp.match(value)
            if not m:
                raise ValueError("Invalid MemorySize string '%s'" % value)
            v = float(m.group(1)) * cls.units[m.group(2)]
            return super().__new__(cls, v)
        else:
            v = int(value)
            if v < 0:
                raise ValueError("Invalid size value %d" % v)
            return super().__new__(cls, v)

    def __str__(self):
        for u in ['EiB', 'PiB', 'TiB', 'GiB', 'MiB', 'KiB']:
            if self >= self.units[u]:
                return "%.2f %s" % (self / self.units[u], u)
        else:
            return "%d B" % (int(self))

    def __add__(self, other):
        v = super().__add__(other)
        if isinstance(other, MemorySize):
            return MemorySize(v)
        else:
            return v

    def __sub__(self, other):
        v = super().__sub__(other)
        if isinstance(other, MemorySize) and v >= 0:
            return MemorySize(v)
        else:
            return v

    def __rmul__(self, other):
        if type(other) == int:
            return MemorySize(other*int(self))
        else:
            return super().__rmul__(other)
