"""Turns a source of text into tokens"""
from __future__ import annotations
from dataclasses import dataclass
from .errors import BorkError, Span
from .values import MAX_I64

OPERATORS = ["+", "-", "*", "/", "%", "(", ")"]

@dataclass
class Token:
    kind: str
    value: object
    span: Span

    def __repr__(self) -> str:
        return f"Token({self.kind!r}, {self.value!r}, {self.span.line}:{self.span.col})"

class Lexer:
    def __init__(self, source: str, filename: str = "<input>"):
        self.src = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1

    # -- character helpers ---------------------------------------------------------------------
    def _peek(self, offset: int = 0) -> str:
        i = self.pos + offset
        return self.src[i] if i < len(self.src) else ""

    def _advance(self) -> str:
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line +=1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _error(self, message: str, span: Span):
        return BorkError(message, span, self.filename)

    # -- main loop -----------------------------------------------------------------------------
    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            self._skip_trivia()
            if self.pos >= len(self.src):
                tokens.append(Token("eof", None, Span(self.line, self.col, 0)))
                return tokens
            tokens.append(self._next_token())

    def _skip_trivia(self) -> None:
        while self.pos < len(self.src):
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                while self.pos < len(self.src) and self._peek() != "\n":
                    self._advance()
            else:
                return

    def _next_token(self) -> Token:
        line, col, start = self.line, self.col, self.pos
        ch = self._peek()

        if ch.isdigit():
            return self._number(line, col, start)

        for op in OPERATORS:
            if self.src.startswith(op, self.pos):
                for _ in op:
                    self._advance()
                return Token(op, op, Span(line, col, len(op)))

        self._advance()
        raise self._error(f"unexpected character {ch!r}", Span(line, col, 1))

    def _number(self, line: int, col: int, start: int) -> Token:
        while self._peek().isdigit():
            self._advance()
        text = self.src[start:self.pos]
        span = Span(line, col, len(text))
        value = int(text)
        if value > MAX_I64:
            raise self._error("integer literal does not fit in a 64-bit int", span)
        return Token("int", value, span)

def tokenize(source: str, filename: str = "<input>") -> list[Token]:
    return Lexer(source, filename).tokenize()