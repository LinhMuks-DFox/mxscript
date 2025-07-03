from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from llvmlite import ir


@dataclass
class LLVMContext:
    """Context object holding LLVM generation state."""

    module: ir.Module
    builder: ir.IRBuilder | None
    entry_builder: ir.IRBuilder | None
    scopes: List[Dict[str, ir.Value]]
    int_t: ir.IntType
    obj_ptr_t: ir.PointerType
    globals: Dict[str, ir.GlobalVariable]

    def __init__(self, module_name: str = "mxscript") -> None:
        self.module = ir.Module(name=module_name)
        self.builder = None
        self.entry_builder = None
        self.int_t = ir.IntType(64)
        self.obj_ptr_t = ir.IntType(8).as_pointer()
        self.scopes = [{}]
        self.globals = {}

    # scope helpers -------------------------------------------------
    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> None:
        self.scopes.pop()

    def set_var(self, name: str, value: ir.Value) -> None:
        self.scopes[-1][name] = value

    def get_var(self, name: str) -> ir.Value:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise KeyError(name)

    # global variable helpers ---------------------------------------
    def get_global(self, name: str) -> ir.GlobalVariable:
        if name not in self.globals:
            g = ir.GlobalVariable(self.module, self.obj_ptr_t, name=name)
            g.linkage = "internal"
            g.initializer = ir.Constant(self.obj_ptr_t, None)
            self.globals[name] = g
        return self.globals[name]
