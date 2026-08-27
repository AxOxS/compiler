"""recursive descent parser"""
from __future__ import annotations

from . import ast_nodes as A
from .errors import Diagnostic, BorkError, Span
from .lexer import Token, tokenize

# Binary operator precedence
PRECEDENCE = {
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6
}

class Parser:
    def __init__(self, tokens: list[Token], source: str = "", filename: str = "<input>"):
        self.tokens = tokens
        self.pos = 0
        self.source = source
        self.filename = filename

    # -- token helpers --------------------------------
    @property
    def current(self) -> None:
        return self.tokens[self.pos]

    def _check(self, kind: str) -> bool:
        return self.current.kind == kind

    def _advance(self) -> Token:
        tok = self.current
        if tok.kind != "eof":
            self.pos += 1
        return tok

    def _expect(self, kind: str) -> Token:
        if self.current.kind == kind:
            return self._advance()
        raise self._error(f"expected '{kind}', found {self._describe(self.current)}",
                          self.current.span,
                          note = "the previous token ends at "
                                f"line {self.tokens[self.pos - 1].span.line}")

    @staticmethod
    def _describe(tok: Token) -> str:
        if tok.kind == "eof":
            return "end of file"
        if tok.kind == "ident":
            return f"identifier '{tok.value}'"
        if tok.kind in ("int", "float"):
            return f"{tok.kind} literal"
        return f"'{tok.kind}'"

    def _error(self, msg: str, span: Span, note: str | None = None) -> BorkError:
        return BorkError([Diagnostic(msg, span, note=note)], self.source, self.filename)

    # -- entry point ----------------------------------------
    def parse_module(self) -> A.Module:
        start = self.current.span
        expr = self.expression()
        if not self._check("eof"):
            raise self._error(f"unexpected {self._describe(self.current)} after the expression",
                              self.current.span)
        return A.Module(start, expr)

    # -- expressions ------------------------------------------
    def expression(self) -> A.Expr:
        return self.binary_expr(0)

    def binary_expr(self, min_prec: int) -> A.Expr:
        left = self.unary_expr()
        while True:
            op = self.current.kind
            prec = PRECEDENCE.get(op, -1)
            if prec < 0 or prec < min_prec:
                return left
            self._advance()
            right = self.binary_expr(prec + 1)
            left = A.Binary(left.span.to(right.span), op, left, right)

    def unary_expr(self) -> A.Expr:
        tok = self.current
        if tok.kind in ("-", "!"):
            self._advance()
            operand = self.unary_expr()
            # Fold "-" into a numeric literal instead of emitting negation
            if tok.kind == "-" and isinstance(operand, A.IntLit):
                return A.IntLit(tok.span.to(operand.span), -operand.value)
            if tok.kind == "-" and isinstance(operand, A.FloatLit):
                return A.FloatLit(tok.span.to(operand.span), -operand.value)
            return A.Unary(tok.span.to(operand.span), tok.kind, operand)
        return self.primary_expr()

    def primary_expr(self) -> A.Expr:
        tok = self.current
        if tok.kind == "int":
            self._advance()
            return A.IntLit(tok.span, tok.value)
        if tok.kind == "float":
            self._advance()
            return A.FloatLit(tok.span, tok.value)
        if tok.kind in ("true", "false"):
            self._advance()
            return A.BoolLit(tok.span, tok.value)
        if tok.kind == "(":
            self._advance()
            inner = self.expression()
            self._expect(")")
            return inner
        raise self._error(f"expected an expression, found {self._describe(tok)}", tok.span)

def parse(source: str, filename: str = "<input>") -> A.Module:
    return Parser(tokenize(source, filename), source, filename).parse_module()