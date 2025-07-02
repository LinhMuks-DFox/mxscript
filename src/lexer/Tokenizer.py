"""Simple tokenizer for the MxScript language."""

from __future__ import annotations

from typing import List

from .Token import Token


KEYWORDS = {
    "import",
    "as",
    "static",
    "dynamic",
    "let",
    "mut",
    "func",
    "struct",
    "class",
    "interface",
    "type",
    "enum",
    "public",
    "private",
    "operator",
    "override",
    "if",
    "else",
    "for",
    "in",
    "loop",
    "do",
    "until",
    "break",
    "continue",
    "return",
    "raise",
    "match",
    "case",
    "nil",
    "@@",  # for annotations
}


OPERATORS = {
    "==",
    "!=",
    ">=",
    "<=",
    "+=",
    "-=",
    "*=",
    "/=",
    "&&",
    "||",
    "->",
    "=>",
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    ">",
    "<",
    "!",
    "?",
    "~",
    ".",
    ",",
    ":",
    ";",
    "..",
    "(",")",
    "{",
    "}",
    "[",
    "]",
    "...",
}


class Tokenizer:
    """Converts source text into a stream of :class:`Token` objects."""

    def __init__(self, source: str) -> None:
        self.source = source

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        line = 1
        col = 1
        length = len(self.source)

        def current_char() -> str:
            return self.source[i] if i < length else ""

        while i < length:
            ch = current_char()

            # Whitespace handling
            if ch in " \t\r":
                i += 1
                col += 1
                continue
            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue

            # Comments: '#' for single-line, '!##!' ... '!##!' and '!#' ... '#!' for multi-line
            if ch == "#":
                start_line, start_col = line, col
                i += 1
                col += 1
                while i < length and self.source[i] != "\n":
                    i += 1
                    col += 1
                tokens.append(Token("COMMENT", "", start_line, start_col))
                continue

            if self.source.startswith("!##!", i):
                start_line, start_col = line, col
                i += 4
                col += 4
                while i < length and not self.source.startswith("!##!", i):
                    if self.source[i] == "\n":
                        line += 1
                        col = 1
                        i += 1
                        continue
                    i += 1
                    col += 1
                if i < length:
                    i += 4
                    col += 4
                tokens.append(Token("COMMENT", "", start_line, start_col))
                continue

            if self.source.startswith("!#", i):
                start_line, start_col = line, col
                i += 2
                col += 2
                while i < length and not self.source.startswith("#!", i):
                    if self.source[i] == "\n":
                        line += 1
                        col = 1
                        i += 1
                        continue
                    i += 1
                    col += 1
                if i < length:
                    i += 2
                    col += 2
                tokens.append(Token("COMMENT", "", start_line, start_col))
                continue

            # Annotation token @@foo
            if ch == "@" and i + 1 < length and self.source[i + 1] == "@":
                tokens.append(Token("ANNOTATION", "@@", line, col))
                i += 2
                col += 2
                continue

            # String literal
            if ch == '"':
                start_line, start_col = line, col
                i += 1
                col += 1
                literal = ""
                while i < length and self.source[i] != '"':
                    if self.source[i] == "\\":
                        if i + 1 < length:
                            esc = self.source[i + 1]
                            if esc == "n":
                                literal += "\n"
                            elif esc == "t":
                                literal += "\t"
                            elif esc == '"':
                                literal += '"'
                            elif esc == "\\":
                                literal += "\\"
                            else:
                                literal += esc
                            i += 2
                            col += 2
                            continue
                    if self.source[i] == "\n":
                        line += 1
                        col = 1
                    else:
                        col += 1
                    literal += self.source[i]
                    i += 1
                i += 1  # consume closing quote
                col += 1
                tokens.append(Token("STRING", literal, start_line, start_col))
                continue

            # Numbers
            if ch.isdigit():
                start_line, start_col = line, col
                num = ch
                i += 1
                col += 1
                while i < length and self.source[i].isdigit():
                    num += self.source[i]
                    i += 1
                    col += 1
                if (
                    i < length
                    and self.source[i] == "."
                    and i + 1 < length
                    and self.source[i + 1].isdigit()
                ):
                    num += "."
                    i += 1
                    col += 1
                    while i < length and self.source[i].isdigit():
                        num += self.source[i]
                        i += 1
                        col += 1
                    tokens.append(Token("FLOAT", num, start_line, start_col))
                else:
                    tokens.append(Token("INTEGER", num, start_line, start_col))
                continue

            # Identifier or keyword
            if ch.isalpha() or ch == "_":
                start_line, start_col = line, col
                ident = ch
                i += 1
                col += 1
                while i < length and (self.source[i].isalnum() or self.source[i] == "_"):
                    ident += self.source[i]
                    i += 1
                    col += 1
                tk_type = "KEYWORD" if ident in KEYWORDS else "IDENTIFIER"
                tokens.append(Token(tk_type, ident, start_line, start_col))
                continue

            # Operators and punctuation - match longest first
            matched = False
            for op in sorted(OPERATORS, key=len, reverse=True):
                if self.source.startswith(op, i):
                    tokens.append(Token("OPERATOR", op, line, col))
                    i += len(op)
                    col += len(op)
                    matched = True
                    break
            if matched:
                continue

            # Unknown characters
            tokens.append(Token("UNKNOWN", ch, line, col))
            i += 1
            col += 1

        tokens.append(Token("EOF", "", line, col))
        return tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function returning a list of tokens."""

    return Tokenizer(source).tokenize()

