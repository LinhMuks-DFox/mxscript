# The MxScript Compiler and Execution Model

This document describes the architecture of the **MxScript** compiler and the lifecycle of a program from source code to execution. The entire toolchain is designed around a single high-performance execution path: **Just-In-Time (JIT)** compilation via **LLVM**.

---

## 1. Compilation Pipeline

An **MxScript** source file goes through a multi-stage compilation process to be transformed into executable machine code. The frontend of the compiler is implemented in Python.

---

### Stage 1: Lexical Analysis (Tokenization)

- **Component:** Tokenizer  
- **Input:** Raw MxScript source code (`.mxs` file)  
- **Output:** Stream of tokens  
- **Process:**  
  - Reads the source code character by character and groups them into meaningful tokens such as keywords (`func`, `if`), identifiers (`my_var`), operators (`+`, `==`), and literals (`123`, `"hello"`).
  - Comments and whitespace are typically discarded at this stage.

---

### Stage 2: Syntactic Analysis (Parsing)

- **Component:** Parser  
- **Input:** The token stream  
- **Output:** Abstract Syntax Tree (AST)  
- **Process:**  
  - Consumes the token stream and applies the grammatical rules defined in `syntax.ebnf`.
  - Verifies that the sequence of tokens forms a valid syntactic structure and builds an AST—a hierarchical tree representation of the code.

---

### Stage 3: Semantic Analysis

- **Component:** Analyzer  
- **Input:** AST  
- **Output:** Annotated and validated AST  
- **Process:**  
  - Interprets the meaning of the code. Key tasks include:
    - **Scope Resolution:** Building and managing symbol tables to track declared variables, functions, and types within scopes.
    - **Type Checking:** Verifying that operations are performed on compatible types (e.g., prohibiting `int + String`).
    - **Mutability Checks:** Enforcing `let` vs. `let mut` rules.
    - **Resolving Names:** Linking variable usages to their declarations.

---

### Stage 4: Intermediate Representation (LLIR) Generation

- **Component:** Compiler / LLIRBuilder  
- **Input:** The validated AST  
- **Output:** Custom high-level **Low-Level Intermediate Representation (LLIR)**  
- **Process:**  
  - Lowers the high-level AST into a more linear, instruction-like format.
  - The LLIR is simpler and platform-independent, using instructions such as `CondBr`, `Label`, and `Call`.

---

### Stage 5: LLVM IR Generation

- **Component:** LLVMGenerator  
- **Input:** Custom LLIR  
- **Output:** LLVM Intermediate Representation (LLVM IR) text  
- **Process:**  
  - Acts as the bridge to the LLVM ecosystem.
  - Iterates over LLIR instructions and translates them to LLVM IR instructions using `llvmlite`.
  - Defines function signatures, data structures, and generates the control flow graph (basic blocks and branches) in LLVM IR format.

---

## 2. Execution Model

Once the LLVM IR is generated, the program is ready for execution.

---

### Stage 1: JIT Engine Initialization

- **LLVM JIT Engine:** Initializes an LLVM Just-In-Time compilation engine.
- **Runtime Linking:** The C runtime library (implementing ARC, string manipulation, and primitives) is compiled into a shared library and loaded into the JIT engine's address space, exposing C functions to JIT-compiled code.
- **Parsing and Optimizing LLVM IR:** Parses the LLVM IR and applies optimization passes (e.g., dead code elimination, function inlining, loop unrolling).
- **Dynamic Optimization Control:** The optimization pipeline is configurable. Command-line arguments (e.g., `--opt-level=2`) can control optimization levels (`-O0`, `-O2`, `-Os`) to trade compilation speed for runtime performance.

---

### Stage 2: Program Initialization

Before executing the main logic, the runtime environment performs setup steps:

- **Load Builtin Module:** Loads the core builtin module containing fundamental types (`Object`, `int`, `String`) and intrinsic functions.
- **Resolve Dependencies:** Processes `import` statements, recursively loading and compiling dependencies.
- **Evaluate Static Bindings:** Evaluates all top-level static `let` declarations and places their values in the global data section.

---

### Stage 3: Program Execution

- **Execute Top-Level Code:** Runs all top-level statements in the main source file sequentially.
- **Invoke `main` Function:**  
  - Searches for a `main()` function with no parameters.
  - If found, calls it automatically.
  - The integer returned becomes the program's exit code (or `0` if `main()` returns `nil`).
  - If no `main()` function is found, the program exits after top-level execution with code `0`.

## 3.1  Scope-Based Lifetimes (RAII)

- **Scope Binding:**  
  - A variable's lifetime is strictly tied to its declaring scope.  
  - **Lexical Scoping:**  
    - A variable exists from its declaration point to the end of its enclosing block (function body, loop block, `if` body, etc.).  

- **Deterministic Destruction:**  
  - When control flow exits a scope, all variables declared within it are **immediately** and **predictably** destroyed.  
  - Follows the **Resource Acquisition Is Initialization (RAII)** principle to ensure resources are released as soon as they are no longer needed.  

- **Release Operation:**  
  - On variable destruction, a **release** operation is automatically performed on the object it references.

---

## 3.2  Automatic Reference Counting (ARC)

- **Division of Responsibility:**  
  - Variable lifetimes are managed by **scope**.  
  - Underlying **object lifetimes** are managed by **ARC**.  

- **Heap Allocation:**  
  - All objects in **MxScript** are allocated on the **heap**.  

- **Reference Count:**  
  - Every object maintains a **reference count** tracking how many variables or structures refer to it.  

- **Compiler-Managed Operations:**  
  - The compiler inserts **retain** (increment) and **release** (decrement) calls automatically:  
    - **Retain:** When a reference is shared (e.g., `let y = x;`, or passing as a function argument).  
    - **Release:** When a reference is destroyed (i.e., variable goes out of scope).  

- **Deallocation Process:**  
  - When an object's reference count reaches **zero**:  
    1. The object's **destructor** (`~ClassName()`) is called for custom cleanup (e.g., closing files, releasing network connections).  
    2. The object's **memory** is deallocated and returned to the system.
