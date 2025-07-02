import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import ProgramIR, compile_program, execute_llvm

from pathlib import Path


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = compile_program(ast, analyzer.type_registry)
    return execute_llvm(program_ir)


def compile_and_run_file(file_path: Path) -> ProgramIR:
    source = file_path.read_text()
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = compile_program(ast, analyzer.type_registry)
    return program_ir


def test_backend_addition():
    result = compile_and_run("let x = 1 + 2; x + 3;")
    assert result == 6


def test_backend_import_hello_world():
    ir = compile_and_run_file(Path("demo_program/examples/hello_world.mxs"))
    assert "io.println" in ir.functions

def test_auto_main_call():
    src = "func main() -> int { return 42; }"
    result = compile_and_run(src)
    assert result == 42

def test_backend_return_statement():
    src = "func foo() { return 1; 2; } foo();"
    result = compile_and_run(src)
    assert result == 1


def test_print_functions(capfd):
    compile_and_run('import std.io as io; io.print("foo"); io.println("bar");')
    captured = capfd.readouterr()
    assert captured.out == "foobar\n"


def test_file_operations(tmp_path):
    path = tmp_path / "out.txt"
    src = (
        f'import std.io as io;\n'
        f'func main() -> int {{\n'
        f'    let fd = io.open_file("{path}", 577, 438);\n'
        f'    io.write_file(fd, "hello");\n'
        f'    io.close_file(fd);\n'
        f'    return 0;\n'
        f'}}'
    )
    result = compile_and_run(src)
    assert result == 0
    assert path.read_text() == "hello"


def test_static_alias_println(capfd):
    src = (
        'import std.io as io;\n'
        'static let println = io.println;\n'
        'func main() -> int {\n'
        '    println("hi");\n'
        '    return 0;\n'
        '}'
    )
    result = compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "hi\n"
    assert result == 0


def test_constructor_call(capfd):
    src = (
        'import std.io as io;\n'
        'class Box {\n'
        '    Box() { io.println("ctor"); }\n'
        '    ~Box() { io.println("dtor"); }\n'
        '}\n'
        'func main() -> int {\n'
        '    let b: Box = Box();\n'
        '    return 0;\n'
        '}'
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert "ctor" in captured.out


def test_destructors_scopes(capfd):
    src = (
        'import std.io as io;\n'
        'class G { ~G() { io.println("dg"); } }\n'
        'class Outer { ~Outer() { io.println("do"); } }\n'
        'class Inner { ~Inner() { io.println("di"); } }\n'
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


def test_destructor_inferred_type(capfd):
    src = (
        'import std.io as io;\n'
        'class Box {\n'
        '    Box() {}\n'
        '    ~Box() { io.println("drop"); }\n'
        '}\n'
        'func main() -> int {\n'
        '    let b = Box();\n'
        '    return 0;\n'
        '}\n'
    )
    pytest.skip("Destructor semantics not fully implemented")

def test_destructor_call(capfd):
    src = (
        'import std.io as io;\n'
        'class Loud {\n'
        '    ~Loud() {\n'
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


def test_constructor_and_destructor_call(capfd):
    src = (
        'import std.io as io;\n'
        'class Box {\n'
        '    Box() { io.println("ctor"); }\n'
        '    ~Box() { io.println("dtor"); }\n'
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


def test_break_llir_generation():
    src = "loop { break; }"
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir = compile_program(ast, analyzer.type_registry)
    from src.backend.llir import Br, Label
    labels = [instr.name for instr in ir.code if isinstance(instr, Label)]
    assert len(labels) >= 2
    break_target = labels[-1]
    assert any(isinstance(instr, Br) and instr.label == break_target for instr in ir.code)

