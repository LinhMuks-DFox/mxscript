from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import os
import ctypes

from llvmlite import binding


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
    MemberAccess,
    String,
    LetStmt,
    BindingStmt,
    StructDef,
    DestructorDef,
    ReturnStmt,
    ImportStmt,
    Program,
    UnaryOp,
)
from ..semantic_analyzer.types import TypeInfo
from ..middleend.symbols import ScopedSymbolTable, Symbol


STD_LIB_DIR = Path(__file__).resolve().parents[2] / "demo_program" / "examples" / "std"
ENV_VAR = "MXSCRIPT_PATH"

# Initialize libc handles for common C functions used via FFI
_libc = ctypes.CDLL(None)
_libc_time = _libc.time
_libc_time.argtypes = [ctypes.c_void_p]
_libc_time.restype = ctypes.c_long
_libc_rand = _libc.rand
_libc_rand.argtypes = []
_libc_rand.restype = ctypes.c_int


def build_search_paths(extra_paths: List[str | Path] | None = None) -> List[Path]:
    """Return module search paths including stdlib and user overrides."""
    paths: List[Path] = [STD_LIB_DIR.parent]
    env = os.environ.get(ENV_VAR)
    if env:
        for p in env.split(os.pathsep):
            if p:
                paths.append(Path(p))
    if extra_paths:
        paths.extend(Path(p) for p in extra_paths)
    return paths


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
    type_name: str | None = None
    is_mut: bool = False


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
class Return(Instr):
    """Marks the end of a function and optionally yields a value."""
    pass


@dataclass
class DestructorCall(Instr):
    """Explicit call to a variable's destructor when it goes out of scope."""

    name: str


@dataclass
class ProgramIR:
    code: List[Instr]
    functions: Dict[str, Function]
    foreign_functions: Dict[str, str]





# ------------ Module Loading --------------------------------------------------

def load_module_ast(module: str, search_paths: List[str | Path] | None = None) -> Program:
    """Locate ``module`` and parse it into an AST."""
    if search_paths is None:
        search_paths = build_search_paths()
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
    type_registry: Dict[str, TypeInfo] | None = None,
    module_cache: Dict[str, ProgramIR] | None = None,
    search_paths: List[str | Path] | None = None,
) -> ProgramIR:
    code: List[Instr] = []
    functions: Dict[str, Function] = {}
    foreign_functions: Dict[str, str] = {}
    alias_map: Dict[str, str] = {}
    symtab = ScopedSymbolTable()
    if module_cache is None:
        module_cache = {}
    if search_paths is None:
        search_paths = build_search_paths()
    has_main = False
    # First gather static aliases
    for stmt in prog.statements:
        if isinstance(stmt, BindingStmt) and stmt.is_static and isinstance(stmt.value, (Identifier, MemberAccess)):
            alias_map[stmt.name] = _flatten_member(stmt.value)

    for stmt in prog.statements:
        if isinstance(stmt, (FuncDef, FunctionDecl)):
            func_ir = _compile_function(stmt, alias_map, type_registry)
            functions[stmt.name] = func_ir
            if stmt.name == "main" and len(func_ir.params) == 0:
                has_main = True
        elif isinstance(stmt, StructDef):
            for member in stmt.body.statements:
                if isinstance(member, DestructorDef):
                    dtor_ir = _compile_destructor(
                        stmt.name, member, alias_map, type_registry
                    )
                    functions[dtor_ir.name] = dtor_ir
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
            # Pull in top-level initialization code from the imported module
            code.extend(mod_ir.code)
            prefix = f"{stmt.alias or stmt.module}."
            rename_map = {n: prefix + n for n in mod_ir.functions}
            rename_map.update({n: prefix + n for n in mod_ir.foreign_functions})
            for name, func in mod_ir.functions.items():
                new_name = rename_map[name]
                new_code: List[Instr] = []
                for instr in func.code:
                    if isinstance(instr, Call) and instr.name in rename_map:
                        new_code.append(Call(rename_map[instr.name], instr.argc))
                    else:
                        new_code.append(instr)
                functions[new_name] = Function(new_name, func.params, new_code)
            for name, c_name in mod_ir.foreign_functions.items():
                foreign_functions[prefix + name] = c_name
            for instr in mod_ir.code:
                if isinstance(instr, Call) and instr.name in rename_map:
                    code.append(Call(rename_map[instr.name], instr.argc))
                else:
                    code.append(instr)
            continue
        elif isinstance(stmt, BindingStmt) and stmt.is_static and isinstance(stmt.value, (Identifier, MemberAccess)):
            target = _flatten_member(stmt.value)
            if target in functions:
                target_func = functions[target]
                functions[stmt.name] = Function(stmt.name, target_func.params, target_func.code)
                continue
            if target in foreign_functions:
                foreign_functions[stmt.name] = foreign_functions[target]
                continue
        else:
            code.extend(_compile_stmt(stmt, alias_map, symtab, type_registry))
    if has_main:
        code.append(Call("main", 0))
    # emit destructor calls for globals
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            code.append(DestructorCall(sym.name))
    return ProgramIR(code, functions, foreign_functions)


def _compile_stmt(
    stmt,
    alias_map: Dict[str, str],
    symtab: ScopedSymbolTable,
    type_registry: Dict[str, TypeInfo] | None,
) -> List[Instr]:
    if isinstance(stmt, LetStmt):
        code: List[Instr] = []
        if stmt.value is not None:
            code.extend(_compile_expr(stmt.value, alias_map, symtab, type_registry))
        code.append(Store(stmt.name, stmt.type_name, stmt.is_mut))
        needs_destruction = False
        if (
            type_registry is not None
            and stmt.type_name is not None
            and stmt.type_name in type_registry
            and type_registry[stmt.type_name].has_destructor
        ):
            needs_destruction = True
        symtab.add_symbol(Symbol(stmt.name, stmt.type_name, needs_destruction))
        return code
    if isinstance(stmt, BindingStmt):
        if stmt.is_static and isinstance(stmt.value, (Identifier, MemberAccess)):
            target = _flatten_member(stmt.value)
            while target in alias_map:
                target = alias_map[target]
            alias_map[stmt.name] = target
            return []
        code = _compile_expr(stmt.value, alias_map, symtab, type_registry)
        code.append(Store(stmt.name, None))
        return code
    if isinstance(stmt, ImportStmt):
        # Import statements produce no executable code
        return []
    if isinstance(stmt, Block):
        code: List[Instr] = []
        symtab.enter_scope()
        for s in stmt.statements:
            code.extend(_compile_stmt(s, alias_map, symtab, type_registry))
        scope = symtab.leave_scope()
        for sym in reversed(list(scope.values())):
            if sym.needs_destruction:
                code.append(DestructorCall(sym.name))
        return code
    if isinstance(stmt, ExprStmt):
        return _compile_expr(stmt.expr, alias_map, symtab, type_registry)
    if isinstance(stmt, ReturnStmt):
        code = (
            _compile_expr(stmt.value, alias_map, symtab, type_registry)
            if stmt.value is not None
            else []
        )
        # emit destructor calls for all active scopes
        for scope in reversed(symtab.scopes):
            for sym in reversed(list(scope.values())):
                if sym.needs_destruction:
                    code.append(DestructorCall(sym.name))
        code.append(Return())
        return code
    raise NotImplementedError(f"Unsupported stmt {type(stmt).__name__}")


def _flatten_member(expr) -> str:
    if isinstance(expr, Identifier):
        return expr.name
    if isinstance(expr, MemberAccess):
        return f"{_flatten_member(expr.object)}.{expr.member.name}"
    raise NotImplementedError("Unsupported member expression")


def _compile_expr(
    expr,
    alias_map: Dict[str, str],
    symtab: ScopedSymbolTable,
    type_registry: Dict[str, TypeInfo] | None,
) -> List[Instr]:
    if isinstance(expr, Integer):
        return [Const(expr.value)]
    if isinstance(expr, String):
        return [Const(expr.value)]
    if isinstance(expr, Identifier):
        name = expr.name
        while name in alias_map:
            name = alias_map[name]
        return [Load(name)]
    if isinstance(expr, MemberAccess):
        name = _flatten_member(expr)
        while name in alias_map:
            name = alias_map[name]
        return [Load(name)]
    if isinstance(expr, BinaryOp):
        return _compile_expr(expr.left, alias_map, symtab, type_registry) + _compile_expr(expr.right, alias_map, symtab, type_registry) + [BinOpInstr(expr.op)]
    if isinstance(expr, UnaryOp):
        # Only unary '-' supported
        if expr.op == '-':
            return [Const(0)] + _compile_expr(expr.operand, alias_map, symtab, type_registry) + [BinOpInstr('-')]
    if isinstance(expr, FunctionCall):
        code: List[Instr] = []
        for arg in expr.args:
            code.extend(_compile_expr(arg, alias_map, symtab, type_registry))
        name = expr.name
        while name in alias_map:
            name = alias_map[name]
        code.append(Call(name, len(expr.args)))
        return code
    raise NotImplementedError(f"Unsupported expr {type(expr).__name__}")


def _compile_function(
    func: FuncDef | FunctionDecl,
    alias_map: Dict[str, str],
    type_registry: Dict[str, TypeInfo] | None,
) -> Function:
    if isinstance(func, FuncDef):
        params = [name for p in func.signature.params for name in p.names]
        body_stmts = func.body.statements
    else:
        params = func.params
        body_stmts = func.body
    body_code: List[Instr] = []
    symtab = ScopedSymbolTable()
    for stmt in body_stmts:
        body_code.extend(_compile_stmt(stmt, alias_map, symtab, type_registry))
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            body_code.append(DestructorCall(sym.name))
    return Function(func.name, params, body_code)


def _compile_destructor(
    struct_name: str,
    destructor: DestructorDef,
    alias_map: Dict[str, str],
    type_registry: Dict[str, TypeInfo] | None,
) -> Function:
    params = ["self"]
    body_code: List[Instr] = []
    symtab = ScopedSymbolTable()
    symtab.add_symbol(Symbol("self", struct_name, False))
    for stmt in destructor.body.statements:
        body_code.extend(_compile_stmt(stmt, alias_map, symtab, type_registry))
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            body_code.append(DestructorCall(sym.name))
    name = f"{struct_name}_destructor"
    return Function(name, params, body_code)


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
            elif isinstance(instr, Return):
                return stack.pop() if stack else None
            elif isinstance(instr, DestructorCall):
                # Destructor calls are placeholders in the interpreter.
                pass
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
    if c_name == "read":
        import os

        fd = int(args[0])
        buf = args[1]
        count = int(args[2])
        data = os.read(fd, count)
        if isinstance(buf, bytearray):
            buf[: len(data)] = data
        return len(data)
    if c_name == "open":
        import os

        path = str(args[0])
        flags = int(args[1])
        mode = int(args[2])
        return os.open(path, flags, mode)
    if c_name == "close":
        import os

        fd = int(args[0])
        os.close(fd)
        return 0
    if c_name == "time_now":
        import time

        return int(time.time())
    if c_name == "random_rand":
        import random

        return int(random.randint(0, 2**31 - 1))
    if c_name == "print":
        print(*args)
        return 0
    if c_name == "time":
        return int(_libc_time(None))
    if c_name == "rand":
        return int(_libc_rand())
    raise RuntimeError(f"Foreign function {c_name} not implemented")


# ------------ LLVM IR Generation ---------------------------------------------

def to_llvm_ir(program: ProgramIR) -> str:
    """Convert :class:`ProgramIR` to LLVM IR string using the new LLVM backend."""
    from .llvm import compile_to_llvm
    return compile_to_llvm(program)


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

    from ctypes import CFUNCTYPE, c_longlong


    engine.finalize_object()
    func_ptr = engine.get_function_address("__start")

    cfunc = CFUNCTYPE(c_longlong)(func_ptr)
    result = cfunc()
    return int(result)

