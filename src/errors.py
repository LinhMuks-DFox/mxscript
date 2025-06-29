from dataclasses import dataclass

from .lexer import Token

@dataclass
class SyntaxErrorWithPos(Exception):
    message: str
    token: Token

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        return f"{self.message} at line {self.token.line}, column {self.token.col}"
