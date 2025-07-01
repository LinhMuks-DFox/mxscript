import argparse
import subprocess
import tempfile
from pathlib import Path

from src.lexer import TokenStream, tokenize
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, optimize, to_llvm_ir, build_search_paths


def compile_source(source: str, filename: str, opt_level: int, search_paths):
    tokens = tokenize(source)
    stream = TokenStream(tokens)
    parser = Parser(stream, source=source, filename=filename)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast, source=source, filename=filename)
    ir_prog = compile_program(ast, search_paths=build_search_paths(search_paths))
    if opt_level > 0:
        ir_prog = optimize(ir_prog)
    return to_llvm_ir(ir_prog)


def build_executable(source_file: Path, output: Path, opt_level: int = 0, search_paths=None):
    llvm_ir = compile_source(source_file.read_text(), str(source_file), opt_level, search_paths)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        ll_path = tmpdir_path / "out.ll"
        ll_path.write_text(llvm_ir)
        obj_path = tmpdir_path / "out.o"
        subprocess.run(["llc", ll_path, "-filetype=obj", "-o", obj_path], check=True)
        runtime_obj = tmpdir_path / "arc_runtime.o"
        subprocess.run(["clang", "-c", "runtime/arc_runtime.c", "-o", runtime_obj], check=True)
        subprocess.run(["clang", obj_path, runtime_obj, "-o", output], check=True)


def main():
    parser = argparse.ArgumentParser(description="Build MxScript program")
    parser.add_argument("source")
    parser.add_argument("-o", "--output", default="a.out")
    parser.add_argument("-O", "--opt", type=int, default=0)
    parser.add_argument("-I", "--search-path", action="append", dest="search_paths")
    args = parser.parse_args()

    build_executable(Path(args.source), Path(args.output), args.opt, args.search_paths)


if __name__ == "__main__":
    main()
