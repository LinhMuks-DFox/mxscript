from __future__ import annotations

from .ast import (
    BinaryOp,
    Integer,
    String,
    UnaryOp,
    MemberAccess,
    Identifier,
    FunctionCall,
    MatchExpr,
    MatchCase,
    MemberAssign,
    RaiseExpr,
)
from ..errors import SyntaxError

BINARY_PRECEDENCE = {
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


class ExpressionParserMixin:
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

        if (
            precedence == 1
            and self.stream.peek().tk_type == 'OPERATOR'
            and self.stream.peek().value == '='
        ):
            assign_tok = self.stream.next()
            value = self.parse_expression()
            if isinstance(expr, MemberAccess):
                expr = MemberAssign(expr.object, expr.member, value, loc=assign_tok)
            else:
                from .ast import AssignExpr
                expr = AssignExpr(expr, value, loc=assign_tok)
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
        expr = None

        if tok.tk_type == 'INTEGER':
            self.stream.next()
            expr = Integer(int(tok.value), loc=tok)
        elif tok.tk_type == 'STRING':
            self.stream.next()
            expr = String(tok.value, loc=tok)
        elif tok.tk_type == 'KEYWORD' and tok.value == 'raise':
            self.stream.next()
            expr_to_raise = self.parse_expression()
            expr = RaiseExpr(expr_to_raise, loc=tok)
        elif tok.tk_type == 'KEYWORD' and tok.value == 'match':
            expr = self.parse_match_expr()
        elif tok.tk_type == 'IDENTIFIER':
            self.stream.next()
            expr = Identifier(tok.value, loc=tok)
        elif tok.tk_type == 'OPERATOR' and tok.value == '(':
            self.stream.next()
            expr = self.parse_expression()
            self._expect('OPERATOR', ')')
        else:
            raise SyntaxError(f'Unexpected token {tok.tk_type}', self._get_location(tok))

        while True:
            peek_tok = self.stream.peek()
            if peek_tok.tk_type == 'OPERATOR' and peek_tok.value == '.':
                dot_tok = self.stream.next()
                member_tok = self._expect('IDENTIFIER')
                member_ident = Identifier(member_tok.value, loc=member_tok)
                expr = MemberAccess(expr, member_ident, loc=dot_tok)
                continue
            if peek_tok.tk_type == 'OPERATOR' and peek_tok.value == '(':
                paren_tok = self.stream.next()
                args = []
                if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
                    args.append(self.parse_expression())
                    while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                        self.stream.next()
                        args.append(self.parse_expression())
                self._expect('OPERATOR', ')')
                name = self._flatten_member(expr)
                expr = FunctionCall(name, args, loc=paren_tok)
                continue
            break
        return expr

    def parse_match_expr(self):
        start_kw = self._expect('KEYWORD', 'match')
        self._expect('OPERATOR', '(')
        value = self.parse_expression()
        self._expect('OPERATOR', ')')
        self._expect('OPERATOR', '{')
        cases = []
        while self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'case':
            case_tok = self.stream.next()
            name = self._expect('IDENTIFIER').value
            self._expect('OPERATOR', ':')
            type_name = self.parse_type_spec()
            self._expect('OPERATOR', '=>')
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '{':
                body = self.parse_block()
            else:
                body = self.parse_expression()
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                self.stream.next()
            cases.append(MatchCase(name, type_name, body, loc=case_tok))
        self._expect('OPERATOR', '}')
        return MatchExpr(value, cases, loc=start_kw)

    def _flatten_member(self, expr) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        if isinstance(expr, MemberAccess):
            return f"{self._flatten_member(expr.object)}.{expr.member.name}"
        raise SyntaxError(
            "Invalid function call target",
            self._get_location(self.stream.peek()),
        )
