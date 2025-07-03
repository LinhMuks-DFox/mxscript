# MxScript Development Rules

## Version

| Item    | Value      |
| ------- | ---------- |
| Version | 1.0.0      |
| Updated | 2025-07-03 |

---

## 1. General Principles

1.  **Single Source of Truth**: The `ffi_map.json` file is the **authoritative ABI contract** between the compiler frontend and the C++ runtime. All development must treat it as such.
2.  **Consistency**: Any changes made to the C++ runtime's exported functions **must** be immediately and accurately reflected in `ffi_map.json`. Conversely, any changes to the ABI contract must be implemented in both the frontend and runtime.
3.  **Clarity over cleverness**: Code should be straightforward and easy to understand.

---

## 2. C++ Runtime Development Rules

### 2.1. Code Formatting

* **Mandatory Tool**: All C++ code (`.cpp`, `.h`) **must** be formatted using `clang-format`.
* **Configuration**: A `.clang-format` file, preferably based on a standard style like "Google" or "LLVM", should be present in the project root. All contributors must use it before committing code.

### 2.2. Language Standard

* **Standard**: The project officially uses **C++23**.
* **Features**: Developers are encouraged to use modern C++23 features where they improve clarity, safety, and performance. This includes ranges, concepts, modules (when tooling is mature), and improved concurrency primitives.

### 2.3. Function Definitions

* **Style**: Prefer `auto`-based, trailing-return-type function definitions, especially for non-trivial functions. This improves readability, particularly with templates and complex types.

    ```cpp
    // Preferred style
    extern "C" auto mxs_print_object(mxs_runtime::MXObject* obj) -> std::size_t {
        // ... implementation
    }

    // Acceptable for very simple, legacy, or C-interop-heavy functions