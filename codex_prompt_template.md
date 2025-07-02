# Codex Prompt Templates

This file contains standardized templates for submitting new tasks and bug reports.

---

## Template 1: New Feature Implementation Task

```markdown
**Task:** [A clear, concise title for the feature]

**Goal:**
[Describe the high-level objective and the desired final outcome. What should be possible after this task is complete?]

**Context/Background:**
[Provide any necessary background information. Why is this feature needed? How does it fit into the existing design? Refer to specific sections of design documents if applicable.]

**Files to Modify:**
* `src/path/to/file1.py`
* `syntax/syntax.ebnf`
* ...

**Detailed Instructions:**
1. **Step 1**: [A clear, imperative instruction.]
2. **Step 2**: [Another clear instruction.]
3. **Step 3**: [Provide code snippets or logic outlines where necessary.]

**Acceptance Criteria:**
* [A list of conditions that must be met for the task to be considered complete. For example: "All existing unit tests must pass," or "A new unit test, `test_my_new_feature`, must be added and pass."]
```

---

## Template 2: Bug Report

```markdown
**Bug:** [A short, descriptive title of the bug]

**Observed Behavior:**
[Describe exactly what is happening. Include full error messages and stack traces.]

**Expected Behavior:**
[Describe what should have happened instead.]

**Steps to Reproduce:**
1. **File:** [Name of the test file or source file, e.g., `tests/test_parser.py`]
2. **Code Snippet:**
    ```mxscript
    // The minimal piece of MxScript code that triggers the bug.
    ```
3. **Command:** [The exact command used to run the code, e.g., `python main.py my_file.mxs`]

**Relevant Files:**
* [List any other files that might be relevant to understanding the bug's context.]
```
