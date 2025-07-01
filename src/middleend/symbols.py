from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Symbol:
    """Represents a variable within a scoped symbol table."""

    name: str
    type_name: Optional[str]
    needs_destruction: bool = False


class ScopedSymbolTable:
    """A simple stack-based scoped symbol table."""

    def __init__(self) -> None:
        self.scopes: List[Dict[str, Symbol]] = [{}]

    def enter_scope(self) -> None:
        self.scopes.append({})

    def leave_scope(self) -> Dict[str, Symbol]:
        return self.scopes.pop()

    def add_symbol(self, symbol: Symbol) -> None:
        self.scopes[-1][symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
