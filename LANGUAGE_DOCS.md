# Sarana Language Reference

Sarana is a high-level, general-purpose, imperative programming language with a Caribbean/nature-inspired keyword set. It was designed and built as a university project for CIT4004 (Analysis of Programming Languages) at the University of Technology, Jamaica.

---

## Quick Reference Table

| Keyword       | Meaning                | Equivalent         |
|---------------|------------------------|--------------------|
| `bloom`       | Declare variable       | `let`, `var`       |
| `echo`        | Print output           | `print()`          |
| `when`        | If condition           | `if`               |
| `otherwise`   | Else branch            | `else`             |
| `cycle`       | While loop             | `while`            |
| `craft`       | Define function        | `def`, `func`      |
| `return`      | Return value           | `return`           |
| `try`         | Try block              | `try`              |
| `ketch`       | Catch exception        | `catch`, `except`  |
| `true`        | Boolean true           | `true`, `True`     |
| `false`       | Boolean false          | `false`, `False`   |
| `and`         | Logical AND            | `&&`, `and`        |
| `or`          | Logical OR             | `\|\|`, `or`       |
| `not`         | Logical NOT            | `!`, `not`         |
| `--`          | Comment                | `//`, `#`          |

---

## Language Characteristics

| Property        | Value                                                          |
|-----------------|----------------------------------------------------------------|
| **Paradigm**    | Imperative / Procedural                                        |
| **Level**       | High-level                                                     |
| **Purpose**     | General-purpose                                                |
| **File ext.**   | `.sa`                                                          |
| **Built with**  | Python 3 + PLY (Python Lex-Yacc)                               |
| **Target code** | Compiles to Python                                             |

---

## 1. Variables

Variables are declared with `bloom` and must end with a semicolon.

```sarana
bloom name = "Serena";
bloom age  = 21;
bloom pi   = 3.14;
bloom flag = true;
```

### Supported types

| Type    | Example             |
|---------|---------------------|
| Integer | `42`, `-7`          |
| Float   | `3.14`, `-0.5`      |
| String  | `"hello"`, `'hi'`   |
| Boolean | `true`, `false`     |
| Array   | `[1, 2, 3]`         |

---

## 2. Output

Use `echo` to print one or more expressions. Multiple expressions are printed space-separated.

```sarana
echo "Hello, World!";
echo "The answer is " 42;

bloom x = 10;
echo x;
echo "x equals " x;
```

---

## 3. Arithmetic

Sarana follows **PEMDAS/BODMAS** operator precedence.

| Operator | Meaning        | Example         |
|----------|----------------|-----------------|
| `+`      | Addition       | `a + b`         |
| `-`      | Subtraction    | `a - b`         |
| `*`      | Multiplication | `a * b`         |
| `/`      | Division       | `a / b`         |
| `%`      | Modulo         | `a % b`         |

```sarana
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;   -- PEMDAS: 20 + (40 * 40) = 1620
echo C;                -- prints: 1620

bloom D = (A + B) * 2; -- parentheses override: (20 + 40) * 2 = 120
echo D;
```

---

## 4. Comparison Operators

| Operator | Meaning               |
|----------|-----------------------|
| `==`     | Equal to              |
| `!=`     | Not equal to          |
| `<`      | Less than             |
| `>`      | Greater than          |
| `<=`     | Less than or equal    |
| `>=`     | Greater than or equal |

```sarana
bloom x = 10;
bloom y = 5;
echo x > y;    -- true
echo x == y;   -- false
```

---

## 5. Conditionals

### Simple when / otherwise

```sarana
bloom score = 85;

when (score >= 60) {
    echo "Passed!";
} otherwise {
    echo "Failed.";
}
```

### else-if chains with `otherwise when`

```sarana
bloom score = 85;

when (score >= 90) {
    echo "Grade: A";
} otherwise when (score >= 80) {
    echo "Grade: B";
} otherwise when (score >= 70) {
    echo "Grade: C";
} otherwise {
    echo "Grade: F";
}
```

---

## 6. Loops

The `cycle` keyword is Sarana's while loop.

```sarana
bloom i = 1;

cycle (i <= 5) {
    echo i;
    bloom i = i + 1;
}
-- prints: 1  2  3  4  5
```

---

## 7. Functions

Functions are declared with `craft` and can accept parameters. Use `return` to return a value.

```sarana
craft add(a, b) {
    return a + b;
}

bloom result = add(10, 20);
echo result;    -- prints: 30
```

### Recursive functions

```sarana
craft factorial(n) {
    when (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

echo factorial(5);   -- prints: 120
```

---

## 8. Exception Handling

Use `try` and `ketch` to handle runtime errors gracefully.

```sarana
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;    -- 1620

try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}

echo "The result is " C;
```

**Output:**
```
Error: Division by zero attempted but not allowed.
The result is 1620
```

---

## 9. Boolean Logic

### AND / OR / NOT

```sarana
bloom a = true;
bloom b = false;

echo a and b;   -- false
echo a or b;    -- true
echo not a;     -- false
```

### Short-circuit evaluation

Sarana implements **short-circuit evaluation**:
- `or`: if the left side is `true`, the right side is **never evaluated**
- `and`: if the left side is `false`, the right side is **never evaluated**

```sarana
bloom x = 10;

-- x > 5 is true, so x / 0 is NEVER evaluated — no error!
when (x > 5 or x / 0 > 1) {
    echo "Short-circuit OR works!";
}
```

---

## 10. Arrays

```sarana
bloom numbers = [1, 2, 3, 4, 5];
echo numbers;
```

---

## 11. Comments

Use `--` for single-line comments. They can appear on their own line or at the end of a line.

```sarana
-- This is a full-line comment
bloom x = 5;   -- This is an inline comment
```

---

## 12. Complete Example Programs

### Sample 1: Required Assignment Demo

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

### Sample 2: Scope and Binding

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

### Sample 3: Functions and Loops

```sarana
-- Functions and Loops
craft multiply(a, b) {
    bloom product = 0;
    bloom count = 0;
    cycle (count < b) {
        bloom product = product + a;
        bloom count = count + 1;
    }
    return product;
}

bloom result = multiply(6, 7);
echo "6 * 7 = " result;
```

### Sample 4: Boolean Logic and Short-Circuit

```sarana
bloom x = 10;

-- Short-circuit: x > 5 is true, so x / 0 is never reached
when (x > 5 or x / 0 > 1) {
    echo "Short-circuit OR works!";
}

-- Grade checker using otherwise when
bloom score = 95;
when (score >= 90) {
    echo "A (with bonus)";
} otherwise when (score >= 80) {
    echo "B";
} otherwise {
    echo "Below B";
}
```

---

## 13. Grammar Summary (EBNF)

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
block         ::= '{' statement* '}'

expression    ::= logic_or
logic_or      ::= logic_and ( 'or' logic_and )*
logic_and     ::= equality ( 'and' equality )*
equality      ::= comparison ( ('==' | '!=') comparison )*
comparison    ::= term ( ('<' | '>' | '<=' | '>=') term )*
term          ::= factor ( ('+' | '-') factor )*
factor        ::= unary ( ('*' | '/' | '%') unary )*
unary         ::= ('not' | '-') unary | primary
primary       ::= INTEGER | FLOAT | STRING | 'true' | 'false'
               | IDENTIFIER | IDENTIFIER '(' args? ')'
               | '[' args? ']' | '(' expression ')'
```

---

## 14. Token Reference

| Token Type      | Pattern / Description              | Examples                    |
|-----------------|------------------------------------|-----------------------------|
| `BLOOM`         | Keyword `bloom`                    | `bloom`                     |
| `ECHO`          | Keyword `echo`                     | `echo`                      |
| `WHEN`          | Keyword `when`                     | `when`                      |
| `OTHERWISE`     | Keyword `otherwise`                | `otherwise`                 |
| `CYCLE`         | Keyword `cycle`                    | `cycle`                     |
| `CRAFT`         | Keyword `craft`                    | `craft`                     |
| `RETURN`        | Keyword `return`                   | `return`                    |
| `TRY`           | Keyword `try`                      | `try`                       |
| `KETCH`         | Keyword `ketch`                    | `ketch`                     |
| `TRUE`          | Keyword `true`                     | `true`                      |
| `FALSE`         | Keyword `false`                    | `false`                     |
| `AND`           | Keyword `and`                      | `and`                       |
| `OR`            | Keyword `or`                       | `or`                        |
| `NOT`           | Keyword `not`                      | `not`                       |
| `IDENTIFIER`    | `[a-zA-Z_][a-zA-Z0-9_]*`           | `x`, `myVar`, `count`       |
| `INTEGER`       | `[0-9]+`                           | `42`, `0`, `1620`           |
| `FLOAT`         | `[0-9]+\.[0-9]+`                   | `3.14`, `0.5`               |
| `STRING`        | `"..."` or `'...'`                 | `"hello"`, `'world'`        |
| `PLUS`          | `+`                                | `a + b`                     |
| `MINUS`         | `-`                                | `a - b`                     |
| `MULTIPLY`      | `*`                                | `a * b`                     |
| `DIVIDE`        | `/`                                | `a / b`                     |
| `MODULO`        | `%`                                | `a % b`                     |
| `ASSIGN`        | `=`                                | `bloom x = 5`               |
| `DOUBLE_EQUALS` | `==`                               | `x == y`                    |
| `NOT_EQUALS`    | `!=`                               | `x != y`                    |
| `LESS_THAN`     | `<`                                | `x < y`                     |
| `GREATER_THAN`  | `>`                                | `x > y`                     |
| `LESS_EQUAL`    | `<=`                               | `x <= y`                    |
| `GREATER_EQUAL` | `>=`                               | `x >= y`                    |
| `LPAREN`        | `(`                                | function calls, conditions  |
| `RPAREN`        | `)`                                |                             |
| `LBRACE`        | `{`                                | block start                 |
| `RBRACE`        | `}`                                | block end                   |
| `LBRACKET`      | `[`                                | array start                 |
| `RBRACKET`      | `]`                                | array end                   |
| `SEMICOLON`     | `;`                                | statement terminator        |
| `COMMA`         | `,`                                | argument separator          |

---

## 15. Error Types

| Error Class           | When it occurs                                          |
|-----------------------|---------------------------------------------------------|
| `LexError`            | Unrecognized character in source code                   |
| `ParseError`          | Source code violates grammar rules                      |
| `SemanticError`       | Variable used before `bloom`, function called before `craft` |
| `SaranaRuntimeError`  | Runtime error (division by zero, type error, etc.)      |
| `UnexpectedEndError`  | Program ends unexpectedly (unclosed block, etc.)        |

---

## 16. Nine Characteristics of a Good Programming Language

The Sarana language was designed to exhibit all nine characteristics studied in CIT4004:

| # | Characteristic    | How Sarana demonstrates  it                                           |
|---|-------------------|-----------------------------------------------------------------------|
| 1 | **Readability**   | Natural English keywords (`bloom`, `echo`, `cycle`, `ketch`) make code self-documenting |
| 2 | **Writability**   | Concise syntax; one keyword per concept, no boilerplate required      |
| 3 | **Reliability**   | Static semantic analysis catches errors before execution              |
| 4 | **Simplicity**    | Small keyword set (14 keywords), consistent grammar rules             |
| 5 | **Orthogonality** | Constructs combine predictably; any expression can appear anywhere an expression is expected |
| 6 | **Data types**    | Integer, Float, String, Boolean, Array — all with appropriate literals |
| 7 | **Syntax design** | Brace-delimited blocks `{ }` and mandatory semicolons reduce ambiguity |
| 8 | **Support for abstraction** | `craft` functions enable procedural abstraction; local scope enforced |
| 9 | **Exception handling** | `try` / `ketch` blocks allow programs to recover from runtime errors  |

---

## Authors

- **Serena Morris** — 2208659
- **Raheem Gordon** — 2208501

*Sarana Language Reference — CIT4004, Semester 2 2025/2026, University of Technology, Jamaica*
