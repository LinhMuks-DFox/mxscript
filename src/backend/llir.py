from __future__ import annotations

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
