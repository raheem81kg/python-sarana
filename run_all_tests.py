#!/usr/bin/env python3
"""
run_all_tests.py
================
Master test suite that runs ALL tests for the Sarana compiler.

Usage:
    python3 run_all_tests.py
"""

import sys
import os

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from errors import (LexError, ParseError, SemanticError, SaranaRuntimeError,
                    UnexpectedEndError, UnexpectedTokenError)
from lexer import tokenize
from parser import parse, get_ast_string
from semantic import analyze
from interpreter import interpret
from colors import Colors


# ══════════════════════════════════════════════════════════════════════════════
# Test tracking
# ══════════════════════════════════════════════════════════════════════════════

TOTAL_PASS = 0
TOTAL_FAIL = 0
SECTION_PASS = 0
SECTION_FAIL = 0


def start_section(title):
    global SECTION_PASS, SECTION_FAIL
    SECTION_PASS = 0
    SECTION_FAIL = 0
    print(f'\n{"=" * 70}')
    print(f'  {title}')
    print(f'{"=" * 70}')


def end_section():
    global SECTION_PASS, SECTION_FAIL, TOTAL_PASS, TOTAL_FAIL
    TOTAL_PASS += SECTION_PASS
    TOTAL_FAIL += SECTION_FAIL
    status = '[PASS] ALL PASSED' if SECTION_FAIL == 0 else f'[FAIL] {SECTION_FAIL} FAILED'
    print(f'\n  Section result: {SECTION_PASS} passed, {SECTION_FAIL} failed [{status}]')


def check(label, condition, got=None):
    global SECTION_PASS, SECTION_FAIL
    if condition:
        SECTION_PASS += 1
        print(Colors.success('  [PASS] {label}'))
    else:
        SECTION_FAIL += 1
        detail = f'  ← got: {got}' if got is not None else ''
        print(Colors.error('  [FAIL] {label}{detail}'))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Error Classes
# ══════════════════════════════════════════════════════════════════════════════

start_section('1 / 6   ERROR CLASSES (src/errors.py)')

e = LexError('bad char', line=3)
check('LexError formats with line number', '[Line 3]' in str(e))

e = ParseError('missing ;', line=5)
check('ParseError formats with line number', '[Line 5]' in str(e))

e = SemanticError('undefined var', line=7)
check('SemanticError formats correctly', 'Semantic Error' in str(e))

e = SaranaRuntimeError('div by zero', line=9)
check('SaranaRuntimeError formats correctly', 'Runtime Error' in str(e))

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Lexer
# ══════════════════════════════════════════════════════════════════════════════

start_section('2 / 6   LEXER (src/lexer.py)')

# All keywords
toks = tokenize('bloom echo when otherwise cycle craft return try ketch;')
types = [t.token_type for t in toks if t.token_type != 'SEMICOLON']
check('All 9 statement keywords recognized', 
      set(['BLOOM','ECHO','WHEN','OTHERWISE','CYCLE','CRAFT','RETURN','TRY','KETCH']).issubset(set(types)))

toks = tokenize('true false and or not;')
types = [t.token_type for t in toks if t.token_type != 'SEMICOLON']
check('All 5 boolean keywords recognized',
      types == ['TRUE','FALSE','AND','OR','NOT'])

# Literals
toks = tokenize('42 3.14 "hello" true;')
check('INTEGER token', toks[0].token_type == 'INTEGER' and toks[0].value == 42)
check('FLOAT token', toks[1].token_type == 'FLOAT' and toks[1].value == 3.14)
check('STRING token', toks[2].token_type == 'STRING' and toks[2].value == 'hello')
check('TRUE token', toks[3].token_type == 'TRUE')

# Operators
toks = tokenize('+ - * / % == != < > <= >=')
ops = [t.token_type for t in toks]
check('All 11 operators recognized', len(ops) == 11)

# Comments ignored
toks = tokenize('-- comment\nbloom x = 5;')
check('Comments completely ignored', all(t.token_type != 'COMMENT' for t in toks))

# Line numbers
toks = tokenize('bloom a = 1;\nbloom b = 2;')
blooms = [t for t in toks if t.token_type == 'BLOOM']
check('Line numbers tracked correctly', blooms[0].line == 1 and blooms[1].line == 2)

# Error detection
try:
    tokenize('bloom x = @5;')
    check('LexError on invalid char @', False)
except LexError:
    check('LexError on invalid char @', True)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Parser
# ══════════════════════════════════════════════════════════════════════════════

start_section('3 / 6   PARSER (src/parser.py)')

# PEMDAS
ast = parse('bloom x = 2 + 3 * 4;')
expr = ast.statements[0].value
check('PEMDAS: 2+3*4 → + is root, * is deeper',
      expr.operator == '+' and expr.right.operator == '*')

ast = parse('bloom x = (2 + 3) * 4;')
expr = ast.statements[0].value
check('Parentheses override PEMDAS',
      expr.operator == '*' and expr.left.operator == '+')

# All statement types
check('BloomStatement parses', 'Bloom' in parse('bloom x = 5;').statements[0].__class__.__name__)
check('EchoStatement parses', 'Echo' in parse('echo "hi";').statements[0].__class__.__name__)
check('WhenStatement parses', 'When' in parse('when(true){}').statements[0].__class__.__name__)
check('CycleStatement parses', 'Cycle' in parse('cycle(true){}').statements[0].__class__.__name__)
check('CraftStatement parses', 'Craft' in parse('craft f(){}').statements[0].__class__.__name__)
check('TryKetchStatement parses', 'TryKetch' in parse('try{}ketch{}').statements[0].__class__.__name__)
check('ReturnStatement parses', 'Return' in parse('return 5;').statements[0].__class__.__name__)

# Error detection
try:
    parse('bloom = 5;')
    check('ParseError on missing var name', False)
except ParseError:
    check('ParseError on missing var name', True)

# AST string generation
ast_str = get_ast_string('bloom x = 5; echo x;')
check('get_ast_string works', 'Program' in ast_str and 'BloomStatement' in ast_str)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Semantic Analyzer
# ══════════════════════════════════════════════════════════════════════════════

start_section('4 / 6   SEMANTIC ANALYZER (src/semantic.py)')

# Errors detected
check('Detects undefined variable', len(analyze(parse('echo x;'))) == 1)
check('Detects undefined function', len(analyze(parse('bloom x = add(1,2);'))) == 1)
check('Detects division by zero', len(analyze(parse('bloom x = 10/0;'))) == 1)
check('Detects type mismatch', len(analyze(parse('bloom x = "hi" - 5;'))) >= 1)
check('Collects multiple errors', len(analyze(parse('echo x; echo y;'))) == 2)

# Valid programs
check('Valid program: no errors', len(analyze(parse('bloom x = 5; echo x;'))) == 0)
check('Valid: function scope', len(analyze(parse('craft f(a){return a+1;} bloom x=f(5);'))) == 0)
check('Valid: try/ketch with div by zero', len(analyze(parse('try{bloom x=10/0;}ketch{echo "e";}'))) == 0)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Interpreter
# ══════════════════════════════════════════════════════════════════════════════

start_section('5 / 6   INTERPRETER (src/interpreter.py)')

# Arithmetic
result = interpret(parse('bloom x = 2 + 3; echo x;'))
check('Addition: 2 + 3 = 5', result.output == ['5'])

result = interpret(parse('bloom x = 2 + 3 * 4; echo x;'))
check('PEMDAS: 2 + 3*4 = 14', result.output == ['14'])

result = interpret(parse('bloom x = 6 * 7; echo x;'))
check('Multiplication: 6 * 7 = 42', result.output == ['42'])

# Variables
result = interpret(parse('bloom x = 5; bloom y = 10; bloom z = x + y; echo z;'))
check('Variable references', result.output == ['15'])

# Conditionals
result = interpret(parse('when (5 > 3) { echo "yes"; }'))
check('When true branch', result.output == ['yes'])

result = interpret(parse('when (5 < 3) { echo "no"; } otherwise { echo "yes"; }'))
check('Otherwise branch', result.output == ['yes'])

# Loops
result = interpret(parse('bloom i = 0; cycle (i < 3) { echo i; bloom i = i + 1; }'))
check('Cycle loop 0 to 2', result.output == ['0', '1', '2'])

# Functions
result = interpret(parse('craft add(a,b){return a+b;} bloom x=add(10,20); echo x;'))
check('Function definition and call', result.output == ['30'])

# Try/Ketch
result = interpret(parse('try{bloom x=10/0;} ketch{echo "caught";} echo "after";'))
check('Try/ketch catches error', result.output == ['caught', 'after'])
check('Try/ketch: program succeeds', result.success)

# Booleans
result = interpret(parse('bloom x = true and false; echo x;'))
check('Boolean AND', result.output == ['false'])

result = interpret(parse('bloom x = not true; echo x;'))
check('Boolean NOT', result.output == ['false'])

# Strings
result = interpret(parse('bloom x = "hello" + " world"; echo x;'))
check('String concatenation', result.output == ['hello world'])

result = interpret(parse('bloom x = "ha" * 3; echo x;'))
check('String repetition', result.output == ['hahaha'])

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Full Pipeline (Required Sample)
# ══════════════════════════════════════════════════════════════════════════════

start_section('6 / 6   FULL PIPELINE — Required Assignment Sample')

REQUIRED_SAMPLE = """-- Sample program in Sarana

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
"""

print()
print('  Running the required assignment sample program:')
print()

# Step 1: Tokenize
tokens = tokenize(REQUIRED_SAMPLE)
check('Lexer produces 39 tokens', len(tokens) == 39, got=len(tokens))
check('Lexer ignores comments', not any(t.token_type == 'COMMENT' for t in tokens))

# Step 2: Parse
ast = parse(REQUIRED_SAMPLE)
check('Parser produces Program node', ast.__class__.__name__ == 'Program')
check('Program has 5 top-level statements', len(ast.statements) == 5, got=len(ast.statements))

# Verify PEMDAS in AST
c_stmt = ast.statements[2]  # bloom C = A + B * B
c_expr = c_stmt.value
check('C = A + B*B: + is root operator', c_expr.operator == '+', got=c_expr.operator)
check('C = A + B*B: right child is * operator', c_expr.right.operator == '*')

# Step 3: Semantic Analysis
errors = analyze(ast)
check('Semantic analysis: no errors', len(errors) == 0, got=f'{len(errors)} errors')
if errors:
    for e in errors:
        print(f'      Unexpected: {e}')

# Step 4: Interpretation
result = interpret(ast)
check('Interpreter executes successfully', result.success)
check('Output line 1 correct', result.output[0] == 'Error: Division by zero attempted but not allowed.')
check('Output line 2 correct', result.output[1] == 'The result is  1620')
check('C computed correctly (20 + 40*40 = 1620)', '1620' in result.output[1])

print()
print('  Expected output:')
print('    Error: Division by zero attempted but not allowed.')
print('    The result is  1620')
print()
print('  Actual output:')
for line in result.output:
    print(f'    {line}')

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

print()
print('=' * 70)
print('  FINAL RESULTS')
print('=' * 70)
print(f'  Total tests  : {TOTAL_PASS + TOTAL_FAIL}')
print(f'  Passed       : {TOTAL_PASS}')
print(f'  Failed       : {TOTAL_FAIL}')
print()

if TOTAL_FAIL == 0:
    print(Colors.success('  [PASS][PASS][PASS] ALL TESTS PASSED [PASS][PASS][PASS]'))
    print()
    print('  The Sarana compiler is working correctly!')
    print('  Ready to proceed to Step 8 (Code Generator).')
else:
    print(Colors.error('  [FAIL] {TOTAL_FAIL} test(s) failed — see details above'))

print('=' * 70)
print()
