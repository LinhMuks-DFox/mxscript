from __future__ import annotations

import ctypes
from pathlib import Path

from src.frontend import tokenize, TokenStream
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, execute_llvm, build_search_paths
from src.errors import CompilerError


def _load_runtime_lib() -> ctypes.CDLL:
    """Load the runtime shared library and return its CDLL handle."""
    base_dir = Path(__file__).resolve().parents[2]
    so_path = base_dir / "bin" / "libruntime.so"
    if not so_path.exists():
        from src.backend.llir import _load_runtime

        _load_runtime()
    return ctypes.CDLL(str(so_path))


def run_shell() -> int:
    """Start an interactive MxScript REPL."""
    runtime = None
    while True:
        try:
            line = input("mxs> ")
        except EOFError:
            print()
            break

        if not line.strip():
            continue

        if line.strip() == ":mem":
            if runtime is None:
                runtime = _load_runtime_lib()
            try:
                runtime.mxs_allocator_dump_stats()
            except Exception as exc:  # pragma: no cover - debug helper
                print(f"Error calling dump_stats: {exc}")
            continue

        try:
            tokens = tokenize(line)
            stream = TokenStream(tokens)
            parser = Parser(stream, source=line, filename="<repl>")
            ast = parser.parse()

            sema = SemanticAnalyzer()
            sema.analyze(ast, source=line, filename="<repl>")

            search_paths = build_search_paths(None)
            ir = compile_program(ast, search_paths=search_paths)
            result = execute_llvm(ir)
            if result is not None:
                print(result)
        except CompilerError as e:  # pragma: no cover - debug helper
            print(f"Error: {e.message}")
    return 0

