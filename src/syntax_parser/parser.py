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
    Block,
    Parameter,
    FuncSig,
    FuncDef,
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
        if tok.tk_type == 'KEYWORD' and tok.value == 'func':
            return self.parse_func_def()
        if tok.tk_type == 'OPERATOR' and tok.value == '{':
            return self.parse_block()
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

    # ------------------------------------------------------------------
    # New parsing rules for functions and blocks
    def parse_func_def(self) -> FuncDef:
        self.stream.expect('KEYWORD', 'func')
        name = self.stream.expect('IDENTIFIER').value
        sig = self.parse_func_sig()
        body = self.parse_block()
        return FuncDef(name, sig, body)

    def parse_func_sig(self) -> FuncSig:
        self.stream.expect('OPERATOR', '(')
        params: list[Parameter] = []
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
            params.append(self.parse_param())
            while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                self.stream.next()
                params.append(self.parse_param())
        self.stream.expect('OPERATOR', ')')
        return_type = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '->':
            self.stream.next()
            return_type = self.parse_type_spec()
        return FuncSig(params, return_type)

    def parse_param(self) -> Parameter:
        names = [self.stream.expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
            # look ahead to distinguish between identifier list and next param
            if self.stream.peek(1) and self.stream.peek(1).tk_type == 'IDENTIFIER':
                self.stream.next()
                names.append(self.stream.expect('IDENTIFIER').value)
            else:
                break
        self.stream.expect('OPERATOR', ':')
        type_name = self.parse_type_spec()
        return Parameter(names, type_name)

    def parse_type_spec(self) -> str:
        parts = [self.stream.expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '.':
            self.stream.next()
            parts.append(self.stream.expect('IDENTIFIER').value)
        return '.'.join(parts)

    def parse_block(self) -> Block:
        self.stream.expect('OPERATOR', '{')
        statements = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            statements.append(self.parse_statement())
        self.stream.expect('OPERATOR', '}')
        return Block(statements)
