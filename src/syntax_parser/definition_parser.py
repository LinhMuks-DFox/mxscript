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


class DefinitionParserMixin:
    def parse_func_def(self, annotation=None):
        start = self._expect('KEYWORD', 'func')
        name = self._expect('IDENTIFIER').value
        sig = self.parse_func_sig()
        if annotation and annotation.get('name') == 'foreign':
            self._expect('OPERATOR', ';')
            c_name = annotation.get('c_name')
            return ForeignFuncDecl(name, sig, c_name, loc=start)
        body = self.parse_block()
        return FuncDef(name, sig, body, loc=start)

    def parse_class_def(self):
        start = self._expect('KEYWORD', 'class')
        name = self._expect('IDENTIFIER').value
        generic_params = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '<':
            generic_params = self.parse_generic_params()
        super_class = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ':':
            self.stream.next()
            super_class = self.parse_type_spec()
        self._expect('OPERATOR', '{')
        members = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            members.append(self.parse_class_member(name))
        self._expect('OPERATOR', '}')
        return ClassDef(name, Block(members), generic_params, super_class, loc=start)

    def parse_interface_def(self):
        start = self._expect('KEYWORD', 'interface')
        name = self._expect('IDENTIFIER').value
        generic_params = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '<':
            generic_params = self.parse_generic_params()
        super_iface = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ':':
            self.stream.next()
            super_iface = self.parse_type_spec()
        self._expect('OPERATOR', '{')
        members = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            members.append(self.parse_interface_member())
        self._expect('OPERATOR', '}')
        return InterfaceDef(name, Block(members), generic_params, [super_iface] if super_iface else None, loc=start)

    def parse_class_member(self, class_name: str):
        tok = self.stream.peek()
        if tok.tk_type == 'KEYWORD' and tok.value in ('public', 'private'):
            level = tok.value
            self.stream.next()
            self._expect('OPERATOR', ':')
            return AccessSpec(level, loc=tok)
        if tok.tk_type == 'KEYWORD' and tok.value == 'static':
            self.stream.next()
            next_tok = self.stream.peek()
            if next_tok.tk_type == 'KEYWORD' and next_tok.value == 'let':
                return self.parse_field_def(is_static=True)
            else:
                return self.parse_class_member(class_name)
        if tok.tk_type == 'OPERATOR' and tok.value == '~':
            return self.parse_destructor_def()
        if tok.tk_type == 'IDENTIFIER' and tok.value == class_name:
            return self.parse_constructor_def()
        if tok.tk_type == 'KEYWORD' and tok.value == 'operator':
            return self.parse_operator_def()
        if tok.tk_type == 'KEYWORD' and tok.value in ('override', 'func'):
            return self.parse_method_def()
        if tok.tk_type == 'KEYWORD' and tok.value == 'let':
            return self.parse_field_def(is_static=False)
        return self.parse_statement()

    def parse_field_def(self, *, is_static: bool = False):
        stmt = self.parse_let()
        assert len(stmt.names) == 1
        return FieldDef(is_static, stmt.is_mut, stmt.names[0], stmt.type_name, stmt.value, loc=stmt.loc)

    def parse_destructor_def(self):
        start = self._expect('OPERATOR', '~')
        self._expect('IDENTIFIER')
        self._expect('OPERATOR', '(')
        self._expect('OPERATOR', ')')
        super_call = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ':':
            self.stream.next()
            self._expect('OPERATOR', '~')
            super_call = self._expect('IDENTIFIER').value
        body = self.parse_block()
        return DestructorDef(body, super_call, loc=start)

    def parse_constructor_def(self):
        start_ident = self._expect('IDENTIFIER')
        sig = self.parse_func_sig()
        super_call = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ':':
            self.stream.next()
            super_name = self._expect('IDENTIFIER').value
            args = self.parse_call_args()
            super_call = (super_name, args)
        body = self.parse_block()
        return ConstructorDef(sig, body, super_call, loc=start_ident)

    def parse_method_def(self):
        override = False
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'override':
            self.stream.next()
            override = True
        start = self._expect('KEYWORD', 'func')
        name = self._expect('IDENTIFIER').value
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '<':
            self.parse_generic_params()  # ignore for now
        sig = self.parse_func_sig()
        body = self.parse_block()
        return MethodDef(name, sig, body, override, loc=start)

    def parse_operator_def(self):
        override = False
        if self.stream.peek().tk_type == 'KEYWORD' and self.stream.peek().value == 'override':
            self.stream.next()
            override = True
        start = self._expect('KEYWORD', 'operator')
        op_token = self._expect('OPERATOR')
        sig = self.parse_func_sig()
        body = self.parse_block()
        return OperatorDef(op_token.value, sig, body, override, loc=start)

    def parse_interface_member(self):
        start = self._expect('KEYWORD', 'func')
        name = self._expect('IDENTIFIER').value
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '<':
            self.parse_generic_params()
        sig = self.parse_func_sig()
        body = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '{':
            body = self.parse_block()
        self._expect('OPERATOR', ';')
        if body is None:
            body = Block([])
        return MethodDef(name, sig, body, False, loc=start)

    def parse_generic_params(self) -> list[str]:
        params = []
        self._expect('OPERATOR', '<')
        params.append(self._expect('IDENTIFIER').value)
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
            self.stream.next()
            params.append(self._expect('IDENTIFIER').value)
        self._expect('OPERATOR', '>')
        return params

    def parse_call_args(self) -> list:
        self._expect('OPERATOR', '(')
        args = []
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
            args.append(self.parse_expression())
            while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                self.stream.next()
                args.append(self.parse_expression())
        self._expect('OPERATOR', ')')
        return args


    def parse_func_sig(self) -> FuncSig:
        start = self._expect('OPERATOR', '(')
        params: list[Parameter] = []
        var_arg = False
        if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
            if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '...':
                self.stream.next()
                var_arg = True
            else:
                params.append(self.parse_param())
                while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                    if self.stream.peek(1) and self.stream.peek(1).tk_type == 'OPERATOR' and self.stream.peek(1).value == '...':
                        self.stream.next()
                        self.stream.next()
                        var_arg = True
                        break
                    self.stream.next()
                    params.append(self.parse_param())
        self._expect('OPERATOR', ')')
        return_type = None
        if self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '->':
            self.stream.next()
            return_type = self.parse_type_spec()
        return FuncSig(params, return_type, var_arg, loc=start)

    def parse_param(self) -> Parameter:
        names = [self._expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
            if self.stream.peek(1) and self.stream.peek(1).tk_type == 'IDENTIFIER':
                self.stream.next()
                names.append(self._expect('IDENTIFIER').value)
            else:
                break
        self._expect('OPERATOR', ':')
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
            parts = [self._expect('IDENTIFIER').value]
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '.':
            self.stream.next()
            parts.append(self._expect('IDENTIFIER').value)
        typ = '.'.join(parts)
        while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '*':
            self.stream.next()
            typ += '*'
        return typ

    def parse_block(self) -> Block:
        start = self._expect('OPERATOR', '{')
        statements = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            statements.append(self.parse_statement())
        self._expect('OPERATOR', '}')
        return Block(statements, loc=start)
