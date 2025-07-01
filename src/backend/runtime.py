from __future__ import annotations

from typing import Dict, List
import ctypes

from .ir import (
    ProgramIR,
    Instr,
    Const,
    Alloc,
    Dup,
    Load,
    Store,
    BinOpInstr,
    Pop,
    Call,
    Return,
    DestructorCall,
    ScopeEnter,
    ScopeExit,
    ErrorValue,
)

# Initialize libc handles for common C functions used via FFI
_libc = ctypes.CDLL(None)
_libc_time = _libc.time
_libc_time.argtypes = [ctypes.c_void_p]
_libc_time.restype = ctypes.c_long
_libc_rand = _libc.rand
_libc_rand.argtypes = []
_libc_rand.restype = ctypes.c_int


def execute(program: ProgramIR) -> int | None:
    def run(
        code: List[Instr],
        env_stack: List[Dict[str, object]],
        var_info_stack: List[Dict[str, Dict[str, object | None]]],
    ) -> object | None:
        stack: List[object] = []
        for instr in code:
            if isinstance(instr, Const):
                stack.append(instr.value)
            elif isinstance(instr, Load):
                for env in reversed(env_stack):
                    if instr.name in env:
                        stack.append(env[instr.name])
                        break
                else:
                    stack.append(0)
            elif isinstance(instr, Alloc):
                stack.append(0)
            elif isinstance(instr, Dup):
                if stack:
                    stack.append(stack[-1])
            elif isinstance(instr, Store):
                val = stack.pop()
                env_stack[-1][instr.name] = val
                var_info_stack[-1][instr.name] = {
                    "type_name": instr.type_name,
                    "ptr": val,
                }
            elif isinstance(instr, BinOpInstr):
                b = stack.pop()
                a = stack.pop()
                stack.append(_apply_op(instr.op, a, b))
            elif isinstance(instr, Call):
                args = [stack.pop() for _ in range(instr.argc)][::-1]
                func = program.functions.get(instr.name)
                if func is None:
                    if instr.name in program.foreign_functions:
                        stack.append(_ffi_call(program.foreign_functions[instr.name], args))
                        continue
                    raise RuntimeError(f"Undefined function {instr.name}")
                new_env = dict(zip(func.params, args))
                env_stack.append(new_env)
                var_info_stack.append({})
                result = run(func.code, env_stack, var_info_stack)
                env_stack.pop()
                var_info_stack.pop()
                if isinstance(result, ErrorValue) and result.panic:
                    return result
                if result is not None:
                    stack.append(result)
            elif isinstance(instr, Return):
                return stack.pop() if stack else None
            elif isinstance(instr, DestructorCall):
                info = None
                for scope in reversed(var_info_stack):
                    if instr.name in scope:
                        info = scope[instr.name]
                        break
                if info is not None:
                    type_name = info.get("type_name")
                    ptr = info.get("ptr")
                    if type_name:
                        func_name = f"{type_name}_destructor"
                        func = program.functions.get(func_name)
                        if func is None:
                            raise RuntimeError(
                                f"Could not find destructor function '{func_name}'"
                            )
                        env_stack.append({func.params[0]: ptr})
                        var_info_stack.append({func.params[0]: {"type_name": None, "ptr": ptr}})
                        run(func.code, env_stack, var_info_stack)
                        env_stack.pop()
                        var_info_stack.pop()
                for scope in reversed(var_info_stack):
                    if instr.name in scope:
                        del scope[instr.name]
                        break
                for env in reversed(env_stack):
                    if instr.name in env:
                        del env[instr.name]
                        break
            elif isinstance(instr, ScopeEnter):
                env_stack.append({})
            elif isinstance(instr, ScopeExit):
                env_stack.pop()

            elif isinstance(instr, Pop):
                if stack:
                    stack.pop()
            else:
                raise RuntimeError(f"Unknown instruction {instr}")
        return stack[-1] if stack else None

    result = run(program.code, [{}], [{}])
    if isinstance(result, ErrorValue) and result.panic:
        raise RuntimeError(f"Panic: {result.msg}")
    return result


def _apply_op(op: str, a: int, b: int) -> int:
    a = int(a)
    b = int(b)
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        return a // b
    if op == '%':
        return a % b
    if op == '==':
        return int(a == b)
    if op == '!=':
        return int(a != b)
    if op == '>':
        return int(a > b)
    if op == '<':
        return int(a < b)
    if op == '>=':
        return int(a >= b)
    if op == '<=':
        return int(a <= b)
    raise RuntimeError(f"Unsupported op {op}")


def _ffi_call(c_name: str, args: List[object]) -> int | None:
    """Very small foreign function handler for the interpreter."""
    if c_name == "write":
        import os

        fd = int(args[0])
        buf = args[1]
        count = int(args[2])
        if isinstance(buf, str):
            data = buf.encode()[:count]
        elif isinstance(buf, bytes):
            data = buf[:count]
        else:
            data = bytes(buf)
        return os.write(fd, data)
    if c_name == "read":
        import os

        fd = int(args[0])
        buf = args[1]
        count = int(args[2])
        data = os.read(fd, count)
        if isinstance(buf, bytearray):
            buf[: len(data)] = data
        return len(data)
    if c_name == "open":
        import os

        path = str(args[0])
        flags = int(args[1])
        mode = int(args[2])
        return os.open(path, flags, mode)
    if c_name == "close":
        import os

        fd = int(args[0])
        os.close(fd)
        return 0
    if c_name == "time_now":
        import time

        return int(time.time())
    if c_name == "random_rand":
        import random

        return int(random.randint(0, 2**31 - 1))
    if c_name == "make_error":
        msg = str(args[0]) if args else ""
        panic = bool(args[1]) if len(args) > 1 else False
        return ErrorValue(msg=msg, panic=panic)
    if c_name == "print":
        print(*args)
        return 0
    if c_name == "time":
        return int(_libc_time(None))
    if c_name == "rand":
        return int(_libc_rand())
    raise RuntimeError(f"Foreign function {c_name} not implemented")
