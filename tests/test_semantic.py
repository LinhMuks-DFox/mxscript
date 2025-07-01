import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.syntax_parser.ast import (
    BinaryOp,
    ExprStmt,
    FunctionCall,
    FunctionDecl,
    Identifier,
    Integer,
    LetStmt,
    Program,
)
from src.semantic_analyzer import SemanticAnalyzer, SemanticError


def analyze(src: str) -> None:
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)


def analyze_ast(program: Program) -> None:
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)


def test_semantic_success():
    analyze("let x = 1; x + 2;")


def test_semantic_undefined():
    with pytest.raises(SemanticError):
        analyze("x + 1;")


def test_function_scope_success():
    prog = Program(
        [
            FunctionDecl(
                "foo",
                ["a", "b"],
                [
                    LetStmt("c", Identifier("a")),
                    ExprStmt(BinaryOp(Identifier("c"), "+", Identifier("b"))),
                ],
            ),
            ExprStmt(FunctionCall("foo", [Integer(1), Integer(2)])),
        ]
    )
    analyze_ast(prog)


def test_function_scope_undefined():
    prog = Program(
        [
            FunctionDecl(
                "foo",
                ["a"],
                [ExprStmt(BinaryOp(Identifier("a"), "+", Identifier("b")))]
            )
        ]
    )
    with pytest.raises(SemanticError):
        analyze_ast(prog)


def test_local_variable_not_global():
    prog = Program(
        [
            FunctionDecl("foo", [], [LetStmt("x", Integer(1))]),
            ExprStmt(Identifier("x")),
        ]
    )
    with pytest.raises(SemanticError):
        analyze_ast(prog)


def test_import_statement_semantic_ok():
    analyze("import std.io as io;")


def test_import_alias_reference():
    analyze("import foo.bar as bar; bar;")


def test_analyzer_registers_class_and_destructor():
    source = "class File { func ~File() {} }"
    ast = Parser(TokenStream(tokenize(source))).parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    assert "File" in analyzer.type_registry
    info = analyzer.type_registry["File"]
    assert info.has_destructor is True


def test_analyzer_registers_constructor():
    source = "class Box { func Box(v: int) {} }"
    ast = Parser(TokenStream(tokenize(source))).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    info = analyzer.type_registry["Box"]
    assert info.constructor is not None


def test_assignment_to_immutable_error():
    src = "let x = 3; x = 5;"
    with pytest.raises(SemanticError):
        analyze(src)


def test_assignment_to_mutable_ok():
    src = "let mut x = 3; x = 5;"
    analyze(src)

