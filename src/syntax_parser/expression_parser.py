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
from ..frontend.tokens import TokenType

BINARY_PRECEDENCE = {
    TokenType.OR_OR: 1,
    TokenType.AND_AND: 2,
    TokenType.EQEQ: 3,
    TokenType.NEQ: 3,
    TokenType.GE: 4,
    TokenType.LE: 4,
    TokenType.GREATER: 4,
    TokenType.LESS: 4,
    TokenType.PLUS: 5,
    TokenType.MINUS: 5,
    TokenType.RANGE: 5,
    TokenType.STAR: 6,
    TokenType.SLASH: 6,
    TokenType.PERCENT: 6,
}


class ExpressionParserMixin:
    def parse_expression(self, precedence: int = 1):
        expr = self.parse_unary()
        while True:
            tok = self.stream.peek()
            if (
                tok
                and tok.type in BINARY_PRECEDENCE
                and BINARY_PRECEDENCE[tok.type] >= precedence
            ):
                op = tok.value
                self.stream.next()
                right = self.parse_expression(BINARY_PRECEDENCE[tok.type] + 1)
                expr = BinaryOp(expr, op, right)
            else:
                break

        if (
            precedence == 1
            and self.stream.peek().type == TokenType.ASSIGN
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
        if tok.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT):
            self.stream.next()
            operand = self.parse_unary()
            return UnaryOp(tok.value, operand)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.stream.peek()
        expr = None

        if tok.type == TokenType.INTEGER:
            self.stream.next()
            expr = Integer(int(tok.value), loc=tok)
        elif tok.type == TokenType.STRING:
            self.stream.next()
            expr = String(tok.value, loc=tok)
        elif tok.type == TokenType.RAISE:
            self.stream.next()
            expr_to_raise = self.parse_expression()
            expr = RaiseExpr(expr_to_raise, loc=tok)
        elif tok.type == TokenType.MATCH:
            expr = self.parse_match_expr()
        elif tok.type == TokenType.IDENTIFIER:
            self.stream.next()
            expr = Identifier(tok.value, loc=tok)
        elif tok.type == TokenType.LPAREN:
            self.stream.next()
            expr = self.parse_expression()
            self._expect(TokenType.RPAREN)
        else:
            raise SyntaxError(f'Unexpected token {tok.type}', self._get_location(tok))

        while True:
            peek_tok = self.stream.peek()
            if peek_tok.type == TokenType.DOT:
                dot_tok = self.stream.next()
                member_tok = self._expect(TokenType.IDENTIFIER)
                member_ident = Identifier(member_tok.value, loc=member_tok)
                expr = MemberAccess(expr, member_ident, loc=dot_tok)
                continue
            if peek_tok.type == TokenType.LPAREN:
                paren_tok = self.stream.next()
                args = []
                if not (self.stream.peek().type == TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.stream.peek().type == TokenType.COMMA:
                        self.stream.next()
                        args.append(self.parse_expression())
                self._expect(TokenType.RPAREN)
                name = self._flatten_member(expr)
                expr = FunctionCall(name, args, loc=paren_tok)
                continue
            break
        return expr

    def parse_match_expr(self):
        start_kw = self._expect(TokenType.MATCH)
        self._expect(TokenType.LPAREN)
        value = self.parse_expression()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.LBRACE)
        cases = []
        while self.stream.peek().type == TokenType.CASE:
            case_tok = self.stream.next()
            name = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            type_name = self.parse_type_spec()
            self._expect(TokenType.FAT_ARROW)
            if self.stream.peek().type == TokenType.LBRACE:
                body = self.parse_block()
            else:
                body = self.parse_expression()
            if self.stream.peek().type == TokenType.COMMA:
                self.stream.next()
            cases.append(MatchCase(name, type_name, body, loc=case_tok))
        self._expect(TokenType.RBRACE)
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
