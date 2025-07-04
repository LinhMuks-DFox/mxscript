# MxScript Foreign Function Interface (FFI) Specification

## Version

| Item | Value |
| :--- | :--- |
| Version | 2.0.0 |
| Status | **Active** |
| Updated | 2025-07-04 |

## 1\. Core Concept

The FFI is the **sole and unified mechanism** for MxScript to interface with compiled C++ code. It is not only for calling external libraries but is also the fundamental way the MxScript standard library binds its high-level APIs to the efficient C++ runtime implementations.

This is achieved through **declaration binding**. A function or method is declared in an `.mxs` file (e.g., in the standard library) and uses a `@@foreign` annotation to link it to a specific C++ function.

## 2\. The `@@foreign` Annotation

The `@@foreign` annotation must be placed directly before a `func` declaration (including `static` methods). It instructs the compiler to treat the function as an external C++ call.

### 2.1. Syntax

```mxscript
@@foreign(lib: string, name: string)
func mxscript_function_name(arg1: Type1, ...) -> ReturnType;
```

  * **`lib: string`**: The name of the shared library file. For all core functionalities, this will be `"runtime.so"` (or the platform-equivalent).
  * **`name: string`**: The exact symbol name of the C function to call. If omitted, the MxScript function name is used.

### 2.2. Example: Standard Library Binding

The `cast` function is a prime example of this mechanism. It is pure syntactic sugar for a static method call, which is itself bound to a C++ function via FFI.

**1. User Code:**

```mxscript
// The user writes this simple, high-level code.
let i_str = cast(String, 3);
```

**2. Compiler Translation:**
The compiler translates the `cast` into a static method call:

```mxscript
let i_str = String.from(3);
```

**3. Standard Library Definition (`stdlib/string.mxs`):**
The `String.from` method is defined in the standard library using the FFI annotation:

```mxscript
class String {
    // This static method is bound to a C++ function in the runtime library.
    @@foreign(lib="runtime.so", name="mxs_string_from_integer")
    static func from(value: Integer) -> String;
}
```

## 3\. Compiler Responsibilities

The compiler's role is unified and simplified. It no longer needs special internal rules for static dispatch.

  * **Parser**: Must parse the `@@foreign(...)` annotation and attach its metadata to the `FunctionDef` AST node.
  * **Semantic Analyzer**: Registers the function as an "external" call and performs type checking based on the MxScript signature.
  * **Code Generator (Codegen)**: When encountering a call to an FFI-bound function:
    1.  **Load Library & Get Symbol**: Generate a call to a runtime helper (`mxs_get_foreign_func`) to resolve the C function pointer from the specified library.
    2.  **Argument Passing**: All arguments passed from MxScript to the C++ function **must be passed as `MXObject*` pointers**. No marshalling to primitive C types occurs at the call site.
    3.  **Generate Call**: Generate an LLVM `call` instruction to the resolved C function pointer.
    4.  **Return Value**: The return value from the C function is expected to be an `MXObject*`, which is then used directly.

## 4\. C++ Runtime Responsibilities

  * **Provide C API Functions**: The runtime must expose a suite of `extern "C"` functions with C-compatible linkage.
  * **Function Signature**: All FFI-callable functions must adhere to the signature:
    `auto function_name(MXObject* arg1, ...) -> MXObject*`.
  * **Internal Type Checking**: Since all arguments are received as `MXObject*`, it is the **responsibility of the C++ function itself** to verify the types of its arguments before using them. It must check the `type_info` of the incoming objects and return an `MXError` if the types are incorrect.

**Example C++ Implementation:**

```cpp
extern "C" auto mxs_string_from_integer(MXObject* integer_obj) -> MXObject* {
    // 1. Perform runtime type check.
    if (integer_obj->type_info != &g_integer_type_info) {
        return new MXError("TypeError", "Argument must be an Integer.");
    }

    // 2. Safely cast and perform the operation.
    auto int_val = static_cast<MXInteger*>(integer_obj)->value;
    auto str_val = std::to_string(int_val);
    
    // 3. Return a new MxScript object.
    return new MXString(str_val);
}
```