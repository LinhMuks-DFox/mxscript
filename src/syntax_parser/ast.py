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
