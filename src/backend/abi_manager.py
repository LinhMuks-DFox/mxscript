from __future__ import annotations

from llvmlite import ir
import json
from pathlib import Path
from typing import Dict, Tuple, List

int32 = ir.IntType(32)
int64 = ir.IntType(64)
char_ptr = ir.IntType(8).as_pointer()

_TYPE_MAP = {
    "int32": int32,
    "int64": int64,
    "char_ptr": char_ptr,
    "cstr_ptr": char_ptr,
    "double": ir.DoubleType(),
    "void": ir.VoidType(),
}

_PATH = Path(__file__).with_name("ffi_map.json")
_RAW_MAP = json.loads(_PATH.read_text())
_TYPED_MAP: Dict[str, dict] = {}

if "ffi_functions" in _RAW_MAP:
    # Minimal map containing only names of FFI-exposed functions
    if "mxs_ffi_call" in _RAW_MAP["ffi_functions"]:
        _TYPED_MAP["mxs_ffi_call"] = {
            "ret": char_ptr,
            "args": [char_ptr, char_ptr, int32, char_ptr.as_pointer()],
        }
    # Builtin runtime functions always available
    _BUILTIN_MAP = {
        "MXCreateInteger": {"ret": char_ptr, "args": [int64]},
        "MXCreateFloat": {"ret": char_ptr, "args": [ir.DoubleType()]},
        "MXCreateString": {"ret": char_ptr, "args": [char_ptr]},
        "mxs_get_true": {"ret": char_ptr, "args": []},
        "mxs_get_false": {"ret": char_ptr, "args": []},
        "mxs_get_nil": {"ret": char_ptr, "args": []},
        "increase_ref": {"ret": int64, "args": [char_ptr]},
        "decrease_ref": {"ret": int64, "args": [char_ptr]},
        "new_mx_object": {"ret": char_ptr, "args": []},
        "mxs_print_object_ext": {"ret": char_ptr, "args": [char_ptr, char_ptr]},
        "mxs_string_from_integer": {"ret": char_ptr, "args": [char_ptr]},
    }
    _TYPED_MAP.update(_BUILTIN_MAP)
else:
    for name, info in _RAW_MAP.items():
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
        _TYPED_MAP[name] = entry


def get_function_signature(name: str) -> Tuple[ir.Type, List[ir.Type]]:
    info = _TYPED_MAP[name]
    return info["ret"], info["args"]


def get_abi_entry(name: str) -> dict:
    return _TYPED_MAP[name]
