import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import ProgramIR, compile_program, optimize, execute

from pathlib import Path


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    program_ir = compile_program(ast)
    program_ir = optimize(program_ir)
    return execute(program_ir)


def compile_and_run_file(file_path: Path) -> ProgramIR:
    source = file_path.read_text()
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    program_ir = optimize(compile_program(ast))
    return program_ir


def test_backend_addition():
    result = compile_and_run("let x = 1 + 2; x + 3;")
    assert result == 6


def test_backend_import_hello_world():
    ir = compile_and_run_file(Path("demo_program/hello_world.mxs"))
    assert "io.println" in ir.functions
