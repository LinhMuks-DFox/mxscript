from __future__ import annotations

from typing import Dict, List

from llvmlite import ir

from ..llir import (
    Instr,
    Const,
    Load,
    Store,
    BinOpInstr,
    Call,
    Return,
    Pop,
    Function,
)
from .context import LLVMContext
from .ffi import FFIManager


class LLVMGenerator:
    """Generate LLVM IR from :class:`ProgramIR`."""

    def __init__(self, context: LLVMContext) -> None:
        self.ctx = context
        self.ffi = FFIManager(self.ctx.module)
        self.functions: Dict[str, ir.Function] = {}
        self.string_idx = 0

    # ------------------------------------------------------------------
    def declare_functions(self, program) -> None:
        for func in program.functions.values():
            ty = ir.FunctionType(self.ctx.int_t, [self.ctx.int_t] * len(func.params))
            self.functions[func.name] = ir.Function(self.ctx.module, ty, name=func.name)
        for name in program.foreign_functions:
            try:
                self.ffi.get_or_declare_function(name)
            except KeyError:
                ir.Function(
                    self.ctx.module,
                    ir.FunctionType(self.ctx.int_t, [], var_arg=True),
                    name=name,
                )

    # Symbol table helpers ---------------------------------------------
    def _get_or_alloc_mut(self, name: str) -> ir.AllocaInstr:
        try:
            ptr = self.ctx.get_var(name)
            if isinstance(ptr.type, ir.PointerType):
                return ptr
        except KeyError:
            pass
        assert self.ctx.entry_builder is not None
        ptr = self.ctx.entry_builder.alloca(self.ctx.int_t, name=name)
        self.ctx.set_var(name, ptr)
        return ptr

    # IR emission ------------------------------------------------------
    def _emit_code(self, code: List[Instr]) -> ir.Value | None:
        assert self.ctx.builder is not None
        stack: List[ir.Value] = []
        for instr in code:
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
            elif isinstance(instr, Store):
                val = stack.pop()
                if instr.is_mut:
                    ptr = self._get_or_alloc_mut(instr.name)
                    self.ctx.builder.store(val, ptr)
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
                    callee = self.ctx.module.get_global(instr.name)
                stack.append(self.ctx.builder.call(callee, args))
            elif isinstance(instr, Return):
                ret_val = stack.pop() if stack else ir.Constant(self.ctx.int_t, 0)
                self.ctx.builder.ret(ret_val)
                return None
            elif isinstance(instr, Pop):
                if stack:
                    stack.pop()
            else:
                raise RuntimeError(f"Unknown instruction {instr}")
        return stack[-1] if stack else None

    # ------------------------------------------------------------------
    def build_function(self, func_ir: Function) -> None:
        func = self.functions[func_ir.name]
        entry = func.append_basic_block("entry")
        self.ctx.builder = ir.IRBuilder(entry)
        self.ctx.entry_builder = self.ctx.builder
        self.ctx.push_scope()
        for arg, name in zip(func.args, func_ir.params):
            self.ctx.set_var(name, arg)
        ret = self._emit_code(func_ir.code)
        if ret is not None:
            self.ctx.builder.ret(ret)
        self.ctx.pop_scope()

    def build_start(self, code: List[Instr]) -> None:
        start_ty = ir.FunctionType(self.ctx.int_t, [])
        fn = ir.Function(self.ctx.module, start_ty, name="__start")
        block = fn.append_basic_block("entry")
        self.ctx.builder = ir.IRBuilder(block)
        self.ctx.entry_builder = self.ctx.builder
        ret = self._emit_code(code)
        if ret is not None:
            self.ctx.builder.ret(ret)
