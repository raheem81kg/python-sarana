# Sarana Programming Language — Project Report

**Course:** CIT4004 — Analysis of Programming Languages  
**Institution:** University of Technology, Jamaica  
**Semester:** Semester 2, 2025/2026  
**Project:** Design and Implementation of a Mini Programming Language and Compiler

---

## Group Members
Serena Morris - 2208659 
Raheem Gordon - 2208501 



## Table of Contents

1. [Introduction](#1-introduction)
2. [Language Classification](#2-language-classification)
3. [Grammar Specification](#3-grammar-specification)
4. [Tokens and Lexical Specification](#4-tokens-and-lexical-specification)
5. [Parse Tree / AST](#5-parse-tree--ast)
6. [Scope and Binding](#6-scope-and-binding)
7. [Implementation Details](#7-implementation-details)
8. [Characteristics of a Good Programming Language](#8-characteristics-of-a-good-programming-language)
9. [Compiler Phases](#9-compiler-phases)
10. [Error Handling](#10-error-handling)
11. [Testing and Validation](#11-testing-and-validation)
12. [References](#13-references)

---

## 1. Introduction

**Sarana** is a high-level, general-purpose, imperative programming language designed with Caribbean/nature-inspired keywords. The language supports:

- Arithmetic computation with correct operator precedence (PEMDAS/BODMAS)
- Variables and identifiers declared with `bloom`
- Character strings (single and double quoted)
- Output statements using `echo`
- Conditional statements (`when` / `otherwise`)
- Loops (`cycle`)
- Functions (`craft` / `return`)
- Exception handling (`try` / `ketch`)
- Boolean logic with short-circuit evaluation

The name "Sarana" reflects our Caribbean heritage and the natural, organic growth of programs written in the language.

### Required Sample Program

The following program satisfies the minimum project requirement:

```sarana
-- Sample program
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;   -- PEMDAS: 20 + (40 * 40) = 1620

-- Demonstrating Exception Handling
try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}

echo "The result is " C;
```

**Expected Output:**
```
Error: Division by zero attempted but not allowed.
The result is 1620
```

---

## 2. Language Classification

### Paradigm
**Imperative / Procedural**

Sarana follows a sequential, step-by-step execution model where the programmer specifies *how* the computer should accomplish a task through explicit commands. Programs are composed of statements that change program state (variable assignments, loops, conditionals, function calls).

### Purpose
**General-purpose**

Sarana is not limited to a specific application domain. It can be used for:
- Mathematical computation
- String manipulation
- Control flow logic
- Function-based abstraction
- General algorithmic problem-solving

### Level
**High-level**

Sarana abstracts away low-level hardware details. Programmers work with:
- Named variables (not memory addresses)
- Natural keywords (`bloom`, `echo`, `cycle`)
- Automatic memory management (handled by the Python runtime during code generation)
- No manual register or stack management

---

## 3. Grammar Specification

The Sarana language is specified in **Extended Backus-Naur Form (EBNF)**:

```ebnf
program       ::= statement* EOF

statement     ::= bloom_stmt
               | echo_stmt
               | when_stmt
               | cycle_stmt
               | craft_stmt
               | try_stmt
               | return_stmt
               | expression_stmt

bloom_stmt    ::= 'bloom' IDENTIFIER '=' expression ';'

echo_stmt     ::= 'echo' expression+ ';'

when_stmt     ::= 'when' '(' expression ')' block else_tail

else_tail     ::= 'otherwise' 'when' '(' expression ')' block else_tail
               | 'otherwise' block
               | ε

cycle_stmt    ::= 'cycle' '(' expression ')' block

craft_stmt    ::= 'craft' IDENTIFIER '(' params? ')' block

return_stmt   ::= 'return' expression ';'

try_stmt      ::= 'try' block 'ketch' block

expression_stmt ::= expression ';'

block         ::= '{' statement* '}'

params        ::= IDENTIFIER (',' IDENTIFIER)*

args          ::= expression (',' expression)*

expression    ::= logic_or

logic_or      ::= logic_and ( 'or' logic_and )*

logic_and     ::= equality ( 'and' equality )*

equality      ::= comparison ( ('==' | '!=') comparison )*

comparison    ::= term ( ('<' | '>' | '<=' | '>=') term )*

term          ::= factor ( ('+' | '-') factor )*

factor        ::= unary ( ('*' | '/' | '%') unary )*

unary         ::= ('not' | '-') unary | primary

primary       ::= INTEGER
               | FLOAT
               | STRING
               | 'true'
               | 'false'
               | IDENTIFIER
               | IDENTIFIER '(' args? ')'
               | '[' args? ']'
               | '(' expression ')'
```

### Grammar Properties

| Property | Value |
|----------|-------|
| **Type** | Context-Free Grammar (CFG) |
| **Notation** | EBNF (Extended Backus-Naur Form) |
| **Precedence** | Encoded in grammar hierarchy (PEMDAS compliant) |
| **Recursion** | Left recursion eliminated for LL parsing |
| **Ambiguity** | Unambiguous (single derivation per valid program) |

---

## 4. Tokens and Lexical Specification

The lexical analyzer (lexer) converts raw source text into a stream of tokens. Each token has a **type**, **value**, and **line number**.

### Full Token List

| Token Type | Pattern | Example |
|------------|---------|---------|
| `BLOOM` | keyword `bloom` | `bloom` |
| `ECHO` | keyword `echo` | `echo` |
| `WHEN` | keyword `when` | `when` |
| `OTHERWISE` | keyword `otherwise` | `otherwise` |
| `CYCLE` | keyword `cycle` | `cycle` |
| `CRAFT` | keyword `craft` | `craft` |
| `RETURN` | keyword `return` | `return` |
| `TRY` | keyword `try` | `try` |
| `KETCH` | keyword `ketch` | `ketch` |
| `TRUE` | keyword `true` | `true` |
| `FALSE` | keyword `false` | `false` |
| `AND` | keyword `and` | `and` |
| `OR` | keyword `or` | `or` |
| `NOT` | keyword `not` | `not` |
| `IDENTIFIER` | `[a-zA-Z_][a-zA-Z0-9_]*` | `x`, `myVar` |
| `INTEGER` | `[0-9]+` | `42`, `1620` |
| `FLOAT` | `[0-9]+\.[0-9]+` | `3.14`, `0.5` |
| `STRING` | `"..."` or `'...'` | `"hello"`, `'world'` |
| `PLUS` | `+` | `a + b` |
| `MINUS` | `-` | `a - b` |
| `MULTIPLY` | `*` | `a * b` |
| `DIVIDE` | `/` | `a / b` |
| `MODULO` | `%` | `a % b` |
| `ASSIGN` | `=` | `bloom x = 5` |
| `DOUBLE_EQUALS` | `==` | `x == y` |
| `NOT_EQUALS` | `!=` | `x != y` |
| `LESS_THAN` | `<` | `x < y` |
| `GREATER_THAN` | `>` | `x > y` |
| `LESS_EQUAL` | `<=` | `x <= y` |
| `GREATER_EQUAL` | `>=` | `x >= y` |
| `LPAREN` | `(` | function calls, conditions |
| `RPAREN` | `)` | |
| `LBRACE` | `{` | block start |
| `RBRACE` | `}` | block end |
| `LBRACKET` | `[` | array start |
| `RBRACKET` | `]` | array end |
| `SEMICOLON` | `;` | statement terminator |
| `COMMA` | `,` | argument separator |

### Regular Expressions

The lexer uses the following regex patterns (implemented via PLY):

```python
# Keywords (checked first, before IDENTIFIER)
reserved = {
    'bloom': 'BLOOM',
    'echo': 'ECHO',
    'when': 'WHEN',
    'otherwise': 'OTHERWISE',
    'cycle': 'CYCLE',
    'craft': 'CRAFT',
    'return': 'RETURN',
    'try': 'TRY',
    'ketch': 'KETCH',
    'true': 'TRUE',
    'false': 'FALSE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}

# Literals
t_IDENTIFIER = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_FLOAT = r'\d+\.\d+'
t_INTEGER = r'\d+'
t_STRING = r'"[^"]*"|\'[^\']*\''

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_ASSIGN = r'='
t_DOUBLE_EQUALS = r'=='
t_NOT_EQUALS = r'!='
t_LESS_EQUAL = r'<='
t_GREATER_EQUAL = r'>='
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'

# Delimiters
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','

# Comments (ignored by lexer)
def t_COMMENT(t):
    r'--[^\n]*'
    pass  # No token returned
```

---

## 5. Parse Tree / AST

The parser builds an **Abstract Syntax Tree (AST)** from the token stream. Each AST node represents a syntactic construct.

### AST Node Classes

| Node Class | Represents |
|------------|-----------|
| `Program` | Root node containing all top-level statements |
| `BloomStatement` | Variable declaration: `bloom x = expr;` |
| `EchoStatement` | Output: `echo expr1 expr2;` |
| `WhenStatement` | Conditional: `when (cond) { ... } otherwise { ... }` |
| `CycleStatement` | Loop: `cycle (cond) { ... }` |
| `CraftStatement` | Function definition: `craft name(params) { ... }` |
| `ReturnStatement` | Return: `return expr;` |
| `TryKetchStatement` | Exception handler: `try { ... } ketch { ... }` |
| `BinaryOp` | Binary operation: `a + b`, `x == y` |
| `UnaryOp` | Unary operation: `not x`, `-5` |
| `FunctionCall` | Function call: `add(1, 2)` |
| `Variable` | Variable reference: `x` |
| `Integer` | Integer literal: `42` |
| `Float` | Float literal: `3.14` |
| `String` | String literal: `"hello"` |
| `Boolean` | Boolean literal: `true`, `false` |
| `Array` | Array literal: `[1, 2, 3]` |

### Parse Tree for Required Sample

For `bloom C = A + B * B;` (with PEMDAS):

```
BloomStatement
├── name: "C"
└── value: BinaryOp(+)
    ├── left: Variable("A")
    └── right: BinaryOp(*)
        ├── left: Variable("B")
        └── right: Variable("B")
```

The multiplication is deeper in the tree, meaning it executes first (correct PEMDAS).

Full parse tree diagrams for all sample programs are available in `PARSE_TREE_DIAGRAMS.txt`.

---

## 6. Scope and Binding

### Scope Rules

Sarana implements **lexical (static) scoping**:

1. **Global scope** — Variables declared at the top level are visible throughout the program
2. **Function scope** — Variables declared inside a function (via `bloom`) are local to that function
3. **Block scope** (runtime) — Enforced by the interpreter; variables declared in `when`, `cycle`, or `try` blocks follow Python's scoping rules when compiled to Python

### Binding Time

| Entity | Binding Time |
|--------|--------------|
| Variable names | Compile-time (semantic analysis checks declaration) |
| Variable values | Run-time (assigned during execution) |
| Function names | Compile-time (checked during semantic analysis) |
| Function bodies | Compile-time (parsed into AST) |
| Operator precedence | Language definition time (fixed in grammar) |

### Demonstration: `samples/sample2.sa`

```sarana
-- Scope and Binding Demonstration

bloom globalVar = 100;

craft showScope(x) {
    bloom localVar = x * 2;
    echo "Inside function, local x is: " localVar;
    echo "Global variable is: " globalVar;
    return localVar;
}

bloom result = showScope(10);
echo "Returned: " result;
echo "Global unchanged: " globalVar;
```

**Output:**
```
Inside function, local x is: 20
Global variable is: 100
Returned: 20
Global unchanged: 100
```

**Analysis:**
- `globalVar` is bound at global scope (line 3)
- `localVar` is bound at function scope (line 6) — not visible outside `showScope`
- `x` (parameter) shadows any global `x` inside the function
- `globalVar` is accessible from within the function (lexical scoping)

---

## 7. Implementation Details

### Programming Language Used

**Python 3.9+**

### Tools and Libraries

| Tool | Purpose |
|------|---------|
| **PLY (Python Lex-Yacc)** | Lexer and parser generation |
| **Streamlit** | Web UI framework |
| **Anthropic API (Claude)** | LLM comparison for execution |
| **pytest** | Unit and integration testing |
| **pandas** | Token table display in UI |
| **streamlit-ace** | Code editor with line numbers |

### File Structure

```
python-sarana/
├── src/
│   ├── lexer.py        # Phase 1 — Lexical analysis
│   ├── parser.py       # Phase 2 — Syntax analysis
│   ├── ast_nodes.py    # AST node definitions
│   ├── semantic.py     # Phase 3 — Semantic analysis
│   ├── interpreter.py  # Phase 4 — Execution
│   ├── codegen.py      # Phase 5 — Python code generation
│   ├── errors.py       # Custom error classes
│   └── sarana.py       # Main entry point / unified API
│
├── app/
│   ├── Code_Editor.py  # Main Streamlit page (code editor)
│   └── pages/
│       └── Language_Docs.py  # Language reference page
│
├── samples/
│   ├── sample1.sa      # Required assignment sample
│   ├── sample2.sa      # Scope and binding demo
│   ├── sample3.sa      # Functions and loops
│   └── sample4.sa      # Boolean logic and else-if
│
├── tests/
│   ├── test_phase1_lexer.py
│   ├── test_phase2_parser.py
│   ├── test_phase3_semantic.py
│   ├── test_phase4_interpreter.py
│   ├── test_phase5_codegen.py
│   └── test_all_samples.py
│
├── assets/             # Logo images
├── LANGUAGE_DOCS.md    # Complete language reference
├── README.md           # Installation and usage guide
└── PROJECT_REPORT.md   # This document
```

---

## 8. Characteristics of a Good Programming Language

Sarana demonstrates all **nine characteristics** studied in CIT4004:

### 1. Readability

**Definition:** How easily a program can be read and understood by humans.

**In Sarana:**
- Natural Caribbean/nature-inspired keywords: `bloom` (declare), `echo` (output), `ketch` (catch)
- Self-documenting statements: `bloom x = 10;` is immediately understandable
- Consistent syntax: all blocks use `{ }`, all statements end with `;`

**Example:**
```sarana
bloom score = 85;
when (score >= 60) {
    echo "Passed!";
}
```
Even a non-programmer can infer what this code does.

### 2. Writability

**Definition:** How easily a language allows a programmer to express solutions.

**In Sarana:**
- Minimal boilerplate — no imports, no `main()` function required
- Expressive operators — PEMDAS arithmetic, comparison, logic
- Multi-expression `echo` — `echo "result is" x` (no concatenation operator needed)

**Example:**
```sarana
craft add(a, b) { return a + b; }
echo add(3, 4);
```
2 lines to define and call a function.

### 3. Reliability

**Definition:** The language's ability to detect and prevent errors.

**In Sarana:**
- **Static semantic analysis** catches undefined variables/functions *before* execution
- **Exception handling** (`try` / `ketch`) allows graceful recovery from runtime errors
- **Type checking** (heuristic) warns about incompatible operations (string + integer)

**Example:**
```sarana
try {
    bloom x = 10 / 0;
}
ketch {
    echo "Division by zero caught!";
}
```
Program does not crash — error is handled.

### 4. Simplicity

**Definition:** Small number of basic constructs; easy to learn.

**In Sarana:**
- Only **14 keywords** (compared to 35+ in Python, 50+ in Java)
- One way to declare variables (`bloom`), one way to loop (`cycle`)
- No multiple assignment operators (`+=`, `-=`, etc.) — just `=`

### 5. Orthogonality

**Definition:** Constructs combine in predictable ways without special cases.

**In Sarana:**
- Any expression can appear wherever an expression is expected:
  - `bloom x = (a > b) and (c < d);` — boolean expression as value
  - `echo f(g(h(x)));` — nested function calls
  - `bloom arr = [1, 2, add(3, 4)];` — function call inside array literal
- No "this operator only works with integers" or "you can't return a boolean from a function" restrictions

### 6. Data Types

**Definition:** Rich set of data types with appropriate operations.

**In Sarana:**

| Type | Literals | Operations |
|------|----------|------------|
| `Integer` | `42`, `-7` | `+`, `-`, `*`, `/`, `%`, comparisons |
| `Float` | `3.14`, `-0.5` | Same as integer |
| `String` | `"hello"`, `'world'` | Concatenation (via `echo`), comparisons |
| `Boolean` | `true`, `false` | `and`, `or`, `not`, comparisons |
| `Array` | `[1, 2, 3]` | Indexing (future), length (future) |

### 7. Syntax Design

**Definition:** Clarity, consistency, and lack of ambiguity in syntax rules.

**In Sarana:**
- **Explicit delimiters:** `{ }` for blocks, `;` for statement terminators → no "significant whitespace" confusion
- **Consistent precedence:** PEMDAS encoded in grammar → `a + b * c` always means `a + (b * c)`
- **Unambiguous grammar:** Single parse tree for every valid program

**Contrast with Python:**
```python
if x > 0:
print("positive")  # IndentationError if wrong indent level
```

**Sarana:**
```sarana
when (x > 0) {
    echo "positive";
}
```
Braces eliminate indent ambiguity.

### 8. Support for Abstraction

**Definition:** Ability to define and use abstract data types, functions, modules.

**In Sarana:**
- **Procedural abstraction:** `craft` functions with parameters and return values
- **Local scope:** Variables inside functions are hidden from the outside
- **Recursion:** Supported (e.g., `factorial(n) = n * factorial(n-1)`)

**Example:**
```sarana
craft multiply(a, b) {
    bloom product = 0;
    bloom count = 0;
    cycle (count < b) {
        bloom product = product + a;
        bloom count = count + 1;
    }
    return product;
}

echo multiply(6, 7);  -- 42
```
User defines a new operation (`multiply`) using primitive operations.

### 9. Exception Handling

**Definition:** Mechanisms to handle runtime errors gracefully.

**In Sarana:**
- `try` / `ketch` blocks catch runtime exceptions
- Program continues after catching an error
- Static analyzer suppresses division-by-zero warnings inside `try` blocks (intentional error handling)

**Example (from required sample):**
```sarana
try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}
echo "Program continues...";
```

---

## 9. Compiler Phases

The Sarana compiler implements all five major phases:

### Phase 1: Lexical Analysis

**Module:** `src/lexer.py`

**Input:** Raw `.sa` source code (string)  
**Output:** List of tokens `[(type, value, line), ...]`

**Process:**
1. Reads source character by character
2. Matches patterns using PLY regex rules
3. Identifies keywords, identifiers, literals, operators, delimiters
4. Strips comments (`--` to end of line)
5. Tracks line numbers for error reporting

**Example:**
```sarana
bloom x = 10;
```
Tokens:
```
[('BLOOM', 'bloom', 1),
 ('IDENTIFIER', 'x', 1),
 ('ASSIGN', '=', 1),
 ('INTEGER', 10, 1),
 ('SEMICOLON', ';', 1)]
```

### Phase 2: Syntax Analysis (Parsing)

**Module:** `src/parser.py`

**Input:** Token stream  
**Output:** Abstract Syntax Tree (AST)

**Process:**
1. PLY YACC parser matches tokens to grammar rules
2. Each grammar rule has a Python action function that constructs AST nodes
3. PEMDAS is enforced by grammar precedence hierarchy
4. Raises `ParseError` if tokens don't match any valid rule

**Example:**
```sarana
bloom C = A + B * B;
```
AST:
```
BloomStatement(
    name='C',
    value=BinaryOp(
        operator='+',
        left=Variable('A'),
        right=BinaryOp(operator='*', left=Variable('B'), right=Variable('B'))
    )
)
```

### Phase 3: Semantic Analysis

**Module:** `src/semantic.py`

**Input:** AST  
**Output:** List of semantic errors (if any)

**Process:**
1. Walk the AST (visitor pattern)
2. Track declared variables and functions (symbol table)
3. Check:
   - Variable used before `bloom`?
   - Function called before `craft`?
   - Division by literal zero (outside `try` blocks)?
   - Type mismatches (heuristic)
4. Collect *all* errors (does not stop at first error)

**Example:**
```sarana
echo x;  -- Error: 'x' used before being declared with 'bloom'
```

### Phase 4: Execution (Interpreter)

**Module:** `src/interpreter.py`

**Input:** AST  
**Output:** Program output (list of strings)

**Process:**
1. Walk the AST (visitor pattern)
2. Maintain environment (variable → value mapping)
3. Execute each statement:
   - `BloomStatement` → store value in environment
   - `EchoStatement` → print values to output list
   - `WhenStatement` → evaluate condition, execute appropriate branch
   - `CycleStatement` → loop while condition is true
   - `CraftStatement` → store function in environment
   - `TryKetchStatement` → execute try body, catch exceptions
4. Short-circuit evaluation for `and` / `or` operators
5. Raise `SaranaRuntimeError` on division by zero, type errors

### Phase 5: Target Code Generation

**Module:** `src/codegen.py`

**Input:** AST  
**Output:** Executable Python source code (string)

**Process:**
1. Walk the AST (visitor pattern)
2. Translate each node to equivalent Python:
   - `bloom x = 5;` → `x = 5`
   - `echo "hi" x;` → `print("hi", x)`
   - `when (x > 0) { ... }` → `if x > 0:\n    ...`
   - `cycle (i < 3) { ... }` → `while i < 3:\n    ...`
   - `craft add(a, b) { ... }` → `def add(a, b):\n    ...`
   - `try { ... } ketch { ... }` → `try:\n    ...\nexcept Exception:\n    ...`
3. Generated code can be saved to a `.py` file and executed with `python3`

**Example:**
```sarana
bloom x = 5;
echo x;
```
Generated Python:
```python
x = 5
print(x)
```

---

## 10. Error Handling

Sarana provides comprehensive error detection and reporting across all phases:

### Error Types

| Error Class | Phase | When it occurs |
|-------------|-------|----------------|
| `LexError` | Lexical | Unrecognized character in source code |
| `ParseError` | Syntax | Source violates grammar rules (e.g., missing `;`) |
| `SemanticError` | Semantic | Undefined variable/function, type mismatch, div-by-zero |
| `SaranaRuntimeError` | Execution | Runtime error (actual division by zero, type error at runtime) |
| `UnexpectedEndError` | Parsing | Unclosed block, missing `}` |

### Error Messages

All errors include:
- **Error type** (e.g., "Semantic Error")
- **Line number** where the error occurred
- **Description** of the problem
- **Suggestion** (when applicable)

**Example:**
```
[Line 5] Semantic Error: Variable 'x' used before being declared with 'bloom'
```

### Color Coding (CLI)
- **Green** — Compilation success
- **Red** — Errors
- **Yellow** — Warnings (e.g., semantic notes that don't block compilation)

### Web UI Error Display

Errors are collected and displayed in an expandable "Errors & Warnings" section with:
- Line-by-line error list
- Color-coded severity (red for errors, yellow for warnings)
- Clickable line numbers (future: jump to code editor line)

---

## 11. Testing and Validation

### Test Coverage by Phase

| File | Phase | Test Count | Coverage |
|------|-------|-----------|----------|
| `test_phase1_lexer.py` | Lexical | 34 | Keywords, literals, operators, line numbers, lex errors |
| `test_phase2_parser.py` | Syntax | 23 | AST structure, PEMDAS, all statement types, parse errors |
| `test_phase3_semantic.py` | Semantic | 15 | Undefined vars/functions, div-by-zero, type checks |
| `test_phase4_interpreter.py` | Execution | 30 | Arithmetic, conditionals, loops, functions, try/ketch, booleans |
| `test_phase5_codegen.py` | Code Gen | 15 | Translation rules, generated code produces correct output |
| `test_all_samples.py` | End-to-end | 12 | All 4 sample `.sa` files compile and run successfully |


### Sample Programs Tested

1. **sample1.sa** — Required assignment sample (PEMDAS + try/ketch)
2. **sample2.sa** — Scope and binding demonstration
3. **sample3.sa** — Functions, loops, recursion (multiply, factorial, fibonacci)
4. **sample4.sa** — Boolean logic, else-if chains, short-circuit evaluation


## 13. References

1. Aho, A. V., Sethi, R., & Ullman, J. D. (1986). *Compilers: Principles, Techniques, and Tools*. Addison-Wesley.
2. Beazley, D. M. (2021). *PLY (Python Lex-Yacc)*. https://www.dabeaz.com/ply/ply.html
3. Sebesta, R. W. (2015). *Concepts of Programming Languages* (11th ed.). Pearson.
4. Anthropic. (2024). *Claude API Documentation*. https://docs.anthropic.com/
5. Streamlit Inc. (2024). *Streamlit Documentation*. https://docs.streamlit.io/


