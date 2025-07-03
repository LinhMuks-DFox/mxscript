# MxScript Refactoring Policy

## Version

| Item    | Value      |
| ------- | ---------- |
| Version | 1.0.0      |
| Status  | **Active** |
| Updated | 2025-07-03 |

---

## 1. Core Principle: Static First, Dynamic for Polymorphism

All operations shall be implemented with a preference for the **Static Dispatch Path**, which is resolved at compile-time. The **Dynamic Dispatch Path** serves as a necessary fallback to support polymorphism (e.g., interfaces, generics) where concrete types are unknown at compile-time. This hybrid approach maximizes performance and type safety while retaining language flexibility.

---

## 2. Static Dispatch Policy (The "Fast Path")

This is the default and preferred code generation strategy for all operations where the types of all operands are known at compile-time.

### 2.1. Applicable Scenarios

* Binary and unary operations where all operands are concrete, known types.
* Examples: `integer + integer`, `float * integer`, `integer == float`.

### 2.2. Component Responsibilities

* **`Semantic Analyzer`**:
    * **Mandate**: Must traverse the AST and precisely annotate all expression nodes (e.g., `BinaryExpr`) with the resolved types of their operands and results. This type annotation is the foundation of the static dispatch strategy.

* **`Codegen`**:
    * **Mandate**: Upon visiting an expression node, it must first inspect the type annotations.
    * It will use a mapping mechanism to find the corresponding type-specific C++ function name (e.g., `(integer, +, integer) -> "integer_add_integer"`).
    * It must then query the `ABI Manager` for this specific function's signature and generate a direct LLVM `call` instruction.

* **`C++ Runtime`**:
    * **Mandate**: Must provide a comprehensive set of non-virtual, `extern "C"` functions, each dedicated to a single operation on a specific combination of types.
    * The naming convention must be clear (e.g., `integer_add_integer`, `float_add_integer`).
    * These functions must omit internal type checking for maximum performance, as type safety is guaranteed by the compiler frontend.

* **`ffi_map.json` (ABI Contract)**:
    * **Mandate**: Must contain an entry for every type-specific static dispatch function exposed by the runtime.

---

## 3. Dynamic Dispatch Policy (The "Polymorphic Path")

This strategy is employed only when static dispatch is not possible due to a lack of compile-time type information.

### 3.1. Applicable Scenarios

* An operand's type is an `interface`.
* An operand's type is a `generic` parameter.
* An operand is retrieved from a heterogeneous container.

### 3.2. Component Responsibilities

* **`Codegen`**:
    * **Mandate**: If the type annotation for an operand is polymorphic (e.g., an interface), the codegen will fail to find a specific static dispatcher.
    * It must then fall back to generating a `call` to a generic, top-level dispatch function (e.g., `mxs_op_add`).

* **`C++ Runtime`**:
    * **Mandate**: Must implement a unified `MXTypeInfo` structure that contains both RTTI metadata (`name`, `parent`) and a VTable of operation function pointers.
    * Each concrete type (e.g., `MXInteger`) must provide a static, constant instance of its `MXTypeInfo`.
    * The runtime must provide generic, top-level dispatch functions (e.g., `mxs_op_add`), whose implementation is a single line that calls through the object's `type_info` pointer: `return left->type_info->op_add(left, right);`.

* **`ffi_map.json` (ABI Contract)**:
    * **Mandate**: Must contain an entry for every generic, top-level dispatch function.

---

## 4. Codegen Decision Flow

The `Codegen` must implement the following logic when processing an expression:

```

function visit\_expression(node):
// 1. Get type information annotated by the Semantic Analyzer.
left\_type = node.left.type\_annotation
right\_type = node.right.type\_annotation
operator = node.op

```
// 2. Attempt to find a static dispatcher first.
specific_func_name = find_static_dispatcher(left_type, operator, right_type)

if specific_func_name is found:
    // Use the "Fast Path".
    generate_direct_call(specific_func_name, node.left, node.right)
else:
    // 3. Fallback to the "Polymorphic Path".
    generic_func_name = find_dynamic_dispatcher(operator)
    if generic_func_name is found:
        generate_vtable_call(generic_func_name, node.left, node.right)
    else:
        // 4. If no path is found, it is a semantic error.
        report_error("Unsupported operation for given types")
```

