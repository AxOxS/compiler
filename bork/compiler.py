"""Code generation AST -> stack bytecode"""
from __future__ import annotations

from . import ast_nodes as A
from .bytecode import Function
from .opcodes import OPERANDS, WIDTH, Op

BINARY_OPS = {"+": Op.ADD, "-": Op.SUB, "*": Op.MUL, "/": Op.DIV, "%": Op.MOD}

class FunctionEmitter:
    def __init__(self, name: str):
        self.fn = Function(name)
        self.const_index: dict = {}

    def emit(self, op: Op, *operands: int) -> int:
        offset = len(self.fn.code)
        self.fn.code.append(int(op))
        kinds = OPERANDS.get(op, ())
        assert len(kinds) == len(operands), f"{op.name} takes {len(kinds)} operands, got {len(operands)}"
        for kind, value in zip(kinds, operands):
            self.fn.code += int(value).to_bytes(WIDTH[kind], "little", signed=(kind == "s16"))
        return offset

    def constant(self, value) -> int:
        if value not in self.const_index:
            self.const_index[value] = len(self.fn.consts)
            self.fn.consts.append(value)
        return self.const_index[value]

    def emit_const(self, value) -> None:
        self.emit(Op.CONST, self.constant(value))

class Compiler:
    def __init__(self):
        self.e = FunctionEmitter("<main>")

    def compile_module(self, module: A.Module) -> Function:
        self.expr(module.expr)
        self.e.emit(Op.HALT)
        return self.e.fn

    def expr(self, node) -> None:
        method = getattr(self, "_expr_" + type(node).__name__)
        method(node)

    def _expr_IntLit(self, node: A.IntLit) -> None:
        self.e.emit_const(node.value)

    def _expr_Unary(self, node: A.Unary) -> None:
        self.expr(node.operand)
        self.e.emit(Op.NEG)

    def _expr_Binary(self, node: A.Binary) -> None:
        self.expr(node.left)
        self.expr(node.right)
        self.e.emit(BINARY_OPS[node.op])

def compile_module(module: A.Module) -> Function:
    return Compiler().compile_module(module)