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
    value: "Expression" | None = None
    type_name: str | None = None
    is_mut: bool = False


@dataclass
class BindingStmt(Statement):
    """Global binding using ``static`` or ``dynamic`` let."""

    name: str
    value: "Expression"
    is_static: bool = True


@dataclass
class ExprStmt(Statement):
    expr: "Expression"


@dataclass
class ImportStmt(Statement):
    """Import statement capturing module path and optional alias."""

    module: str
    alias: str | None = None


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
class MemberAccess(Expression):
    """Access to ``member`` of ``object`` via the ``.`` operator."""

    object: Expression
    member: Identifier


@dataclass
class Integer(Expression):
    value: int


@dataclass
class String(Expression):
    """String literal expression."""

    value: str

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
class StructDef(Statement):
    """Definition of a user-defined struct."""

    name: str
    body: Block


@dataclass
class DestructorDef(Statement):
    """Destructor within a struct definition."""

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


@dataclass
class ForInStmt(Statement):
    """Represents a simple 'for' loop over an iterable expression."""

    var: str
    iterable: Expression
    body: Block
    is_mut: bool = False


@dataclass
class ReturnStmt(Statement):
    """Return statement inside a function."""

    value: Expression | None = None


@dataclass
class RaiseStmt(Statement):
    """`raise` statement used for value-based error handling."""

    expr: Expression


@dataclass
class RaiseExpr(Expression):
    expr: Expression


@dataclass
class MatchCase(Node):
    name: str
    type_name: str
    body: Block | Expression


@dataclass
class MatchExpr(Expression):
    value: Expression
    cases: List[MatchCase]

