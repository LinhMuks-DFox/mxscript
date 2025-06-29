from __future__ import annotations

from typing import Dict

from ..lexer import TokenStream
from ..errors import SyntaxErrorWithPos
from .ast import (
    BinaryOp,
    ExprStmt,
    ImportStmt,
    FunctionCall,
    Identifier,
    Integer,
    String,
    LetStmt,
    Program,
    Block,
    Parameter,
    FuncSig,
    FuncDef,
    ForeignFuncDecl,
    UnaryOp,
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
    '..': 5,
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
        if tok.tk_type == 'ANNOTATION':
            annotation = self.parse_annotation()
            next_tok = self.stream.peek()
            if next_tok.tk_type == 'KEYWORD' and next_tok.value == 'func':
                return self.parse_func_def(annotation)
            else:
                raise SyntaxErrorWithPos(
                    'Annotation only supported before functions',
                    next_tok,
                )
        if tok.tk_type == 'KEYWORD' and tok.value in ('public', 'private'):
            self.stream.next()
            tok = self.stream.peek()
        if tok.tk_type == 'KEYWORD' and tok.value == 'import':
            return self.parse_import()
        if tok.tk_type == 'KEYWORD' and tok.value == 'let':
            return self.parse_let()
        if tok.tk_type == 'KEYWORD' and tok.value in ('static', 'dynamic'):
            return self.parse_binding(tok.value == 'static')
        if tok.tk_type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for_in()
        if tok.tk_type == 'KEYWORD' and tok.value == 'raise':
            return self.parse_raise_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'return':
            return self.parse_return_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'func':
            return self.parse_func_def()
        if tok.tk_type == 'OPERATOR' and tok.value == '{':
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self.stream.expect('OPERATOR', ';')
            return ExprStmt(expr)

    def parse_annotation(self):
        self.stream.expect('ANNOTATION', '@@')
        name = self.stream.expect('IDENTIFIER').value
        args = {}
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '(':
            self.stream.next()
            key = self.stream.expect('IDENTIFIER').value
            self.stream.expect('OPERATOR', '=')
            val_tok = self.stream.expect('STRING')
            args[key] = val_tok.value
            self.stream.expect('OPERATOR', ')')
        return {"name": name, **args}

    def parse_let(self) -> LetStmt:
        self.stream.expect('KEYWORD', 'let')
        # optional 'mut' ignored for now
        name = self.stream.expect('IDENTIFIER').value
        self.stream.expect('OPERATOR', '=')
        value = self.parse_expression()
        self.stream.expect('OPERATOR', ';')
        return LetStmt(name, value)

    def parse_binding(self, is_static: bool):
        self.stream.next()  # consume 'static' or 'dynamic'
        self.stream.expect('KEYWORD', 'let')
        name = self.stream.expect('IDENTIFIER').value
        self.stream.expect('OPERATOR', '=')
        value = self.parse_expression()
        self.stream.expect('OPERATOR', ';')
        from .ast import BindingStmt
        return BindingStmt(name, value, is_static)

    def parse_for_in(self):
        self.stream.expect('KEYWORD', 'for')
        is_mut = False
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'mut':
            self.stream.next()
            is_mut = True
        var = self.stream.expect('IDENTIFIER').value
        self.stream.expect('KEYWORD', 'in')
        iterable = self.parse_expression()
        body = self.parse_block()
        from .ast import ForInStmt
        return ForInStmt(var, iterable, body, is_mut)

    def parse_raise_stmt(self):
        self.stream.expect('KEYWORD', 'raise')
        expr = self.parse_expression()
        self.stream.expect('OPERATOR', ';')
        from .ast import RaiseStmt
        return RaiseStmt(expr)

    def parse_return_stmt(self):
        self.stream.expect('KEYWORD', 'return')
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ';'):
            value = self.parse_expression()
        else:
            value = None
        self.stream.expect('OPERATOR', ';')
        from .ast import ReturnStmt
        return ReturnStmt(value)

    def parse_match_expr(self):
        self.stream.expect('KEYWORD', 'match')
        self.stream.expect('OPERATOR', '(')
        value = self.parse_expression()
        self.stream.expect('OPERATOR', ')')
        self.stream.expect('OPERATOR', '{')
        cases = []
        from .ast import MatchExpr, MatchCase
        while self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'case':
            self.stream.next()
            name = self.stream.expect('IDENTIFIER').value
            self.stream.expect('OPERATOR', ':')
            type_name = self.parse_type_spec()
            self.stream.expect('OPERATOR', '=>')
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '{':
                body = self.parse_block()
            else:
                body = self.parse_expression()
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                self.stream.next()
            cases.append(MatchCase(name, type_name, body))
        self.stream.expect('OPERATOR', '}')
        return MatchExpr(value, cases)

    def parse_import(self) -> ImportStmt:
        """Parse an import statement."""
        self.stream.expect('KEYWORD', 'import')
        parts = [self.stream.expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '.':
            self.stream.next()
            parts.append(self.stream.expect('IDENTIFIER').value)
        module = '.'.join(parts)
        alias = None
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'as':
            self.stream.next()
            alias = self.stream.expect('IDENTIFIER').value
        self.stream.expect('OPERATOR', ';')
        return ImportStmt(module, alias)

    def parse_expression(self, precedence: int = 1):
        expr = self.parse_unary()
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

    def parse_unary(self):
        tok = self.stream.peek()
        if tok.tk_type == 'OPERATOR' and tok.value in ('+', '-', '!'):
            self.stream.next()
            operand = self.parse_unary()
            return UnaryOp(tok.value, operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.stream.peek()
        if tok.tk_type == 'INTEGER':
            self.stream.next()
            return Integer(int(tok.value))
        if tok.tk_type == 'STRING':
            self.stream.next()
            return String(tok.value)
        if tok.tk_type == 'KEYWORD' and tok.value == 'raise':
            self.stream.next()
            expr = self.parse_expression()
            from .ast import RaiseExpr
            return RaiseExpr(expr)
        if tok.tk_type == 'KEYWORD' and tok.value == 'match':
            return self.parse_match_expr()
        if tok.tk_type == 'IDENTIFIER':
            self.stream.next()
            parts = [tok.value]
            while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '.':
                self.stream.next()
                parts.append(self.stream.expect('IDENTIFIER').value)
            name = '.'.join(parts)
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '(':
                self.stream.next()
                args = []
                if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
                    args.append(self.parse_expression())
                    while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                        self.stream.next()
                        args.append(self.parse_expression())
                self.stream.expect('OPERATOR', ')')
                return FunctionCall(name, args)
            return Identifier(name)
        if tok.tk_type == 'OPERATOR' and tok.value == '(':
            self.stream.next()
            expr = self.parse_expression()
            self.stream.expect('OPERATOR', ')')
            return expr
        raise SyntaxErrorWithPos(f'Unexpected token {tok.tk_type}', tok)

    # ------------------------------------------------------------------
    # New parsing rules for functions and blocks
    def parse_func_def(self, annotation=None):
        self.stream.expect('KEYWORD', 'func')
        name = self.stream.expect('IDENTIFIER').value
        sig = self.parse_func_sig()
        if annotation and annotation.get('name') == 'foreign':
            self.stream.expect('OPERATOR', ';')
            c_name = annotation.get('c_name')
            return ForeignFuncDecl(name, sig, c_name)
        body = self.parse_block()
        return FuncDef(name, sig, body)

    def parse_func_sig(self) -> FuncSig:
        self.stream.expect('OPERATOR', '(')
        params: list[Parameter] = []
        var_arg = False
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '...':
                self.stream.next()
                var_arg = True
            else:
                params.append(self.parse_param())
                while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                    # check for vararg
                    if self.stream.peek(1) and self.stream.peek(1).tk_type == 'OPERATOR' and self.stream.peek(1).value == '...':
                        self.stream.next()  # consume ','
                        self.stream.next()  # consume '...'
                        var_arg = True
                        break
                    self.stream.next()
                    params.append(self.parse_param())
        self.stream.expect('OPERATOR', ')')
        return_type = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '->':
            self.stream.next()
            return_type = self.parse_type_spec()
        return FuncSig(params, return_type, var_arg)

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
        parts = [self._parse_single_type_spec()]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '|':
            self.stream.next()
            parts.append(self._parse_single_type_spec())
        return ' | '.join(parts)

    def _parse_single_type_spec(self) -> str:

        tok = self.stream.peek()
        if tok.tk_type == 'KEYWORD' and tok.value == 'nil':
            self.stream.next()
            parts = ['nil']
        else:
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
