import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from pathlib import Path
from src.backend import compile_program, optimize, execute_llvm, to_llvm_ir


def compile_and_run(src: str) -> int:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    ir_prog = optimize(compile_program(ast))
    return execute_llvm(ir_prog)



def compile_to_ir(src: str) -> str:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    ir_prog = optimize(compile_program(ast))
    return to_llvm_ir(ir_prog)

def compile_and_run_file(file_path: Path) -> int:
    source = file_path.read_text()
    tokens = tokenize(source)

    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    SemanticAnalyzer().analyze(ast)
    ir_prog = optimize(compile_program(ast))
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