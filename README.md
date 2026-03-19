# 🌿 Sarana Programming Language

**Sarana** is a high-level, general-purpose, imperative programming language with a Caribbean/nature-inspired keyword set. It was designed and built as a university project for CIT4004 (Analysis of Programming Languages) at the University of Technology, Jamaica.

---

## Language at a Glance

Sarana uses readable English-like keywords with JavaScript-style braces and semicolons.

| Sarana Keyword | Meaning         | Equivalent in other languages |
|----------------|-----------------|-------------------------------|
| `bloom`        | Declare variable | `let`, `var`                 |
| `echo`         | Print output     | `print()`                    |
| `when`         | If condition     | `if`                         |
| `otherwise`    | Else branch      | `else`                       |
| `cycle`        | While loop       | `while`                      |
| `craft`        | Define function  | `def`, `func`                |
| `return`       | Return value     | `return`                     |
| `try`          | Try block        | `try`                        |
| `ketch`        | Catch exception  | `catch`, `except`            |
| `--`           | Comment          | `#`, `//`                    |

---

## Sample Program

```sarana
-- Required assignment sample program

bloom A = 20;
bloom B = 40;
bloom C = A + B * B;

-- Demonstrating Exception Handling
try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}

echo "The result is " C;
```

**Expected output:**
```
Error: Division by zero attempted but not allowed.
The result is 1620
```

---

## Project Structure

```
python-sarana/
├── src/
│   ├── lexer.py        # Tokenizer — converts source code to tokens
│   ├── parser.py       # Parser — builds AST from tokens
│   ├── ast_nodes.py    # AST node class definitions
│   ├── semantic.py     # Semantic analyzer — scope, types, error detection
│   ├── interpreter.py  # AST walker — executes the program
│   ├── codegen.py      # Code generator — outputs Python source code
│   ├── errors.py       # Custom error classes
│   └── sarana.py       # Main entry point — ties all phases together
│
├── app/
│   └── ui.py           # Streamlit web UI
│
├── samples/
│   ├── sample1.sara    # Required assignment sample
│   ├── sample2.sara    # Scope and binding demo
│   ├── sample3.sara    # Functions and loops
│   └── sample4.sara    # Boolean logic
│
├── output/             # Generated Python code goes here
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Running a Sarana File

```bash
python src/sarana.py samples/sample1.sara
```

## Launching the Web UI

```bash
streamlit run app/ui.py
```

---

## Group Members

- *(Add names and IDs here)*

---

## How the Compiler Works

1. **Lexer** — Reads raw `.sara` source code character by character and produces a list of tokens (like splitting a sentence into individual words)
2. **Parser** — Takes the token list and checks grammar, building an Abstract Syntax Tree (AST) — a tree structure representing the program's logic
3. **Semantic Analyzer** — Walks the AST and checks for logical errors (undefined variables, type mismatches, etc.) before the program runs
4. **Interpreter** — Walks the AST and executes it directly, producing output
5. **Code Generator** — Walks the AST and emits equivalent Python source code, which can be run independently

---

*Built with Python 3 and PLY (Python Lex-Yacc)*
