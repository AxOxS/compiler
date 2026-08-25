from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from .errors import Span

@dataclass
class Node:
    span: Span

@dataclass
class Expr(Node):
    pass

@dataclass
class IntLit(Expr):
    value: int

@dataclass
class Unary(Expr):
    op: str
    operand: Expr

@dataclass
class Binary(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class Module(Node):
    expr: Expr

def dump(node, indent: int = 0) -> str:
    """used for rendering AST as indented tree, used by borkc ast"""
    pad = "  " * indent
    if not dataclasses.is_dataclass(node):
        return pad + repr(node)
    scalars, children = [], []
    for f in dataclasses.fields(node):
        if f.name == "span":
            continue
        value = getattr(node, f.name)
        if dataclasses.is_dataclass(value):
            children.append((f.name, value))
        elif value is not None:
            scalars.append(f"{f.name}={value!r}")
    head = pad + type(node).__name__
    if scalars:
        head += " (" + ", ".join(scalars) + ")"
    out = [head]
    for name, value in children:
        out.append(f"{pad}  .{name}")
        out.append(dump(value, indent + 2))
    return "\n".join(out)