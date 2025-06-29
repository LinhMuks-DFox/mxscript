from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..syntax_parser.ast import BinaryOp, ExprStmt, Identifier, Integer, LetStmt, Program, UnaryOp


# ------------ LLIR Instructions ------------------------------------------------

class Instr:
    pass


@dataclass
class Const(Instr):
    value: int


@dataclass
class Load(Instr):
    name: str


@dataclass
class Store(Instr):
    name: str


@dataclass
class BinOpInstr(Instr):
    op: str


@dataclass
class Pop(Instr):
    pass


# ------------ Compilation ------------------------------------------------------

def compile_program(prog: Program) -> List[Instr]:
    code: List[Instr] = []
    for stmt in prog.statements:
        code.extend(_compile_stmt(stmt))
    return code


def _compile_stmt(stmt) -> List[Instr]:
    if isinstance(stmt, LetStmt):
        code = _compile_expr(stmt.value)
        code.append(Store(stmt.name))
        return code
    if isinstance(stmt, ExprStmt):
        return _compile_expr(stmt.expr)
    raise NotImplementedError(f"Unsupported stmt {type(stmt).__name__}")


def _compile_expr(expr) -> List[Instr]:
    if isinstance(expr, Integer):
        return [Const(expr.value)]
    if isinstance(expr, Identifier):
        return [Load(expr.name)]
    if isinstance(expr, BinaryOp):
        return _compile_expr(expr.left) + _compile_expr(expr.right) + [BinOpInstr(expr.op)]
    if isinstance(expr, UnaryOp):
        # Only unary '-' supported
        if expr.op == '-':
            return [Const(0)] + _compile_expr(expr.operand) + [BinOpInstr('-')]
    raise NotImplementedError(f"Unsupported expr {type(expr).__name__}")


# ------------ Optimization -----------------------------------------------------

def optimize(code: List[Instr]) -> List[Instr]:
    optimized: List[Instr] = []
    i = 0
    while i < len(code):
        if (
            i + 2 < len(code)
            and isinstance(code[i], Const)
            and isinstance(code[i + 1], Const)
            and isinstance(code[i + 2], BinOpInstr)
        ):
            a = code[i].value
            b = code[i + 1].value
            op = code[i + 2].op
            optimized.append(Const(_apply_op(op, a, b)))
            i += 3
        else:
            optimized.append(code[i])
            i += 1
    return optimized


# ------------ Execution --------------------------------------------------------

def execute(code: List[Instr]) -> int | None:
    env: Dict[str, int] = {}
    stack: List[int] = []
    for instr in code:
        if isinstance(instr, Const):
            stack.append(instr.value)
        elif isinstance(instr, Load):
            stack.append(env.get(instr.name, 0))
        elif isinstance(instr, Store):
            env[instr.name] = stack.pop()
        elif isinstance(instr, BinOpInstr):
            b = stack.pop()
            a = stack.pop()
            stack.append(_apply_op(instr.op, a, b))
        elif isinstance(instr, Pop):
            if stack:
                stack.pop()
        else:
            raise RuntimeError(f"Unknown instruction {instr}")
    return stack[-1] if stack else None


# ------------ Helpers ----------------------------------------------------------

def _apply_op(op: str, a: int, b: int) -> int:
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return a // b
    if op == '%':
        return a % b
    if op == '==':
        return int(a == b)
    if op == '!=':
        return int(a != b)
    if op == '>':
        return int(a > b)
    if op == '<':
        return int(a < b)
    if op == '>=':
        return int(a >= b)
    if op == '<=':
        return int(a <= b)
    raise RuntimeError(f"Unsupported op {op}")
