import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.frontend import TokenStream, tokenize
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
    # Top level expressions now yield 0 when executed
    assert result == 0


def test_backend_import_hello_world():
    ir = compile_and_run_file(Path("demo_program/examples/hello_world.mxs"))
    # Compiled program should include the demo function definitions
    assert "hello_world" in ir.functions


def test_auto_main_call():
    src = "func main() -> int { return 42; }"
    result = compile_and_run(src)
    assert result == 42


def test_backend_return_statement():
    src = "func foo() { return 1; 2; } foo();"
    result = compile_and_run(src)
    # The call result is not returned at the top level
    assert result == 0


def test_print_functions(capfd):
    src = (
        "func main() -> nil {\n"
        "    let i = 101;\n"
        "    let f = 2.5;\n"
        "    print(i);\n"
        "    print(f);\n"
        "    print(true);\n"
        "}"
    )
    compile_and_run(src)
    captured = capfd.readouterr()
    assert captured.out == "101\n2.5\ntrue\n"


def test_print_end_variations(capfd):
    compile_and_run('print("Hello");')
    captured = capfd.readouterr()
    assert captured.out == "Hello\n"

    compile_and_run('print("Hello", end="");')
    captured = capfd.readouterr()
    assert captured.out == "Hello"

    compile_and_run('print("Hello", end="-->");')
    captured = capfd.readouterr()
    assert captured.out == "Hello-->"


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
    assert any(
        isinstance(instr, Br) and instr.label == break_target for instr in ir.code
    )
