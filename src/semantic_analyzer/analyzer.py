from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

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
    Identifier,
    Integer,
    String,
    LetStmt,
    BindingStmt,
    ImportStmt,
    Program,
    Statement,
    Expression,
    UnaryOp,
)


class SemanticError(Exception):
    """Raised when semantic analysis fails."""


@dataclass
class SemanticAnalyzer:
    """A very small semantic analyzer checking variable usage with functions."""

    variables_stack: List[Set[str]] | None = None
    functions: Set[str] | None = None

    def analyze(self, program: Program) -> None:
        # Gather all function names first so they can be referenced before
        # their declaration.
        self.functions = {
            stmt.name
            for stmt in program.statements
            if isinstance(
                stmt,
                (
                    FunctionDecl,
                    FuncDef,
                    ForeignFuncDecl,
                ),
            )
        }
        self.variables_stack = [set()]
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

    def _visit_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, (LetStmt, BindingStmt)):
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
        else:
            raise SemanticError(f"Unsupported statement {type(stmt).__name__}")

    def _visit_expression(self, expr: Expression) -> None:
        if isinstance(expr, Identifier):
            name = expr.name.split('.')[0]
            if not self._is_defined(name):
                raise SemanticError(f"Undefined variable '{expr.name}'")
        elif isinstance(expr, Integer):
            pass
        elif isinstance(expr, String):
            pass
        elif isinstance(expr, BinaryOp):
            self._visit_expression(expr.left)
            self._visit_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._visit_expression(expr.operand)
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
            # Check that the function exists
            if '.' not in expr.name and self.functions is not None and expr.name not in self.functions:
                raise SemanticError(f"Undefined function '{expr.name}'")
            for arg in expr.args:
                self._visit_expression(arg)
        else:
            raise SemanticError(f"Unsupported expression {type(expr).__name__}")
