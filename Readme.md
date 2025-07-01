# MxScript

MxScript is a prototype programming language that mixes the convenience of a
scripting language with the safety of a statically typed language. The project
is composed of several stages:

1. **Tokenizer** – breaks source text into tokens.
2. **Syntax parser** – builds an Abstract Syntax Tree (AST) according to
   [`syntax/syntax.ebnf`](syntax/syntax.ebnf).
3. **Semantic analyzer** – performs simple semantic checks such as verifying that
   variables are defined before use.
4. **Backend** – converts the AST into a tiny LLIR, performs constant folding
   and interprets the result.

The repository contains a minimal driver which wires all stages together so you
can parse and execute `.mxs` files:

```bash
python main.py demo_program/examples/hello_world.mxs
```

Additional examples are located in `demo_program/examples`. Each file focuses on
a single feature. You can run them the same way:

```bash
python main.py demo_program/examples/generic_swap.mxs
```

To execute using the LLVM backend, pass `--compile-mode llvm`.

### Module search path

Modules are loaded from `demo_program/examples/std` by default. Additional
directories can be provided via the `MXSCRIPT_PATH` environment variable or the
`-I/--search-path` command-line flag.

### Standard library

The prototype includes a few builtin modules. `std.time` exposes `now()` to get
the current time, while `std.random` offers `rand()` for generating
pseudo-random values. These functions are implemented through small FFI wrappers
that call the underlying system facilities.

## Development

Tests can be run with `pytest` and code style is enforced with `ruff`:

```bash
ruff check src tests
pytest -q
```

The implementation is intentionally small to keep the focus on the language
design. See `AGENTS.md` for the project philosophy and roadmap.
