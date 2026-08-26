"""
Bork - a small statically typed language with it's own compiler.

Pipeline: source -> tokens -> AST -> bytecode -> VM
"""
from __future__ import annotations

from .bytecode import Function
from .compiler import compile_module
from .errors import BorkError, BorkRuntimeError
from .lexer import tokenize
from .parser import parse
from .vm import VM

__version__ = "0.0.1"
__all__ = {"compile_source", "run_source", "tokenize", "parse", "compile_module",
           "Function", "VM", "BorkError", "BorkRuntimeError"}

def compile_source(source: str, filename: str = "<input>") -> Function:
   """Run the pipeline"""
   return compile_module(parse(source, filename))

def run_source(source: str, filename: str = "<input>"):
    """Compile and execute"""
    return VM(compile_source(source, filename)).run()