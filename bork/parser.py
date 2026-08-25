"""recursive descent parser"""
from __future__ import annotations

from . import ast_nodes as A
from .errors import BorkError, Span
from .lexer import Token, tokenize

# Binary operator precedence
PRECEDENCE = {
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6
}

class Parser:
    def __init__(self, tokens: list[Token], filename: str = "<input>"):
        self.tokens = tokens
        self.pos = 0
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
                          self.current.span)

    @staticmethod
    def _describe(tok: Token) -> str:
        if tok.kind == "eof":
            return "end of file"
        if tok.kind == "int":
            return "int literal"
        return f"'{tok.kind}'"

    def _error(self, message: str, span: Span) -> BorkError:
        return BorkError(message, span, self.filename)

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
        if tok.kind == "-":
            self._advance()
            operand = self.unary_expr()
            return A.Unary(tok.span.to(operand.span), tok.kind, operand)
        return self.primary_expr()

    def primary_expr(self) -> A.Expr:
        tok = self.current
        if tok.kind == "int":
            self._advance()
            return A.IntLit(tok.span, tok.value)
        if tok.kind == "(":
            self._advance()
            inner = self.expression()
            self._expect(")")
            return inner
        raise self._error(f"expected an expression, found {self._describe(tok)}", tok.span)

def parse(source: str, filename: str = "<input>") -> A.Module:
    return Parser(tokenize(source, filename), filename).parse_module()