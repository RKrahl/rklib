"""Test module rklib.units.
"""

import pytest
from rklib.units import Time, MemorySize


def test_time():
    """Test class Time.
    """
    t1 = Time(2)
    assert str(t1) == "2.000 s"
    assert Time("2s") == t1
    t2 = Time(2.0)
    assert str(t2) == "2.000 s"
    assert Time("2.0 s") == t2
    t3 = Time(90*60)
    assert str(t3) == "1.500 h"
    assert Time("1.50 h") == t3
    t4 = Time(30*60*60)
    assert str(t4) == "1.250 d"
    assert Time("1.25 d") == t4
    t5 = Time(0.0205)
    assert str(t5) == "20.500 ms"
    assert Time("20.50ms") == t5

    t6 = 2*Time(1)
    assert str(t6) == "2.000 s"
    t7 = 1.5*Time("1h")
    assert str(t7) == "1.500 h"
    assert t7 == 5400.0
    t8 = Time("2d") + 4*(Time("1h") + Time("12min"))
    assert str(t8) == "2.200 d"
    t9 = Time("1h") + Time("15 min") - 0.5*Time("1h")
    assert str(t9) == "45.000 min"


def test_memsize():
    """Test class MemorySize.
    """
    s1 = MemorySize(2)
    assert str(s1) == "2 B"
    assert MemorySize("2B") == s1
    s2 = MemorySize(2.0)
    assert str(s2) == "2 B"
    assert MemorySize("2.0 B") == s2
    s3 = MemorySize(1536*1024)
    assert str(s3) == "1.50 MiB"
    assert MemorySize("1.50 MiB") == s3
    s4 = MemorySize(30.12*1024*1024*1024*1024)
    assert str(s4) == "30.12 TiB"
    assert MemorySize("30.12 TiB") == s4

    s5 = 2*MemorySize(1)
    assert str(s5) == "2 B"
    s6 = MemorySize("2 GiB") + 5*MemorySize("256 MiB")
    assert str(s6) == "3.25 GiB"
    assert s6 == 3328*1024*1024
    s7 = MemorySize("1 PiB") + 3*MemorySize("128 TiB") - MemorySize("512 TiB")
    assert str(s7) == "896.00 TiB"
