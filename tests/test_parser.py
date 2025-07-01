import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lexer import TokenStream, tokenize
from src.syntax_parser import (
    BinaryOp,
    ExprStmt,
    Integer,
    String,
    LetStmt,
    BindingStmt,
    ReturnStmt,
    FuncDef,
    StructDef,
    DestructorDef,
    Block,
    ImportStmt,
    ForInStmt,
    RaiseStmt,
    MatchExpr,
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


def test_parse_typed_let():
    program = parse("let x: int = 42;")
    stmt = program.statements[0]
    assert isinstance(stmt, LetStmt)
    assert stmt.name == "x"
    assert stmt.type_name == "int"
    assert isinstance(stmt.value, Integer)


def test_parse_mutable_let():
    program = parse("let mut y = 1;")
    stmt = program.statements[0]
    assert isinstance(stmt, LetStmt)
    assert stmt.is_mut


def test_parse_static_binding():
    program = parse("static let x = 1;")
    stmt = program.statements[0]
    assert isinstance(stmt, BindingStmt)
    assert stmt.is_static
    assert stmt.name == "x"
    assert isinstance(stmt.value, Integer)


def test_parse_dynamic_binding():
    program = parse("dynamic let y = 2;")
    stmt = program.statements[0]
    assert isinstance(stmt, BindingStmt)
    assert not stmt.is_static
    assert stmt.name == "y"


def test_parse_string_literal():
    program = parse('"hello";')
    stmt = program.statements[0]
    assert isinstance(stmt, ExprStmt)
    assert isinstance(stmt.expr, String)
    assert stmt.expr.value == "hello"


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


def test_parse_import():
    program = parse("import std.io as io;")
    stmt = program.statements[0]
    assert isinstance(stmt, ImportStmt)
    assert stmt.module == "std.io"
    assert stmt.alias == "io"


def test_parse_for_loop():
    src = "for i in 0..10 { let x = i; }"
    program = parse(src)
    stmt = program.statements[0]
    assert isinstance(stmt, ForInStmt)
    assert stmt.var == "i"


def test_parse_raise_stmt():
    program = parse("raise 1;")
    stmt = program.statements[0]
    assert isinstance(stmt, RaiseStmt)


def test_parse_return_stmt():
    program = parse("return 1;")
    stmt = program.statements[0]
    assert isinstance(stmt, ReturnStmt)


def test_parse_match_expr():
    program = parse("match (x) { case v: int => v, case s: string => 0 };")
    stmt = program.statements[0]
    assert isinstance(stmt, ExprStmt)
    assert isinstance(stmt.expr, MatchExpr)


def test_parse_struct_with_destructor():
    source = """
    struct File {
        let fd: int;

        func ~File() {
            io.close_file(self.fd);
        }
    }
    """
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()

    assert isinstance(ast.statements[0], StructDef)
    struct_def = ast.statements[0]
    assert struct_def.name == "File"

    destructor_found = False
    for stmt in struct_def.body.statements:
        if isinstance(stmt, DestructorDef):
            destructor_found = True
            break
    assert destructor_found

