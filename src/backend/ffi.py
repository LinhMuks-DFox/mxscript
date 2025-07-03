from llvmlite import ir
from typing import Dict
from .abi_manager import get_abi_entry

# Map of supported libc functions. Keys are names used in MxScript FFI
# declarations. Each entry can optionally specify a different symbol name
# via the 'name' field.
from .abi_manager import _TYPED_MAP as LIBC_FUNCTIONS

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
    try:
        info = get_abi_entry(name)
    except KeyError:
        return name
    return info.get("name", name)
