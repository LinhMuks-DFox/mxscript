from src.frontend import tokenize, TokenStream
from src.syntax_parser import Parser
from src.semantic_analyzer import SemanticAnalyzer
from src.backend import compile_program, to_llvm_ir

def compile_ir(code: str) -> str:
    tokens = tokenize(code)
    stream = TokenStream(tokens)
    ast = Parser(stream).parse()
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    ir_prog = compile_program(ast, analyzer.type_registry)
    return to_llvm_ir(ir_prog)

def test_integer_add_dispatch():
    ir = compile_ir("1 + 2;")
    assert 'call i8* @\"integer_add_integer\"' in ir
    assert 'add i64' not in ir

def test_integer_sub_dispatch():
    ir = compile_ir("1 - 2;")
    assert 'call i8* @\"integer_sub_integer\"' in ir
    assert 'sub i64' not in ir
