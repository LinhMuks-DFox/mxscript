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


def _load_runtime() -> None:
    """
    Check for the runtime library in the project's bin/ directory.
    If not found, configure and build it using CMake.
    Finally, load the shared library.
    """
    global _RUNTIME_LOADED
    if _RUNTIME_LOADED:
        return
    base_dir = Path(__file__).resolve().parents[2]
    runtime_dir = base_dir / "runtime"
    build_dir = runtime_dir / "build"
    so_path = base_dir / "bin" / "libruntime.so"
    extra = os.environ.get("MXSCRIPT_EXTRA_RUNTIMES", "")
    extra_libs = [Path(p) for p in extra.split(os.pathsep) if p]

    if not so_path.exists():
        print("Runtime library not found. Building...")
        build_dir.mkdir(exist_ok=True)

        subprocess.run(
            ["cmake", str(runtime_dir)],
            cwd=build_dir, # 在构建目录中运行
            check=True,
        )

        subprocess.run(
            ["cmake", "--build", "."],
            cwd=build_dir, # 在构建目录中运行
            check=True,
        )
        print("Runtime library built successfully.")

    # --- 加载共享库 ---
    binding.load_library_permanently(str(so_path))
    for lib in extra_libs:
        if lib.exists():
            binding.load_library_permanently(str(lib))
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
    _load_runtime()

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
