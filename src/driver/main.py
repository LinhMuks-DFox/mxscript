from __future__ import annotations

import argparse
from pathlib import Path

from ..lexer import TokenStream, tokenize
from ..syntax_parser import Parser, dump_ast
from ..semantic_analyzer import SemanticAnalyzer
from ..backend import (
    compile_program,
    execute,
    execute_llvm,
    optimize,
    to_llvm_ir,
)



def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MxScript driver")
    parser.add_argument("source", help="MxScript source file")
    parser.add_argument("--dump-llir", action="store_true", help="print LLVM IR")
    parser.add_argument(
        "--compile-mode",
        choices=["interpreter", "llvm"],
        default="interpreter",
        help="execution backend",
    )
    parser.add_argument("-o", "--output", help="write LLVM IR to file")
    parser.add_argument(
        "-O", "--optimization", type=int, default=0, help="optimization level"
    )
    parser.add_argument("--dump-ast", action="store_true", help="print parsed AST")

    args = parser.parse_args(argv)

    path = Path(args.source)
    source = path.read_text()
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    parser_obj = Parser(stream)
    ast = parser_obj.parse()

    if args.dump_ast:
        print(dump_ast(ast))

    sema = SemanticAnalyzer()
    sema.analyze(ast)

    ir_prog = compile_program(ast)
    if args.optimization > 0:
        ir_prog = optimize(ir_prog)

    if args.dump_llir or args.output:
        llvm_ir = to_llvm_ir(ir_prog)
        if args.dump_llir:
            print(llvm_ir)
        if args.output:
            Path(args.output).write_text(llvm_ir)

    if args.compile_mode == "interpreter":
        result = execute(ir_prog)
    else:
        result = execute_llvm(ir_prog)

    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
