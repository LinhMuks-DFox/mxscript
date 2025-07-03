import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend import tokenize, TokenStream
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, execute_llvm


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = compile_program(ast, analyzer.type_registry)
    return execute_llvm(program_ir)


def test_default_string(capfd):
    src = (
        'func hello(x:string="Hello") {\n'
        '    print(x);\n'
        '}\n'
        'func main() {\n'
        '    hello();\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "Hello\n"


def test_default_int(capfd):
    src = (
        'func test_default_int(val:int=123) {\n'
        '    print(val);\n'
        '}\n'
        'func main() {\n'
        '    test_default_int();\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "123\n"
