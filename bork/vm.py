"""Bork virtual machine - stack interpreter for compiled bytecode"""

from __future__ import annotations

import math

from .bytecode import Function
from .errors import BorkRuntimeError
from .opcodes import Op
from .values import idiv, imod, wrap64

def fdiv(a: float, b: float) -> float:
    if b == 0.0:
        if a != a or a == 0.0:
            return float("nan")
        return math.copysign(float("inf"), a) * math.copysign(1.0, b)
    return a / b

def fmod(a: float, b: float) -> float:
    if b == 0.0 or a != a or b != b:
        return float("nan")
    try:
        return math.fmod(a, b)
    except ValueError:
        return float("nan")

def _is_float(a, b) -> bool:
    return isinstance(a, float) or isinstance(b, float)

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
                b = stack.pop(); a = stack[-1]
                stack[-1] = a + b if _is_float(a, b) else wrap64(a + b)
            elif op == Op.SUB:
                b = stack.pop(); a = stack[-1]
                stack[-1] = a - b if _is_float(a, b) else wrap64(a - b)
            elif op == Op.MUL:
                b = stack.pop(); a = stack[-1]
                stack[-1] = a * b if _is_float(a, b) else wrap64(a * b)
            elif op == Op.DIV:
                b = stack.pop(); a = stack[-1]
                if _is_float(a, b):
                    stack[-1] = fdiv(a, b)
                elif b == 0:
                    raise BorkRuntimeError("integer division by zero")
                else:
                    stack[-1] = wrap64(idiv(a, b))
            elif op == Op.MOD:
                b = stack.pop(); a = stack[-1]
                if _is_float(a, b):
                    stack[-1] = fmod(a, b)
                elif b == 0:
                    raise BorkRuntimeError("integer remainder by zero")
                else:
                    stack[-1] = wrap64(imod(a, b))
            elif op == Op.NEG:
                a = stack[-1]
                stack[-1] = -a if isinstance(a, float) else wrap64(-a)

            elif op == Op.TRUE:
                stack.append(True)
            elif op == Op.FALSE:
                stack.append(False)
            elif op == Op.LT:
                b = stack.pop(); stack[-1] = stack[-1] < b
            elif op == Op.LE:
                b = stack.pop(); stack[-1] = stack[-1] <= b
            elif op == Op.GT:
                b = stack.pop(); stack[-1] = stack[-1] > b
            elif op == Op.GE:
                b = stack.pop(); stack[-1] = stack[-1] >= b
            elif op == Op.EQ:
                b = stack.pop(); stack[-1] = stack[-1] == b
            elif op == Op.NE:
                b = stack.pop(); stack[-1] = stack[-1] != b
            elif op == Op.NOT:
                stack[-1] = not stack[-1]

            elif op == Op.HALT:
                return stack[-1] if stack else None
            elif op == op.NOP:
                pass
            else:
                raise BorkRuntimeError(f"illegal instruction {op} at offset {ip - 1}")

def run(fn: Function):
    return VM(fn).run()
