# MxScript Language Specification

## Version Info

* Version: 1.3.0
* Last Updated: 2025-06-29

---

## 1. Project Vision & Philosophy

**Vision and Philosophy**

MxScript is a modern, general-purpose programming language designed to bridge the gap between dynamic scripting languages and static, compiled languages.

* **Core Philosophy**: Prioritize a dynamic-first scripting experience while providing developers with optional, explicit control over static analysis, performance optimizations, and memory safety.
* **Primary Goal**: Easy to learn and use for simple scripts, yet powerful and safe enough for complex, performance-critical applications.

---

## 2. Core Language Architecture

* **Frontend (Python)**: Parses source code and builds a semantic representation.
* **Bridge (llvmlite)**: A Python library that generates LLVM IR.
* **Backend (LLVM)**: Handles JIT/AOT optimization and code generation.

---

## 3. Formal Grammar (EBNF)

The official, unambiguous syntax of the language is defined in the `syntax/syntax.ebnf` file, which is the single source of truth for the language's syntax.

---

## 4. Core Semantic Rules

### 4.1 Type System

#### Primitive Types

* `int`: 64-bit signed integer
* `float`: 64-bit double-precision floating-point
* `bool`: Boolean value
* `string`: UTF-8 encoded immutable string
* `nil`: A single-value type representing absence of value

#### Dynamic Type (object)

* **Definition**: Root type for all complex, heap-allocated data structures (class instances, arrays, etc.).
* **Usage**: Enables dynamic dispatch when static type information is unavailable or undesired.

```mxscript
func accept_anything(val: object) {
  // May require runtime type checking
}
```

#### Union Types & Type Narrowing

* Mainly for error handling.
* `match` expressions safely handle different types within a union.

```mxscript
func might_fail(s: string) -> int | Error {
  if s.is_empty() {
    return raise Error("InputError", msg="Input cannot be empty.");
  }
  return s.to_int();
}

let result = might_fail("123");

let value = match (result) {
  case v: int => {
    println("Success:", v);
    v;
  }
  case e: Error => {
    println("Failure:", e.msg);
    -1;
  }
};
```

---

### 4.2 Error Handling

#### Value-Based Errors (raise)

* Primary mechanism is returning Error objects.
* `raise` is syntactic sugar for `return Error(...)`.

```mxscript
import std.error.Error;

func divide(a: int, b: int) -> float | Error {
  if b == 0 {
    return raise Error("DivisionByZero");
  }
  return a as float / b as float;
}
```

#### Panic Mechanism

* For unrecoverable errors.
* Immediately terminates the program and outputs diagnostic information.

```mxscript
func assert_positive(n: int) {
  if n <= 0 {
    raise Error("AssertionFailed", msg="Input must be positive.", panic=True);
  }
}
```

---

### 4.3 Memory Model & Scope

#### RAII & Destructors

* Scope-bound resource management (RAII).
* Destructors are automatically called when objects go out of scope.

```mxscript
class File {
  ~File() {
    __internal_close_file(self.handle);
  }
}

func process_file() {
  let f = File("data.txt", mode="read");
  // ... use f ...
} // f goes out of scope, ~File() is called automatically
```

#### Automatic Reference Counting (ARC)

* Heap-allocated object lifetimes managed via ARC.
* Compiler inserts retain/release calls automatically.
* When the count drops to zero, the object is deallocated and its destructor runs.

---

### 4.4 Annotations & Metaprogramming

#### @@manual\_optimize\_level

* Hints the LLVM backend for optimization level.

```mxscript
@@manual_optimize_level(level=3)
func matrix_multiply(a: Matrix, b: Matrix) -> Matrix {
  // ...
}
```

#### @@static\_deterministic

* Promises function purity for compile-time evaluation.

```mxscript
@@static_deterministic
func factorial(n: int) -> int {
  if n == 0 { return 1; }
  return n * factorial(n - 1);
}

let f5 = factorial(5);
```

#### @@template

* Declares generic functions or classes via monomorphization.

```mxscript
@@template(type T)
func get_first(arr: [T]) -> T {
  return arr[0];
}

let first_num = get_first<int>([1, 2, 3]);
let first_word = get_first<string>(["a", "b", "c"]);
```

---

### 4.5 Standard Library & Runtime Primitives

* Hybrid model for standard library implementation.

#### Runtime Primitives

* Minimal core functions provided via FFI to a C library.
* Not intended for direct public use.

```mxscript
@@foreign(c_name="write")
func __internal_write(fd: int, buffer: byte*, count: int) -> int;
```

#### High-Level API

* Most of the standard library is implemented in MxScript.
* Provides a safe, ergonomic layer over runtime primitives.

```mxscript
public func println(s: string) {
  let stdout_fd = 1;
  let buffer = s.to_internal_buffer();
  let len = s.length();

  __internal_write(stdout_fd, buffer, len);
  __internal_write(stdout_fd, "\n", 1);
}
```
