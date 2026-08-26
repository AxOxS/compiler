"""Compiled program representation"""

from __future__ import annotations

from .opcodes import OPERANDS, WIDTH, Op

class Function:
    __slots__ = ("name", "code", "consts")

    def __init__(self, name: str):
        self.name = name
        self.code = bytearray()
        self.consts: list = []

    def __repr__(self) -> str:
        return f"<Function {self.name} {len(self.code)} bytes>"

def decode(code: bytes, offset: int):
    op = code[offset]
    pos = offset + 1
    operands = []
    for kind in OPERANDS.get(op, ()):
        width = WIDTH[kind]
        operands.append(int.from_bytes(code[pos:pos + width], "little", signed = (kind == "s16")))
        pos += width
    return Op(op), operands, pos