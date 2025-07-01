import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
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
    assert "arc_alloc" in LIBC_FUNCTIONS
    assert "arc_retain" in LIBC_FUNCTIONS
    assert "arc_release" in LIBC_FUNCTIONS


def test_arc_runtime_calls_emit_correct_ir():
    src = (
        '@@foreign(c_name="arc_alloc")\n'
        'func arc_alloc(size: int) -> byte*;\n'
        '@@foreign(c_name="arc_retain")\n'
        'func arc_retain(ptr: byte*) -> byte*;\n'
        '@@foreign(c_name="arc_release")\n'
        'func arc_release(ptr: byte*);\n'
        'func main() -> int {\n'
        '    let p: byte* = arc_alloc(4);\n'
        '    arc_retain(p);\n'
        '    arc_release(p);\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'declare i8* @"arc_alloc"(i64' in ir
    assert 'declare i8* @"arc_retain"(i8*' in ir
    assert 'declare void @"arc_release"(i8*' in ir
    assert 'call i8* @"arc_alloc"' in ir
    assert 'call i8* @"arc_retain"' in ir
    assert 'call void @"arc_release"' in ir


def test_struct_allocation_uses_arc_runtime():
    src = (
        'struct Point {\n'
        '    func Point() {}\n'
        '    func ~Point() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let p: Point = Point();\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'call i8* @"arc_alloc"' in ir
    assert 'call void @"arc_release"' in ir


def test_arc_retain_on_assignment():
    src = (
        'struct Point {\n'
        '    func Point() {}\n'
        '}\n'
        'func main() -> int {\n'
        '    let p1: Point = Point();\n'
        '    let p2: Point = p1;\n'
        '    return 0;\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert 'call i8* @"arc_retain"' in ir


def test_arc_release_on_reassignment():
    src = (
        'struct Data {\n'
        '    func Data() {}\n'
        '}\n'
        'func main() {\n'
        '    let d: Data = Data();\n'
        '    let d: Data = Data();\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert ir.count('call void @"arc_release"') == 1


def test_arc_retain_for_function_args():
    src = (
        'struct Token {\n'
        '    func Token() {}\n'
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
    assert ir.count('call i8* @"arc_retain"') == 1


def test_arc_release_on_member_assignment():
    src = (
        'struct Data {\n'
        '    func Data() {}\n'
        '}\n'
        'struct Container {\n'
        '    let mut d: Data;\n'
        '    func Container() {}\n'
        '}\n'
        'func main() {\n'
        '    let c: Container = Container();\n'
        '    c.d = Data();\n'
        '    c.d = Data();\n'
        '}\n'
    )
    ir = compile_to_ir(src)
    assert ir.count('call void @"arc_release"') == 1

