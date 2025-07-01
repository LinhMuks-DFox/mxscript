from __future__ import annotations

from typing import Dict

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
    StructDef,
    DestructorDef,
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
            if (
                self.stream.peek(1)
                and self.stream.peek(1).tk_type == 'OPERATOR'
                and self.stream.peek(1).value == '~'
            ):
                return self.parse_destructor_def()
            return self.parse_func_def()
        if tok.tk_type == 'KEYWORD' and tok.value == 'struct':
            return self.parse_struct_def()
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
        expr = None

        if tok.tk_type == 'INTEGER':
            self.stream.next()
            # 结合: 从 codex 分支获取 loc=tok
            expr = Integer(int(tok.value), loc=tok)
        elif tok.tk_type == 'STRING':
            self.stream.next()
            # 结合: 从 codex 分支获取 loc=tok
            expr = String(tok.value, loc=tok)
        elif tok.tk_type == 'KEYWORD' and tok.value == 'raise':
            self.stream.next()
            from .ast import RaiseExpr
            # 结合: 使用 master 的逻辑，但从 codex 获取 loc
            expr_to_raise = self.parse_expression()
            expr = RaiseExpr(expr_to_raise, loc=tok)
        elif tok.tk_type == 'KEYWORD' and tok.value == 'match':
            expr = self.parse_match_expr()
        elif tok.tk_type == 'IDENTIFIER':
            self.stream.next()
            # 结合: 从 codex 分支获取 loc=tok
            expr = Identifier(tok.value, loc=tok)
        elif tok.tk_type == 'OPERATOR' and tok.value == '(':
            self.stream.next()
            expr = self.parse_expression()
            self._expect('OPERATOR', ')')
        else:
            # 结合: 使用 codex 分支的新错误报告机制
            raise SyntaxError(f'Unexpected token {tok.tk_type}', self._get_location(tok))

        # 采纳 master 分支的链式解析循环结构，这是正确的逻辑
        from .ast import MemberAccess, FunctionCall

        while True:
            peek_tok = self.stream.peek()
            
            # 处理成员访问 '.'
            if peek_tok.tk_type == 'OPERATOR' and peek_tok.value == '.':
                dot_tok = self.stream.next()
                member_tok = self._expect('IDENTIFIER')
                member_ident = Identifier(member_tok.value, loc=member_tok)
                # 结合: 创建 MemberAccess 节点时，从 codex 获取 loc
                expr = MemberAccess(expr, member_ident, loc=dot_tok)
                continue

            # 处理函数调用 '('
            if peek_tok.tk_type == 'OPERATOR' and peek_tok.value == '(':
                paren_tok = self.stream.next()
                args = []
                if not (self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ')'):
                    args.append(self.parse_expression())
                    while self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == ',':
                        self.stream.next()
                        args.append(self.parse_expression())
                
                self._expect('OPERATOR', ')')
                
                # 优化：创建一个更健壮的 FunctionCall 节点，它接受一个表达式作为 callee
                # 而不是一个扁平化的字符串。这可能需要你将 FunctionCall 的 AST 定义从
                # name: str 改为 callee: Expr。
                expr = FunctionCall(expr, args, loc=paren_tok)
                continue
            
            break
        return expr

    # ------------------------------------------------------------------
    # New parsing rules for functions and blocks
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

    def parse_struct_def(self):
        start = self._expect('KEYWORD', 'struct')
        name = self._expect('IDENTIFIER').value
        self._expect('OPERATOR', '{')
        statements = []
        while self.stream.peek() and not (
            self.stream.peek().tk_type == 'OPERATOR' and self.stream.peek().value == '}'
        ):
            tok = self.stream.peek()
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
            else:
                statements.append(self.parse_statement())
        self._expect('OPERATOR', '}')
        return StructDef(name, Block(statements), loc=start)

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
        # struct name after '~' is ignored for now
        self._expect('IDENTIFIER')
        # signature is expected but typically empty
        self._expect('OPERATOR', '(')
        self._expect('OPERATOR', ')')
        body = self.parse_block()
        return DestructorDef(body, loc=start)

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
                    # check for vararg
                    if self.stream.peek(1) and self.stream.peek(1).tk_type == 'OPERATOR' and self.stream.peek(1).value == '...':
                        self.stream.next()  # consume ','
                        self.stream.next()  # consume '...'
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
            # look ahead to distinguish between identifier list and next param
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
