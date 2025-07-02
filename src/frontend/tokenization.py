from __future__ import annotations

from typing import List

from .tokens import TokenType, Token, KEYWORDS, OPERATORS


class Tokenizer:
    """Converts source text into a stream of :class:`Token` objects."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.col = 1

    # ------------------------------------------------------------------
    def _peek(self) -> str:
        return self.source[self.index] if self.index < self.length else ""

    def _advance(self) -> str:
        ch = self._peek()
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    # ------------------------------------------------------------------
    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.index < self.length:
            ch = self._peek()

            # Skip whitespace
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "\n":
                self._advance()
                continue

            # Single line comment starting with '#'
            if ch == "#":
                start_line, start_col = self.line, self.col
                self._advance()
                while self.index < self.length and self._peek() != "\n":
                    self._advance()
                tokens.append(Token(TokenType.COMMENT, "", start_line, start_col))
                continue

            # Multi-line comments !##! ... !##! or !# ... #!
            if self.source.startswith("!##!", self.index):
                start_line, start_col = self.line, self.col
                self.index += 4
                self.col += 4
                while self.index < self.length and not self.source.startswith("!##!", self.index):
                    self._advance()
                if self.source.startswith("!##!", self.index):
                    self.index += 4
                    self.col += 4
                tokens.append(Token(TokenType.COMMENT, "", start_line, start_col))
                continue
            if self.source.startswith("!#", self.index):
                start_line, start_col = self.line, self.col
                self.index += 2
                self.col += 2
                while self.index < self.length and not self.source.startswith("#!", self.index):
                    self._advance()
                if self.source.startswith("#!", self.index):
                    self.index += 2
                    self.col += 2
                tokens.append(Token(TokenType.COMMENT, "", start_line, start_col))
                continue

            # Annotation token @@
            if ch == "@" and self.index + 1 < self.length and self.source[self.index + 1] == "@":
                tokens.append(Token(TokenType.ANNOTATION, "@@", self.line, self.col))
                self.index += 2
                self.col += 2
                continue

            # String literals
            if ch == '"':
                tokens.append(self._parse_string())
                continue

            # Numbers
            if ch.isdigit():
                tokens.append(self._parse_number())
                continue

            # Identifier or keyword
            if ch.isalpha() or ch == "_":
                tokens.append(self._parse_identifier())
                continue

            # Operators and punctuation
            matched = None
            for op in sorted(OPERATORS.keys(), key=len, reverse=True):
                if self.source.startswith(op, self.index):
                    matched = op
                    break
            if matched is not None:
                tokens.append(Token(OPERATORS[matched], matched, self.line, self.col))
                self.index += len(matched)
                self.col += len(matched)
                continue

            # Unknown characters
            tokens.append(Token(TokenType.UNKNOWN, ch, self.line, self.col))
            self._advance()

        tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return tokens

    # ------------------------------------------------------------------
    def _parse_string(self) -> Token:
        start_line, start_col = self.line, self.col
        self._advance()  # consume opening quote
        literal = ""
        escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            '"': '"',
        }
        while self.index < self.length and self._peek() != '"':
            ch = self._peek()
            if ch == "\\":
                self._advance()
                if self.index < self.length:
                    esc = self._advance()
                    literal += escape_map.get(esc, esc)
                continue
            literal += self._advance()
        if self._peek() == '"':
            self._advance()
        return Token(TokenType.STRING, literal, start_line, start_col)

    def _parse_number(self) -> Token:
        start_line, start_col = self.line, self.col
        num = self._advance()
        while self.index < self.length and self._peek().isdigit():
            num += self._advance()
        if (
            self.index < self.length
            and self._peek() == "."
            and self.index + 1 < self.length
            and self.source[self.index + 1].isdigit()
        ):
            num += self._advance()  # consume '.'
            while self.index < self.length and self._peek().isdigit():
                num += self._advance()
            return Token(TokenType.FLOAT, num, start_line, start_col)
        return Token(TokenType.INTEGER, num, start_line, start_col)

    def _parse_identifier(self) -> Token:
        start_line, start_col = self.line, self.col
        ident = self._advance()
        while self.index < self.length and (self._peek().isalnum() or self._peek() == "_"):
            ident += self._advance()
        tk_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(tk_type, ident, start_line, start_col)


def tokenize(source: str) -> List[Token]:
    return Tokenizer(source).tokenize()
