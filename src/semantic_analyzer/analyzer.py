from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..backend.llir import load_module_ast
from .types import TypeInfo
from ..errors import SemanticError, SourceLocation, NameError

from ..syntax_parser.ast import (
    BinaryOp,
    FunctionCall,
    FunctionDecl,
    FuncDef,
    ForeignFuncDecl,
    ExprStmt,
    ForInStmt,
    ReturnStmt,
    RaiseStmt,
    RaiseExpr,
    MatchExpr,
    MemberAccess,
    Identifier,
    Integer,
    String,
    LetStmt,
    BindingStmt,
    ImportStmt,
    StructDef,
    DestructorDef,
    ConstructorDef,
    Program,
    Statement,
    Expression,
    UnaryOp,
)
from ..lexer.Token import Token


@dataclass
class SemanticAnalyzer:
    """A very small semantic analyzer checking variable usage with functions."""

    variables_stack: List[Set[str]] | None = None
    functions: Set[str] | None = None
    type_registry: Dict[str, TypeInfo] | None = None
    filename: str = "<stdin>"
    source_lines: List[str] = field(default_factory=list)

    def analyze(self, program: Program, *, source: str = "", filename: str = "<stdin>") -> None:
        self.filename = filename
        self.source_lines = source.splitlines()
        self.functions = set()
        self._collect_functions(program)
        self.type_registry = {}
        self.variables_stack = [set()]
        self._visit_program(program)

    def _collect_functions(self, program: Program) -> None:
        for stmt in program.statements:
            if isinstance(stmt, (FunctionDecl, FuncDef, ForeignFuncDecl)):
                self.functions.add(stmt.name)
            elif isinstance(stmt, ImportStmt):
                try:
                    mod_ast = load_module_ast(stmt.module)
                except FileNotFoundError:
                    continue
                self._collect_functions(mod_ast)

    def _visit_program(self, program: Program) -> None:
        for stmt in program.statements:
            self._visit_statement(stmt)

    # Internal helpers -------------------------------------------------
    def _current_scope(self) -> Set[str]:
        assert self.variables_stack is not None
        return self.variables_stack[-1]

    def _is_defined(self, name: str) -> bool:
        assert self.variables_stack is not None
        for scope in reversed(self.variables_stack):
            if name in scope:
                return True
        return False

    def _get_location(self, token: Token | None) -> SourceLocation | None:
        if token is None:
            return None
        line = token.line
        column = token.col
        source_line = self.source_lines[line - 1] if 0 <= line - 1 < len(self.source_lines) else ""
        return SourceLocation(self.filename, line, column, source_line)

    def _visit_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, (LetStmt, BindingStmt)):
            if stmt.value is not None:
                self._visit_expression(stmt.value)
            self._current_scope().add(stmt.name)
        elif isinstance(stmt, ExprStmt):
            self._visit_expression(stmt.expr)
        elif isinstance(stmt, RaiseStmt):
            self._visit_expression(stmt.expr)
        elif isinstance(stmt, ReturnStmt):
            if stmt.value is not None:
                self._visit_expression(stmt.value)
        elif isinstance(stmt, ForInStmt):
            self._visit_expression(stmt.iterable)
            self.variables_stack.append({stmt.var})
            for s in stmt.body.statements:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, ImportStmt):
            # record alias so it can be referenced later
            if stmt.alias:
                self._current_scope().add(stmt.alias)
            try:
                mod_ast = load_module_ast(stmt.module)
            except FileNotFoundError:
                return
            self.variables_stack.append(set())
            for s in mod_ast.statements:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, (FunctionDecl, FuncDef)):
            # Enter a new scope for parameters and locals
            if isinstance(stmt, FunctionDecl):
                params = set(stmt.params)
                body = stmt.body
            else:
                params = {n for p in stmt.signature.params for n in p.names}
                body = stmt.body.statements
            self.variables_stack.append(params)
            for s in body:
                self._visit_statement(s)
            self.variables_stack.pop()
        elif isinstance(stmt, ForeignFuncDecl):
            # no body to check
            pass
        elif isinstance(stmt, StructDef):
            self._visit_struct_def(stmt)
        else:
            raise SemanticError(
                f"Unsupported statement {type(stmt).__name__}",
                self._get_location(stmt.loc),
            )

    def _visit_struct_def(self, struct: StructDef) -> None:
        assert self.type_registry is not None
        if struct.name in self.type_registry:
            raise SemanticError(
                f"Type '{struct.name}' is already defined.",
                self._get_location(struct.loc),
            )

        type_info = TypeInfo(name=struct.name)
        self.type_registry[struct.name] = type_info

        for member in struct.body.statements:
            if isinstance(member, DestructorDef):
                type_info.has_destructor = True
                # analyze destructor body in its own scope with 'self'
                self.variables_stack.append({"self"})
                for stmt in member.body.statements:
                    self._visit_statement(stmt)
                self.variables_stack.pop()
            elif isinstance(member, ConstructorDef):
                type_info.constructor = member.signature
                self.variables_stack.append({"self"})
                for stmt in member.body.statements:
                    self._visit_statement(stmt)
                self.variables_stack.pop()
            elif isinstance(member, LetStmt):
                # store member type information (type name may be None)
                type_info.members[member.name] = member.type_name
            else:
                # For now, simply visit any nested statements
                self._visit_statement(member)

    def _visit_expression(self, expr: Expression) -> None:
        if isinstance(expr, Identifier):
            name = expr.name.split('.')[0]
            if not self._is_defined(name):
                raise NameError(
                    f"Undefined variable '{expr.name}'",
                    self._get_location(expr.loc),
                )
        elif isinstance(expr, Integer):
            pass
        elif isinstance(expr, String):
            pass
        elif isinstance(expr, BinaryOp):
            self._visit_expression(expr.left)
            self._visit_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._visit_expression(expr.operand)
        elif isinstance(expr, MemberAccess):
            self._visit_expression(expr.object)
        elif isinstance(expr, RaiseExpr):
            self._visit_expression(expr.expr)
        elif isinstance(expr, MatchExpr):
            self._visit_expression(expr.value)
            for case in expr.cases:
                self.variables_stack.append({case.name})
                if isinstance(case.body, Expression):
                    self._visit_expression(case.body)
                else:
                    for s in case.body.statements:
                        self._visit_statement(s)
                self.variables_stack.pop()
        elif isinstance(expr, FunctionCall):
            if (
                self.type_registry is not None
                and expr.name in self.type_registry
            ):
                ctor_sig = self.type_registry[expr.name].constructor
                if ctor_sig is not None:
                    expected = [n for p in ctor_sig.params for n in p.names]
                    if len(expected) != len(expr.args):
                        raise SemanticError(
                            f"Constructor for {expr.name} takes {len(expected)} arguments",
                            self._get_location(expr.loc),
                        )
                for arg in expr.args:
                    self._visit_expression(arg)
            else:
                if '.' not in expr.name and self.functions is not None and expr.name not in self.functions:
                    raise NameError(
                        f"Undefined function '{expr.name}'",
                        self._get_location(expr.loc),
                    )
                for arg in expr.args:
                    self._visit_expression(arg)
        else:
            raise SemanticError(
                f"Unsupported expression {type(expr).__name__}",
                self._get_location(expr.loc),
            )
