"""Command-line interface for testing the lexer and parser."""

from __future__ import annotations

import sys
from pathlib import Path

from ..lexer import TokenStream, tokenize
from ..syntax_parser import Parser, dump_ast


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


if __name__ == "__main__":
    main()
