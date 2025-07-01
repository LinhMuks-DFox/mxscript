import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from pathlib import Path
from src.backend import compile_program, optimize, execute_llvm, to_llvm_ir
import pytest


def compile_and_run(src: str) -> int:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir_prog = optimize(compile_program(ast, analyzer.type_registry))
    return execute_llvm(ir_prog)



def compile_to_ir(src: str) -> str:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir_prog = optimize(compile_program(ast, analyzer.type_registry))
    return to_llvm_ir(ir_prog)

def compile_and_run_file(file_path: Path) -> int:
    source = file_path.read_text()
    tokens = tokenize(source)

    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir_prog = optimize(compile_program(ast, analyzer.type_registry))
    return execute_llvm(ir_prog)



def test_llvm_backend_addition():
    result = compile_and_run("let x = 1 + 2; x + 3;")
    assert result == 6


def test_llvm_return_statement():
    src = "func foo() { return 1; 2; } foo();"
    result = compile_and_run(src)
    assert result == 1



def test_llvm_static_alias_println():
    src = (
        'import std.io as io;\n'
        'static let println = io.println;\n'
        'println("hi");'
    )
    ir_text = compile_to_ir(src)
    assert "io.println" in ir_text

def test_llvm_hello_world_example():
    path = Path("demo_program/examples/hello_world.mxs")
    result = compile_and_run_file(path)
    assert result == 0



def test_llvm_ffi_time_random():
    res_time = compile_and_run('import std.time as time; time.now();')
    assert isinstance(res_time, int)
    res_rand = compile_and_run('import std.random as random; random.rand();')
    assert isinstance(res_rand, int)

def test_llvm_print_functions(capfd):
    src = (
        '@@foreign(c_name="write")\n'
        'func __internal_write(fd: int, buf: byte*, len: int) -> int;\n'
        'func main() -> int {\n'
        '    __internal_write(1, "foo", 3);\n'
        '    __internal_write(1, "bar\\n", 4);\n'
        '    return 0;\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "foobar\n"


def test_llvm_file_operations(tmp_path):
    path = tmp_path / "out.txt"
    src = (
        '@@foreign(c_name="open")\n'
        'func __internal_open(path: string, flags: int, mode: int) -> int;\n'
        '@@foreign(c_name="write")\n'
        'func __internal_write(fd: int, buf: byte*, len: int) -> int;\n'
        '@@foreign(c_name="close")\n'
        'func __internal_close(fd: int) -> int;\n'
        'func main() -> int {\n'
        f'    let fd = __internal_open("{path}", 577, 438);\n'
        '    __internal_write(fd, "hello", 5);\n'
        '    __internal_close(fd);\n'
        '    return 0;\n'
        '}'
    )
    result = compile_and_run(src)
    assert result == 0
    assert path.read_text() == "hello"


def test_llvm_destructor_call(capfd):
    src = (
        'import std.io as io;\n'
        'class Loud {\n'
        '    func ~Loud() {\n'
        '        io.println("Object destroyed!");\n'
        '    }\n'
        '}\n'
        'func main() -> int {\n'
        '    io.println("Creating object...");\n'
        '    let obj: Loud = 0;\n'
        '    io.println("Object created. Exiting main...");\n'
        '    return 0;\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert "Object destroyed!" in captured.out


def test_llvm_shadowed_destructors(capfd):
    src = (
        'import std.io as io;\n'
        'class Loud {\n'
        '    func ~Loud() { io.println("dtor"); }\n'
        '}\n'
        'func main() -> int {\n'
        '    let obj: Loud = 0;\n'
        '    { let obj: Loud = 0; }\n'
        '    return 0;\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out.count("dtor") == 2


def test_llvm_constructor(capfd):
    src = (
        'import std.io as io;\n'
        'class Box {\n'
        '    func Box() { io.println("ctor"); }\n'
        '    func ~Box() { io.println("dtor"); }\n'
        '}\n'
        'func main() -> int {\n'
        '    let b: Box = Box();\n'
        '    return 0;\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert "ctor" in captured.out
    assert "dtor" in captured.out


def test_llvm_destructors_scopes(capfd):
    src = (
        'import std.io as io;\n'
        'class G { func ~G() { io.println("dg"); } }\n'
        'class Outer { func ~Outer() { io.println("do"); } }\n'
        'class Inner { func ~Inner() { io.println("di"); } }\n'
        'let g: G = 0;\n'
        'func main() -> int {\n'
        '    let x: Outer = 0;\n'
        '    {\n'
        '        let x: Inner = 0;\n'
        '        io.println("inner");\n'
        '    }\n'
        '    io.println("outer");\n'
        '    return 0;\n'
        '}\n'
    )
    pytest.skip("Destructor semantics not fully implemented")


def test_llvm_destructor_inferred_type(capfd):
    src = (
        'import std.io as io;\n'
        'class Box {\n'
        '    func Box() {}\n'
        '    func ~Box() { io.println("drop"); }\n'
        '}\n'
        'func main() -> int {\n'
        '    let b = Box();\n'
        '    return 0;\n'
        '}\n'
    )
    pytest.skip("Destructor semantics not fully implemented")
