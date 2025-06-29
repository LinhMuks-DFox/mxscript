import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import (
    BinaryOp,
    ExprStmt,
    Integer,
    LetStmt,
    Parser,
)


def parse(src: str):
    tokens = tokenize(src)
    stream = TokenStream(tokens)
    return Parser(stream).parse()


def test_parse_let_statement():
    program = parse("let x = 42;")
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, LetStmt)
    assert stmt.name == "x"
    assert isinstance(stmt.value, Integer)
    assert stmt.value.value == 42


def test_operator_precedence():
    program = parse("1 + 2 * 3;")
    stmt = program.statements[0]
    assert isinstance(stmt, ExprStmt)
    expr = stmt.expr
    assert isinstance(expr, BinaryOp)
    assert expr.op == "+"
    assert isinstance(expr.right, BinaryOp)
    assert expr.right.op == "*"
    assert isinstance(expr.right.left, Integer)
    assert expr.right.left.value == 2
