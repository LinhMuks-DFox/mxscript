from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..syntax_parser.ast import (
    BinaryOp,
    Block,
    ExprStmt,
    FunctionCall,
    FunctionDecl,
    FuncDef,
    ForeignFuncDecl,
    Identifier,
    Integer,
    LetStmt,
    Program,
    UnaryOp,
)


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


@dataclass
class Call(Instr):
    name: str
    argc: int


@dataclass
class Function:
    name: str
    params: List[str]
    code: List[Instr]


@dataclass
class ProgramIR:
    code: List[Instr]
    functions: Dict[str, Function]
    foreign_functions: Dict[str, str]


# ------------ Compilation ------------------------------------------------------

def compile_program(prog: Program) -> ProgramIR:
    code: List[Instr] = []
    functions: Dict[str, Function] = {}
    foreign_functions: Dict[str, str] = {}
    for stmt in prog.statements:
        if isinstance(stmt, (FuncDef, FunctionDecl)):
            func_ir = _compile_function(stmt)
            functions[stmt.name] = func_ir
        elif isinstance(stmt, ForeignFuncDecl):
            foreign_functions[stmt.name] = stmt.c_name
        else:
            code.extend(_compile_stmt(stmt))
    return ProgramIR(code, functions, foreign_functions)


def _compile_stmt(stmt) -> List[Instr]:
    if isinstance(stmt, LetStmt):
        code = _compile_expr(stmt.value)
        code.append(Store(stmt.name))
        return code
    if isinstance(stmt, Block):
        code: List[Instr] = []
        for s in stmt.statements:
            code.extend(_compile_stmt(s))
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
    if isinstance(expr, FunctionCall):
        code: List[Instr] = []
        for arg in expr.args:
            code.extend(_compile_expr(arg))
        code.append(Call(expr.name, len(expr.args)))
        return code
    raise NotImplementedError(f"Unsupported expr {type(expr).__name__}")


def _compile_function(func: FuncDef | FunctionDecl) -> Function:
    if isinstance(func, FuncDef):
        params = [name for p in func.signature.params for name in p.names]
        body_stmts = func.body.statements
    else:
        params = func.params
        body_stmts = func.body
    body_code: List[Instr] = []
    for stmt in body_stmts:
        body_code.extend(_compile_stmt(stmt))
    return Function(func.name, params, body_code)


# ------------ Optimization -----------------------------------------------------

def optimize(program: ProgramIR) -> ProgramIR:
    return ProgramIR(
        _optimize_list(program.code),
        {
            name: Function(f.name, f.params, _optimize_list(f.code))
            for name, f in program.functions.items()
        },
        program.foreign_functions,
    )


def _optimize_list(code: List[Instr]) -> List[Instr]:
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

def execute(program: ProgramIR) -> int | None:
    def run(code: List[Instr], env_stack: List[Dict[str, int]]) -> int | None:
        stack: List[int] = []
        for instr in code:
            if isinstance(instr, Const):
                stack.append(instr.value)
            elif isinstance(instr, Load):
                for env in reversed(env_stack):
                    if instr.name in env:
                        stack.append(env[instr.name])
                        break
                else:
                    stack.append(0)
            elif isinstance(instr, Store):
                env_stack[-1][instr.name] = stack.pop()
            elif isinstance(instr, BinOpInstr):
                b = stack.pop()
                a = stack.pop()
                stack.append(_apply_op(instr.op, a, b))
            elif isinstance(instr, Call):
                args = [stack.pop() for _ in range(instr.argc)][::-1]
                func = program.functions.get(instr.name)
                if func is None:
                    if instr.name in program.foreign_functions:
                        raise RuntimeError(
                            f"Foreign function {instr.name} not executable in interpreter"
                        )
                    raise RuntimeError(f"Undefined function {instr.name}")
                new_env = dict(zip(func.params, args))
                env_stack.append(new_env)
                result = run(func.code, env_stack)
                env_stack.pop()
                if result is not None:
                    stack.append(result)
            elif isinstance(instr, Pop):
                if stack:
                    stack.pop()
            else:
                raise RuntimeError(f"Unknown instruction {instr}")
        return stack[-1] if stack else None

    return run(program.code, [{}])


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
