import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer, SemanticError
from src.backend import compile_program, optimize, to_llvm_ir
from src.backend.ffi import LIBC_FUNCTIONS


def compile_to_ir(src: str) -> str:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir_prog = optimize(compile_program(ast, analyzer.type_registry))
    return to_llvm_ir(ir_prog)


def test_ffi_registry_contains_arc_functions():
    assert "new_mx_object" in LIBC_FUNCTIONS
    assert "increase_ref" in LIBC_FUNCTIONS
    assert "decrease_ref" in LIBC_FUNCTIONS


def test_arc_runtime_calls_emit_correct_ir():
    src = (
        '@@foreign(c_name="new_mx_object")\n'
        'func new_mx_object() -> byte*;\n'
        '@@foreign(c_name="increase_ref")\n'
        'func increase_ref(ptr: byte*) -> int;\n'
        '@@foreign(c_name="decrease_ref")\n'
        'func decrease_ref(ptr: byte*) -> int;\n'
        'func main() -> int {\n'
        '    let p: byte* = new_mx_object();\n'
        '    increase_ref(p);\n'
        '    decrease_ref(p);\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'declare i8* @"new_mx_object"(' in ir
    assert 'declare i64 @"increase_ref"(i8*' in ir
    assert 'declare i64 @"decrease_ref"(i8*' in ir
    assert 'call i8* @"new_mx_object"' in ir
    assert 'call i64 @"increase_ref"' in ir
    assert 'call i64 @"decrease_ref"' in ir


def test_class_allocation_uses_arc_runtime():
    src = (
        'class Point {\n'
        '    Point() {}\n'
        '    ~Point() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let p: Point = Point();\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'call i8* @"new_mx_object"' in ir
    assert 'call i64 @"decrease_ref"' in ir


def test_arc_retain_on_assignment():
    src = (
        'class Point {\n'
        '    Point() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let p1: Point = Point();\n'
        '    let p2: Point = p1;\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'call i64 @"increase_ref"' in ir


def test_arc_release_on_reassignment():
    src = (
        'class Data {\n'
        '    Data() {}\n'
        '}\n'
        'func main() {\n'
        '    let d: Data = Data();\n'
        '    let d: Data = Data();\n'
        '}\n'
    )
    with pytest.raises(SemanticError):
        compile_to_ir(src)


def test_arc_retain_for_function_args():
    src = (
        'class Token {\n'
        '    Token() {}\n'
        '}\n'
        'func process_token(t: Token) -> Token {\n'
        '    return t;\n'
        '}\n'
        'func main() -> int {\n'
        '    let tok1: Token = Token();\n'
        '    let tok2: Token = process_token(tok1);\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert ir.count('call i64 @"increase_ref"') == 1


def test_arc_release_on_member_assignment():
    src = (
        'class Data {\n'
        '    Data() {}\n'
        '}\n'
        'class Container {\n'
        '    let mut d: Data;\n'
        '    Container() {}\n'
        '}\n'
        'func main() {\n'
        '    let c: Container = Container();\n'
        '    c.d = Data();\n'
        '    c.d = Data();\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert ir.count('call i64 @"decrease_ref"') == 1

