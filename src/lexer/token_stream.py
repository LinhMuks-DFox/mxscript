"""Utility container for navigating a list of tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .Token import Token


@dataclass
class TokenStream:
    """Simple stream wrapper around a list of tokens."""

    tokens: List[Token]
    position: int = 0

    def peek(self, offset: int = 0) -> Optional[Token]:
        index = self.position + offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None

    def next(self) -> Optional[Token]:
        tok = self.peek()
        if tok is not None:
            self.position += 1
        return tok

    def expect(self, tk_type: str, value: Optional[str] = None) -> Token:
        token = self.next()
        if token is None:
            raise SyntaxError(f"Expected {tk_type}, got EOF")
        if token.tk_type != tk_type or (value is not None and token.value != value):
            raise SyntaxError(f"Expected {tk_type} '{value}', got {token}")
        return token

    def __iter__(self) -> Iterable[Token]:
        while self.position < len(self.tokens):
            yield self.next()

