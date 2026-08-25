"""Compiler errors and error location span"""

from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Span:
    line: int
    col: int
    length: int = 1

class BorkError(Exception):
    def __init__(self, message: str, span: Span, filename: str = "<input>"):
        self.message = message
        self.span = span
        self.filename = filename
        super().__init__(message)

    def render(self) -> str:
        return f"{self.filename}:{self.span.line}:{self.span.col}: error: {self.message}"