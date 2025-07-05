import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, execute_llvm


def compile_and_run(src: str) -> int:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir = compile_program(ast, analyzer.type_registry)
    return execute_llvm(ir)


def test_variadic_ffi_call(capfd):
    src = (
        '@@foreign(lib="runtime.so", symbol_name="printf_wrapper", argv=[1,...])\n'
        "func c_printf(format: String, ...) -> int;\n"
        "func main() -> int {\n"
        '    c_printf("hi", 1, 2);\n'
        "    return 0;\n"
        "}\n"
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert "hi 1 2" in captured.out
