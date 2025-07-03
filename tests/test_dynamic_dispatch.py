from src.backend.ir import ProgramIR, Const, BinOpInstr
from src.backend import to_llvm_ir


def test_dynamic_add():
    prog = ProgramIR(code=[Const(1), Const(2), BinOpInstr('+', 'object', 'object', 'object')],
                     functions={}, foreign_functions={})
    ir = to_llvm_ir(prog)
    assert 'call i8* @\"mxs_op_add\"' in ir
