import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize
from src.backend.llir import execute_llvm


def compile_and_run(src: str) -> int:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = compile_program(ast, analyzer.type_registry)
    program_ir = optimize(program_ir)
    return execute_llvm(program_ir)


def test_until_loop_scope():
    src = (
        'func main() -> int {\n'
        '    until (1) {\n'
        '    }\n'
        '    return 5;\n'
        '}'
    )
    result = compile_and_run(src)
    assert result == 5


def test_do_until_loop():
    src = (
        'func main() -> int {\n'
        '    let mut x = 0;\n'
        '    do {\n'
        '        x = x + 1;\n'
        '    } until (x == 3);\n'
        '    return x;\n'
        '}'
    )
    result = compile_and_run(src)
    assert result == 3


def test_loop_break_continue():
    src = (
        'func main() -> int {\n'
        '    let mut i = 0;\n'
        '    let mut sum = 0;\n'
        '    loop {\n'
        '        i = i + 1;\n'
        '        if i > 5 {\n'
        '            break;\n'
        '        }\n'
        '        if i % 2 == 0 {\n'
        '            continue;\n'
        '        }\n'
        '        sum = sum + i;\n'
        '    }\n'
        '    return sum;\n'
        '}'
    )
    result = compile_and_run(src)
    assert result == 9

