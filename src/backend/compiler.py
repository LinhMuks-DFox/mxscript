from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import os

from ..lexer import TokenStream, tokenize
from ..syntax_parser import Parser
from ..syntax_parser.ast import (
    BinaryOp,
    Block,
    ExprStmt,
    FunctionCall,
    FunctionDecl,
    FuncDef,
    AssignExpr,
    ForeignFuncDecl,
    Identifier,
    Integer,
    MemberAccess,
    MemberAssign,
    RaiseStmt,
    RaiseExpr,
    String,
    LetStmt,
    BindingStmt,
    ClassDef,
    DestructorDef,
    ConstructorDef,
    ReturnStmt,
    ImportStmt,
    ForInStmt,
    LoopStmt,
    UntilStmt,
    DoUntilStmt,
    BreakStmt,
    ContinueStmt,
    IfStmt,
    Program,
    UnaryOp,
)
from ..semantic_analyzer.types import TypeInfo
from ..middleend.symbols import ScopedSymbolTable, Symbol

from .ir import (
    ProgramIR,
    Instr,
    Const,
    Alloc,
    Dup,
    Load,
    Store,
    BinOpInstr,
    Pop,
    Call,
    Function,
    Return,
    DestructorCall,
    ScopeEnter,
    ScopeExit,
)
from .runtime import _apply_op
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .llir import Label, Br, CondBr

STD_LIB_DIR = Path(__file__).resolve().parents[2] / "stdlib"
ENV_VAR = "MXSCRIPT_PATH"

# Global counters for generating unique labels and temporaries
_label_counter = 0
_temp_counter = 0


def _new_label(prefix: str) -> str:
    """Generate a unique label name."""
    global _label_counter
    _label_counter += 1
    return f".{prefix}_{_label_counter}"


def _new_temp() -> str:
    """Generate a unique temporary variable name."""
    global _temp_counter
    _temp_counter += 1
    return f"__tmp_{_temp_counter}"


def build_search_paths(extra_paths: List[str | Path] | None = None) -> List[Path]:
    """Return module search paths including stdlib and user overrides."""
    paths: List[Path] = [STD_LIB_DIR]
    env = os.environ.get(ENV_VAR)
    if env:
        for p in env.split(os.pathsep):
            if p:
                paths.append(Path(p))
    if extra_paths:
        paths.extend(Path(p) for p in extra_paths)
    return paths


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


# ------------ Compilation -----------------------------------------------------

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
        elif isinstance(stmt, ClassDef):
            for member in stmt.body.statements:
                if isinstance(member, DestructorDef):
                    dtor_ir = _compile_destructor(
                        stmt.name, member, alias_map, type_registry
                    )
                    functions[dtor_ir.name] = dtor_ir
                elif isinstance(member, ConstructorDef):
                    ctor_ir = _compile_constructor(
                        stmt.name, member, alias_map, type_registry
                    )
                    functions[ctor_ir.name] = ctor_ir
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
            code.extend(
                _compile_stmt(stmt, alias_map, symtab, type_registry, break_targets=[])
            )
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
    break_targets: List[tuple[str, str]],
) -> List[Instr]:
    if isinstance(stmt, LetStmt):
        code: List[Instr] = []
        if stmt.value is not None:
            code.extend(_compile_expr(stmt.value, alias_map, symtab, type_registry))

        # If assigning from another ARC-managed variable, retain the value
        if isinstance(stmt.value, Identifier) and type_registry is not None:
            sym = symtab.lookup(stmt.value.name)
            if (
                sym is not None
                and sym.type_name is not None
                and sym.type_name in type_registry
            ):
                code.append(Call("arc_retain", 1))

        resolved_type = stmt.type_name
        needs_destruction = False

        if type_registry is not None:
            if (
                resolved_type is None
                and isinstance(stmt.value, FunctionCall)
                and stmt.value.name in type_registry
                and type_registry[stmt.value.name].has_destructor
            ):
                resolved_type = stmt.value.name
                needs_destruction = True
            elif (
                resolved_type is not None
                and resolved_type in type_registry
                and type_registry[resolved_type].has_destructor
            ):
                needs_destruction = True

        for name in stmt.names:
            code.append(Store(name, resolved_type, stmt.is_mut))
            symtab.add_symbol(Symbol(name, resolved_type, needs_destruction))
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
        code: List[Instr] = [ScopeEnter()]
        symtab.enter_scope()
        for s in stmt.statements:
            code.extend(
                _compile_stmt(s, alias_map, symtab, type_registry, break_targets)
            )
        scope = symtab.leave_scope()
        for sym in reversed(list(scope.values())):
            if sym.needs_destruction:
                code.append(DestructorCall(sym.name))
        code.append(ScopeExit())
        return code
    if isinstance(stmt, IfStmt):
        from .llir import Label, Br, CondBr  # local import to avoid circular

        code: List[Instr] = []
        then_label = _new_label("if_then")
        end_label = _new_label("if_end")
        else_label = _new_label("if_else") if stmt.else_block is not None else None

        code.extend(_compile_expr(stmt.condition, alias_map, symtab, type_registry))
        cond_var = _new_temp()
        code.append(Store(cond_var))

        if stmt.else_block is not None:
            code.append(
                CondBr(cond=cond_var, then_label=then_label, else_label=else_label)
            )
        else:
            code.append(
                CondBr(cond=cond_var, then_label=then_label, else_label=end_label)
            )

        # then block
        code.append(Label(name=then_label))
        code.extend(
            _compile_stmt(
                stmt.then_block,
                alias_map,
                symtab,
                type_registry,
                break_targets,
            )
        )
        if stmt.else_block is not None:
            code.append(Br(label=end_label))

        # else block
        if stmt.else_block is not None:
            code.append(Label(name=else_label))
            code.extend(
                _compile_stmt(
                    stmt.else_block,
                    alias_map,
                    symtab,
                    type_registry,
                    break_targets,
                )
            )

        # end label
        code.append(Label(name=end_label))
        return code
    if isinstance(stmt, ExprStmt):
        return _compile_expr(stmt.expr, alias_map, symtab, type_registry)
    if isinstance(stmt, LoopStmt):
        from .llir import Label, Br
        code: List[Instr] = []
        body_label = _new_label("loop_body")
        end_label = _new_label("loop_end")
        code.append(Label(name=body_label))
        break_targets.append((end_label, body_label))
        code.extend(
            _compile_stmt(stmt.body, alias_map, symtab, type_registry, break_targets)
        )
        break_targets.pop()
        code.append(Br(label=body_label))
        code.append(Label(name=end_label))
        return code
    if isinstance(stmt, UntilStmt):
        from .llir import Label, Br, CondBr
        code: List[Instr] = []
        cond_label = _new_label("until_cond")
        body_label = _new_label("until_body")
        end_label = _new_label("until_end")
        code.append(Br(label=cond_label))
        code.append(Label(name=cond_label))
        code.append(ScopeEnter())
        symtab.enter_scope()
        code.extend(_compile_expr(stmt.condition, alias_map, symtab, type_registry))
        cond_var = _new_temp()
        code.append(Store(cond_var))
        code.append(CondBr(cond=cond_var, then_label=end_label, else_label=body_label))
        symtab.leave_scope()
        code.append(ScopeExit())
        code.append(Label(name=body_label))
        break_targets.append((end_label, cond_label))
        code.extend(
            _compile_stmt(stmt.body, alias_map, symtab, type_registry, break_targets)
        )
        break_targets.pop()
        code.append(Br(label=cond_label))
        code.append(Label(name=end_label))
        return code
    if isinstance(stmt, DoUntilStmt):
        from .llir import Label, CondBr
        code: List[Instr] = []
        body_label = _new_label("do_body")
        end_label = _new_label("do_end")
        code.append(Label(name=body_label))
        break_targets.append((end_label, body_label))
        code.extend(
            _compile_stmt(stmt.body, alias_map, symtab, type_registry, break_targets)
        )
        break_targets.pop()
        code.append(ScopeEnter())
        symtab.enter_scope()
        code.extend(_compile_expr(stmt.condition, alias_map, symtab, type_registry))
        cond_var = _new_temp()
        code.append(Store(cond_var))
        code.append(CondBr(cond=cond_var, then_label=end_label, else_label=body_label))
        symtab.leave_scope()
        code.append(ScopeExit())
        code.append(Label(name=end_label))
        return code
    if isinstance(stmt, ForInStmt):
        from .llir import Label, Br, CondBr
        code: List[Instr] = []
        cond_label = _new_label("for_cond")
        body_label = _new_label("for_body")
        end_label = _new_label("for_end")
        code.extend(_compile_expr(stmt.iterable, alias_map, symtab, type_registry))
        code.append(Call("iter_start", 1))
        iter_reg = _new_temp()
        code.append(Store(iter_reg))
        code.append(Br(label=cond_label))
        code.append(Label(name=cond_label))
        code.append(ScopeEnter())
        symtab.enter_scope()
        code.append(Load(iter_reg))
        code.append(Call("iter_has_next", 1))
        has_next = _new_temp()
        code.append(Store(has_next))
        code.append(CondBr(cond=has_next, then_label=body_label, else_label=end_label))
        symtab.leave_scope()
        code.append(ScopeExit())
        code.append(Label(name=body_label))
        code.append(ScopeEnter())
        symtab.enter_scope()
        code.append(Load(iter_reg))
        code.append(Call("iter_next", 1))
        code.append(Store(stmt.var, None, stmt.is_mut))
        symtab.add_symbol(Symbol(stmt.var, None, False))
        break_targets.append((end_label, cond_label))
        for s in stmt.body.statements:
            code.extend(
                _compile_stmt(s, alias_map, symtab, type_registry, break_targets)
            )
        break_targets.pop()
        scope = symtab.leave_scope()
        for sym in reversed(list(scope.values())):
            if sym.needs_destruction:
                code.append(DestructorCall(sym.name))
        code.append(ScopeExit())
        code.append(Br(label=cond_label))
        code.append(Label(name=end_label))
        return code
    if isinstance(stmt, BreakStmt):
        from .llir import Br
        target = break_targets[-1][0]
        return [Br(label=target)]
    if isinstance(stmt, ContinueStmt):
        from .llir import Br
        target = break_targets[-1][1]
        return [Br(label=target)]
    if isinstance(stmt, RaiseStmt):
        code = _compile_expr(stmt.expr, alias_map, symtab, type_registry)
        for scope in reversed(symtab.scopes):
            for sym in reversed(list(scope.values())):
                if sym.needs_destruction:
                    code.append(DestructorCall(sym.name))
        code.append(Return())
        return code
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
    if isinstance(expr, RaiseExpr):
        return _compile_expr(expr.expr, alias_map, symtab, type_registry)
    if isinstance(expr, MemberAssign):
        code = _compile_expr(expr.value, alias_map, symtab, type_registry)

        if isinstance(expr.value, Identifier) and type_registry is not None:
            sym = symtab.lookup(expr.value.name)
            if (
                sym is not None
                and sym.type_name is not None
                and sym.type_name in type_registry
            ):
                code.append(Call("arc_retain", 1))

        name = _flatten_member(MemberAccess(expr.object, expr.member))
        resolved_type = None
        if (
            isinstance(expr.object, Identifier)
            and type_registry is not None
        ):
            obj_sym = symtab.lookup(expr.object.name)
            if (
                obj_sym is not None
                and obj_sym.type_name is not None
                and obj_sym.type_name in type_registry
            ):
                resolved_type = type_registry[obj_sym.type_name].members.get(
                    expr.member.name
                )

        code.append(Store(name, resolved_type))
        return code
    if isinstance(expr, AssignExpr):
        code = _compile_expr(expr.value, alias_map, symtab, type_registry)

        if isinstance(expr.value, Identifier) and type_registry is not None:
            sym = symtab.lookup(expr.value.name)
            if (
                sym is not None
                and sym.type_name is not None
                and sym.type_name in type_registry
            ):
                code.append(Call("arc_retain", 1))

        if not isinstance(expr.target, Identifier):
            raise NotImplementedError("Invalid assignment target")

        target_sym = symtab.lookup(expr.target.name)
        resolved_type = target_sym.type_name if target_sym is not None else None
        is_mut = target_sym.type_name is None if target_sym is not None else False
        code.append(Store(expr.target.name, resolved_type, is_mut))
        return code
    if isinstance(expr, BinaryOp):
        return _compile_expr(expr.left, alias_map, symtab, type_registry) + _compile_expr(expr.right, alias_map, symtab, type_registry) + [BinOpInstr(expr.op)]
    if isinstance(expr, UnaryOp):
        # Only unary '-' supported
        if expr.op == '-':
            return [Const(0)] + _compile_expr(expr.operand, alias_map, symtab, type_registry) + [BinOpInstr('-')]
    if isinstance(expr, FunctionCall):
        code: List[Instr] = []
        if type_registry is not None and expr.name in type_registry:
            # struct instantiation
            code.append(Alloc(0))
            code.append(Dup())
            for arg in expr.args:
                code.extend(_compile_expr(arg, alias_map, symtab, type_registry))
                if isinstance(arg, Identifier) and type_registry is not None:
                    sym = symtab.lookup(arg.name)
                    if (
                        sym is not None
                        and sym.type_name is not None
                        and sym.type_name in type_registry
                    ):
                        code.append(Call("arc_retain", 1))
            code.append(Call(f"{expr.name}_constructor", len(expr.args) + 1))
            code.append(Pop())
            return code
        for arg in expr.args:
            code.extend(_compile_expr(arg, alias_map, symtab, type_registry))
            if isinstance(arg, Identifier) and type_registry is not None:
                sym = symtab.lookup(arg.name)
                if (
                    sym is not None
                    and sym.type_name is not None
                    and sym.type_name in type_registry
                ):
                    code.append(Call("arc_retain", 1))
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
    break_targets: List[tuple[str, str]] = []
    for stmt in body_stmts:
        body_code.extend(
            _compile_stmt(stmt, alias_map, symtab, type_registry, break_targets)
        )
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            body_code.append(DestructorCall(sym.name))
    return Function(func.name, params, body_code)


def _compile_constructor(
    class_name: str,
    constructor: ConstructorDef,
    alias_map: Dict[str, str],
    type_registry: Dict[str, TypeInfo] | None,
) -> Function:
    params = ["self"] + [n for p in constructor.signature.params for n in p.names]
    body_code: List[Instr] = []
    symtab = ScopedSymbolTable()
    symtab.add_symbol(Symbol("self", class_name, False))
    break_targets: List[tuple[str, str]] = []
    for stmt in constructor.body.statements:
        body_code.extend(
            _compile_stmt(stmt, alias_map, symtab, type_registry, break_targets)
        )
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            body_code.append(DestructorCall(sym.name))
    name = f"{class_name}_constructor"
    return Function(name, params, body_code)


def _compile_destructor(
    class_name: str,
    destructor: DestructorDef,
    alias_map: Dict[str, str],
    type_registry: Dict[str, TypeInfo] | None,
) -> Function:
    params = ["self"]
    body_code: List[Instr] = []
    symtab = ScopedSymbolTable()
    symtab.add_symbol(Symbol("self", class_name, False))
    break_targets: List[tuple[str, str]] = []
    for stmt in destructor.body.statements:
        body_code.extend(
            _compile_stmt(stmt, alias_map, symtab, type_registry, break_targets)
        )
    for sym in reversed(list(symtab.scopes[-1].values())):
        if sym.needs_destruction:
            body_code.append(DestructorCall(sym.name))
    name = f"{class_name}_destructor"
    return Function(name, params, body_code)


# ------------ Optimization ----------------------------------------------------

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
