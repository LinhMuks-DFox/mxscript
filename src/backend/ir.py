from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


class Instr:
    pass


@dataclass
class Const(Instr):
    value: int | float | bool | str | None


@dataclass
class Alloc(Instr):
    size: int


@dataclass
class Dup(Instr):
    pass


@dataclass
class Load(Instr):
    name: str


@dataclass
class Store(Instr):
    name: str
    type_name: str | None = None
    is_mut: bool = False


@dataclass
class BinOpInstr(Instr):
    op: str


@dataclass
class Pop(Instr):
    pass


@dataclass
class Call(Instr):
    name: str
    argc: int


@dataclass
class Function:
    name: str
    params: List[str]
    code: List[Instr]


@dataclass
class Return(Instr):
    """Marks the end of a function and optionally yields a value."""

    pass


@dataclass
class DestructorCall(Instr):
    """Explicit call to a variable's destructor when it goes out of scope."""

    name: str


@dataclass
class ScopeEnter(Instr):
    """Marks entering a new lexical scope."""


@dataclass
class ScopeExit(Instr):
    """Marks leaving a lexical scope."""


@dataclass
class ProgramIR:
    code: List[Instr]
    functions: Dict[str, Function]
    foreign_functions: Dict[str, str]


@dataclass
class ErrorValue:
    """Runtime representation of an Error object."""

    msg: str = ""
    panic: bool = False
