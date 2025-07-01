from __future__ import annotations

from typing import List

from .llir import LLIRInstr, Label, Br, CondBr
from ..syntax_parser.ast import (
    Program,
    Statement,
    Block,
    Expression,
    IfStmt,
)


class LLIRBuilder:
    """Convert AST nodes into a sequence of LLIR instructions."""

    def __init__(self) -> None:
        self.code: List[LLIRInstr] = []
        self.label_counter = 0

    # ------------------------------------------------------------------
    def emit(self, instr: LLIRInstr) -> None:
        self.code.append(instr)

    def build(self, program: Program) -> List[LLIRInstr]:
        for stmt in program.statements:
            self._visit_statement(stmt)
        return self.code

    # ------------------------------------------------------------------
    def _new_label(self, name: str) -> str:
        self.label_counter += 1
        return f".{name}_{self.label_counter}"

    # ------------------------------------------------------------------
    def _visit_block(self, block: Block) -> None:
        for stmt in block.statements:
            self._visit_statement(stmt)

    def _visit_expression(self, expr: Expression) -> str:  # pragma: no cover - placeholder
        raise NotImplementedError

    def _visit_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, IfStmt):
            self._visit_if_stmt(stmt)
        elif isinstance(stmt, Block):
            self._visit_block(stmt)
        else:
            pass  # other statements not yet implemented

    # ------------------------------------------------------------------
    def _visit_if_stmt(self, stmt: IfStmt) -> None:
        then_label = self._new_label("then")
        else_label = self._new_label("else")
        end_label = self._new_label("end")

        cond_reg = self._visit_expression(stmt.condition)
        self.emit(CondBr(cond=cond_reg, then_label=then_label, else_label=else_label))

        # then block
        self.emit(Label(name=then_label))
        self._visit_block(stmt.then_block)
        self.emit(Br(label=end_label))

        # else block
        self.emit(Label(name=else_label))
        if stmt.else_block is not None:
            if isinstance(stmt.else_block, IfStmt):
                self._visit_if_stmt(stmt.else_block)
            else:
                self._visit_block(stmt.else_block)

        # end label
        self.emit(Label(name=end_label))

