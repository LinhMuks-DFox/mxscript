from __future__ import annotations

from typing import Dict, List

from llvmlite import ir

from ..llir import (
    Instr,
    Const,
    Load,
    Store,
    BinOpInstr,
    Alloc,
    Dup,
    Call,
    Return,
    Pop,
    DestructorCall,
    Function,
    ScopeEnter,
    ScopeExit,
    Label,
    Br,
    CondBr,
)
from .context import LLVMContext
from ..ffi import FFIManager


class LLVMGenerator:
    """Generate LLVM IR from :class:`ProgramIR`."""

    def __init__(self, context: LLVMContext) -> None:
        self.ctx = context
        self.ffi = FFIManager(self.ctx.module)
        self.functions: Dict[str, ir.Function] = {}
        self.string_idx = 0
        self.var_info_stack: List[Dict[str, Dict[str, ir.Value | str | None]]] = []
        # Mapping of label names to LLVM basic blocks for the current function
        self.blocks: Dict[str, ir.Block] = {}

    # ------------------------------------------------------------------
    def declare_functions(self, program) -> None:
        for func in program.functions.values():
            arg_types = [self.ctx.int_t] * len(func.params)
            if func.name.endswith("_destructor"):
                arg_types = [self.ctx.int_t.as_pointer()]
            elif func.name.endswith("_constructor"):
                arg_types = [self.ctx.int_t.as_pointer()] + [self.ctx.int_t] * (len(func.params) - 1)
            ty = ir.FunctionType(self.ctx.int_t, arg_types)
            self.functions[func.name] = ir.Function(self.ctx.module, ty, name=func.name)
        for alias, c_name in program.foreign_functions.items():
            try:
                func = self.ffi.get_or_declare_function(c_name)
            except KeyError:
                func = ir.Function(
                    self.ctx.module,
                    ir.FunctionType(self.ctx.int_t, [], var_arg=True),
                    name=c_name,
                )
            self.functions[alias] = func

    # Symbol table helpers ---------------------------------------------
    def _get_or_alloc_mut(self, name: str) -> ir.AllocaInstr:
        """Get an existing alloca from the **current** scope or allocate a new one."""
        current_scope = self.ctx.scopes[-1]
        val = current_scope.get(name)
        if val is not None and isinstance(val.type, ir.PointerType):
            return val

        assert self.ctx.entry_builder is not None
        ptr = self.ctx.entry_builder.alloca(self.ctx.int_t, name=name)
        current_scope[name] = ptr
        return ptr

    def _lookup_var_info(self, name: str) -> Dict[str, ir.Value | str | None]:
        for scope in reversed(self.var_info_stack):
            if name in scope:
                return scope[name]
        raise KeyError(name)

    def _process_DestructorCall(self, instr: DestructorCall) -> None:
        info = self._lookup_var_info(instr.name)
        type_name = info.get("type_name")
        ptr = info.get("ptr")
        if type_name is None or ptr is None:
            return
        func_name = f"{type_name}_destructor"
        callee = self.functions.get(func_name)
        if callee is None:
            try:
                callee = self.ctx.module.get_global(func_name)
            except KeyError:
                raise RuntimeError(f"Could not find destructor function '{func_name}'")
        self.ctx.builder.call(callee, [ptr])
        arc_release = self.ffi.get_or_declare_function("arc_release")
        loaded = self.ctx.builder.load(ptr)
        obj_ptr = self.ctx.builder.inttoptr(loaded, self.ctx.obj_ptr_t)
        self.ctx.builder.call(arc_release, [obj_ptr])
        # remove variable after destruction
        for scope in reversed(self.var_info_stack):
            if instr.name in scope:
                del scope[instr.name]
                break

    # IR emission ------------------------------------------------------
    def _emit_code(self, code: List[Instr]) -> ir.Value | None:
        assert self.ctx.builder is not None
        stack: List[ir.Value] = []
        terminated = False
        for instr in code:
            if terminated and not isinstance(instr, Label):
                continue
            if isinstance(instr, Const):
                if isinstance(instr.value, str):
                    arr_ty = ir.ArrayType(ir.IntType(8), len(instr.value.encode()) + 1)
                    const_val = ir.Constant(arr_ty, bytearray(instr.value.encode() + b"\x00"))
                    global_name = f".str{self.string_idx}"
                    gvar = ir.GlobalVariable(self.ctx.module, arr_ty, name=global_name)
                    gvar.linkage = "internal"
                    gvar.global_constant = True
                    gvar.initializer = const_val
                    ptr = self.ctx.builder.gep(gvar, [ir.Constant(self.ctx.int_t, 0), ir.Constant(self.ctx.int_t, 0)])
                    stack.append(self.ctx.builder.ptrtoint(ptr, self.ctx.int_t))
                    self.string_idx += 1
                else:
                    stack.append(ir.Constant(self.ctx.int_t, instr.value))
            elif isinstance(instr, Load):
                val = self.ctx.get_var(instr.name)
                if isinstance(val.type, ir.PointerType):
                    stack.append(self.ctx.builder.load(val))
                else:
                    stack.append(val)
            elif isinstance(instr, Alloc):
                arc_alloc = self.ffi.get_or_declare_function("arc_alloc")
                size_val = ir.Constant(self.ctx.int_t, instr.size)
                ptr = self.ctx.builder.call(arc_alloc, [size_val])
                stack.append(self.ctx.builder.ptrtoint(ptr, self.ctx.int_t))
            elif isinstance(instr, Dup):
                if stack:
                    stack.append(stack[-1])
            elif isinstance(instr, Store):
                val = stack.pop()
                if instr.is_mut or instr.type_name is not None:
                    ptr = self._get_or_alloc_mut(instr.name)

                    current_scope = self.var_info_stack[-1]
                    info = current_scope.get(instr.name)

                    # If the variable already holds an ARC-managed object,
                    # release the previous value before overwriting it.
                    if (
                        info is not None
                        and info.get("type_name") is not None
                        and info.get("ptr") is not None
                    ):
                        arc_release = self.ffi.get_or_declare_function("arc_release")
                        loaded_old = self.ctx.builder.load(info["ptr"])
                        obj_ptr = self.ctx.builder.inttoptr(loaded_old, self.ctx.obj_ptr_t)
                        self.ctx.builder.call(arc_release, [obj_ptr])

                    self.ctx.builder.store(val, ptr)

                    current_scope[instr.name] = {
                        "type_name": instr.type_name,
                        "ptr": ptr,
                    }
                else:
                    self.ctx.set_var(instr.name, val)
            elif isinstance(instr, BinOpInstr):
                b = stack.pop()
                a = stack.pop()
                op = instr.op
                if op == '+':
                    stack.append(self.ctx.builder.add(a, b))
                elif op == '-':
                    stack.append(self.ctx.builder.sub(a, b))
                elif op == '*':
                    stack.append(self.ctx.builder.mul(a, b))
                elif op == '/':
                    stack.append(self.ctx.builder.sdiv(a, b))
                elif op == '%':
                    stack.append(self.ctx.builder.srem(a, b))
                elif op == '==':
                    stack.append(self.ctx.builder.icmp_signed('==', a, b))
                elif op == '!=':
                    stack.append(self.ctx.builder.icmp_signed('!=', a, b))
                elif op == '>':
                    stack.append(self.ctx.builder.icmp_signed('>', a, b))
                elif op == '<':
                    stack.append(self.ctx.builder.icmp_signed('<', a, b))
                elif op == '>=':
                    stack.append(self.ctx.builder.icmp_signed('>=', a, b))
                elif op == '<=':
                    stack.append(self.ctx.builder.icmp_signed('<=', a, b))
                else:
                    raise RuntimeError(f"Unsupported op {op}")
            elif isinstance(instr, Call):
                args = [stack.pop() for _ in range(instr.argc)][::-1]
                callee = self.functions.get(instr.name)
                if callee is None:
                    try:
                        callee = self.ctx.module.get_global(instr.name)
                    except KeyError:
                        callee = self.ffi.get_or_declare_function(instr.name)
                func_ty = callee.function_type
                cast_args: List[ir.Value] = []
                for i, arg in enumerate(args):
                    if i < len(func_ty.args):
                        target_ty = func_ty.args[i]
                        if arg.type != target_ty:
                            if isinstance(target_ty, ir.PointerType) and isinstance(arg.type, ir.IntType):
                                arg = self.ctx.builder.inttoptr(arg, target_ty)
                            elif isinstance(target_ty, ir.IntType) and isinstance(arg.type, ir.PointerType):
                                arg = self.ctx.builder.ptrtoint(arg, target_ty)
                            elif isinstance(target_ty, ir.IntType) and isinstance(arg.type, ir.IntType):
                                if arg.type.width > target_ty.width:
                                    arg = self.ctx.builder.trunc(arg, target_ty)
                                elif arg.type.width < target_ty.width:
                                    arg = self.ctx.builder.zext(arg, target_ty)
                                # widths equal handled above
                            else:
                                arg = self.ctx.builder.bitcast(arg, target_ty)
                    cast_args.append(arg)
                result = self.ctx.builder.call(callee, cast_args)
                if result.type != self.ctx.int_t:
                    if isinstance(result.type, ir.IntType):
                        if result.type.width < self.ctx.int_t.width:
                            result = self.ctx.builder.zext(result, self.ctx.int_t)
                        elif result.type.width > self.ctx.int_t.width:
                            result = self.ctx.builder.trunc(result, self.ctx.int_t)
                    elif isinstance(result.type, ir.PointerType):
                        result = self.ctx.builder.ptrtoint(result, self.ctx.int_t)
                    else:
                        result = self.ctx.builder.bitcast(result, self.ctx.int_t)
                stack.append(result)
            elif isinstance(instr, DestructorCall):
                self._process_DestructorCall(instr)
            elif isinstance(instr, Return):
                ret_val = stack.pop() if stack else ir.Constant(self.ctx.int_t, 0)
                self.ctx.builder.ret(ret_val)
                terminated = True
                stack = []
                continue
            elif isinstance(instr, Pop):
                if stack:
                    stack.pop()
            elif isinstance(instr, ScopeEnter):
                self.var_info_stack.append({})
                self.ctx.push_scope()
            elif isinstance(instr, ScopeExit):
                self.ctx.pop_scope()
                if self.var_info_stack:
                    self.var_info_stack.pop()
            elif isinstance(instr, Label):
                block = self.blocks.get(instr.name)
                if block is None:
                    raise RuntimeError(f"Unknown label {instr.name}")
                if not terminated and not self.ctx.builder.block.is_terminated:
                    self.ctx.builder.branch(block)
                    terminated = True
                self.ctx.builder.position_at_end(block)
                terminated = False
            elif isinstance(instr, Br):
                target = self.blocks.get(instr.label)
                if target is None:
                    raise RuntimeError(f"Unknown label {instr.label}")
                self.ctx.builder.branch(target)
                terminated = True
            elif isinstance(instr, CondBr):
                cond_val = self.ctx.get_var(instr.cond)
                if isinstance(cond_val.type, ir.PointerType):
                    cond_val = self.ctx.builder.load(cond_val)
                # Ensure condition is i1 for LLVM branching
                if cond_val.type != ir.IntType(1):
                    zero = ir.Constant(cond_val.type, 0)
                    cond_val = self.ctx.builder.icmp_signed('!=', cond_val, zero)
                then_block = self.blocks.get(instr.then_label)
                else_block = self.blocks.get(instr.else_label)
                if then_block is None or else_block is None:
                    raise RuntimeError(
                        f"Unknown labels {instr.then_label} or {instr.else_label}"
                    )
                self.ctx.builder.cbranch(cond_val, then_block, else_block)
                terminated = True
            else:
                raise RuntimeError(f"Unknown instruction {instr}")
        return stack[-1] if stack else None

    # ------------------------------------------------------------------
    def build_function(self, func_ir: Function) -> None:
        func = self.functions[func_ir.name]
        entry = func.append_basic_block("entry")
        # reset blocks mapping for this function
        self.blocks = {}
        # first pass: create blocks for all labels
        for instr in func_ir.code:
            if isinstance(instr, Label):
                self.blocks[instr.name] = func.append_basic_block(instr.name)

        self.ctx.builder = ir.IRBuilder(entry)
        self.ctx.entry_builder = self.ctx.builder
        self.ctx.push_scope()
        self.var_info_stack.append({})
        for arg, name in zip(func.args, func_ir.params):
            self.ctx.set_var(name, arg)
            self.var_info_stack[-1][name] = {"type_name": None, "ptr": arg}
        ret = self._emit_code(func_ir.code)
        if ret is not None:
            self.ctx.builder.ret(ret)
        if not self.ctx.builder.block.is_terminated:
            self.ctx.builder.ret(ir.Constant(self.ctx.int_t, 0))
        self.ctx.pop_scope()
        self.var_info_stack.pop()
        # clear label map after finishing this function
        self.blocks = {}

    def build_start(self, code: List[Instr]) -> None:
        start_ty = ir.FunctionType(self.ctx.int_t, [])
        fn = ir.Function(self.ctx.module, start_ty, name="__start")
        entry = fn.append_basic_block("entry")

        # reset blocks mapping and pre-create blocks for labels
        self.blocks = {}
        for instr in code:
            if isinstance(instr, Label):
                self.blocks[instr.name] = fn.append_basic_block(instr.name)

        self.ctx.builder = ir.IRBuilder(entry)
        self.ctx.entry_builder = self.ctx.builder
        self.var_info_stack.append({})
        ret = self._emit_code(code)
        if ret is not None:
            self.ctx.builder.ret(ret)
        if not self.ctx.builder.block.is_terminated:
            self.ctx.builder.ret(ir.Constant(self.ctx.int_t, 0))
        self.var_info_stack.pop()
        # clear label map
        self.blocks = {}
