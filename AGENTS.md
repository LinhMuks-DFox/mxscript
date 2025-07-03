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

### 2.2  Implementing a New Feature



1. **Tokenizer** – add or update tokens.  

2. **Parser** – extend grammar and AST construction.  

3. **LLVM IR generator** – emit correct IR for the new construct.



**Testing**  

* Provide comprehensive **unit tests**:  

  * **Positive** cases compile, generate valid IR, and run without error.  

  * **Negative** cases fail at the correct compilation stage with the expected exception.



### 2.3  Bug-Fix Workflow



1. **Reproduce** the reported issue.  

2. **Diagnose** root cause (Tokenizer / Parser / IR generation).  

3. **Patch** with minimal, targeted changes.  

4. **Update tests**:  

   * Add positive tests proving the fix.  

   * Add negative tests ensuring correct error handling.  

5. **Ensure all tests pass** before delivery.



---



## 3  Task Formats



| Type | Contents |

|------|----------|

| **Feature Task** | **Background** – rationale<br>**Requirements** – exact behaviour<br>**Proposed Implementation** – suggested modules / design notes |

| **Bug Report** | **Reproduction Steps** – input & command<br>**Observed** – actual error / output<br>**Expected** – correct behaviour |



Implement each request following the **Preparation → Implementation / Bug-Fix → Testing** cycle to maintain consistency and quality.

