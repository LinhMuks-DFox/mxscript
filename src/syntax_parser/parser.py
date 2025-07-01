from __future__ import annotations

from typing import Dict

from .expression_parser import ExpressionParserMixin, BINARY_PRECEDENCE
from .definition_parser import DefinitionParserMixin

from ..lexer import TokenStream
from ..errors import SourceLocation, SyntaxError
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
    ClassDef,
    DestructorDef,
    ForeignFuncDecl,
    UnaryOp,
    MemberAccess,
    MemberAssign,
    IfStmt,
)



class Parser(ExpressionParserMixin, DefinitionParserMixin):
    """Very small recursive descent parser building an AST."""

    def __init__(self, stream: TokenStream, *, source: str = "", filename: str = "<stdin>") -> None:
        self.stream = stream
        self.filename = filename
        self.source_lines = source.splitlines()

    # ------------------------------------------------------------------
    def _get_location(self, token) -> SourceLocation:
        line = token.line
        column = token.col
        source_line = self.source_lines[line - 1] if 0 <= line - 1 < len(self.source_lines) else ""
        return SourceLocation(self.filename, line, column, source_line)

    def _expect(self, tk_type: str, value: str | None = None):
        token = self.stream.next()
        if token is None:
            token = self.stream.tokens[-1]
            loc = self._get_location(token)
            raise SyntaxError(f"Expected {tk_type}", loc)
        if token.tk_type != tk_type or (value is not None and token.value != value):
            msg = f"Expected {tk_type} '{value}'" if value else f"Expected {tk_type}"
            loc = self._get_location(token)
            raise SyntaxError(msg, loc)
        return token

    def parse(self) -> Program:
        statements = []
        while self.stream.peek() and self.stream.peek().tk_type != 'EOF':
            statements.append(self.parse_statement())
        start_token = statements[0].loc if statements else self.stream.tokens[0]
        return Program(statements, loc=start_token)

    def parse_statement(self):
        tok = self.stream.peek()
        if tok.tk_type == 'KEYWORD' and tok.value in ('public', 'private'):
            self.stream.next()
            if (
                self.stream.peek().tk_type == 'OPERATOR'
                and self.stream.peek().value == ':'
            ):
                self.stream.next()

            return self.parse_statement()
        if tok.tk_type == 'ANNOTATION':
            annotation = self.parse_annotation()
            next_tok = self.stream.peek()
            if next_tok.tk_type == 'KEYWORD' and next_tok.value == 'func':
                return self.parse_func_def(annotation)
            else:
                raise SyntaxError(
                    'Annotation only supported before functions',
                    self._get_location(next_tok),
                )
        if tok.tk_type == 'KEYWORD' and tok.value == 'import':
            return self.parse_import()
        if tok.tk_type == 'KEYWORD' and tok.value == 'let':
            return self.parse_let()
        if tok.tk_type == 'KEYWORD' and tok.value in ('static', 'dynamic'):
            return self.parse_binding(tok.value == 'static')
        if tok.tk_type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for_in()
        if tok.tk_type == 'KEYWORD' and tok.value == 'loop':
            return self.parse_loop_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'until':
            return self.parse_until_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'do':
            return self.parse_do_until_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'raise':
            return self.parse_raise_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'return':
            return self.parse_return_stmt()
        if tok.tk_type == 'KEYWORD' and tok.value == 'func':
            if (
                self.stream.peek(1)
                and self.stream.peek(1).tk_type == 'OPERATOR'
                and self.stream.peek(1).value == '~'
            ):
                return self.parse_destructor_def()
            return self.parse_func_def()
        if tok.tk_type == 'KEYWORD' and tok.value == 'class':
            return self.parse_class_def()
        if tok.tk_type == 'OPERATOR' and tok.value == '{':
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self._expect('OPERATOR', ';')
            return ExprStmt(expr)

    def parse_annotation(self):
        start_tok = self._expect('ANNOTATION', '@@')
        name = self._expect('IDENTIFIER').value
        args = {}
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '(':
            self.stream.next()
            key = self._expect('IDENTIFIER').value
            self._expect('OPERATOR', '=')
            val_tok = self._expect('STRING')
            args[key] = val_tok.value
            self._expect('OPERATOR', ')')
        return {"name": name, **args}

    def parse_let(self) -> LetStmt:
        start = self._expect('KEYWORD', 'let')
        is_mut = False
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'mut':
            self.stream.next()
            is_mut = True
        name = self._expect('IDENTIFIER').value
        type_name = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ':':
            self.stream.next()
            type_name = self.parse_type_spec()
        self._expect('OPERATOR', '=')
        value = self.parse_expression()
        self._expect('OPERATOR', ';')
        return LetStmt(name, value, type_name, is_mut, loc=start)

    def parse_binding(self, is_static: bool):
        start = self.stream.next()  # consume 'static' or 'dynamic'
        self._expect('KEYWORD', 'let')
        name = self._expect('IDENTIFIER').value
        self._expect('OPERATOR', '=')
        value = self.parse_expression()
        self._expect('OPERATOR', ';')
        from .ast import BindingStmt
        return BindingStmt(name, value, is_static, loc=start)

    def parse_for_in(self):
        start = self._expect('KEYWORD', 'for')
        is_mut = False
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'mut':
            self.stream.next()
            is_mut = True
        var = self._expect('IDENTIFIER').value
        self._expect('KEYWORD', 'in')
        iterable = self.parse_expression()
        body = self.parse_block()
        from .ast import ForInStmt
        return ForInStmt(var, iterable, body, is_mut, loc=start)

    def parse_loop_stmt(self):
        start = self._expect('KEYWORD', 'loop')
        body = self.parse_block()
        from .ast import LoopStmt
        return LoopStmt(body, loc=start)

    def parse_until_stmt(self):
        start = self._expect('KEYWORD', 'until')
        self._expect('OPERATOR', '(')
        condition = self.parse_expression()
        self._expect('OPERATOR', ')')
        body = self.parse_block()
        from .ast import UntilStmt
        return UntilStmt(condition, body, loc=start)

    def parse_do_until_stmt(self):
        start = self._expect('KEYWORD', 'do')
        body = self.parse_block()
        self._expect('KEYWORD', 'until')
        self._expect('OPERATOR', '(')
        condition = self.parse_expression()
        self._expect('OPERATOR', ')')
        self._expect('OPERATOR', ';')
        from .ast import DoUntilStmt
        return DoUntilStmt(body, condition, loc=start)

    def parse_if_stmt(self) -> IfStmt:
        start = self._expect('KEYWORD', 'if')
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'else':
            self.stream.next()
            if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'if':
                else_block = self.parse_if_stmt()
            else:
                else_block = self.parse_block()
        return IfStmt(condition, then_block, else_block, loc=start)

    def parse_raise_stmt(self):
        start = self._expect('KEYWORD', 'raise')
        expr = self.parse_expression()
        self._expect('OPERATOR', ';')
        from .ast import RaiseStmt
        return RaiseStmt(expr, loc=start)

    def parse_return_stmt(self):
        start = self._expect('KEYWORD', 'return')
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ';'):
            value = self.parse_expression()
        else:
            value = None
        self._expect('OPERATOR', ';')
        from .ast import ReturnStmt
        return ReturnStmt(value, loc=start)

    def parse_match_expr(self):
        start_kw = self._expect('KEYWORD', 'match')
        self._expect('OPERATOR', '(')
        value = self.parse_expression()
        self._expect('OPERATOR', ')')
        self._expect('OPERATOR', '{')
        cases = []
        from .ast import MatchExpr, MatchCase
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

    def parse_import(self) -> ImportStmt:
        """Parse an import statement."""
        start = self._expect('KEYWORD', 'import')
        parts = [self._expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '.':
            self.stream.next()
            parts.append(self._expect('IDENTIFIER').value)
        module = '.'.join(parts)
        alias = None
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'as':
            self.stream.next()
            alias = self._expect('IDENTIFIER').value
        self._expect('OPERATOR', ';')
        return ImportStmt(module, alias, loc=start)

