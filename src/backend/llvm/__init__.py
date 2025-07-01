from __future__ import annotations

from .context import LLVMContext
from .generator import LLVMGenerator


def compile_to_llvm(program_ir) -> str:
    """Generate LLVM IR text for a :class:`ProgramIR`."""
    ctx = LLVMContext()
    gen = LLVMGenerator(ctx)
    gen.declare_functions(program_ir)
    gen.build_start(program_ir.code)
    for func in program_ir.functions.values():
        gen.build_function(func)
    return str(ctx.module)

__all__ = ["compile_to_llvm", "LLVMContext", "LLVMGenerator"]
