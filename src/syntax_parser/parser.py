from __future__ import annotations

from typing import Dict, Any

from .expression_parser import ExpressionParserMixin, BINARY_PRECEDENCE
from .definition_parser import DefinitionParserMixin

from ..frontend import TokenStream
from ..frontend.tokens import TokenType
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

    def _expect(self, tk_type: TokenType | str, value: str | None = None):
        token = self.stream.next()
        if token is None:
            token = self.stream.tokens[-1]
            loc = self._get_location(token)
            name = tk_type.name if isinstance(tk_type, TokenType) else tk_type
            raise SyntaxError(f"Expected {name}", loc)
        expected_match = token.type == tk_type if isinstance(tk_type, TokenType) else token.type.name == tk_type
        if not expected_match or (value is not None and token.value != value):
            name = tk_type.name if isinstance(tk_type, TokenType) else tk_type
            msg = f"Expected {name} '{value}'" if value else f"Expected {name}"
            loc = self._get_location(token)
            raise SyntaxError(msg, loc)
        return token

    def parse(self) -> Program:
        statements = []
        while self.stream.peek() and self.stream.peek().type != TokenType.EOF:
            statements.append(self.parse_statement())
        start_token = statements[0].loc if statements else self.stream.tokens[0]
        return Program(statements, loc=start_token)

    def parse_statement(self):
        tok = self.stream.peek()
        if tok.type in (TokenType.PUBLIC, TokenType.PRIVATE):
            self.stream.next()
            if (
                self.stream.peek().type == TokenType.COLON
            ):
                self.stream.next()

            return self.parse_statement()
        if tok.type == TokenType.ANNOTATION:
            annotation = self.parse_annotation()
            next_tok = self.stream.peek()
            if next_tok.type == TokenType.FUNC:
                return self.parse_func_def(annotation)
            if next_tok.type == TokenType.CLASS:
                return self.parse_class_def(annotation)
            if next_tok.type == TokenType.INTERFACE:
                return self.parse_interface_def(annotation)
            raise SyntaxError(
                'Annotation only supported before functions or classes',
                self._get_location(next_tok),
            )
        if tok.type == TokenType.IMPORT:
            return self.parse_import()
        if tok.type == TokenType.LET:
            return self.parse_let()
        if tok.type in (TokenType.STATIC, TokenType.DYNAMIC):
            return self.parse_binding(tok.type == TokenType.STATIC)
        if tok.type == TokenType.FOR:
            return self.parse_for_in_stmt()
        if tok.type == TokenType.LOOP:
            return self.parse_loop_stmt()
        if tok.type == TokenType.UNTIL:
            return self.parse_until_stmt()
        if tok.type == TokenType.DO:
            return self.parse_do_until_stmt()
        if tok.type == TokenType.BREAK:
            return self.parse_break_stmt()
        if tok.type == TokenType.CONTINUE:
            return self.parse_continue_stmt()
        if tok.type == TokenType.IF:
            return self.parse_if_stmt()
        if tok.type == TokenType.RAISE:
            return self.parse_raise_stmt()
        if tok.type == TokenType.RETURN:
            return self.parse_return_stmt()
        if tok.type == TokenType.TILDE:
            return self.parse_destructor_def()
        if tok.type == TokenType.FUNC:
            return self.parse_func_def()
        if tok.type == TokenType.CLASS:
            return self.parse_class_def()
        if tok.type == TokenType.INTERFACE:
            return self.parse_interface_def()
        if tok.type == TokenType.LBRACE:
            return self.parse_block()
        else:
            expr = self.parse_expression()
            self._expect(TokenType.SEMICOLON)
            return ExprStmt(expr)

    def parse_annotation(self):
        start_tok = self._expect(TokenType.ANNOTATION, '@@')
        name = self._expect(TokenType.IDENTIFIER).value
        if name == "template":
            next_tok = self.stream.peek()
            if not next_tok or next_tok.type != TokenType.LPAREN:
                loc = self._get_location(next_tok or start_tok)
                raise SyntaxError("@@template must be followed by parentheses", loc)
            params = self.parse_template_params(allow_angles=False)
            return {"name": name, "params": params}
        args: Dict[str, Any] = {}
        if self.stream.peek().type == TokenType.LPAREN:
            self.stream.next()
            while True:
                key = self._expect(TokenType.IDENTIFIER).value
                self._expect(TokenType.ASSIGN)
                if key == "argc":
                    val_tok = self._expect(TokenType.INTEGER)
                    args[key] = int(val_tok.value)
                else:
                    val_tok = self._expect(TokenType.STRING)
                    args[key] = val_tok.value
                if self.stream.peek().type == TokenType.COMMA:
                    self.stream.next()
                    continue
                break
            self._expect(TokenType.RPAREN)
        return {"name": name, **args}

    def parse_template_params(self, *, allow_angles: bool = True) -> list[str]:
        params: list[str] = []
        if self.stream.peek().type in (TokenType.LPAREN, TokenType.LESS):
            start = self.stream.next()
            if start.type == TokenType.LESS and not allow_angles:
                loc = self._get_location(start)
                raise SyntaxError("Template parameters must use parentheses", loc)
            end = TokenType.RPAREN if start.type == TokenType.LPAREN else TokenType.GREATER
            while True:
                name = self._expect(TokenType.IDENTIFIER).value
                if self.stream.peek().type == TokenType.ASSIGN:
                    self.stream.next()
                    typ = self.parse_type_spec()
                    name = f"{name}={typ}"
                params.append(name)
                if self.stream.peek().type == TokenType.COMMA:
                    self.stream.next()
                    continue
                break
            self._expect(end)
        return params

    def parse_let(self) -> LetStmt:
        start = self._expect(TokenType.LET)
        is_mut = False
        if self.stream.peek().type == TokenType.MUT:
            self.stream.next()
            is_mut = True
        names = [self._expect(TokenType.IDENTIFIER).value]
        while self.stream.peek().type == TokenType.COMMA:
            self.stream.next()
            names.append(self._expect(TokenType.IDENTIFIER).value)
        type_name = None
        if self.stream.peek().type == TokenType.COLON:
            self.stream.next()
            type_name = self.parse_type_spec()
        value = None
        if self.stream.peek().type == TokenType.ASSIGN:
            self.stream.next()
            value = self.parse_expression()
        self._expect(TokenType.SEMICOLON)
        return LetStmt(names, value, type_name, is_mut, loc=start)

    def parse_binding(self, is_static: bool):
        start = self.stream.next()  # consume 'static' or 'dynamic'
        self._expect(TokenType.LET)
        name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self._expect(TokenType.SEMICOLON)
        from .ast import BindingStmt
        return BindingStmt(name, value, is_static, loc=start)

    def parse_for_in_stmt(self):
        start = self._expect(TokenType.FOR)
        is_mut = False
        if self.stream.peek().type == TokenType.MUT:
            self.stream.next()
            is_mut = True
        var = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        from .ast import ForInStmt
        return ForInStmt(var, iterable, body, is_mut, loc=start)

    def parse_loop_stmt(self):
        start = self._expect(TokenType.LOOP)
        body = self.parse_block()
        from .ast import LoopStmt
        return LoopStmt(body, loc=start)

    def parse_until_stmt(self):
        start = self._expect(TokenType.UNTIL)
        self._expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self._expect(TokenType.RPAREN)
        body = self.parse_block()
        from .ast import UntilStmt
        return UntilStmt(condition, body, loc=start)

    def parse_do_until_stmt(self):
        start = self._expect(TokenType.DO)
        body = self.parse_block()
        self._expect(TokenType.UNTIL)
        self._expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.SEMICOLON)
        from .ast import DoUntilStmt
        return DoUntilStmt(body, condition, loc=start)

    def parse_break_stmt(self):
        start = self._expect(TokenType.BREAK)
        self._expect(TokenType.SEMICOLON)
        from .ast import BreakStmt
        return BreakStmt(loc=start)

    def parse_continue_stmt(self):
        start = self._expect(TokenType.CONTINUE)
        self._expect(TokenType.SEMICOLON)
        from .ast import ContinueStmt
        return ContinueStmt(loc=start)

    def parse_if_stmt(self) -> IfStmt:
        start = self._expect(TokenType.IF)
        condition = self.parse_expression()
        then_block = self.parse_block()
        else_block = None
        if self.stream.peek().type == TokenType.ELSE:
            self.stream.next()
            if self.stream.peek().type == TokenType.IF:
                else_block = self.parse_if_stmt()
            else:
                else_block = self.parse_block()
        return IfStmt(condition, then_block, else_block, loc=start)

    def parse_raise_stmt(self):
        start = self._expect(TokenType.RAISE)
        expr = self.parse_expression()
        self._expect(TokenType.SEMICOLON)
        from .ast import RaiseStmt
        return RaiseStmt(expr, loc=start)

    def parse_return_stmt(self):
        start = self._expect(TokenType.RETURN)
        if not (self.stream.peek().type == TokenType.SEMICOLON):
            value = self.parse_expression()
        else:
            value = None
        self._expect(TokenType.SEMICOLON)
        from .ast import ReturnStmt
        return ReturnStmt(value, loc=start)


    def parse_match_expr(self):
        start_kw = self._expect(TokenType.MATCH)
        self._expect(TokenType.LPAREN)
        value = self.parse_expression()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.LBRACE)
        cases = []
        from .ast import MatchExpr, MatchCase
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

    def parse_import(self) -> ImportStmt:
        """Parse an import statement."""
        start = self._expect(TokenType.IMPORT)
        parts = [self._expect(TokenType.IDENTIFIER).value]
        while self.stream.peek().type == TokenType.DOT:
            self.stream.next()
            parts.append(self._expect(TokenType.IDENTIFIER).value)
        module = '.'.join(parts)
        alias = None
        if self.stream.peek().type == TokenType.AS:
            self.stream.next()
            alias = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.SEMICOLON)
        return ImportStmt(module, alias, loc=start)

