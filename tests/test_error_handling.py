import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize, execute
from src.backend.llir import ErrorValue


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = optimize(compile_program(ast, analyzer.type_registry))
    return execute(program_ir)


def test_raise_returns_error_value():
    src = (
        '@@foreign(c_name="make_error")\n'
        'func make_error(msg: string, panic: int) -> int;\n'
        'func raise_error() -> int { raise make_error("oops", 0); }\n'
        'raise_error();'
    )
    result = compile_and_run(src)
    assert isinstance(result, ErrorValue)
    assert result.msg == "oops"
    assert result.panic is False


def test_panic_terminates():
    src = (
        '@@foreign(c_name="make_error")\n'
        'func make_error(msg: string, panic: int) -> int;\n'
        'func boom() { raise make_error("boom", 1); }\n'
        'boom();'
    )
    with pytest.raises(RuntimeError):
        compile_and_run(src)
