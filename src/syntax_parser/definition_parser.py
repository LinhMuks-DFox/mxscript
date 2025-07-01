from __future__ import annotations

from .ast import (
    Parameter,
    FuncSig,
    FuncDef,
    ForeignFuncDecl,
    ClassDef,
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
        self._expect('OPERATOR', '{')
        statements = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            tok = self.stream.peek()
            if tok.tk_type == 'KEYWORD' and tok.value in ('public', 'private'):
                self.stream.next()
                if (
                    self.stream.peek().tk_type == 'OPERATOR'
                    and self.stream.peek().value == ':'
                ):
                    self.stream.next()
                continue
            if tok.tk_type == 'KEYWORD' and tok.value == 'let':
                statements.append(self.parse_field_decl())
            elif (
                tok.tk_type == 'KEYWORD'
                and tok.value == 'func'
                and self.stream.peek(1)
                and self.stream.peek(1).tk_type == 'OPERATOR'
                and self.stream.peek(1).value == '~'
            ):
                statements.append(self.parse_destructor_def())
            elif (
                tok.tk_type == 'KEYWORD'
                and tok.value == 'func'
                and self.stream.peek(1)
                and self.stream.peek(1).tk_type == 'IDENTIFIER'
                and self.stream.peek(1).value == name
            ):
                statements.append(self.parse_constructor_def())
            elif tok.tk_type == 'KEYWORD' and tok.value == 'func':
                statements.append(self.parse_method_def())
            elif tok.tk_type == 'KEYWORD' and tok.value == 'operator':
                statements.append(self.parse_operator_def())
            else:
                statements.append(self.parse_statement())
        self._expect('OPERATOR', '}')
        return ClassDef(name, Block(statements), loc=start)

    def parse_field_decl(self):
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
        self._expect('OPERATOR', ';')
        return LetStmt(name, None, type_name, is_mut, loc=start)

    def parse_destructor_def(self):
        start = self._expect('KEYWORD', 'func')
        self._expect('OPERATOR', '~')
        self._expect('IDENTIFIER')
        self._expect('OPERATOR', '(')
        self._expect('OPERATOR', ')')
        body = self.parse_block()
        return DestructorDef(body, loc=start)

    def parse_constructor_def(self):
        start = self._expect('KEYWORD', 'func')
        self._expect('IDENTIFIER')
        sig = self.parse_func_sig()
        body = self.parse_block()
        return ConstructorDef(sig, body, loc=start)

    def parse_method_def(self):
        start = self._expect('KEYWORD', 'func')
        name = self._expect('IDENTIFIER').value
        sig = self.parse_func_sig()
        body = self.parse_block()
        return MethodDef(name, sig, body, loc=start)

    def parse_operator_def(self):
        start = self._expect('KEYWORD', 'operator')
        op_token = self._expect('OPERATOR')
        sig = self.parse_func_sig()
        body = self.parse_block()
        return OperatorDef(op_token.value, sig, body, loc=start)

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
