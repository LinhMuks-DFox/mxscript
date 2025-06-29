AGENT.md: MxScript Language Specification & Development Guide

Version: 1.0.0

Last Updated: 2025-06-29

1. Project Vision & Philosophy

MxScript is a modern, general-purpose programming language designed to bridge the gap between dynamic scripting languages and static, compiled languages.

Core Philosophy: To provide a highly ergonomic, dynamic-first scripting experience while empowering the developer with explicit, optional control over static analysis, performance optimizations, and memory safety.

Primary Goal: To be a language that is easy to learn and use for simple scripts, but powerful and safe enough for complex, performance-critical applications.

2. Core Language Architecture

Frontend (Python): Responsible for parsing source code and building a semantic representation.

Tokenizer: Converts source text into a stream of tokens.

Parser: Consumes the token stream to build an Abstract Syntax Tree (AST), guided by mxscript.ebnf.

Semantic Analyzer: Traverses the AST to perform type checking, scope analysis, and enforce semantic rules.

Bridge (llvmlite): A Python library used by the frontend to emit LLVM Intermediate Representation (IR).

Backend (LLVM): The LLVM infrastructure is responsible for optimization and code generation.

JIT Engine: For immediate execution of code, enabling the "scripting" feel.

AOT Compiler: For compiling MxScript source into standalone native executables.

3. Formal Grammar (EBNF)

The official, unambiguous syntax of the language is defined in the mxscript.ebnf file (Version 1.0). This EBNF is the single source of truth for the parser's implementation.

4. Core Semantic Rules

This section defines language behaviors not captured by the EBNF syntax.

4.1. Type System

Typing Model: Strong and static, but with an opt-out to dynamic behavior via an object or any type (TBD).

Type Inference: The compiler infers types for let bindings (let x = 10; infers x as int). Explicit type annotation is required for function signatures and class/type fields.

Union Types: The type system must support union types, primarily for the error handling pattern (e.g., Matrix | Error). Type narrowing shall be performed within control flow structures like match.

4.2. Error Handling

Value-Based Errors: The primary error handling mechanism is returning error objects as values, inspired by Rust's Result<T, E>. This is the standard behavior of the raise keyword.

Panic Mechanism: For unrecoverable errors (programmer bugs), a panic mechanism is provided. This is triggered by raise stdlib:Error(..., panic=True). A panic will cause immediate program termination with diagnostics, and does not unwind the stack.

4.3. Memory Model

Ownership & Lifetime: The model is based on scope-bound resource management (RAII). When a variable binding goes out of scope, its resources are released (i.e., its destructor is called).

Immutability: Bindings are immutable by default (let). Mutability must be explicitly declared (mut).

Allocation: Simple value types are stack-allocated. Complex objects (class instances, etc.) are heap-allocated and their lifetime is managed via automatic reference counting (ARC).

4.4. Annotations & Metaprogramming

Annotations provide metadata to the compiler and runtime, enabling powerful optimizations and features.

@@manual_optimize_level(level: int): A hint to the compiler to apply a specific LLVM optimization level to the annotated function. The level argument should typically range from 0 (no optimization) to 3 (most aggressive optimization). This allows developers to fine-tune the performance of critical code sections, trading longer compile times for faster execution.

@@static_deterministic: A promise to the compiler that the function is pure (same input yields same output, no side effects). This allows for aggressive optimizations like compile-time function evaluation (CTFE) and memoization.

@@template(type T, ...): Declares a function or class as generic. Generics are implemented via Monomorphization at compile-time to ensure zero-cost abstraction.
5. Development Roadmap

Phase 1: Foundation (Parser & AST)

Implement the Tokenizer.

Implement a Recursive Descent Parser based on the EBNF to produce an AST.

Phase 2: Semantic Analysis

Implement Symbol Tables and a Type Checker.

Phase 3: Code Generation

Implement an AST walker that emits LLVM IR using llvmlite.

Phase 4: Execution & Runtime

Implement the JIT execution engine and basic runtime (memory management, object model).

Phase 5: Standard Library

Begin implementation of the std library.

6. About This Document

This is a living document. It is the single source of truth for the MxScript language design and must be updated before the implementation of any new or modified feature.