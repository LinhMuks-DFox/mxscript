import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize, execute


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    code = compile_program(ast)
    code = optimize(code)
    return execute(code)


def test_backend_addition():
    result = compile_and_run("let x = 1 + 2; x + 3;")
    assert result == 6
