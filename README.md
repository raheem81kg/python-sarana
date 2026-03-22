# Sarana Programming Language

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
│   ├── lexer.py        # Tokenizer
│   ├── parser.py       # Parser
│   ├── ast_nodes.py    # AST definitions
│   ├── semantic.py     # Semantic analyzer
│   ├── interpreter.py  # Interpreter
│   ├── codegen.py      # Code generator
│   ├── errors.py       # Error classes
│   └── sarana.py       # Main entry point
│
├── app/
│   └── ui.py           # Streamlit web UI
│
├── assets/
│   ├── NoBackgroundLogo.PNG      # Logo (transparent)
│   └── BlackBackgroundLogo.png   # Logo (black bg)
│
├── samples/
│   ├── sample1.sa      # Required assignment sample
│   ├── sample2.sa      # Scope and binding demo
│   ├── sample3.sa      # Functions and loops
│   └── sample4.sa      # Boolean logic
│
├── tests/              # Test suite
├── output/             # Generated Python code
├── requirements.txt
├── launch_ui.sh        # Quick launch script
└── README.md
```

---

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or on macOS if you get permission errors:
pip install --break-system-packages -r requirements.txt
```

---

## Usage

### Method 1: Web UI (Recommended)

```bash
# Launch the web interface
streamlit run app/ui.py

# Or use the launch script
./launch_ui.sh
```

Then open your browser to `http://localhost:8501`

**Features:**
- Real-time compilation
- 6 interactive tabs (Output, Tokens, AST, Semantic, Generated Code, LLM)
- Sample program dropdown
- Syntax highlighting
- Download generated code
- Color-coded error messages

### Method 2: Command Line

```bash
# Compile and run a Sarana program
python3 src/sarana.py samples/sample1.sa

# Specify output file
python3 src/sarana.py program.sa --output generated.py

# View AST only
python3 src/sarana.py program.sa --ast-only

# Verbose mode
python3 src/sarana.py program.sa --verbose
```

### Method 3: Python API

```python
from src.sarana import compile_and_run

code = """
bloom x = 10;
echo x;
"""

result = compile_and_run(code)
print(result.output)          # ['10']
print(result.generated_code)  # Python code
```

---

## Running Tests

```bash
# Run all tests (79 total)
python3 run_all_tests.py

# Run individual test suites
python3 test_1_errors.py
python3 test_2_lexer.py
python3 test_3_parser.py
python3 test_4_semantic.py
python3 test_5_interpreter.py
python3 test_6_full_pipeline.py
python3 test_7_codegen.py
python3 test_8_main_entry.py
```

---

## How the Compiler Works

1. **Lexer** - Reads raw `.sa` source code and produces tokens
2. **Parser** - Builds Abstract Syntax Tree (AST) from tokens
3. **Semantic Analyzer** - Checks for logical errors before execution
4. **Interpreter** - Executes the AST directly, producing output
5. **Code Generator** - Translates AST to Python source code

---

## Features

### Language Features
- Variables with `bloom`
- Output with `echo`
- PEMDAS arithmetic (`+`, `-`, `*`, `/`, `%`)
- Conditionals with `when`/`otherwise`
- Loops with `cycle`
- Functions with `craft` and `return`
- Exception handling with `try`/`ketch`
- Boolean logic (`true`, `false`, `and`, `or`, `not`)
- String and array support
- Comments with `--`

### Compiler Features
- Complete lexical analysis
- Syntax analysis with parse tree generation
- Semantic analysis with error detection
- Target code generation (Python)
- Direct interpretation
- Comprehensive error messages with line numbers
- 79 comprehensive tests (all passing)

### UI Features
- Professional color-coded interface
- Real-time compilation
- 6 interactive tabs
- Sample program library
- Download generated code
- LLM comparison (with Anthropic API)
- Responsive design

---

## Color Coding

The web UI uses professional color coding:

- **Success messages** - Green background
- **Error messages** - Red background
- **Warning messages** - Yellow background
- **Info messages** - Blue background
- **Token types** - Different colors for keywords, literals, identifiers, operators

---

## Generated Code

Sarana compiles to Python. Example:

**Sarana:**
```sarana
bloom x = 5;
echo x;
```

**Generated Python:**
```python
x = 5
print(x)
```

The generated code is executable:
```bash
python3 samples/sample1.py
```

---

## Documentation

- `QUICK_START.md` - 5-minute setup guide
- `FINAL_SUMMARY.md` - Complete project overview
- `COMPLETE_EXPLANATION.md` - Deep dive into how everything works
- `TESTING.md` - Test documentation
- `TEST_RESULTS.md` - Test results summary
- `PARSE_TREE_DIAGRAMS.txt` - Parse trees for report

---

## Group Members

- [Add your names and student IDs here]

---

## License & Credits

Built for CIT4004 Analysis of Programming Languages  
University of Technology, Jamaica  
Based on the python-braid open-source project

---

## Troubleshooting

**UI won't start?**
```bash
pip install streamlit
streamlit run app/ui.py
```

**Tests failing?**
```bash
# Make sure you're in project root
cd python-sarana
python3 run_all_tests.py
```

**Import errors?**
```bash
pip install -r requirements.txt
python3 --version  # Need Python 3.8+
```

---

**Status: Production Ready**  
All 79 tests passing | Complete compiler pipeline | Professional UI | Comprehensive documentation
