import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize, execute_llvm
from src.backend import to_llvm_ir


def compile_and_run(src: str) -> int:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    ir_prog = optimize(compile_program(ast))
    return execute_llvm(ir_prog)


def compile_to_ir(src: str) -> str:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    ir_prog = optimize(compile_program(ast))
    return to_llvm_ir(ir_prog)


def test_llvm_backend_addition():
    result = compile_and_run("let x = 1 + 2; x + 3;")
    assert result == 6


def test_llvm_return_statement():
    src = "func foo() { return 1; 2; } foo();"
    result = compile_and_run(src)
    assert result == 1


def test_llvm_static_alias_println():
    src = (
        'import std.io as io;\n'
        'static let println = io.println;\n'
        'println("hi");'
    )
    ir_text = compile_to_ir(src)
    assert "io.println" in ir_text
