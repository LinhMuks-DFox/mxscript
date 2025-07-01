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

