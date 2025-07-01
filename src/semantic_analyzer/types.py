from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from ..syntax_parser.ast import FuncSig


@dataclass
class TypeInfo:
    """Holds semantic information for a user-defined type."""

    name: str
    members: Dict[str, Any] = field(default_factory=dict)
    has_destructor: bool = False
    constructor: "FuncSig" | None = None
