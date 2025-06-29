from __future__ import annotations

from .ast import (
    BinaryOp,
    ExprStmt,
    Identifier,
    Integer,
    LetStmt,
    BindingStmt,
    ReturnStmt,
    Program,
    String,
    UnaryOp,
)


def dump_ast(node, indent: int = 0) -> str:
    """Return a readable multi-line string representation of the AST."""
    prefix = "  " * indent
    if isinstance(node, Program):
        lines = [prefix + "Program"]
        for stmt in node.statements:
            lines.append(dump_ast(stmt, indent + 1))
        return "\n".join(lines)
    if isinstance(node, LetStmt):
        lines = [prefix + f"LetStmt(name={node.name})", dump_ast(node.value, indent + 1)]
        return "\n".join(lines)
    if isinstance(node, BindingStmt):
        kind = "static" if node.is_static else "dynamic"
        lines = [prefix + f"BindingStmt({kind}, name={node.name})", dump_ast(node.value, indent + 1)]
        return "\n".join(lines)
    if isinstance(node, ExprStmt):
        lines = [prefix + "ExprStmt", dump_ast(node.expr, indent + 1)]
        return "\n".join(lines)
    if isinstance(node, Integer):
        return prefix + f"Integer({node.value})"
    if isinstance(node, String):
        return prefix + f"String({node.value!r})"
    if isinstance(node, Identifier):
        return prefix + f"Identifier({node.name})"
    if isinstance(node, BinaryOp):
        lines = [prefix + f"BinaryOp({node.op})", dump_ast(node.left, indent + 1), dump_ast(node.right, indent + 1)]
        return "\n".join(lines)
    if isinstance(node, UnaryOp):
        lines = [prefix + f"UnaryOp({node.op})", dump_ast(node.operand, indent + 1)]
        return "\n".join(lines)
    if isinstance(node, ReturnStmt):
        lines = [prefix + "ReturnStmt"]
        if node.value is not None:
            lines.append(dump_ast(node.value, indent + 1))
        return "\n".join(lines)
    if hasattr(node, "__class__") and node.__class__.__name__ == "ForeignFuncDecl":
        lines = [
            prefix + f"ForeignFuncDecl(name={node.name}, c_name={node.c_name})",
            dump_ast(node.signature, indent + 1),
        ]
        return "\n".join(lines)
    return prefix + repr(node)
