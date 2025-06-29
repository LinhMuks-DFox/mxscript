"""Command-line interface for testing the full compiler pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

from ..lexer import TokenStream, tokenize
from ..syntax_parser import Parser, dump_ast
from ..semantic_analyzer import SemanticAnalyzer
from ..backend import compile_program, optimize, execute


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m src.driver.main <source-file>")
        return

    path = Path(sys.argv[1])
    source = path.read_text()
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    parser = Parser(stream)
    ast = parser.parse()
    print(dump_ast(ast))

    # Semantic analysis
    SemanticAnalyzer().analyze(ast)

    # Backend
    code = compile_program(ast)
    code = optimize(code)
    result = execute(code)
    print("Program result:", result)


if __name__ == "__main__":
    main()
