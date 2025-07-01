import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import ProgramIR, compile_program, optimize, execute

from pathlib import Path


def compile_and_run(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = compile_program(ast, analyzer.type_registry)
    program_ir = optimize(program_ir)
    return execute(program_ir)


def compile_and_run_file(file_path: Path) -> ProgramIR:
    source = file_path.read_text()
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    program_ir = optimize(compile_program(ast, analyzer.type_registry))
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

