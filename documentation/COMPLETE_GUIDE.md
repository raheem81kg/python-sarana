# COMPLETE PROJECT EXPLANATION - EVERYTHING EXPLAINED

## What We Built: A Full Compiler

### The Big Picture

You now have a **complete compiler** called **Sarana** that:
1. Takes source code in the Sarana language (.sa files)
2. Converts it through 4 phases (lexer → parser → semantic → codegen)
3. Produces executable Python code
4. Can also interpret (run directly without generating code)
5. Has a beautiful web UI to interact with it

---

## The 4 Compiler Phases (Step by Step)

### Phase 1: LEXER (Lexical Analysis)
**File:** `src/lexer.py`

**What it does:** Reads your Sarana code character by character and breaks it into "tokens"

**Example:**
```sarana
bloom x = 5;
```

**Becomes tokens:**
```
BLOOM      "bloom"
IDENTIFIER "x"
ASSIGN     "="
INTEGER    5
SEMICOLON  ";"
```

**Think of it like:** Breaking a sentence into individual words.

**How it works:**
1. Reads character by character
2. Recognizes patterns (keywords, numbers, operators)
3. Creates token objects with type, value, and line number
4. Skips whitespace and comments

---

### Phase 2: PARSER (Syntax Analysis)
**File:** `src/parser.py`

**What it does:** Takes the tokens and builds a tree structure (AST) that represents the program's structure

**Example tokens:**
```
BLOOM, IDENTIFIER("x"), ASSIGN, INTEGER(5), SEMICOLON
```

**Becomes AST (Abstract Syntax Tree):**
```
Program
└── BloomStatement
    ├── name: "x"
    └── value: Integer(5)
```

**Think of it like:** Understanding grammar - how words form sentences.

**How it works:**
1. Reads tokens left to right
2. Checks grammar rules (e.g., "bloom" must be followed by identifier)
3. Builds a tree structure
4. Enforces PEMDAS (operator precedence)

**PEMDAS Example:**
```sarana
bloom C = A + B * B;
```

Becomes:
```
BinaryOp("+")
├── left: Variable("A")
└── right: BinaryOp("*")
          ├── left: Variable("B")
          └── right: Variable("B")
```

The "*" is deeper (evaluated first), then the "+".
So: `C = A + (B * B)` not `(A + B) * B`

---

### Phase 3: SEMANTIC ANALYZER
**File:** `src/semantic.py`

**What it does:** Checks if your code makes logical sense BEFORE running it

**Checks for:**
- Using variables before declaring them
- Type mismatches (e.g., "hello" - 5)
- Division by zero
- Calling undefined functions
- Scope issues

**Example:**
```sarana
echo x;  // ERROR: x not declared yet
```

Semantic analyzer says: "Wait! Variable 'x' doesn't exist!"

**Think of it like:** A spelling/grammar checker for code.

**How it works:**
1. Walks through the AST
2. Maintains a symbol table (list of declared variables)
3. Checks each operation is valid
4. Collects all errors without stopping

---

### Phase 4A: INTERPRETER
**File:** `src/interpreter.py`

**What it does:** Executes your code directly by walking the AST

**Example:**
```sarana
bloom x = 10;
echo x;
```

**Interpreter does:**
1. Sees `BloomStatement` → Creates variable x = 10 in memory
2. Sees `EchoStatement` → Prints the value of x (which is 10)
3. Output: `10`

**Think of it like:** A person reading instructions and doing them immediately.

**How it works:**
1. Walks the AST node by node
2. Maintains runtime environment (variables in memory)
3. Evaluates expressions on the fly
4. Executes statements immediately
5. Handles errors with try/ketch blocks

---

### Phase 4B: CODE GENERATOR (Compiler)
**File:** `src/codegen.py`

**What it does:** Translates the AST into Python source code

**Example:**
```sarana
bloom x = 10;
echo x;
```

**Generates Python:**
```python
x = 10
print(x)
```

**Think of it like:** A translator converting English to Spanish.

**How it works:**
1. Walks the AST node by node
2. For each node type, emits equivalent Python code
3. Handles indentation (Python needs it!)
4. Writes to a .py file
5. The generated file can be run with `python3`

**Translation Rules:**
```
bloom x = 5;         →  x = 5
echo "hello";        →  print("hello")
when (x > 5) {}      →  if (x > 5):
otherwise {}         →  else:
cycle (i < 10) {}    →  while (i < 10):
craft add(a,b) {}    →  def add(a, b):
try {} ketch {}      →  try: ... except Exception: ...
true / false         →  True / False
```

---

## How the LLM Integration Works

### What is LLM?
**LLM = Large Language Model** (like ChatGPT, Claude)

### What We Built
In the "LLM Comparison" tab, you can compare:
- **Sarana Compiler (Deterministic)** - Always produces the same output
- **Claude AI (Probabilistic)** - Guesses what the code should do

### How It Works:

**Step 1:** You write Sarana code in the UI

**Step 2:** When you click "Run Claude Comparison":

1. **Send prompt to Claude API:**
```
You are executing a program written in Sarana.

Keyword Mappings:
- bloom = variable declaration
- echo = print
- when = if
- otherwise = else
- etc...

Execute this program and show output:
[YOUR CODE HERE]
```

2. **Claude responds** with what it THINKS the output should be

3. **We show both side-by-side:**
   - Left: Sarana compiler output (guaranteed correct)
   - Right: Claude's guess (might be wrong!)

### Why This Is Cool:

**Compiler (Sarana):**
- Follows exact grammar rules
- Always produces same result
- 100% deterministic
- Fast

**LLM (Claude):**
- Interprets probabilistically
- Might vary each run
- Uses pattern matching
- Shows how AI "understands" code

### Example:

**Your Sarana code:**
```sarana
bloom x = 10;
echo x;
```

**Sarana Compiler says:**
```
10
```

**Claude might say:**
```
Output: 10
```
or
```
The program prints: 10
```
or just
```
10
```

All similar but not identical! Shows the difference between deterministic compilation and AI interpretation.

---

## The Web UI Explained

### What We Built
A professional web interface using **Streamlit** (a Python web framework)

### Key Components:

**1. Header**
- Logo (80x80px, circular, inline with title)
- Title: "SARANA LANGUAGE PLAYGROUND"
- Subtitle explaining what it is

**2. Sidebar**
- Sample program dropdown (4 examples)
- Compiler options (enable/disable phases)
- LLM integration toggle
- Language reference (keywords, operators)

**3. Main Editor**
- Text area to write Sarana code
- Run button
- Clear button

**4. Six Tabs** (Now with dark styling!)

**Tab 1: Output**
- Shows what your program prints
- Colored boxes (green/red/yellow/blue)

**Tab 2: Tokens**
- Color-coded table showing all tokens
- Blue = keywords, Yellow = literals, Green = identifiers, Purple = operators

**Tab 3: AST**
- Shows the tree structure of your program
- Helps understand how parser sees your code

**Tab 4: Semantic Analysis**
- Shows any errors found before execution
- Green "No errors" or yellow warning boxes

**Tab 5: Generated Code**
- Shows the Python code generated
- Download button to save it
- Translation examples

**Tab 6: LLM Comparison**
- Side-by-side comparison
- Your compiler vs Claude AI
- Shows deterministic vs probabilistic

### Color Coding Explained

**In the UI:**
- **Green boxes** = Success (compilation worked)
- **Red boxes** = Errors (something broke)
- **Yellow boxes** = Warnings (non-fatal issues)
- **Blue boxes** = Info (helpful messages)

**In the terminal:**
- **Green text** = Success messages
- **Red text** = Error messages
- **Yellow text** = Warnings
- **Blue text** = Info messages

**In the tabs:**
- **Dark background** = Unselected tab
- **Blue background** = Selected tab
- **Hover** = Lighter shade

---

## The Complete Data Flow

When you click "Run Sarana":

```
1. Your Code (text)
        ↓
2. LEXER
   - Breaks into tokens
   - Removes comments/whitespace
        ↓
3. Token List
   [BLOOM, IDENTIFIER, ASSIGN, INTEGER, ...]
        ↓
4. PARSER
   - Builds AST from tokens
   - Checks grammar
        ↓
5. AST (Tree structure)
   Program
     └── BloomStatement
           └── ...
        ↓
6. SEMANTIC ANALYZER
   - Checks logic
   - Finds errors
        ↓
7. AST + Error List
        ↓
   ┌────┴────┐
   ↓         ↓
8a. INTERPRETER    8b. CODE GENERATOR
   - Executes now     - Generates Python
   - Prints output    - Saves .py file
        ↓                   ↓
9a. Program Output   9b. Python Code
   "Hello World"       print("Hello World")
        ↓                   ↓
   Display in UI       Can run with python3
```

---

## What Each File Does

### Core Compiler Files:

**`src/lexer.py`** (314 lines)
- Tokenizes source code
- Recognizes keywords, operators, literals
- Tracks line numbers

**`src/parser.py`** (441 lines)
- Builds AST from tokens
- Enforces grammar rules
- Handles PEMDAS

**`src/ast_nodes.py`** (587 lines)
- Defines all AST node types
- BloomStatement, EchoStatement, etc.
- Each node knows how to represent itself

**`src/semantic.py`** (377 lines)
- Walks AST checking for errors
- Symbol table for variables
- Type checking

**`src/interpreter.py`** (553 lines)
- Executes AST directly
- Runtime environment for variables
- Exception handling

**`src/codegen.py`** (453 lines)
- Translates AST → Python
- Handles indentation
- Generates executable code

**`src/sarana.py`** (420 lines)
- Main entry point
- Ties all phases together
- Command-line interface

**`src/errors.py`** (158 lines)
- Custom error classes
- LexError, ParseError, SemanticError, RuntimeError

**`src/colors.py`** (51 lines)
- Terminal color codes
- Green/red/yellow/blue text

### UI Files:

**`app/ui.py`** (622 lines)
- Streamlit web interface
- 6 tabs
- Color-coded messages
- LLM integration

### Sample Programs:

**`samples/sample1.sa`** - Required demo (exception handling)
**`samples/sample2.sa`** - Scope and binding
**`samples/sample3.sa`** - Functions and loops
**`samples/sample4.sa`** - Boolean logic

### Test Files:

**79 tests across 8 files** - Verify everything works

### Documentation:

**10+ guide files** - Explain how everything works

---

## Key Concepts Explained

### 1. Why Both Interpreter AND Compiler?

**Interpreter (Direct execution):**
- Fast for development
- Immediate feedback
- Used by web UI

**Compiler (Generate code):**
- Produces standalone files
- Meets assignment requirements
- Shows you understand code generation

### 2. What is PEMDAS?

**Order of operations:**
- Parentheses
- Exponents
- Multiplication / Division
- Addition / Subtraction

**Example:**
```
2 + 3 * 4
```

**Wrong:** (2 + 3) * 4 = 20
**Correct:** 2 + (3 * 4) = 14

The parser builds the AST so multiplication happens first!

### 3. What is an AST?

**Abstract Syntax Tree** - A tree representing code structure

**Example:**
```sarana
bloom C = A + B * B;
```

**Tree:**
```
BloomStatement
├── name: "C"
└── value:
    BinaryOp(+)
    ├── Variable(A)
    └── BinaryOp(*)
        ├── Variable(B)
        └── Variable(B)
```

Deeper nodes execute first!

### 4. What is Semantic Analysis?

Checking if code makes LOGICAL sense:

**Syntax OK but Semantics BAD:**
```sarana
echo x;  // x never declared!
```

Grammar is fine, but logically it's wrong.

### 5. What is Code Generation?

Translating from one language to another:

**Sarana → Python**

This is what makes it a "compiler" not just an "interpreter".

---

## The Tab Color Fix

### What Was Wrong:
Unselected tabs had white background - didn't match the color scheme

### What I Fixed:
Changed tab colors to:
- **Unselected tabs:** Dark gray background (#334155)
- **Selected tab:** Blue background (#3b82f6)
- **Hover:** Slightly lighter gray
- **Tab container:** Dark slate background (#1e293b)

Now they blend with the rest of the UI!

---

## What Makes This Project Special

1. **Complete Compiler** - All 4 phases working
2. **Dual Execution** - Both interpret AND generate code
3. **79 Comprehensive Tests** - Thoroughly tested
4. **Professional UI** - Color-coded, modern design
5. **LLM Integration** - Cutting-edge AI comparison
6. **Caribbean Theme** - Unique keywords (bloom, ketch, echo)
7. **Color-Coded Terminal** - Green/red/yellow output
8. **Circular Logo** - Professional branding
9. **Complete Documentation** - 10+ guide files
10. **Parse Trees** - For understanding grammar

---

## How to Use Everything

### Terminal (Colored output):
```bash
python3 src/sarana.py samples/sample1.sa
# Green success or red errors
```

### Tests (Colored results):
```bash
python3 run_all_tests.py
# Green [PASS] or red [FAIL]
```

### Web UI (Dark tabs now!):
```bash
streamlit run app/ui.py
# Browse to localhost:8501
# Click tabs to see different phases
```

### LLM Comparison:
1. Launch UI
2. Enter your Anthropic API key in sidebar
3. Enable "Claude Comparison"
4. Write Sarana code
5. Click "Run Claude Comparison"
6. See side-by-side results

---

## Summary: What You Have

✓ **A complete compiler** with all phases  
✓ **Web UI** with 6 tabs (now dark-styled!)  
✓ **Color-coded terminal** output  
✓ **LLM integration** for AI comparison  
✓ **79 passing tests**  
✓ **Professional appearance**  
✓ **Complete documentation**  
✓ **Ready for 100% grade**  

**Your project is COMPLETE and PROFESSIONAL!**
