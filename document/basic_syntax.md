# MxScript Language Guide

This document provides a comprehensive overview of the MxScript language syntax, covering fundamental concepts from variables to control flow and object-oriented programming.

### 1. Comments

Comments are used to annotate code and are ignored by the compiler.

* **Single-line comments**: Start with `#` and continue to the end of the line.

* **Multi-line comments**: Are enclosed between `!##!` and `!##!`.

```mxscript
# This is a single-line comment.

!##!
  This is a
  multi-line comment block.
!##!
```

### 2. Variables and Assignments

Variables are references to objects. They are declared using the `let` keyword. By default, variables are immutable.

#### 2.1. Immutable Variables

An immutable variable's reference cannot be changed after its initial assignment.

```mxscript
let x: int = 10; // Declared with an explicit type and initialized.
let y = "hello";  // Type is inferred from the assigned value.

// The following line would cause a compile-time error:
// x = 20; // Error: Cannot assign to immutable variable 'x'.
```

#### 2.2. Mutable Variables

To declare a variable whose reference can be changed, use the `let mut` keywords.

```mxscript
let mut count: int = 0;
count = 1; // This is valid.
```

#### 2.3. Assignment

Assignment is done using the `=` operator. It is an expression that changes the reference held by a mutable variable.

```mxscript
let mut a = 5;
a = 100; // 'a' now refers to the object representing 100.
```

### 3. Functions

Functions are first-class citizens in MxScript. They are defined using the `func` keyword.

#### 3.1. Function Definition

A function definition includes its name, a parameter list, an optional return type (`-> Type`), and a body block.

* **Parameters**: Multiple consecutive parameters of the same type can be grouped. Parameters can also be assigned a default value, making them optional at the call site.
* **Return Type**: If the return type is omitted, it implicitly defaults to `nil`.

```mxscript
// A function with an explicit return type.
func add(a: int, b: int) -> int {
    return a + b;
}

// A function demonstrating parameter grouping and default values.
// 'width' and 'height' share the type 'int' and default to 800.
func create_window(title: string, width, height: int, some_default_value: bool = true) {
    // ... function body ...
}

// A function with no explicit return type, so it implicitly returns nil.
func log_message(message: string) {
    println(message);
    // No 'return' statement needed for a nil return.
}
```

#### 3.2. Function Calls

Functions are called using their name followed by parentheses containing the arguments.

```mxscript
let sum = add(5, 10);
create_window("My App"); // Uses the default values for width and height.
```

### 4. Control Flow

MxScript provides a rich set of control flow statements.

#### 4.1. Conditional: `if-else`

Executes code based on a boolean condition. It supports `else if` for chaining conditions.

```mxscript
let score = 85;

if score >= 90 {
    println("Grade: A");
} else if score >= 80 {
    println("Grade: B");
} else {
    println("Grade: C or lower");
}
```

#### 4.2. Pre-test Loop: `until`

The `until` loop executes its body as long as its condition is **false**. The condition is checked *before* each iteration.

```mxscript
let mut counter = 0;

// This loop will run until counter is 5.
until (counter == 5) {
    print(counter); // Prints 0, 1, 2, 3, 4
    counter = counter + 1;
}
```

#### 4.3. Post-test Loop: `do-until`

The `do-until` loop executes its body at least once, and continues to loop as long as its condition is **false**. The condition is checked *after* each iteration.

```mxscript
let mut input = "";

// The body executes at least once.
do {
    input = read_line();
} until (input == "quit");
```

#### 4.4. Infinite Loop: `loop`

The `loop` statement creates an infinite loop that must be exited explicitly using a `break` statement.

```mxscript
loop {
    let command = get_command();
    if command == "exit" {
        break; // Exits the loop.
    }
    process_command(command);
}
```

#### 4.5. Iterator Loop: `for-in`

The `for-in` loop iterates over the elements of a collection. (Note: Requires a collection that supports the iterator protocol).

```mxscript
let names: [] List<string> = ["Alice", "Bob", "Charlie"];

for name in names {
    println(name);
}

for i in 1..100 {
    println(i);
}
```

### 5. Class, interface, builtin classes, and type system
See ![](./type_system.md)