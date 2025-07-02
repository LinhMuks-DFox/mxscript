# MXScript Type System Specification

This document outlines the architecture and design of the MXScript type system. It is a unified, object-oriented system designed for safety, expressiveness, and clarity.

### 1. Core Philosophy

The type system is built on three fundamental principles that create a consistent and predictable programming model:

1.  **Everything is an Object**: There is no distinction between primitive types and object types. Every value, from an integer to a user-defined class instance, is treated as a first-class object.
2.  **All Variables are References**: Variables in MXScript do not store objects directly. Instead, they hold references (pointers) to objects that reside on the heap.
3.  **Memory is Managed Automatically**: Object lifetimes are managed by an Automatic Reference Counting (ARC) system. The compiler is responsible for inserting the necessary `retain` and `release` calls to manage memory automatically.

### 2. The `Object` Root Type

`Object` is the implicit root class for all types in MXScript. Every other type, whether built-in or user-defined, inherits from `Object`. It provides a common interface and foundational capabilities.

The backend representation of every object includes a header containing:

* **Reference Count**: A 64-bit integer for the ARC system. A special value (e.g., -1) can be used to denote global, immutable constants that should not be deallocated.
* **Virtual Table Pointer**: A pointer to the type's virtual method table (v-table), enabling dynamic dispatch for polymorphic method calls like `to_string()`.
* **Destructor Pointer**: A function pointer to the object's specific destructor (`~Type()`) for proper cleanup.

The `Object` class defines the following core methods that can be overridden by subclasses:

* `func hash() -> int`: Returns a hash code for the object. The default implementation may be based on the object's memory address (identity hashing).
* `func equals(other: Object) -> bool`: Compares two objects. The default implementation performs a reference comparison (identity equality). Subclasses should override this to provide value equality.
* `func to_string() -> String`: Returns a string representation of the object. This is used by `println()` and for general serialization.

### 3. Built-in Types

#### 3.1. Fundamental Types

* **`bool`**
    * **Description**: Represents a boolean value.
    * **Semantics**: Has only two possible instances: the global constants `true` and `false`.

* **`String`**
    * **Description**: Represents a sequence of characters.
    * **Semantics**: `String` objects are **immutable**. Any operation that appears to modify a string (e.g., concatenation) will produce a new `String` object.
    * **Implementation**: Implemented as a hybrid type. The compiler has intrinsic knowledge of its memory layout (`ref_count`, `length`, `data*`) and provides high-performance implementations for core methods (e.g., `length()`). Higher-level methods are implemented in the standard library.

* **`nil`**
    * **Description**: Represents the absence of a value.
    * **Semantics**: `nil` is a singleton value. It can be assigned to any variable of any reference type.

#### 3.2. Numeric Types

* **`int`**
    * **Description**: A signed integer of arbitrary precision.
    * **Implementation**: The compiler may use optimized representations for common sizes (e.g., i64) and automatically promote to a heap-allocated "long int" representation when the value exceeds the optimized range.

* **`float`**
    * **Description**: A floating-point number.
    * **Implementation**: Can be backed by standard `float32` or `float64` representations.

* **`decimal`**
    * **Description**: A high-precision decimal type suitable for financial calculations, avoiding binary floating-point inaccuracies.
    * **Implementation**: Represented by a struct containing the sign and digits for the integer and fractional parts.

* **`complex`**
    * **Description**: Represents a complex number with real and imaginary parts.

#### 3.3. Container Types

* **`List<T>`**
    * **Description**: A dynamic, ordered collection of elements of type `T`.
    * **Syntax**: Can be instantiated via `List<T>()` or with the literal syntax `[element1, element2, ...]`.

* **`Array<T>`**
    * **Description**: A fixed-size, contiguous array of elements of type `T`. The compiler employs an intelligent storage strategy to optimize for performance and memory layout based on the element type `T`.
    * **Syntax**: Defined by the type signature `[length]Type`, e.g., `[10]int`.
    * **Storage Strategy**:
        * **Direct Storage (Unboxed)**: For maximum performance and C-interoperability, the array stores values directly in a contiguous memory block under the following conditions:
            * The element type is a primitive numeric type (`int`, `float`).
            * The element type is a user-defined `Object` that implements the `to_pod()` method, which provides a Plain Old Data (POD) representation.
        * **Indirect Storage (Boxed)**: This is the default, safe strategy for all other types. The array stores a contiguous sequence of pointers to the objects on the heap. This applies to:
            * The built-in `String` type.
            * Any user-defined `Object` that does not implement the `to_pod()` method.

* **`Tuple`**
    * **Description**: A fixed-size, ordered collection of elements that can have different types. Tuples are immutable.
    * **Syntax**: Defined by `(element1, "hello", 5)`.

* **`Dict<K, V>`**
    * **Description**: A collection of key-value pairs.
    * **Syntax**: Instantiated via `Dict<K, V>()` or a literal syntax like `[key1: value1, key2: value2]`.

### 4. User-Defined Types

#### 4.1. Classes

Classes are the primary mechanism for creating custom types with state and behavior.

```mxscript
class ClassName : SuperClass {
public:
    let pub_immutable_member: int;
    let mut pub_mutable_member: int;

    // Constructor
    ClassName(arg: int) : SuperClass() {
        // Immutable members can only be assigned within a constructor.
        self.pub_immutable_member = arg;
    }

    // Destructor
    ~ClassName() : ~SuperClass() {
        // Cleanup logic here. Superclass destructor is called automatically.
    }

    func method() {
        self.pub_mutable_member = 1;
    }

    override func to_string() -> String {
        return "An instance of ClassName";
    }

private:
    let _private_member: int;
}
```

* **Inheritance**: Classes support single inheritance using the `:` syntax.
* **Member Declaration**: Members are declared with `let` (immutable) or `let mut` (mutable).
* **Constructors**: Responsible for initializing the object. Immutable members can only be assigned within the scope of a constructor.
* **Destructors**: Called automatically by the ARC system when an object's reference count drops to zero. A subclass destructor automatically chains to its superclass's destructor.
* **Method Overriding**: The `override` keyword is mandatory when providing a new implementation for a method inherited from a superclass.

#### 4.2. Interfaces

Interfaces define a contract of methods that a class can choose to implement. They are a powerful tool for abstraction.

```mxscript
interface Printable {
    // All interface methods are implicitly public.
    func print_to_console();

    func get_debug_info() -> String {
        // Interfaces can provide default implementations.
        return "No debug info";
    }
}

class MyReport : Printable {
    override func print_to_console() {
        // Implementation of the interface method.
    }
}
```

* **Contract**: An interface defines a set of method signatures.
* **Implementation**: A class implements an interface by listing it in its inheritance clause and providing implementations for its methods.
* **Default Implementations**: Interfaces can provide default implementations for their methods, which can be used or overridden by conforming types.

### 5. Generics (Templates)

Generics allow for writing flexible, reusable functions and types that can work with any type that satisfies the necessary constraints.

* **Generic Definition**: A generic function or type is defined using the `@@template` annotation.
    ```mxscript
    @@template(T)
    func swap(a: T, b: T) -> (T, T) {
        return (b, a);
    }
    ```

* **Generic Specialization**: The system can support providing specialized, high-performance implementations for specific types.
    ```mxscript
    // A specialized version of a generic function for when T is int.
    @@template<T=int>
    func do_something(val: T) {
        // Highly optimized code for integers.
    }
    ```
* **Compilation Strategy**: Generics are compiled using **Monomorphization**. The compiler creates a specialized version of the generic code for each concrete type it is used with, ensuring static type safety and eliminating runtime overhead.


### 6. Plain Old Data (POD)

To bridge the gap between high-level object-oriented abstractions and low-level performance, MXScript incorporates the concept of Plain Old Data (POD). A POD type is a type that has a simple, C-compatible memory layout and can be safely manipulated with direct memory operations, enabling significant optimizations, especially for arrays.

#### 6.1. The `@@POD` Annotation

A type is designated as POD through the `@@POD` annotation. This annotation is a contract with the compiler, declaring that instances of the class can be treated as simple, contiguous blocks of data without requiring complex object-oriented machinery like v-table lookups or ARC for their members.

```mxscript
// Vector3D is declared as a POD type.
@@POD
class Vector3D {
    let x: float;
    let y: float;
    let z: float;
}
```

#### 6.2. Rules for a POD Type

For the `@@POD` annotation to be valid, the compiler performs a strict, recursive static analysis at compile-time. A class is considered a valid POD type if and only if **all of its instance members are also POD types**.

The base cases for this recursive definition are:
* All primitive numeric types (`int`, `float`, `bool`, `decimal`) are inherently POD.
* An `Array<T>` is a POD type if and only if `T` is a POD type.
* Any class correctly marked with `@@POD` is considered a POD type.

If a class is marked `@@POD` but contains a non-POD member (like a `String` or a standard `Object` reference), the compiler will raise a compile-time error.

#### 6.3. Compiler-Managed Storage Strategy

The primary benefit of the POD system is its impact on the `Array<T>` storage strategy. The compiler uses the POD designation to choose the most efficient memory layout:

* **Direct Storage (Unboxed)**: If `T` is a POD type, an `Array<T>` will be a true, contiguous block of `T` values in memory. For example, `[10]Vector3D` will be a single memory block of `10 * sizeof(Vector3D)`. This layout is cache-friendly, offers maximum performance, and allows for zero-copy interoperability with C/C++ libraries.
* **Indirect Storage (Boxed)**: If `T` is not a POD type (the default for most classes), the `Array<T>` stores a contiguous sequence of pointers to the objects, which are individually allocated on the heap.
