from __future__ import annotations

from dataclasses import dataclass
from typing import Set

from ..syntax_parser.ast import (
    BinaryOp,
    ExprStmt,
    Identifier,
    Integer,
    LetStmt,
    Program,
    Statement,
    Expression,
    UnaryOp,
)


class SemanticError(Exception):
    """Raised when semantic analysis fails."""


@dataclass
class SemanticAnalyzer:
    """A very small semantic analyzer checking variable usage."""

    variables: Set[str] | None = None

    def analyze(self, program: Program) -> None:
        self.variables = set()
        for stmt in program.statements:
            self._visit_statement(stmt)

    # Internal helpers -------------------------------------------------
    def _visit_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, LetStmt):
            self._visit_expression(stmt.value)
            self.variables.add(stmt.name)
        elif isinstance(stmt, ExprStmt):
            self._visit_expression(stmt.expr)
        else:
            raise SemanticError(f"Unsupported statement {type(stmt).__name__}")

    def _visit_expression(self, expr: Expression) -> None:
        if isinstance(expr, Identifier):
            assert self.variables is not None
            if expr.name not in self.variables:
                raise SemanticError(f"Undefined variable '{expr.name}'")
        elif isinstance(expr, Integer):
            pass
        elif isinstance(expr, BinaryOp):
            self._visit_expression(expr.left)
            self._visit_expression(expr.right)
        elif isinstance(expr, UnaryOp):
            self._visit_expression(expr.operand)
        else:
            raise SemanticError(f"Unsupported expression {type(expr).__name__}")
