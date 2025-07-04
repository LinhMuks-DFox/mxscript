````markdown
# MxScript Foreign Function Interface (FFI) Specification

## Document Purpose
This document provides the authoritative specification for the MxScript Foreign Function Interface (FFI). All FFI-related implementation work must strictly adhere to the architecture and mechanisms described herein.

## 1. Core Philosophy
The FFI is the sole and unified mechanism for MxScript to interface with compiled C++ code. It is used both to bind the language's standard library to its C++ runtime implementation and to allow users to call arbitrary external shared libraries.

The system is based on **Declaration Binding**. Its core principle is that any C++ function exposed to MxScript must conform to the MxScript type system. Specifically, all function arguments and return values must be of the type `MXObject*`. Interfacing with native C libraries (e.g., libc) requires a C++ wrapper that adheres to this specification.

## 2. The `@@foreign` Annotation

### 2.1. Syntax and Placement
The `@@foreign` annotation must be placed directly before a `func` declaration.

```mxscript
@@foreign(lib: string, symbol_name: string, ...)
func mxscript_function_name(arg1: Type1, ...) -> ReturnType;
````

### 2.2. Parameters

* **lib: string (Mandatory):** The filename of the shared library (e.g., "runtime.so", "my\_wrappers.so").
* **symbol\_name: string (Optional):** The exact symbol name of the C++ function to be called. If omitted, the MxScript function name is used as the default.
* **argc: int (Optional):** For validation purposes, explicitly declares the number of arguments the target function expects.
* **argv: list (Optional, Special):** A special directive that instructs the compiler to pack some or all of the function's arguments into an `MXList` object. This triggers the "Packed Dispatch Mode".

## 3. End-to-End Workflow & Dispatch Modes

The compiler always translates an FFI-bound call into a call to a universal runtime helper function, `mxs_ffi_call`. The method of preparing arguments for this helper depends on the `@@foreign` annotation, resulting in two distinct dispatch modes.

### 3.1. Default Dispatch Mode

This mode is used when the `argv` parameter is not present in the `@@foreign` annotation.

**MxScript Declaration:**

```mxscript
class String {
    @@foreign(lib="runtime.so", symbol_name="mxs_string_from_integer")
    static func from(value: Integer) -> String;
}
```

**Compiler Behavior:**
A call to `String.from(3)` is translated into a call to `mxs_ffi_call`. The compiler collects all of `String.from`'s arguments (in this case, one) into an array of `MXObject*` and passes it to the helper.

**The conceptual call is:**

```cpp
mxs_ffi_call("runtime.so", "mxs_string_from_integer", 1, [ &mx_integer_obj_for_3 ])
```

### 3.2. Packed Dispatch Mode

This special mode is triggered when the `argv` parameter is present in the `@@foreign` annotation. It is primarily designed to support functions that need to receive a list of arguments.

**MxScript Declaration:**

```mxscript
// The "..." in the MxScript signature indicates it is variadic.
// "argv=[1,...]" in the annotation instructs the compiler to pack all
// arguments from index 1 onwards into an MXList object.
@@foreign(lib="my_wrappers.so", symbol_name="wrapped_printf", argv=[1,...])
func c_printf(format: String, ...) -> Integer;
```

**Compiler Behavior:**
A call to `c_printf("Hello %s %d", "world", 123)` is handled differently:

* The CodeGen detects the `argv` directive.
* It creates a new `MXList` object at the call site.
* It populates this `MXList` with the specified arguments ("world" and 123).
* The final call to `mxs_ffi_call` receives the fixed format string object and the newly created `MXList` object as its arguments.

**The conceptual call is:**

```cpp
mxs_ffi_call("my_wrappers.so", "wrapped_printf", 2, [ &format_string_obj, &list_obj ])
```

## 4. C++ API Contract

### 4.1. The Universal FFI Helper: `mxs_ffi_call`

**Signature:**

```cpp
auto mxs_ffi_call(MXString* lib, MXString* name, int argc, MXObject** argv) -> MXObject*;
```

**Responsibilities:**
This function encapsulates the core logic for all FFI calls. It is the only FFI-related function that the CodeGen should call directly. Its responsibilities include:

* Loading the specified shared library using `dlopen`.
* Looking up the target symbol using `dlsym`.
* Invoking the target function. `mxs_ffi_call` must handle both dispatch modes. It internally unpacks the `MXObject*` pointers from the `argv` array and calls the target C++ function with the correct number of arguments.
* Returning the `MXObject*` received from the target function.

### 4.2. Target C++ Function Contract

**Signature:**
All C++ functions exposed via the FFI must accept `MXObject*` pointers as arguments and must return an `MXObject*`.

**Internal Type Safety:**
It is the strict responsibility of every target C++ function to perform runtime type checking on the `MXObject*` pointers it receives. It must verify the `type_info` of each argument and return an `MXError` object on a mismatch.

```
```
