from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from llvmlite import binding, ir

from ..lexer import TokenStream, tokenize
from ..syntax_parser import Parser

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
    String,
    LetStmt,
    BindingStmt,
    ReturnStmt,
    ImportStmt,
    Program,
    UnaryOp,
)


# ------------ LLIR Instructions ------------------------------------------------

class Instr:
    pass


@dataclass
class Const(Instr):
    value: int | str


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


# ------------ Module Loading --------------------------------------------------

def load_module_ast(module: str, search_paths: List[str | Path] | None = None) -> Program:
    """Locate ``module`` and parse it into an AST."""
    if search_paths is None:
        search_paths = [Path("demo_program")]
    rel = Path(module.replace(".", "/") + ".mxs")
    for base in search_paths:
        path = Path(base) / rel
        if path.exists():
            lines = path.read_text().splitlines()
            # Skip a simple header delimited by !# and #!
            if lines and lines[0].startswith("!#"):
                while lines and not lines.pop(0).startswith("#!"):
                    pass
            source_text = "\n".join(lines)
            tokens = tokenize(source_text)
            stream = TokenStream(tokens)
            return Parser(stream).parse()
    raise FileNotFoundError(f"Module {module} not found")


# ------------ Compilation ------------------------------------------------------

def compile_program(
    prog: Program,
    module_cache: Dict[str, ProgramIR] | None = None,
    search_paths: List[str | Path] | None = None,
) -> ProgramIR:
    code: List[Instr] = []
    functions: Dict[str, Function] = {}
    foreign_functions: Dict[str, str] = {}
    if module_cache is None:
        module_cache = {}
    if search_paths is None:
        search_paths = [Path("demo_program")]
    for stmt in prog.statements:
        if isinstance(stmt, (FuncDef, FunctionDecl)):
            func_ir = _compile_function(stmt)
            functions[stmt.name] = func_ir
        elif isinstance(stmt, ForeignFuncDecl):
            foreign_functions[stmt.name] = stmt.c_name
        elif isinstance(stmt, ImportStmt):
            mod_name = stmt.module
            try:
                if mod_name not in module_cache:
                    mod_ast = load_module_ast(mod_name, search_paths)
                    module_cache[mod_name] = compile_program(
                        mod_ast, module_cache, search_paths
                    )
                mod_ir = module_cache[mod_name]
            except FileNotFoundError:
                continue
            prefix = f"{stmt.alias or stmt.module}."
            rename_map = {n: prefix + n for n in mod_ir.functions}
            for name, func in mod_ir.functions.items():
                new_name = rename_map[name]
                new_code: List[Instr] = []
                for instr in func.code:
                    if isinstance(instr, Call) and instr.name in rename_map:
                        new_code.append(Call(rename_map[instr.name], instr.argc))
                    else:
                        new_code.append(instr)
                functions[new_name] = Function(new_name, func.params, new_code)
            foreign_functions.update(mod_ir.foreign_functions)
            continue
        else:
            code.extend(_compile_stmt(stmt))
    return ProgramIR(code, functions, foreign_functions)


def _compile_stmt(stmt) -> List[Instr]:
    if isinstance(stmt, LetStmt):
        code = _compile_expr(stmt.value)
        code.append(Store(stmt.name))
        return code
    if isinstance(stmt, BindingStmt):
        code = _compile_expr(stmt.value)
        code.append(Store(stmt.name))
        return code
    if isinstance(stmt, ImportStmt):
        # Import statements produce no executable code
        return []
    if isinstance(stmt, Block):
        code: List[Instr] = []
        for s in stmt.statements:
            code.extend(_compile_stmt(s))
        return code
    if isinstance(stmt, ExprStmt):
        return _compile_expr(stmt.expr)
    if isinstance(stmt, ReturnStmt):
        return _compile_expr(stmt.value) if stmt.value is not None else []
    raise NotImplementedError(f"Unsupported stmt {type(stmt).__name__}")


def _compile_expr(expr) -> List[Instr]:
    if isinstance(expr, Integer):
        return [Const(expr.value)]
    if isinstance(expr, String):
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
    def run(code: List[Instr], env_stack: List[Dict[str, object]]) -> object | None:
        stack: List[object] = []
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
                        stack.append(_ffi_call(program.foreign_functions[instr.name], args))
                        continue
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
    a = int(a)
    b = int(b)
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


def _ffi_call(c_name: str, args: List[object]) -> int | None:
    """Very small foreign function handler for the interpreter."""
    if c_name == "write":
        import os

        fd = int(args[0])
        buf = args[1]
        count = int(args[2])
        if isinstance(buf, str):
            data = buf.encode()[:count]
        elif isinstance(buf, bytes):
            data = buf[:count]
        else:
            data = bytes(buf)
        return os.write(fd, data)
    if c_name == "print":
        print(*args)
        return 0
    raise RuntimeError(f"Foreign function {c_name} not implemented")


# ------------ LLVM IR Generation ---------------------------------------------

def to_llvm_ir(program: ProgramIR) -> str:
    """Convert :class:`ProgramIR` to LLVM IR string."""

    int_t = ir.IntType(64)
    module = ir.Module(name="mxscript")

    # Declare all functions first
    llvm_funcs: Dict[str, ir.Function] = {}

    for func in program.functions.values():
        func_ty = ir.FunctionType(int_t, [int_t] * len(func.params))
        llvm_funcs[func.name] = ir.Function(module, func_ty, name=func.name)

    # Foreign functions as external declarations
    for name in program.foreign_functions:
        ir.Function(module, ir.FunctionType(int_t, []), name=name)

    def emit_code(builder: ir.IRBuilder, code: List[Instr], vars: Dict[str, ir.AllocaInstr]) -> ir.Value:
        stack: List[ir.Value] = []

        def get_var(name: str) -> ir.AllocaInstr:
            if name not in vars:
                vars[name] = builder.alloca(int_t, name=name)
                builder.store(ir.Constant(int_t, 0), vars[name])
            return vars[name]

        for instr in code:
            if isinstance(instr, Const):
                stack.append(ir.Constant(int_t, instr.value))
            elif isinstance(instr, Load):
                stack.append(builder.load(get_var(instr.name)))
            elif isinstance(instr, Store):
                builder.store(stack.pop(), get_var(instr.name))
            elif isinstance(instr, BinOpInstr):
                b = stack.pop()
                a = stack.pop()
                if instr.op == '+':
                    stack.append(builder.add(a, b))
                elif instr.op == '-':
                    stack.append(builder.sub(a, b))
                elif instr.op == '*':
                    stack.append(builder.mul(a, b))
                elif instr.op == '/':
                    stack.append(builder.sdiv(a, b))
                elif instr.op == '%':
                    stack.append(builder.srem(a, b))
                elif instr.op == '==':
                    stack.append(builder.icmp_signed('==', a, b))
                elif instr.op == '!=':
                    stack.append(builder.icmp_signed('!=', a, b))
                elif instr.op == '>':
                    stack.append(builder.icmp_signed('>', a, b))
                elif instr.op == '<':
                    stack.append(builder.icmp_signed('<', a, b))
                elif instr.op == '>=':
                    stack.append(builder.icmp_signed('>=', a, b))
                elif instr.op == '<=':
                    stack.append(builder.icmp_signed('<=', a, b))
                else:
                    raise RuntimeError(f"Unsupported op {instr.op}")
            elif isinstance(instr, Call):
                args = [stack.pop() for _ in range(instr.argc)][::-1]
                callee = llvm_funcs.get(instr.name)
                if callee is None:
                    callee = module.get_global(instr.name)
                stack.append(builder.call(callee, args))
            elif isinstance(instr, Pop):
                if stack:
                    stack.pop()
            else:
                raise RuntimeError(f"Unknown instruction {instr}")

        return stack[-1] if stack else ir.Constant(int_t, 0)

    # Build function bodies
    for func_ir in program.functions.values():
        func = llvm_funcs[func_ir.name]
        block = func.append_basic_block("entry")
        builder = ir.IRBuilder(block)

        vars: Dict[str, ir.AllocaInstr] = {}
        for arg, name in zip(func.args, func_ir.params):
            ptr = builder.alloca(int_t, name=name)
            builder.store(arg, ptr)
            vars[name] = ptr

        ret_val = emit_code(builder, func_ir.code, vars)
        builder.ret(ret_val)

    # Build main from top-level code
    main_ty = ir.FunctionType(int_t, [])
    main_fn = ir.Function(module, main_ty, name="main")
    block = main_fn.append_basic_block("entry")
    builder = ir.IRBuilder(block)
    ret = emit_code(builder, program.code, {})
    builder.ret(ret)

    return str(module)


def execute_llvm(program: ProgramIR) -> int:
    """JIT compile and execute program via LLVM."""

    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()

    llvm_ir = to_llvm_ir(program)
    mod = binding.parse_assembly(llvm_ir)
    mod.verify()
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    engine = binding.create_mcjit_compiler(mod, target_machine)
    engine.finalize_object()
    func_ptr = engine.get_function_address("main")

    from ctypes import CFUNCTYPE, c_longlong

    cfunc = CFUNCTYPE(c_longlong)(func_ptr)
    result = cfunc()
    return int(result)

