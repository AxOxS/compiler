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

def format_float(value: float) -> str:
    if value != value:
        return "nan"
    if value == float("inf"):
        return "inf"
    if value == float("-inf"):
        return "-inf"
    if value == int(value) and abs(value) <1e16:
        return f"{int(value)}.0"
    return repr(value)

def to_display(value) -> str:
    """front facing form of runtime value"""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float):
        return format_float(value)
    return str(value)