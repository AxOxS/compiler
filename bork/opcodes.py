"Bork VM instruction set"

from __future__ import annotations
from enum import IntEnum

class Op(IntEnum):
    HALT = 0
    NOP = 1

    CONST = 10 # u16 const index -> push consts[i]
    POP = 14

    ADD = 30
    SUB = 31
    MUL = 32
    DIV = 33
    MOD = 34
    NEG = 35

U8, U16, S16 = "u8", "u16", "s16"

OPERANDS: dict[int, tuple[str, ...]] = {
    Op.CONST: (U16,),
}

WIDTH = {U8: 1, U16: 2, S16: 2}

def instruction_size(op: int) -> int:
    return 1 + sum(WIDTH[kind] for kind in OPERANDS.get(op, ()))