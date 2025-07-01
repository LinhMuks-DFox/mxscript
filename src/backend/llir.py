from __future__ import annotations

from dataclasses import dataclass
from typing import Union
import subprocess
from pathlib import Path
import os

from llvmlite import binding

from .compiler import (
    build_search_paths,
    load_module_ast,
    compile_program,
    optimize,
)
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
    ErrorValue,
)
from .runtime import execute

_RUNTIME_LOADED = False


def _load_arc_runtime() -> None:
    """Compile and load the ARC runtime as a shared library."""
    global _RUNTIME_LOADED
    if _RUNTIME_LOADED:
        return

    base_dir = Path(__file__).resolve().parents[2]
    src_path = base_dir / "runtime" / "arc_runtime.c"
    so_path = base_dir / "runtime" / "arc_runtime.so"

    if not so_path.exists():
        subprocess.run(
            [
                "clang",
                "-shared",
                "-fPIC",
                "-o",
                str(so_path),
                str(src_path),
            ],
            check=True,
        )

    binding.load_library_permanently(str(so_path))
    _RUNTIME_LOADED = True

class LLIRInstr:
    """Base class for low-level IR instructions."""


@dataclass
class Label(LLIRInstr):
    """A labeled jump target."""

    name: str


@dataclass
class Br(LLIRInstr):
    """Unconditional branch to ``label``."""

    label: str


@dataclass
class CondBr(LLIRInstr):
    """Conditional branch based on ``cond``."""

    cond: str
    then_label: str
    else_label: str

LLIRInstr = Union[
    Instr,
    Const,
    Alloc,
    Dup,
    Load,
    Store,
    BinOpInstr,
    Pop,
    Call,
    Return,
    DestructorCall,
    ScopeEnter,
    ScopeExit,
    Label,
    Br,
    CondBr,
]

__all__ = [
    "Const",
    "Load",
    "Store",
    "BinOpInstr",
    "Alloc",
    "Dup",
    "Pop",
    "Call",
    "Function",
    "Return",
    "DestructorCall",
    "ScopeEnter",
    "ScopeExit",
    "Label",
    "Br",
    "CondBr",
    "ProgramIR",
    "Instr",
    "ErrorValue",
    "compile_program",
    "optimize",
    "execute",
    "build_search_paths",
    "load_module_ast",
    "to_llvm_ir",
    "execute_llvm",
]


def to_llvm_ir(program: ProgramIR) -> str:
    """Convert :class:`ProgramIR` to LLVM IR string using the new LLVM backend."""
    from .llvm import compile_to_llvm

    return compile_to_llvm(program)


def execute_llvm(program: ProgramIR) -> int:
    """JIT compile and execute program via LLVM."""
    _load_arc_runtime()

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
