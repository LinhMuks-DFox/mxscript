import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.syntax_parser.ast import StructDef
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, DestructorCall


def test_destructor_call_injection():
    source = """
    struct File {
        func ~File() {}
    }
    func main() {
        let f: File = 0;
    }
    """
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    ir = compile_program(ast, analyzer.type_registry)
    assert "File_destructor" in ir.functions

    code = ir.functions["main"].code
    assert isinstance(code[-1], DestructorCall)
    assert code[-1].name == "f"


def test_shadowed_variable_destructors():
    source = """
    struct File {
        func ~File() {}
    }
    func main() {
        let f: File = 0;
        {
            let f: File = 0;
        }
    }
    """
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    ir = compile_program(ast, analyzer.type_registry)
    code = ir.functions["main"].code
    dtor_calls = [i for i in code if isinstance(i, DestructorCall)]
    assert len(dtor_calls) == 2
    assert all(call.name == "f" for call in dtor_calls)

