from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict

from ..frontend.tokens import Token


@dataclass(kw_only=True)
class Node:
    """Base class for all AST nodes."""

    loc: Optional[Token] = None


@dataclass
class Program(Node):
    statements: List["Statement"]


class Statement(Node):
    pass


@dataclass
class LetStmt(Statement):
    names: List[str]
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
class MemberAssign(Expression):
    """Assignment to ``object.member`` via the ``=`` operator."""

    object: Expression
    member: Identifier
    value: Expression


@dataclass
class AssignExpr(Expression):
    """Assignment expression like ``x = value``."""

    target: Expression
    value: Expression


@dataclass
class Integer(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float


@dataclass
class Boolean(Expression):
    value: bool


@dataclass
class NilLiteral(Expression):
    pass


@dataclass
class String(Expression):
    """String literal expression."""

    value: str

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression
    left_type: str | None = None
    right_type: str | None = None
    result_type: str | None = None


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
    default: "Expression" | None = None


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
    template_params: list[str] | None = None
    ffi_info: Dict[str, str] | None = None


@dataclass
class MethodDef(Statement):
    """Method definition inside a class."""

    name: str
    signature: FuncSig
    body: Block
    is_override: bool = False
    template_params: list[str] | None = None
    ffi_info: Dict[str, str] | None = None


@dataclass
class OperatorDef(Statement):
    """Operator overload definition inside a class."""

    op: str
    signature: FuncSig
    body: Block
    is_override: bool = False


@dataclass
class ConstructorDef(Statement):
    """Constructor inside a class definition."""

    signature: FuncSig
    body: Block
    super_call: tuple[str, List[Expression]] | None = None


@dataclass
class ClassDef(Statement):
    """Definition of a user-defined class."""

    name: str
    body: Block
    generic_params: List[str] | None = None
    super_class: str | None = None
    is_pod: bool = False
    template_params: list[str] | None = None


@dataclass
class DestructorDef(Statement):
    """Destructor within a class definition."""

    body: Block
    super_call: str | None = None


@dataclass
class FieldDef(Statement):
    """Field definition inside a class."""

    is_static: bool
    is_mutable: bool
    name: str
    type_spec: str | None = None
    initializer: Expression | None = None


@dataclass
class AccessSpec(Statement):
    level: str


@dataclass
class InterfaceDef(Statement):
    name: str
    body: Block
    generic_params: List[str] | None = None
    super_interfaces: List[str] | None = None

@dataclass
class FunctionCall(Expression):
    name: str
    args: List[Expression]
    kwargs: List[tuple[str, Expression]] | None = None


@dataclass
class ForInStmt(Statement):
    """Represents a simple 'for' loop over an iterable expression."""

    var: str
    iterable: Expression
    body: Block
    is_mut: bool = False


@dataclass
class LoopStmt(Statement):
    """An infinite loop that repeatedly executes ``body``."""

    body: Block


@dataclass
class UntilStmt(Statement):
    """Pre-test loop that executes ``body`` until ``condition`` is true."""

    condition: Expression
    body: Block


@dataclass
class DoUntilStmt(Statement):
    """Post-test loop that executes ``body`` at least once."""

    body: Block
    condition: Expression


@dataclass
class BreakStmt(Statement):
    """Terminate the innermost enclosing loop."""

    pass


@dataclass
class ContinueStmt(Statement):
    """Skip to the next iteration of the innermost loop."""

    pass


@dataclass
class IfStmt(Statement):
    """Classic if-else statement."""

    condition: Expression
    then_block: Block
    else_block: Optional[Block | "IfStmt"] = None


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

