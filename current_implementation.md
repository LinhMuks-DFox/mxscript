# MxScript Implementation Gap Analysis

This report outlines the discrepancies between the language design documents and the current formal grammar (`syntax.ebnf`).

## 1. Features Implemented Correctly
- **Variable Declarations**: The language guide shows `let` and `let mut` variables with optional type annotations and initializers【F:document/basic_syntax.md†L22-L44】. The grammar mirrors this with `let_stmt` allowing an optional `mut`, type, and initializer【F:syntax/syntax.ebnf†L76-L78】.
- **Function Definitions and Parameters**: Functions may have parameters with default values as illustrated in the guide【F:document/basic_syntax.md†L62-L76】. The rule `param` in the EBNF supports optional `= expression` for defaults【F:syntax/syntax.ebnf†L41-L42】.
- **Control Flow Constructs**: `if`, `for`, `loop`, `until`, and `do-until` statements are described in the guide【F:document/basic_syntax.md†L95-L146】 and all appear in `control_stmt` and related rules【F:syntax/syntax.ebnf†L81-L104】.
- **Interfaces**: The type system document defines interfaces with optional default implementations【F:document/type_system.md†L130-L154】. The grammar includes `interface_def` and `interface_member` rules matching this feature【F:syntax/syntax.ebnf†L24-L26】【F:syntax/syntax.ebnf†L55-L56】.
- **Error Handling with `raise` and `match`**: The guide specifies `raise` expressions and pattern matching for union types【F:document/basic_syntax.md†L216-L239】【F:document/basic_syntax.md†L268-L295】. The grammar provides `raise_expr`, `match_expr`, and `case_clause` rules【F:syntax/syntax.ebnf†L145-L153】.

## 2. Features Missing or Incomplete
- **Array and Tuple Types**: The type system specification discusses built-in `Array<T>` and tuple types, including fixed-size syntax like `[10]Vector3D`【F:document/type_system.md†L69-L212】. These type forms are absent from `type_spec`, which only accepts named types or function types【F:syntax/syntax.ebnf†L166-L170】.
- **POD and Template Annotations**: Documents introduce annotations like `@@POD` and `@@template` for generics and memory layout【F:document/type_system.md†L160-L199】【F:document/type_system.md†L181-L195】. While the grammar allows generic `annotation` syntax, it lacks dedicated rules enforcing or recognizing these specific annotations beyond free-form identifiers【F:syntax/syntax.ebnf†L156-L159】.
- **Documentation Gap for `continue` and `defer`**: The grammar supports `continue` statements and `defer` blocks【F:syntax/syntax.ebnf†L87-L106】, but these constructs are not described in the language guide.

## 3. Inconsistencies and Suggestions
- **Semicolon Usage**: Statements like `do_until_stmt` require a trailing semicolon, whereas `until_stmt`, `for_in_stmt`, and other block-based loops do not. Consider clarifying this rule in the documentation or standardizing the syntax across loops.
- **Undocumented Expressions**: The grammar includes `lambda_expr` and `block_expr`【F:syntax/syntax.ebnf†L145-L148】, yet the language guide does not explain these expressions. Documenting them or removing them from the grammar would improve alignment.
- **Missing Array Grammar**: To fully match the specification’s array features, extend `type_spec` with production rules for `[length]Type` and tuple literal syntax.
