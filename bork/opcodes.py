"Bork VM instruction set"

from __future__ import annotations
from enum import IntEnum

class Op(IntEnum):
    HALT = 0
    NOP = 1

    CONST = 10 # u16 const index -> push consts[i]
    TRUE = 11
    FALSE = 12
    POP = 14

    ADD = 30
    SUB = 31
    MUL = 32
    DIV = 33
    MOD = 34
    NEG = 35

    EQ = 50
    NE = 51
    LT = 52
    LE = 53
    GT = 54
    GE = 55
    NOT = 56

U8, U16, S16 = "u8", "u16", "s16"

OPERANDS: dict[int, tuple[str, ...]] = {
    Op.CONST: (U16,),
}

WIDTH = {U8: 1, U16: 2, S16: 2}

COMPARE_OPS = {"==": Op.EQ, "!=": Op.NE, "<": Op.LT, "<=": Op.LE, ">": Op.GT, ">=": Op.GE}

def instruction_size(op: int) -> int:
    return 1 + sum(WIDTH[kind] for kind in OPERANDS.get(op, ()))