from llvmlite import ir
from typing import Dict
import json
from pathlib import Path

# Map of supported libc functions. Keys are names used in MxScript FFI
# declarations. Each entry can optionally specify a different symbol name
# via the 'name' field.
int32 = ir.IntType(32)
int64 = ir.IntType(64)
char_ptr = ir.IntType(8).as_pointer()


_TYPE_MAP = {
    "int32": int32,
    "int64": int64,
    "char_ptr": char_ptr,
    "double": ir.DoubleType(),
    "void": ir.VoidType(),
}


def _load_ffi_map() -> Dict[str, dict]:
    path = Path(__file__).with_name("ffi_map.json")
    raw = json.loads(path.read_text())
    result: Dict[str, dict] = {}
    for name, info in raw.items():
        entry = {
            "ret": _TYPE_MAP[info["ret"]],
            "args": [_TYPE_MAP[a] for a in info["args"]],
        }
        if "name" in info:
            entry["name"] = info["name"]
        if "wrapper_args" in info:
            entry["wrapper_args"] = [_TYPE_MAP[a] for a in info["wrapper_args"]]
        if "var_arg" in info:
            entry["var_arg"] = info["var_arg"]
        result[name] = entry
    return result


LIBC_FUNCTIONS: Dict[str, dict] = _load_ffi_map()

class FFIManager:
    """Helper for declaring and reusing foreign function declarations."""

    def __init__(self, module: ir.Module):
        self.module = module
        self._declared: Dict[str, ir.Function] = {}

    def get_or_declare_function(self, name: str) -> ir.Function:
        if name in self._declared:
            return self._declared[name]
        info = LIBC_FUNCTIONS.get(name)
        if info is None:
            raise KeyError(f"Unknown foreign function '{name}'")
        symbol = info.get('name', name)
        func_ty = ir.FunctionType(info['ret'], info['args'], var_arg=info.get('var_arg', False))
        target_fn = ir.Function(self.module, func_ty, name=symbol)
        wrapper_args = info.get('wrapper_args')
        if wrapper_args is not None:
            # Build a small wrapper to adapt arguments at call time
            wrapper_ty = ir.FunctionType(info['ret'], wrapper_args)
            wrapper = ir.Function(self.module, wrapper_ty, name=name)
            block = wrapper.append_basic_block('entry')
            builder = ir.IRBuilder(block)
            call_args = []
            if info['args'] and not wrapper_args:
                # typically for time_now -> time(NULL)
                call_args.append(ir.Constant(info['args'][0], None))
            builder.ret(builder.call(target_fn, call_args))
            self._declared[name] = wrapper
            return wrapper
        self._declared[name] = target_fn
        return target_fn

def resolve_symbol(name: str) -> str:
    info = LIBC_FUNCTIONS.get(name)
    if info is None:
        return name
    return info.get('name', name)
