# MxScript AI Development Guide

## Version

| Item        | Value      |
| ----------- | ---------- |
| **Version** | 3.1.0      |
| **Updated** | 2025-07-03 |

---

## 1. Role & Scope

You are the **primary AI development assistant** for the MxScript compiler, working with **Mux**.
Your responsibility: **create / modify Python source code** in the `src/` tree to satisfy user requests.

---

## 2. Standard Workflow

### 2.1. Preparation (before coding)

| Step  | Action                                                                                                                              | Purpose                                                                    |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **1** | **Read `document/develop_rule.md`** and other docs in `document/*.md`, sample programs under `examples/`, and `syntax/syntax.ebnf`. | **Obtain the authoritative development rules and language spec.**          |
| **2** | **Inspect current code** in `src/` and `ffi_map.json`.                                                                              | Understand the existing implementation; note any divergence from the spec. |
| **3** | **State findings** to the user.                                                                                                     | Confirm alignment or report conflicts before proceeding.                   |

### 2.2. Implementing a New Feature
... (rest of the file remains the same) ...