import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize, execute_llvm


def compile_and_run(source: str) -> int:
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir = optimize(compile_program(ast, analyzer.type_registry))
    return execute_llvm(ir)


def test_complex_member_lifecycle():
    src = (
        'struct Inner {\n'
        '    func Inner() {}\n'
        '}\n'
        'struct Outer {\n'
        '    let mut member: Inner;\n'
        '    func Outer() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let o: Outer = Outer();\n'
        '    o.member = Inner();\n'
        '    return 0;\n'
        '}\n'
    )
    result = compile_and_run(src)
    assert result == 0


def test_member_reassignment():
    src = (
        'struct Inner {\n'
        '    func Inner() {}\n'
        '}\n'
        'struct Outer {\n'
        '    let mut member: Inner;\n'
        '    func Outer() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let o: Outer = Outer();\n'
        '    o.member = Inner();\n'
        '    o.member = Inner();\n'
        '    return 0;\n'
        '}\n'
    )
    result = compile_and_run(src)
    assert result == 0


def test_function_call_chain():
    src = (
        'struct Data {\n'
        '    func Data() {}\n'
        '}\n'
        'func make_data() -> Data {\n'
        '    return Data();\n'
        '}\n'
        'func pass_through(d: Data) -> Data {\n'
        '    return d;\n'
        '}\n'
        'func main() -> int {\n'
        '    let d1: Data = make_data();\n'
        '    let d2: Data = pass_through(d1);\n'
        '    return 0;\n'
        '}\n'
    )
    result = compile_and_run(src)
    assert result == 0


def test_allocation_in_loop():
    pytest.skip("For loops not yet implemented")
    src = (
        'struct Data {\n'
        '    func Data() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    for i in 0..1000 {\n'
        '        let temp: Data = Data();\n'
        '    }\n'
        '    return 0;\n'
        '}\n'
    )
    result = compile_and_run(src)
    assert result == 0

