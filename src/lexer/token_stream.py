"""Utility container for navigating a list of tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .Token import Token
from ..errors import SyntaxErrorWithPos


@dataclass
class TokenStream:
    """Simple stream wrapper around a list of tokens."""

    tokens: List[Token]
    position: int = 0

    def _skip_comments_from(self, index: int) -> int:
        """Return the next index at or after *index* that is not a comment."""
        while index < len(self.tokens) and self.tokens[index].tk_type == "COMMENT":
            index += 1
        return index

    def peek(self, offset: int = 0) -> Optional[Token]:
        index = self._skip_comments_from(self.position)
        while offset > 0 and index < len(self.tokens):
            index += 1
            index = self._skip_comments_from(index)
            offset -= 1
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def next(self) -> Optional[Token]:
        tok = self.peek()
        if tok is not None:
            self.position = self._skip_comments_from(self.position)
            self.position += 1
            self.position = self._skip_comments_from(self.position)
        return tok

    def expect(self, tk_type: str, value: Optional[str] = None) -> Token:
        token = self.next()
        if token is None:
            raise SyntaxErrorWithPos(f"Expected {tk_type}", self.tokens[-1])
        if token.tk_type != tk_type or (value is not None and token.value != value):
            msg = f"Expected {tk_type} '{value}'" if value else f"Expected {tk_type}"
            raise SyntaxErrorWithPos(msg, token)
        return token

    def __iter__(self) -> Iterable[Token]:
        while self.position < len(self.tokens):
            yield self.next()

