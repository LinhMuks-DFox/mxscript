from __future__ import annotations

from .ast import (
    Parameter,
    FuncSig,
    FuncDef,
    ForeignFuncDecl,
    ClassDef,
    InterfaceDef,
    FieldDef,
    AccessSpec,
    LetStmt,
    DestructorDef,
    ConstructorDef,
    Block,
    MethodDef,
    OperatorDef,
)
from ..frontend.tokens import TokenType


class DefinitionParserMixin:
    def parse_func_def(self, annotation=None):
        start = self._expect(TokenType.FUNC)
        name = self._expect(TokenType.IDENTIFIER).value
        sig = self.parse_func_sig()
        if annotation and annotation.get('name') == 'foreign':
            self._expect(TokenType.SEMICOLON)
            c_name = annotation.get('c_name')
            return ForeignFuncDecl(name, sig, c_name, loc=start)
        body = self.parse_block()
        return FuncDef(name, sig, body, loc=start)

    def parse_class_def(self):
        start = self._expect(TokenType.CLASS)
        name = self._expect(TokenType.IDENTIFIER).value
        generic_params = None
        if self.stream.peek().type == TokenType.LESS:
            generic_params = self.parse_generic_params()
        super_class = None
        if self.stream.peek().type == TokenType.COLON:
            self.stream.next()
            super_class = self.parse_type_spec()
        self._expect(TokenType.LBRACE)
        members = []
        while self.stream.peek() and not (
            self.stream.peek().type == TokenType.RBRACE
        ):
            members.append(self.parse_class_member(name))
        self._expect(TokenType.RBRACE)
        return ClassDef(name, Block(members), generic_params, super_class, loc=start)

    def parse_interface_def(self):
        start = self._expect(TokenType.INTERFACE)
        name = self._expect(TokenType.IDENTIFIER).value
        generic_params = None
        if self.stream.peek().type == TokenType.LESS:
            generic_params = self.parse_generic_params()
        super_iface = None
        if self.stream.peek().type == TokenType.COLON:
            self.stream.next()
            super_iface = self.parse_type_spec()
        self._expect(TokenType.LBRACE)
        members = []
        while self.stream.peek() and not (
            self.stream.peek().type == TokenType.RBRACE
        ):
            members.append(self.parse_interface_member())
        self._expect(TokenType.RBRACE)
        return InterfaceDef(name, Block(members), generic_params, [super_iface] if super_iface else None, loc=start)

    def parse_class_member(self, class_name: str):
        tok = self.stream.peek()
        if tok.type in (TokenType.PUBLIC, TokenType.PRIVATE):
            level = tok.value
            self.stream.next()
            self._expect(TokenType.COLON)
            return AccessSpec(level, loc=tok)
        if tok.type == TokenType.STATIC:
            self.stream.next()
            next_tok = self.stream.peek()
            if next_tok.type == TokenType.LET:
                return self.parse_field_def(is_static=True)
            else:
                return self.parse_class_member(class_name)
        if tok.type == TokenType.TILDE:
            return self.parse_destructor_def()
        if tok.type == TokenType.IDENTIFIER and tok.value == class_name:
            return self.parse_constructor_def()
        if tok.type == TokenType.OPERATOR_KW:
            return self.parse_operator_def()
        if tok.type in (TokenType.OVERRIDE, TokenType.FUNC):
            return self.parse_method_def()
        if tok.type == TokenType.LET:
            return self.parse_field_def(is_static=False)
        return self.parse_statement()

    def parse_field_def(self, *, is_static: bool = False):
        stmt = self.parse_let()
        assert len(stmt.names) == 1
        return FieldDef(is_static, stmt.is_mut, stmt.names[0], stmt.type_name, stmt.value, loc=stmt.loc)

    def parse_destructor_def(self):
        start = self._expect(TokenType.TILDE)
        self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.LPAREN)
        self._expect(TokenType.RPAREN)
        super_call = None
        if self.stream.peek().type == TokenType.COLON:
            self.stream.next()
            self._expect(TokenType.TILDE)
            super_call = self._expect(TokenType.IDENTIFIER).value
        body = self.parse_block()
        return DestructorDef(body, super_call, loc=start)

    def parse_constructor_def(self):
        start_ident = self._expect(TokenType.IDENTIFIER)
        sig = self.parse_func_sig()
        super_call = None
        if self.stream.peek().type == TokenType.COLON:
            self.stream.next()
            super_name = self._expect(TokenType.IDENTIFIER).value
            args = self.parse_call_args()
            super_call = (super_name, args)
        body = self.parse_block()
        return ConstructorDef(sig, body, super_call, loc=start_ident)

    def parse_method_def(self):
        override = False
        if self.stream.peek().type == TokenType.OVERRIDE:
            self.stream.next()
            override = True
        start = self._expect(TokenType.FUNC)
        name = self._expect(TokenType.IDENTIFIER).value
        if self.stream.peek().type == TokenType.LESS:
            self.parse_generic_params()  # ignore for now
        sig = self.parse_func_sig()
        body = self.parse_block()
        return MethodDef(name, sig, body, override, loc=start)

    def parse_operator_def(self):
        override = False
        if self.stream.peek().type == TokenType.OVERRIDE:
            self.stream.next()
            override = True
        start = self._expect(TokenType.OPERATOR_KW)
        op_token = self.stream.next()
        sig = self.parse_func_sig()
        body = self.parse_block()
        return OperatorDef(op_token.value, sig, body, override, loc=start)

    def parse_interface_member(self):
        start = self._expect(TokenType.FUNC)
        name = self._expect(TokenType.IDENTIFIER).value
        if self.stream.peek().type == TokenType.LESS:
            self.parse_generic_params()
        sig = self.parse_func_sig()
        body = None
        if self.stream.peek().type == TokenType.LBRACE:
            body = self.parse_block()
        self._expect(TokenType.SEMICOLON)
        if body is None:
            body = Block([])
        return MethodDef(name, sig, body, False, loc=start)

    def parse_generic_params(self) -> list[str]:
        params = []
        self._expect(TokenType.LESS)
        params.append(self._expect(TokenType.IDENTIFIER).value)
        while self.stream.peek().type == TokenType.COMMA:
            self.stream.next()
            params.append(self._expect(TokenType.IDENTIFIER).value)
        self._expect(TokenType.GREATER)
        return params

    def parse_call_args(self) -> list:
        self._expect(TokenType.LPAREN)
        args = []
        if not (self.stream.peek().type == TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.stream.peek().type == TokenType.COMMA:
                self.stream.next()
                args.append(self.parse_expression())
        self._expect(TokenType.RPAREN)
        return args


    def parse_func_sig(self) -> FuncSig:
        start = self._expect(TokenType.LPAREN)
        params: list[Parameter] = []
        var_arg = False
        if not (self.stream.peek().type == TokenType.RPAREN):
            if self.stream.peek().type == TokenType.ELLIPSIS:
                self.stream.next()
                var_arg = True
            else:
                params.append(self.parse_param())
                while self.stream.peek().type == TokenType.COMMA:
                    if self.stream.peek(1) and self.stream.peek(1).type == TokenType.ELLIPSIS:
                        self.stream.next()
                        self.stream.next()
                        var_arg = True
                        break
                    self.stream.next()
                    params.append(self.parse_param())
        self._expect(TokenType.RPAREN)
        return_type = None
        if self.stream.peek().type == TokenType.ARROW:
            self.stream.next()
            return_type = self.parse_type_spec()
        return FuncSig(params, return_type, var_arg, loc=start)

    def parse_param(self) -> Parameter:
        names = [self._expect(TokenType.IDENTIFIER).value]
        while self.stream.peek().type == TokenType.COMMA:
            if self.stream.peek(1) and self.stream.peek(1).type == TokenType.IDENTIFIER:
                self.stream.next()
                names.append(self._expect(TokenType.IDENTIFIER).value)
            else:
                break
        self._expect(TokenType.COLON)
        type_name = self.parse_type_spec()
        default = None
        if self.stream.peek().type == TokenType.ASSIGN:
            self.stream.next()
            default = self.parse_expression()
        return Parameter(names, type_name, default)

    def parse_type_spec(self) -> str:
        # Union types using '|' are not yet supported by the tokenizer.
        return self._parse_single_type_spec()

    def _parse_single_type_spec(self) -> str:
        tok = self.stream.peek()
        if tok.type == TokenType.NIL:
            self.stream.next()
            parts = ['nil']
        else:
            parts = [self._expect(TokenType.IDENTIFIER).value]
        while self.stream.peek().type == TokenType.DOT:
            self.stream.next()
            parts.append(self._expect(TokenType.IDENTIFIER).value)
        typ = '.'.join(parts)
        while self.stream.peek().type == TokenType.STAR:
            self.stream.next()
            typ += '*'
        return typ

    def parse_block(self) -> Block:
        start = self._expect(TokenType.LBRACE)
        statements = []
        while self.stream.peek() and not (
            self.stream.peek().type == TokenType.RBRACE
        ):
            statements.append(self.parse_statement())
        self._expect(TokenType.RBRACE)
        return Block(statements, loc=start)
