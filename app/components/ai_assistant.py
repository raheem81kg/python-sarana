"""
app/components/ai_assistant.py
================================
Enhanced Gemini AI integration for the Sarana Programming Language.

Provides comprehensive language context to Gemini and handles various AI tasks:
- Code execution comparison (deterministic vs probabilistic)
- Code explanation and analysis
- Error diagnosis and suggestions
- Code optimization suggestions
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import google.generativeai as genai
import streamlit as st


# =============================================================================
# SARANA LANGUAGE CONTEXT - Comprehensive documentation for the AI
# =============================================================================

SARANA_LANGUAGE_CONTEXT = """
You are an expert in the Sarana Programming Language, a custom-built educational 
programming language with Caribbean/nature-inspired keywords.

## LANGUAGE OVERVIEW

| Property      | Value                                 |
|---------------|---------------------------------------|
| Paradigm      | Imperative / Procedural               |
| Level         | High-level                            |
| Purpose       | General-purpose                       |
| File ext.     | `.sa`                                 |
| Target code   | Compiles to Python                    |

## KEYWORD REFERENCE (CRITICAL - These are NOT standard programming terms)

| Sarana       | Standard Equivalent    | Meaning                          |
|--------------|------------------------|----------------------------------|
| `bloom`      | `let`, `var`          | Declare variable                 |
| `echo`       | `print()`             | Print output                     |
| `when`       | `if`                  | If condition                     |
| `otherwise`  | `else`                | Else branch                      |
| `otherwise when` | `else if`       | Else-if chain                    |
| `cycle`      | `while`               | While loop                       |
| `craft`      | `def`, `func`         | Define function                  |
| `return`     | `return`              | Return value                     |
| `try`        | `try`                 | Try block                        |
| `ketch`      | `catch`, `except`     | Catch exception                  |
| `true`       | `true`, `True`        | Boolean true                     |
| `false`      | `false`, `False`      | Boolean false                    |
| `and`        | `&&`, `and`           | Logical AND                      |
| `or`         | `\|\|`, `or`            | Logical OR                       |
| `not`        | `!`, `not`            | Logical NOT                      |
| `--`         | `//`, `#`             | Single-line comment              |

## GRAMMAR RULES

### Variables
- Declared with: `bloom <name> = <value>;`
- Types: Integer, Float, String, Boolean, Array
- MUST end with semicolon
- Examples:
  - `bloom x = 10;`
  - `bloom name = "Serena";`
  - `bloom flag = true;`
  - `bloom arr = [1, 2, 3];`

### Output
- `echo <expression>;` or `echo <expr1> <expr2> ...;`
- Multiple expressions are space-separated
- Examples:
  - `echo "Hello";`
  - `echo "Sum is:" x + y;`

### Control Flow
- IF: `when (<condition>) { <statements> }`
- IF-ELSE: `when (<condition>) { } otherwise { }`
- ELSE-IF: `when (<cond1>) { } otherwise when (<cond2>) { } otherwise { }`
- WHILE: `cycle (<condition>) { <statements> }`

### Functions
- Declaration: `craft <name>(<params>) { <body> }`
- Parameters are comma-separated identifiers
- Return: `return <expression>;`
- Examples:
  - `craft add(a, b) { return a + b; }`
  - `craft greet(name) { echo "Hello" name; }`

### Exception Handling
- `try { <statements> } ketch { <handler> }`
- Catches runtime errors like division by zero

### Operators
- Arithmetic (PEMDAS): `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Assignment: `=`
- Logical: `and`, `or`, `not`
- Short-circuit evaluation for `and` and `or`

### Syntax Rules
- Statements MUST end with semicolon `;`
- Blocks use curly braces `{ }`
- Parentheses `()` for conditions and expressions
- Arrays use square brackets `[ ]` with comma-separated values
- Comments start with `--`

## COMPLETE EXAMPLE PROGRAMS

### Example 1: Variables and Arithmetic
```
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;   -- PEMDAS: 20 + (40*40) = 1620
echo "Result:" C;
```

### Example 2: Exception Handling
```
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;

try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero!";
}

echo "The result is " C;
```
Output:
```
Error: Division by zero!
The result is 1620
```

### Example 3: Functions and Recursion
```
craft factorial(n) {
    when (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

echo factorial(5);   -- prints: 120
```

### Example 4: Loops
```
bloom i = 1;
cycle (i <= 5) {
    echo i;
    bloom i = i + 1;   -- Note: shadowing creates new variable
}
```

### Example 5: Short-circuit Evaluation
```
bloom x = 10;
when (x > 5 or x / 0 > 1) {   -- x/0 NEVER evaluated!
    echo "Short-circuit works!";
}
```

## COMPILER PHASES (actual implementation)

### Phase 1: Lexical Analysis (src/lexer.py)
- Uses PLY (Python Lex-Yacc) to tokenize source code
- 14 reserved keywords: bloom, echo, when, otherwise, cycle, craft, return, try, ketch, true, false, and, or, not
- Tokens: IDENTIFIER, INTEGER, FLOAT, STRING, PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, DOUBLE_EQUALS, NOT_EQUALS, comparison operators, ASSIGN, delimiters (parentheses, braces, brackets, semicolon, comma)
- Comments: `--` to end of line (skipped by lexer)
- Whitespace: spaces, tabs, newlines are ignored
- String literals: double or single quotes
- Identifiers: `[a-zA-Z_][a-zA-Z0-9_]*`
- Numbers: integers `[0-9]+`, floats `[0-9]+\.[0-9]+`

### Phase 2: Syntax Analysis / AST (src/ast_nodes.py, src/parser.py)
AST Node Types:
- `Program` — root node containing list of statements
- `BloomStatement` — variable declaration (name, value expression, line)
- `EchoStatement` — output (list of expressions, line)
- `WhenStatement` — if/else (condition, then_body, otherwise_body, line)
- `CycleStatement` — while loop (condition, body, line)
- `CraftStatement` — function def (name, params, body, line)
- `ReturnStatement` — return (value expression, line)
- `TryKetchStatement` — try/catch (try_body, ketch_body, line)
- `BinaryOp` — arithmetic/comparison/logical (operator, left, right, line)
- `UnaryOp` — not, negation (operator, operand, line)
- `Variable` — variable reference (name, line)
- `FunctionCall` — function invocation (name, arguments, line)
- `Integer`, `Float`, `String`, `Boolean`, `Array` — literal values

Operator Precedence (from lowest to highest):
1. `or`
2. `and`
3. `==`, `!=`
4. `<`, `>`, `<=`, `>=`
5. `+`, `-`
6. `*`, `/`, `%`
7. unary `not`, unary `-`

### Phase 3: Semantic Analysis (src/semantic.py)
Checks performed before execution:
- Undefined variables (used before `bloom`)
- Undefined functions (called before `craft`)
- Division by zero (when divisor is literal 0)
- Type compatibility (catches some type errors)
- Symbol table tracks variables and functions across nested scopes

### Phase 4: Interpretation (src/interpreter.py)
Tree-walking interpreter with Environment for variable storage.
Key execution semantics detailed above.

### Phase 5: Code Generation (src/codegen.py)
Translation to Python:
- `bloom x = 5;` → `x = 5`
- `echo x y;` → `print(x, y)`
- `when (cond) { }` → `if cond:`
- `otherwise { }` → `else:`
- `cycle (cond) { }` → `while cond:`
- `craft f() { }` → `def f():`
- `try/ketch` → `try/except Exception:`
- `true/false` → `True/False`
- `and/or/not` → `and/or/not`
- Arrays use Python list syntax

## ERROR TYPES (src/errors.py)

1. **LexError** — Unrecognized characters, malformed tokens
2. **ParseError** — Syntax violations (missing semicolons, unclosed braces, etc.)
3. **SemanticError** — Undefined variables/functions, type mismatches
4. **SaranaRuntimeError** — Division by zero, type errors during execution
5. **UnexpectedEndError** — Unclosed blocks at end of file

## STRING CONCATENATION BEHAVIOR
The `+` operator concatenates strings:
- `"Hello " + "World"` → `"Hello World"`
- `"Value: " + 42` → `"Value: 42"` (number converted to string)
- String repetition: `"hi" * 3` → `"hihihi"`

## TYPE SYSTEM
- Dynamic typing (no type declarations)
- Runtime type checking for operations
- Types: Integer, Float, String, Boolean, Array, null
- Automatic type conversion only for string concatenation

## IMPORTANT EXECUTION NOTES (from actual interpreter implementation)

### Environment / Scope System (src/interpreter.py lines 42-84)
- Environment has: `vars` (dict) for current scope, `parent` (link to outer scope)
- `env.set(name, value)` — ALWAYS writes to current scope's vars dict (line 61)
- `env.get(name)` — Searches current scope first, then walks up parent chain (lines 68-75)
- `env.exists(name)` — Checks if variable exists in any scope (lines 77-83)

### Bloom Statement Execution (src/interpreter.py lines 162-168)
```python
def visit_BloomStatement(self, node):
    value = self.visit(node.value)      # STEP 1: Evaluate RHS FIRST
    self.env.set(node.name, value)     # STEP 2: Create binding in CURRENT scope
```
CRITICAL: RHS is evaluated BEFORE the new binding is created. This means:
- In `bloom x = x + 1`, the right-side `x` is looked up from outer scope
- Then a NEW `x` is created in the inner (current) scope
- The outer `x` remains unchanged but is no longer visible in this scope

### Cycle (While Loop) Execution (src/interpreter.py lines 221-231)
```python
def visit_CycleStatement(self, node):
    while True:
        condition_value = self.visit(node.condition)
        if not self._is_truthy(condition_value):
            break
        for stmt in node.body:
            self.visit(stmt)             # Each iteration runs in SAME scope
```
IMPORTANT: The cycle body does NOT create a new scope. All iterations share
the same environment. This is different from function calls.

### Function Call Execution (src/interpreter.py lines 346-388)
- Creates NEW environment with `func.closure` as parent (line 370)
- Parameters are set in this new function scope (lines 371-372)
- Body executes in this new scope (lines 376-386)
- After function returns, original environment is restored (line 386)

### Common Pattern: Accumulator in Loops
This is the CORRECT and WORKING pattern:
```
craft multiply(a, b) {
    bloom result = 0;                   -- result in outer (function) scope
    bloom counter = 0;
    
    cycle (counter < b) {
        bloom result = result + a;      -- RHS reads outer result, LHS creates new binding
        bloom counter = counter + 1;    -- Same pattern
    }
    
    return result;                      -- Returns the accumulated value
}
```
WHY IT WORKS:
1. First iteration: `result + a` → 0 + a = a, new `result` = a
2. Second iteration: `result + a` → a + a = 2a, new `result` = 2a
3. Continues until counter reaches b, returning a * b

### Variable Resolution Rules
1. **Read (env.get)**: Search current scope → parent → grandparent → ... → global
2. **Write (env.set)**: ALWAYS write to current scope, shadowing any parent variable
3. **Bloom RHS**: Evaluated using current visible bindings (before new binding created)

### Truthiness (src/interpreter.py lines 431-441)
- Falsy: `false`, `0`, `""` (empty string), `[]` (empty array), `null`
- Truthy: Everything else (including negative numbers, non-empty strings/arrays)

### Division by Zero
- Raises `SaranaRuntimeError("Division by zero")` (line 469)
- Can be caught by `try`/`ketch` blocks

### Short-circuit Evaluation (src/interpreter.py lines 271-283)
- `and`: If left is falsy, return False immediately (right side NOT evaluated)
- `or`: If left is truthy, return True immediately (right side NOT evaluated)
- Used for: `when (x > 5 or x / 0 > 1)` — x/0 is never evaluated!
"""


@dataclass
class AIAnalysisResult:
    """Container for AI analysis results."""
    success: bool
    content: str
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    analysis_type: str = "general"


class SaranaAIAssistant:
    """
    Gemini-powered AI assistant for the Sarana programming language.
    Provides contextual understanding and analysis of Sarana code.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the AI assistant.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model_name: Gemini model to use
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = model_name
        self._model: Optional[Any] = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(model_name)

    def is_configured(self) -> bool:
        """Check if the assistant has a valid API key."""
        return bool(self.api_key) and self._model is not None

    def _generate_with_context(
        self, 
        user_prompt: str, 
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> AIAnalysisResult:
        """
        Generate a response with full Sarana context.
        
        Args:
            user_prompt: The specific task/prompt
            temperature: Creativity level (0.0-1.0, lower for code tasks)
            max_tokens: Maximum response length
            
        Returns:
            AIAnalysisResult with the generated content
        """
        if not self.is_configured():
            return AIAnalysisResult(
                success=False,
                content="",
                error_message="Gemini API key not configured. Set GEMINI_API_KEY environment variable or enter key in sidebar."
            )

        full_prompt = f"{SARANA_LANGUAGE_CONTEXT}\n\n{'='*60}\nUSER REQUEST\n{'='*60}\n\n{user_prompt}"
        
        try:
            response = self._model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            return AIAnalysisResult(
                success=True,
                content=response.text,
                tokens_used=response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None,
                analysis_type="generated"
            )
            
        except Exception as exc:
            return AIAnalysisResult(
                success=False,
                content="",
                error_message=f"Error calling Gemini API: {str(exc)}"
            )

    def execute_code(self, code: str, expected_output: Optional[List[str]] = None) -> AIAnalysisResult:
        """
        Ask Gemini to execute Sarana code and return the output.
        
        Args:
            code: The Sarana source code to execute
            expected_output: Optional expected output for comparison
            
        Returns:
            AIAnalysisResult with the execution output
        """
        prompt = f"""Execute the following Sarana program step by step and show ONLY the output.

Rules:
1. Follow PEMDAS for arithmetic
2. Variables declared with 'bloom' are created in current scope
3. 'echo' prints values space-separated
4. Handle exception blocks correctly
5. Show ONLY the final output, no explanations

Sarana Code:
```
{code}
```

Output:"""

        result = self._generate_with_context(prompt, temperature=0.1, max_tokens=1024)
        result.analysis_type = "execution"
        return result

    def explain_code(self, code: str) -> AIAnalysisResult:
        """
        Provide a detailed explanation of what the code does.
        
        Args:
            code: The Sarana source code to explain
            
        Returns:
            AIAnalysisResult with the explanation
        """
        prompt = f"""Explain the following Sarana program in detail.

For each section, provide:
1. What the code does at a high level
2. Line-by-line breakdown with variable state changes
3. Expected output with reasoning
4. Any notable language features used

Format your response with clear headings and bullet points.

Sarana Code:
```
{code}
```

Explanation:"""

        result = self._generate_with_context(prompt, temperature=0.3, max_tokens=2048)
        result.analysis_type = "explanation"
        return result

    def analyze_errors(
        self, 
        code: str, 
        error_messages: List[str],
        compilation_phase: str
    ) -> AIAnalysisResult:
        """
        Analyze errors and provide suggestions for fixes.
        
        Args:
            code: The Sarana source code with errors
            error_messages: List of error messages from the compiler
            compilation_phase: Which phase failed (lexical, syntax, semantic, runtime)
            
        Returns:
            AIAnalysisResult with error analysis and fix suggestions
        """
        errors_text = "\n".join(f"- {err}" for err in error_messages)
        
        prompt = f"""Analyze the following errors in the Sarana program and provide detailed fixes.

Failed Phase: {compilation_phase}

Error Messages:
{errors_text}

Problematic Code:
```
{code}
```

For each error:
1. Identify the root cause
2. Explain what's wrong using Sarana grammar rules
3. Provide the exact corrected code
4. Explain why the fix works

If this is a semantic error, check for:
- Undefined variables (used before 'bloom')
- Missing semicolons
- Incorrect block structure
- Type mismatches

Error Analysis and Fixes:"""

        result = self._generate_with_context(prompt, temperature=0.2, max_tokens=2048)
        result.analysis_type = "error_analysis"
        return result

    def suggest_optimizations(self, code: str) -> AIAnalysisResult:
        """
        Suggest optimizations and improvements for the code.
        
        Args:
            code: The Sarana source code to optimize
            
        Returns:
            AIAnalysisResult with optimization suggestions
        """
        prompt = f"""Analyze the following Sarana program and suggest optimizations.

For each suggestion:
1. Current approach and its limitation
2. Optimized approach using Sarana features
3. Before/after code comparison
4. Expected benefit

Consider:
- Loop efficiency
- Variable scope management
- Redundant operations
- Algorithm improvements
- Readability improvements

Sarana Code:
```
{code}
```

Optimization Suggestions:"""

        result = self._generate_with_context(prompt, temperature=0.3, max_tokens=2048)
        result.analysis_type = "optimization"
        return result

    def compare_with_compiler(
        self, 
        code: str, 
        compiler_output: List[str],
        compiler_generated_code: Optional[str] = None
    ) -> AIAnalysisResult:
        """
        Compare AI execution with compiler output and explain differences.
        
        Args:
            code: The Sarana source code
            compiler_output: Output from the Sarana compiler/interpreter
            compiler_generated_code: Optional Python code generated by compiler
            
        Returns:
            AIAnalysisResult with comparison analysis
        """
        compiler_out = "\n".join(compiler_output) if compiler_output else "(no output)"
        
        gen_code_section = ""
        if compiler_generated_code:
            gen_code_section = f"""

Generated Python Code:
```python
{compiler_generated_code}
```"""
        
        prompt = f"""Execute this Sarana program and produce the output with your reasoning.

Sarana Code:
```
{code}
```

YOUR TASK:
1. Simulate the program execution mentally following Sarana semantics
2. Execute each line, tracking variable values
3. Collect ALL output from `echo` statements in order
4. Provide your execution output AND your reasoning/thought process

IMPORTANT: Keep these sections COMPLETELY SEPARATE.

=== OUTPUT SECTION ===
List ONLY the echo output lines here, one per line, exactly as they would print.
NO markdown code blocks in this section. Just the raw output lines.

=== REASONING SECTION ===
Explain your execution process here:
- How you handled variable shadowing in loops
- Key variable values at each iteration
- Any tricky semantics you considered
- Confirmation you executed this yourself

This proves you did the work, not just copied."""

        result = self._generate_with_context(prompt, temperature=0.1, max_tokens=8192)
        result.analysis_type = "comparison"
        return result

    def generate_example(self, concept: str, difficulty: str = "beginner") -> AIAnalysisResult:
        """
        Generate a Sarana code example for a specific concept.
        
        Args:
            concept: The concept to demonstrate (e.g., "loops", "recursion", "exception handling")
            difficulty: beginner, intermediate, or advanced
            
        Returns:
            AIAnalysisResult with the generated example
        """
        prompt = f"""Generate a {difficulty}-level Sarana program demonstrating: {concept}

Requirements:
1. Complete, runnable code
2. Comments explaining key parts
3. Expected output shown in comments
4. Use appropriate Sarana keywords
5. Follow all grammar rules (semicolons, braces, etc.)

Format:
```sarana
<code here>
```

Explanation of how it works:"""

        result = self._generate_with_context(prompt, temperature=0.4, max_tokens=2048)
        result.analysis_type = "example_generation"
        return result


# =============================================================================
# Helper functions for UI integration
# =============================================================================

def create_ai_assistant(
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash"
) -> SaranaAIAssistant:
    """
    Factory function to create an AI assistant instance.
    
    Args:
        api_key: Gemini API key (optional, uses env var or session state)
        model_name: Model to use
        
    Returns:
        Configured SaranaAIAssistant instance
    """
    # Try to get from session state if not provided
    if not api_key:
        api_key = st.session_state.get("gemini_api_key", "")
    
    return SaranaAIAssistant(api_key=api_key, model_name=model_name)
