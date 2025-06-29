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
python -m src.driver.main demo_program/hello_world.mxs
```

## Development

Tests can be run with `pytest` and code style is enforced with `ruff`:

```bash
ruff check src tests
pytest -q
```

The implementation is intentionally small to keep the focus on the language
design. See `AGENT.md` for the project philosophy and roadmap.
