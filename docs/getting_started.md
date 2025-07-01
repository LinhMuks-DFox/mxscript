# Getting Started with MxScript (v0.0.1)

This guide will walk you through compiling and running your first MxScript program.

## 1. Prerequisites

* Python 3.x
* LLVM installed on your system. You must have the `llc` command available in your PATH.
* A C compiler like `clang` or `gcc` for the final linking stage.

## 2. Installation

Clone the MxScript repository and install the required Python packages:

```bash
git clone <repository_url>
cd mxscript
pip install -r requirements.txt
```

## 3. Your First Program: "Hello, World!"

Create a file named `hello.mxs` with the following content:

```mxscript
// hello.mxs
import std.io as io;

func main() -> int {
    io.println("Hello, MxScript!");
    return 0;
}
```

This program imports the standard I/O library and prints a message to the console.

## 4. Compiling and Running

The MxScript compiler can generate LLVM IR, which can then be compiled into a native executable.

### Step 1: Generate LLVM IR

Run the `main.py` script with the `--emit-llvm` flag to produce an LLVM IR file (`.ll`).

```bash
python main.py --emit-llvm hello.mxs -o hello.ll
```

### Step 2: Compile to an Object File

Use `llc` to compile the LLVM IR into a native object file (`.o`).

```bash
llc -filetype=obj hello.ll -o hello.o
```

### Step 3: Link into an Executable

Use `clang` or `gcc` to link the object file with the necessary system libraries to create the final executable.

```bash
clang hello.o -o hello
```

### Step 4: Run the Program!

Execute your newly created program.

```bash
./hello
```

**Expected Output:**
```
Hello, MxScript!
```

Congratulations! You have successfully compiled and run your first MxScript program.
