from __future__ import annotations

from dataclasses import dataclass
from typing import List


class Node:
    """Base class for all AST nodes."""


@dataclass
class Program(Node):
    statements: List["Statement"]


class Statement(Node):
    pass


@dataclass
class LetStmt(Statement):
    name: str
    value: "Expression"


@dataclass
class ExprStmt(Statement):
    expr: "Expression"


@dataclass
class FunctionDecl(Statement):
    name: str
    params: List[str]
    body: List[Statement]


class Expression(Node):
    pass


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Integer(Expression):
    value: int


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression


@dataclass
class Block(Statement):
    """A sequence of statements."""

    statements: List[Statement]


@dataclass
class Parameter(Node):
    names: List[str]
    type_name: str


@dataclass
class FuncSig(Node):
    params: List[Parameter]
    return_type: str | None
    var_arg: bool = False


@dataclass
class FuncDef(Statement):
    name: str
    signature: FuncSig
    body: Block


@dataclass
class ForeignFuncDecl(Statement):
    name: str
    signature: FuncSig
    c_name: str

@dataclass
class FunctionCall(Expression):
    name: str
    args: List[Expression]

