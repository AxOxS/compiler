"""Bytecode disassembler --- borkc dis"""

from __future__ import annotations

from .bytecode import Function, decode
from .opcodes import Op

def disassemble_function(fn: Function) -> str:
    out = [fn.name,
           f"   ; {len(fn.code)} bytes, {len(fn.consts)} constant(s)"]
    offset = 0
    while offset < len(fn.code):
        op, operands, next_offset = decode(fn.code, offset)
        text = f"   {offset:>5} {op.name:<22}"
        if op == Op.CONST:
            text += f"{operands[0]:<6}  ;   {fn.consts[operands[0]]!r}"
        elif operands:
            text += ", ".join(str(x) for x in operands)
        out.append(text.rstrip())
        offset = next_offset
    return "\n".join(out)

def disassemble(fn: Function) -> str:
    return disassemble_function(fn) + "\n"