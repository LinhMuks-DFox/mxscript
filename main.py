from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.frontend import TokenStream, tokenize
from src.syntax_parser import Parser, dump_ast
from src.syntax_parser.ast import Program
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
    parser.add_argument("source", nargs="?", help="MxScript source file")
    parser.add_argument("--dump-llvm", action="store_true", help="print LLVM IR")
    parser.add_argument("--dump-tokens", action="store_true", help="print token list")
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

    if args.source is None:
        from src.cui.shell import run_shell
        return run_shell()

    path = Path(args.source)
    source = path.read_text()

    builtin_path = Path(__file__).resolve().parent / "stdlib" / "_builtin.mxs"
    builtin_source = builtin_path.read_text()

    try:
        builtin_tokens = tokenize(builtin_source)
        builtin_stream = TokenStream(builtin_tokens)
        builtin_parser = Parser(
            builtin_stream, source=builtin_source, filename=str(builtin_path)
        )
        builtin_ast = builtin_parser.parse()

        tokens = tokenize(source)
        if args.dump_tokens:
            print(tokens)
            return 0

        stream = TokenStream(tokens)
        parser_obj = Parser(stream, source=source, filename=str(path))
        user_ast = parser_obj.parse()

        ast = Program(builtin_ast.statements + user_ast.statements)

        if args.dump_ast:
            print(dump_ast(ast))
            return 0

        combined_source = builtin_source + "\n" + source

        sema = SemanticAnalyzer()
        sema.analyze(ast, source=combined_source, filename=str(path))

        search_paths = build_search_paths(args.search_paths)
        ir_prog = compile_program(ast, search_paths=search_paths)

        if args.dump_llvm or args.output:
            llvm_ir = to_llvm_ir(ir_prog)
            if args.dump_llvm:
                print(llvm_ir)
                if not args.output:
                    return 0
            if args.output:
                Path(args.output).write_text(llvm_ir)
                if not args.dump_llvm:
                    return 0

        result = execute_llvm(ir_prog)
    except CompilerError as e:
        print_error(e)
        return 1

    return int(result) if result is not None else 0


if __name__ == "__main__":
    sys.exit(main())
