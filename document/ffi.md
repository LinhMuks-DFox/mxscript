# MxScript Foreign Function Interface (FFI) Master Specification

## Document Purpose

This document provides the authoritative specification for the MxScript Foreign Function Interface (FFI). All implementation work related to FFI **must** strictly adhere to the architecture and mechanisms described herein.

## 1\. Core Philosophy

The FFI is the **unified and sole mechanism** for MxScript to interface with compiled C++ code. It is used both to bind the standard library to its C++ runtime implementation and to allow users to call arbitrary external shared libraries. The system is based on **declaration binding**.

## 2\. The `@@foreign` Annotation

### 2.1. Syntax and Placement

The `@@foreign` annotation must be placed directly before a `func` declaration.

```mxscript
@@foreign(lib: string, symbol_name: string, ...)
func mxscript_function_name(arg1: Type1, ...) -> ReturnType;
```

### 2.2. Parameters

  * **`lib: string` (Mandatory)**: The name of the shared library file (e.g., `"runtime.so"`, `"libc.so.6"`).
  * **`symbol_name: string` (Optional)**: The exact symbol name of the C function to call. If omitted, the MxScript function name is used as the default.
  * **`argc: int` (Optional)**: Explicitly declares the expected number of arguments for validation purposes.
  * **`argv: list` (Optional, Special Handling)**: Specifies that the arguments should be packed into a container. See Section 3.2.2 for details.

## 3\. End-to-End Workflow & Dispatch Modes

The compiler translates an FFI-bound MxScript call into a call to a universal C++ runtime helper, `mxs_ffi_call`. The way arguments are prepared for this call depends on the FFI annotation.

### 3.1. Default Dispatch Mode (Individual Arguments)

This is the standard mode used when the `argv` parameter is **not** present in the `@@foreign` annotation.

  * **MxScript Declaration**:
    ```mxscript
    class String {
        @@foreign(lib="runtime.so", symbol_name="mxs_string_from_integer")
        static func from(value: Integer) -> String;
    }
    ```
  * **Compiler `CodeGen` Behavior**:
    The call `String.from(3)` is translated into a conceptual call to the universal FFI helper, passing the arguments individually.
    `mxs_ffi_call("runtime.so", "mxs_string_from_integer", 1, [ &mx_integer_obj ])`

### 3.2. Packed Dispatch Mode (Variadic/List Arguments)

This special mode is triggered when the `argv` parameter **is** present in the `@@foreign` annotation. It is designed for calling C functions that expect an array of arguments, such as `execv` or variadic functions like `printf`.

  * **MxScript Declaration**:
    ```mxscript
    # The "..." in the MxScript signature indicates it's variadic.
    # The `argv` parameter tells the compiler to pack all arguments
    # starting from the first one into a List.
    @@foreign(lib="libc.so.6", symbol_name="printf", argv=[1,...])
    func c_printf(format: String, ...) -> int;
    ```
  * **Compiler `CodeGen` Behavior**:
    The call `c_printf("Hello %s %d", "world", 123)` is translated differently:
    1.  The `CodeGen` sees the `argv` directive.
    2.  It creates a new `MXList` object at the call site.
    3.  It populates this list with the specified arguments (`"world"` and `123`).
    4.  The final call to the universal FFI helper passes the format string and the **`MXList` object** as its two arguments.
        `mxs_ffi_call("runtime.so", "printf", 2, [ &format_string_obj, &list_obj ])`

## 4\. C++ API Contract

### 4.1. The Universal FFI Helper

  * **Function**: `mxs_ffi_call`
  * **Signature**: `auto mxs_ffi_call(MXString* lib, MXString* name, int argc, MXObject** argv) -> MXObject*`
  * **Responsibility**: Encapsulates all logic for library loading, symbol lookup, and function invocation. This is the **only** FFI-related function the `CodeGen` should directly call. It needs to be flexible enough to handle both dispatch modes.

### 4.2. Target Function Contract

  * **Signature**: All target C++ functions must accept `MXObject*` pointers as arguments and return an `MXObject*`.
  * **Internal Type Safety**: It is the strict responsibility of every target C++ function to perform **runtime type checking** on the `MXObject*` pointers it receives. It must verify the `type_info` of each argument and return an `MXError` object on mismatch.

**Example C++ Implementation**:

```cpp
extern "C" auto mxs_string_from_integer(MXObject* integer_obj) -> MXObject* {
    // 1. Perform runtime type check.
    if (integer_obj->type_info != &g_integer_type_info) {
        return new MXError("TypeError", "Argument must be an Integer.");
    }
    // 2. Safely cast and perform the operation.
    auto int_val = static_cast<MXInteger*>(integer_obj)->value;
    // 3. Return a new MxScript object.
    return new MXString(std::to_string(int_val));
}
```