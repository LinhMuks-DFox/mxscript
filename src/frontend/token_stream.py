"""Utility container for navigating a list of tokens for the frontend tokenizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .tokens import Token, TokenType
from ..errors import SyntaxError, SourceLocation


@dataclass
class TokenStream:
    """Simple stream wrapper around a list of tokens."""

    tokens: List[Token]
    position: int = 0

    def _skip_comments_from(self, index: int) -> int:
        """Return the next index at or after *index* that is not a comment."""
        while index < len(self.tokens) and self.tokens[index].type == TokenType.COMMENT:
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

    def expect(self, tk_type: TokenType | str, value: Optional[str] = None) -> Token:
        token = self.next()
        if token is None:
            loc = SourceLocation("<tokens>", self.tokens[-1].line, self.tokens[-1].column, "")
            name = tk_type.name if isinstance(tk_type, TokenType) else tk_type
            raise SyntaxError(f"Expected {name}", loc)
        expected_match = token.type == tk_type if isinstance(tk_type, TokenType) else token.type.name == tk_type
        if not expected_match or (value is not None and token.value != value):
            name = tk_type.name if isinstance(tk_type, TokenType) else tk_type
            msg = f"Expected {name} '{value}'" if value else f"Expected {name}"
            loc = SourceLocation("<tokens>", token.line, token.column, "")
            raise SyntaxError(msg, loc)
        return token

    def __iter__(self) -> Iterable[Token]:
        while self.position < len(self.tokens):
            yield self.next()
