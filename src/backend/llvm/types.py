from __future__ import annotations

from llvmlite import ir


def to_llvm_type(mxscript_type: str) -> ir.Type:
    """Convert a simple MxScript type name to an LLVM type."""
    if mxscript_type == "int":
        return ir.IntType(64)
    if mxscript_type == "byte*":
        return ir.IntType(8).as_pointer()
    raise ValueError(f"Unknown MxScript type: {mxscript_type}")
