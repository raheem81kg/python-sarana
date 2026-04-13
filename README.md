# Sarana Programming Language

**Sarana** is a high-level, general-purpose, imperative programming language with a Caribbean/nature-inspired keyword set. 

hosted link: https://python-sarana.streamlit.app
## Group Members

Serena Morris - 2208659 
Raheem Gordon - 2208501 
Chadrick Atkinson - 2204885
Akeem Creary - 2110275

--- 

| Property      | Value                                 |
|---------------|---------------------------------------|
| Paradigm      | Imperative / Procedural               |
| Level         | High-level                            |
| Purpose       | General-purpose                       |
| File ext.     | `.sa`                                 |
| Target code   | Compiles to Python                    |
| Built with    | Python 3, PLY (Python Lex-Yacc)       |
| Course        | CIT4004 — Analysis of Programming Languages |
| Institution   | University of Technology, Jamaica     |
| Semester      | Semester 2, 2025/2026                 |

---

## Keyword Reference

| Sarana Keyword | Meaning          | Other languages    |
|----------------|------------------|--------------------|
| `bloom`        | Declare variable | `let`, `var`       |
| `echo`         | Print output     | `print()`          |
| `when`         | If condition     | `if`               |
| `otherwise`    | Else branch      | `else`             |
| `cycle`        | While loop       | `while`            |
| `craft`        | Define function  | `def`, `func`      |
| `return`       | Return value     | `return`           |
| `try`          | Try block        | `try`              |
| `ketch`        | Catch exception  | `catch`, `except`  |
| `--`           | Comment          | `#`, `//`          |

---

## Required Assignment Sample

The following program satisfies the minimum required sample :

```sarana
-- Required assignment sample program

bloom A = 20;
bloom B = 40;
bloom C = A + B * B;   -- PEMDAS: 20 + (40*40) = 1620

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
│   ├── lexer.py        # Phase 1 — Lexical analysis (PLY)
│   ├── parser.py       # Phase 2 — Syntax analysis / AST (PLY YACC)
│   ├── ast_nodes.py    # AST node class definitions
│   ├── semantic.py     # Phase 3 — Semantic analysis
│   ├── interpreter.py  # Phase 4 — Tree-walking interpreter
│   ├── codegen.py      # Phase 5 — Python code generator
│   ├── errors.py       # Custom error classes
│   └── sarana.py       # Main entry point / unified API
│
├── utils/
│   └── colors.py       # ANSI terminal color codes (CLI)
│
├── app/
│   ├── Code_Editor.py  # Streamlit entry — editor + results
│   ├── pages/
│   │   └── Language_Docs.py
│   └── components/     # sidebar, header, styles, results, AI assistant
│
├── assets/
│   ├── NoBackgroundLogo.PNG
│   └── BlackBackgroundLogo.png
│
├── samples/
│   ├── sample1.sa      # Required assignment sample (PEMDAS + try/ketch)
│   ├── sample2.sa      # Scope and binding demonstration
│   ├── sample3.sa      # Functions, loops, recursion
│   └── sample4.sa      # Boolean logic, else-if chains, short-circuit
│
├── tests/
│   ├── conftest.py              # Shared pytest setup
│   ├── test_phase1_lexer.py     # Phase 1 — Lexer tests
│   ├── test_phase2_parser.py    # Phase 2 — Parser / AST tests
│   ├── test_phase3_semantic.py  # Phase 3 — Semantic analyzer tests
│   ├── test_phase4_interpreter.py  # Phase 4 — Interpreter tests
│   ├── test_phase5_codegen.py   # Phase 5 — Code generator tests
│   └── test_all_samples.py      # End-to-end sample program tests
│
├── requirements.txt
├── pyproject.toml      # Ruff / Pyright config
├── .flake8             # Flake8 (optional; VS Code can use this)
├── pyrightconfig.json  # Pylance/Pyright import resolution
├── launch_ui.sh        # Quick launch script
└── README.md
```

---

## Installation

```bash
# 1. Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# On macOS without a venv:
pip install --break-system-packages -r requirements.txt
```

---

## Usage

### Method 1: Web UI (Recommended)

```bash
streamlit run app/Code_Editor.py

# Or use the launch script
./launch_ui.sh
```

Open your browser to `http://localhost:8501`

**UI Features:**
- Code editor with line numbers
- 6 tabs: Output, Tokens, AST, Semantic Analysis, Generated Code, AI Assistant (Gemini)
- Sample program library (dropdown in sidebar)
- Language reference in sidebar (`Language Docs` page)
- Download generated Python code
- Color-coded error / success / warning messages
- Theme-aware styling (follows Streamlit light / dark mode)
- AI Assistant tab (optional): Google Gemini via `google-generativeai` and `GEMINI_API_KEY`

### Method 2: Command Line

```bash
# Compile and run a Sarana program
python3 src/sarana.py samples/sample1.sa

# View the AST only
python3 src/sarana.py program.sa --ast-only

# Verbose output (all phases)
python3 src/sarana.py program.sa --verbose

# Write generated code to a file
python3 src/sarana.py program.sa --output out.py
```

### Method 3: Python API

```python
import sys
sys.path.insert(0, "src")
from sarana import compile_and_run

code = """
bloom x = 10;
echo x;
"""

result = compile_and_run(code)
print(result.output)           # ['10']
print(result.generated_code)   # Python source
print(result.success)          # True
```

---

## Running Tests

```bash
# Run all 117 tests
cd python-sarana
PYTHONPATH=src python3 -m pytest tests/ -v

# Run a specific phase
PYTHONPATH=src python3 -m pytest tests/test_phase1_lexer.py -v
PYTHONPATH=src python3 -m pytest tests/test_phase2_parser.py -v
PYTHONPATH=src python3 -m pytest tests/test_phase3_semantic.py -v
PYTHONPATH=src python3 -m pytest tests/test_phase4_interpreter.py -v
PYTHONPATH=src python3 -m pytest tests/test_phase5_codegen.py -v

# End-to-end sample tests only
PYTHONPATH=src python3 -m pytest tests/test_all_samples.py -v
```

---

## How the Compiler Works

The Sarana compiler implements all five major compiler phases:

```
Source (.sa file)
       |
       v
[1. Lexer]        src/lexer.py      — tokenizes raw text using PLY regex rules
       |
       v
[2. Parser]       src/parser.py     — builds an Abstract Syntax Tree via PLY YACC
       |
       v
[3. Semantic]     src/semantic.py   — checks for undefined vars, div-by-zero, scope
       |
       v
[4. Interpreter]  src/interpreter.py — tree-walking execution, produces output
       |
       v
[5. Code Gen]     src/codegen.py    — translates AST to executable Python source
```

### AI Assistant (Gemini)

The web UI includes an **AI Assistant** tab powered by **Google Gemini** (`google-generativeai`):

1. Sarana source is still compiled and run by the interpreter (deterministic pipeline).
2. Optionally, you can ask Gemini for explanations, fixes, or help; it uses the same source and compiler context in the prompt.

Install the SDK (included in `requirements.txt` when you `pip install -r requirements.txt`):

```bash
pip install google-generativeai
```

Set your API key (or paste it in the sidebar when prompted):

```bash
export GEMINI_API_KEY="your-key"
streamlit run app/Code_Editor.py
```

Default model is `gemini-2.5-flash`. Override with the `GEMINI_MODEL` environment variable or the model dropdown in the sidebar.

---

## Language Features

### Core
- Variables with `bloom`
- Output with `echo` (multiple expressions on one line)
- PEMDAS arithmetic (`+`, `-`, `*`, `/`, `%`)
- Comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`)

### Control Flow
- `when` / `otherwise` conditionals
- `otherwise when` else-if chains
- `cycle` while loop

### Functions
- `craft` function definitions with parameters
- `return` statement
- Recursive functions
- Local scope

### Reliability
- `try` / `ketch` exception handling
- Boolean logic (`true`, `false`, `and`, `or`, `not`)
- Short-circuit evaluation for `and` and `or`
- Static semantic analysis before execution

---

## Nine Characteristics of Good Programming Languages

Sarana demonstrates all nine characteristics studied in CIT4004:

1. **Readability** — Natural keywords (`bloom`, `echo`, `ketch`) make programs self-documenting
2. **Writability** — Concise, consistent syntax with minimal boilerplate
3. **Reliability** — Static semantic analysis + `try`/`ketch` runtime safety
4. **Simplicity** — 14 keywords, one consistent grammar style throughout
5. **Orthogonality** — Any expression can appear wherever an expression is expected
6. **Data types** — Integer, Float, String, Boolean, Array with proper literals
7. **Syntax design** — Braces `{ }` and mandatory `;` eliminate ambiguity
8. **Support for abstraction** — `craft` functions with local scope
9. **Exception handling** — `try`/`ketch` for graceful error recovery

---

## Color Coding

### Terminal (CLI)
- Green — Success messages
- Red — Errors
- Yellow — Warnings

### Web UI
- Green banner — Compilation success
- Red banner — Errors
- Yellow banner — Warnings / semantic notes
- Blue banner — Informational

---

## Generated Code Example

**Sarana:**
```sarana
bloom x = 5;
when (x > 3) {
    echo "big";
} otherwise {
    echo "small";
}
```

**Generated Python:**
```python
x = 5
if x > 3:
    print("big")
else:
    print("small")
```