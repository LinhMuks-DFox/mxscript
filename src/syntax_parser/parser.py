from __future__ import annotations

from typing import Dict

from ..lexer import TokenStream
from .ast import (
    BinaryOp,
    ExprStmt,
    Identifier,
    Integer,
    LetStmt,
    Program,
)

BINARY_PRECEDENCE: Dict[str, int] = {
    '||': 1,
    '&&': 2,
    '==': 3,
    '!=': 3,
    '>=': 4,
    '<=': 4,
    '>': 4,
    '<': 4,
    '+': 5,
    '-': 5,
    '*': 6,
    '/': 6,
    '%': 6,
}


class Parser:
    """Very small recursive descent parser building an AST."""

    def __init__(self, stream: TokenStream) -> None:
        self.stream = stream

    def parse(self) -> Program:
        statements = []
        while self.stream.peek() and self.stream.peek().tk_type != 'EOF':
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        tok = self.stream.peek()
        if tok.tk_type == 'KEYWORD' and tok.value == 'let':
            return self.parse_let()
        else:
            expr = self.parse_expression()
            self.stream.expect('OPERATOR', ';')
            return ExprStmt(expr)

    def parse_let(self) -> LetStmt:
        self.stream.expect('KEYWORD', 'let')
        # optional 'mut' ignored for now
        name = self.stream.expect('IDENTIFIER').value
        self.stream.expect('OPERATOR', '=')
        value = self.parse_expression()
        self.stream.expect('OPERATOR', ';')
        return LetStmt(name, value)

    def parse_expression(self, precedence: int = 1):
        expr = self.parse_primary()
        while True:
            tok = self.stream.peek()
            if (
                tok
                and tok.tk_type == 'OPERATOR'
                and tok.value in BINARY_PRECEDENCE
                and BINARY_PRECEDENCE[tok.value] >= precedence
            ):
                op = tok.value
                self.stream.next()
                right = self.parse_expression(BINARY_PRECEDENCE[op] + 1)
                expr = BinaryOp(expr, op, right)
            else:
                break
        return expr

    def parse_primary(self):
        tok = self.stream.peek()
        if tok.tk_type == 'INTEGER':
            self.stream.next()
            return Integer(int(tok.value))
        if tok.tk_type == 'IDENTIFIER':
            self.stream.next()
            return Identifier(tok.value)
        if tok.tk_type == 'OPERATOR' and tok.value == '(':
            self.stream.next()
            expr = self.parse_expression()
            self.stream.expect('OPERATOR', ')')
            return expr
        raise SyntaxError(f'Unexpected token {tok}')
