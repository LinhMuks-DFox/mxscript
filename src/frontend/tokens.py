from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Generic token types
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    COMMENT = auto()
    EOF = auto()
    UNKNOWN = auto()
    ANNOTATION = auto()

    # Keywords
    IMPORT = auto()
    AS = auto()
    STATIC = auto()
    DYNAMIC = auto()
    LET = auto()
    MUT = auto()
    FUNC = auto()
    STRUCT = auto()
    CLASS = auto()
    INTERFACE = auto()
    TYPE = auto()
    ENUM = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    OPERATOR_KW = auto()
    OVERRIDE = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    IN = auto()
    LOOP = auto()
    DO = auto()
    UNTIL = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    RAISE = auto()
    MATCH = auto()
    CASE = auto()
    NIL = auto()

    # Operators and punctuation
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQEQ = auto()
    NEQ = auto()
    GE = auto()
    LE = auto()
    GREATER = auto()
    LESS = auto()
    PLUS_EQ = auto()
    MINUS_EQ = auto()
    STAR_EQ = auto()
    SLASH_EQ = auto()
    AND_AND = auto()
    OR_OR = auto()
    ARROW = auto()
    FAT_ARROW = auto()
    DOT = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    RANGE = auto()
    ELLIPSIS = auto()
    QUESTION = auto()
    NOT = auto()
    TILDE = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    @property
    def tk_type(self) -> str:
        """Compatibility alias matching the old lexer attribute."""
        return self.type.name

    @property
    def col(self) -> int:
        """Compatibility alias for ``column``."""
        return self.column


KEYWORDS = {
    "import": TokenType.IMPORT,
    "as": TokenType.AS,
    "static": TokenType.STATIC,
    "dynamic": TokenType.DYNAMIC,
    "let": TokenType.LET,
    "mut": TokenType.MUT,
    "func": TokenType.FUNC,
    "struct": TokenType.STRUCT,
    "class": TokenType.CLASS,
    "interface": TokenType.INTERFACE,
    "type": TokenType.TYPE,
    "enum": TokenType.ENUM,
    "public": TokenType.PUBLIC,
    "private": TokenType.PRIVATE,
    "operator": TokenType.OPERATOR_KW,
    "override": TokenType.OVERRIDE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "loop": TokenType.LOOP,
    "do": TokenType.DO,
    "until": TokenType.UNTIL,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return": TokenType.RETURN,
    "raise": TokenType.RAISE,
    "match": TokenType.MATCH,
    "case": TokenType.CASE,
    "nil": TokenType.NIL,
}


OPERATORS = {
    "==": TokenType.EQEQ,
    "!=": TokenType.NEQ,
    ">=": TokenType.GE,
    "<=": TokenType.LE,
    "+=": TokenType.PLUS_EQ,
    "-=": TokenType.MINUS_EQ,
    "*=": TokenType.STAR_EQ,
    "/=": TokenType.SLASH_EQ,
    "&&": TokenType.AND_AND,
    "||": TokenType.OR_OR,
    "->": TokenType.ARROW,
    "=>": TokenType.FAT_ARROW,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "%": TokenType.PERCENT,
    "=": TokenType.ASSIGN,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    "!": TokenType.NOT,
    "?": TokenType.QUESTION,
    "~": TokenType.TILDE,
    ".": TokenType.DOT,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    ";": TokenType.SEMICOLON,
    "..": TokenType.RANGE,
    "...": TokenType.ELLIPSIS,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
}
