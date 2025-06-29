import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import (
    BinaryOp,
    ExprStmt,
    Integer,
    LetStmt,
    FuncDef,
    Block,
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


def test_parse_func_def():
    src = "func add(x: int, y: int) -> int { let z = x + y; }"
    program = parse(src)
    assert len(program.statements) == 1
    func = program.statements[0]
    assert isinstance(func, FuncDef)
    assert func.name == "add"
    assert len(func.signature.params) == 2
    assert func.signature.params[0].names == ["x"]
    assert func.signature.params[0].type_name == "int"
    assert func.signature.return_type == "int"
    assert isinstance(func.body, Block)
    assert len(func.body.statements) == 1
    assert isinstance(func.body.statements[0], LetStmt)


def test_nested_blocks():
    src = "func foo() { let x = 1; { let y = 2; } }"
    program = parse(src)
    func = program.statements[0]
    assert isinstance(func, FuncDef)
    assert len(func.body.statements) == 2
    inner = func.body.statements[1]
    assert isinstance(inner, Block)
    assert len(inner.statements) == 1
    assert isinstance(inner.statements[0], LetStmt)

