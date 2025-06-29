"""Basic token representation used by the lexer."""

from dataclasses import dataclass


@dataclass
class Token:
    """Represents a single lexeme in the source file."""

    tk_type: str  # Token 的類型, 例如 'INTEGER', 'KEYWORD_LET', 'OPERATOR'
    value: str  # Token 的實際文本值, 例如 '10', 'let', '+'
    line: int  # Token 所在的行號
    col: int  # Token 所在的列號

    def __repr__(self) -> str:  # pragma: no cover - simple helper
        return f"Token({self.tk_type}, '{self.value}', at {self.line}:{self.col})"

