"""Bork virtual machine - stack interpreter for compiled bytecode"""

from __future__ import annotations

from .bytecode import Function
from .errors import BorkRuntimeError
from .opcodes import Op
from .values import idiv, imod, wrap64

class VM:
    def __init__(self, fn: Function):
        self.fn = fn
        self.stack: list = []
        self.instructions = 0

    def run(self):
        code = self.fn.code
        consts = self.fn.consts
        stack = self.stack
        ip = 0
        while True:
            self.instructions += 1
            op = code[ip]
            ip += 1

            if op == Op.CONST:
                stack.append(consts[code[ip] | (code[ip + 1] << 8)])
                ip += 2
            elif op == Op.POP:
                stack.pop()

            elif op == Op.ADD:
                b = stack.pop(); stack[-1] = wrap64(stack[-1] + b)
            elif op == Op.SUB:
                b = stack.pop(); stack[-1] = wrap64(stack[-1] - b)
            elif op == Op.MUL:
                b = stack.pop(); stack[-1] = wrap64(stack[-1] * b)
            elif op == Op.DIV:
                b = stack.pop()
                if b == 0:
                    raise BorkRuntimeError("integer division by zero")
                stack[-1] = wrap64(idiv(stack[-1], b))
            elif op == Op.MOD:
                b = stack.pop()
                if b == 0:
                    raise BorkRuntimeError("integer remainder by zero")
                stack[-1] = wrap64(imod(stack[-1], b))
            elif op == Op.NEG:
                stack[-1] = wrap64(-stack[-1])

            elif op == Op.HALT:
                return stack[-1] if stack else None
            elif op == op.NOP:
                pass
            else:
                raise BorkRuntimeError(f"illegal instruction {op} at offset {ip - 1}")

def run(fn: Function):
    return VM(fn).run()
