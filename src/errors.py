from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLocation:
    """Represents a position within a source file."""

    filename: str
    line: int
    column: int
    source_line: str = ""


class CompilerError(Exception):
    """Base class for all controlled compiler errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None) -> None:
        self.message = message
        self.location = location
        super().__init__(self.message)


class SyntaxError(CompilerError):
    """Error raised when the parser encounters invalid syntax."""

    pass


class SemanticError(CompilerError):
    """Error raised during semantic analysis."""

    pass


class NameError(SemanticError):
    """Semantic error for undefined or duplicate names."""

    pass
