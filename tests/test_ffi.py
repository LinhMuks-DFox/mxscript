import os
import sys

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


def test_fixed_arity_foreign_print(capfd):
    src = (
        '@@foreign(lib="runtime.so", symbol_name="mxs_print_object_ext")\n'
        'func c_print(obj: Integer, end: String) -> Nil;\n'
        'func main() -> int {\n'
        '    c_print(123, "!");\n'
        '    return 0;\n'
        '}'
    )
    result = compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "123!"
    assert result == 0


def test_variadic_printf_wrapper(capfd):
    src = (
        '@@foreign(lib="runtime.so", symbol_name="printf_wrapper", argv=[1,...])\n'
        'func c_printf(fmt: String, ...) -> int;\n'
        'func main() -> int {\n'
        '    c_printf("Args:", "yay", 42);\n'
        '    return 0;\n'
        '}'
    )
    result = compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "Args: yay 42"
    assert result >= 0
