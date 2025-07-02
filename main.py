from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser, dump_ast
from src.semantic_analyzer import SemanticAnalyzer
from src.errors import CompilerError, SourceLocation
from src.backend import (
    compile_program,
    execute_llvm,
    to_llvm_ir,
    build_search_paths,
)


def print_error(err: CompilerError) -> None:
    print(f"Error: {err.message}", file=sys.stderr)
    if err.location:
        loc = err.location
        print(f"  --> {loc.filename}:{loc.line}:{loc.column}", file=sys.stderr)
        print(f"{loc.line:4} | {loc.source_line}", file=sys.stderr)
        print(f"{' ' * 4} | {' ' * (loc.column - 1)}^", file=sys.stderr)



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MxScript driver")
    parser.add_argument("source", help="MxScript source file")
    parser.add_argument("--dump-llir", action="store_true", help="print LLVM IR")
    parser.add_argument("-o", "--output", help="write LLVM IR to file")
    parser.add_argument("--dump-ast", action="store_true", help="print parsed AST")
    parser.add_argument(
        "-I",
        "--search-path",
        action="append",
        dest="search_paths",
        help="additional module search path",
    )

    args = parser.parse_args(argv)

    path = Path(args.source)
    source = path.read_text()

    try:
        tokens = tokenize(source)
        stream = TokenStream(tokens)
        parser_obj = Parser(stream, source=source, filename=str(path))
        ast = parser_obj.parse()

        if args.dump_ast:
            print(dump_ast(ast))

        sema = SemanticAnalyzer()
        sema.analyze(ast, source=source, filename=str(path))

        search_paths = build_search_paths(args.search_paths)
        ir_prog = compile_program(ast, search_paths=search_paths)

        if args.dump_llir or args.output:
            llvm_ir = to_llvm_ir(ir_prog)
            if args.dump_llir:
                print(llvm_ir)
            if args.output:
                Path(args.output).write_text(llvm_ir)

        result = execute_llvm(ir_prog)
    except CompilerError as e:
        print_error(e)
        return 1

    return int(result) if result is not None else 0


if __name__ == "__main__":
    sys.exit(main())
