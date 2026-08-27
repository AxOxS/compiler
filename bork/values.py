"""Runtime value representation and borks integer semantics"""

from __future__ import annotations

MIN_I64 = -(1 << 63)
MAX_I64 = (1 << 63) -1
_MASK = (1 << 64) -1

def wrap64(value: int) -> int:
    value &= _MASK
    return value - (1 << 64) if value > MAX_I64 else value

def idiv(a: int, b: int) -> int:
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q

def imod(a: int, b: int) -> int:
    return a - idiv(a, b) * b