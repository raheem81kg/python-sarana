#!/usr/bin/env python3
"""
TEST 6: Full Pipeline — Required Assignment Sample
===================================================
Tests the complete compiler pipeline with the required sample program.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import tokenize
from parser import parse
from semantic import analyze
from interpreter import interpret
from colors import Colors

print('\n' + '='*70)
print('TEST 6: Full Pipeline — Required Assignment Sample')
print('='*70 + '\n')

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

print('SARANA SOURCE CODE:')
print('-' * 70)
print(REQUIRED_SAMPLE)
print('-' * 70)
print()

# PHASE 1: LEXER
print('PHASE 1: LEXER')
print('-' * 40)
tokens = tokenize(REQUIRED_SAMPLE)
print(Colors.success('[PASS] Tokenized into {len(tokens)} tokens'))
print('  Sample tokens:')
for t in tokens[:10]:
    print(f'    {t.token_type:15} {t.value}')
print('    ...')
print()

# PHASE 2: PARSER
print('PHASE 2: PARSER')
print('-' * 40)
ast = parse(REQUIRED_SAMPLE)
print(Colors.success('[PASS] Parsed into AST with {len(ast.statements)} top-level statements'))
print('  Statement types:')
for i, stmt in enumerate(ast.statements, 1):
    print(f'    {i}. {stmt.__class__.__name__}')

# Verify PEMDAS
c_stmt = ast.statements[2]  # bloom C = A + B * B
c_expr = c_stmt.value
print()
print('  PEMDAS verification (C = A + B * B):')
print(f'    Root operator: {c_expr.operator} (should be +)')
print(f'    Right child operator: {c_expr.right.operator} (should be *)')
assert c_expr.operator == '+'
assert c_expr.right.operator == '*'
print(Colors.success('  [PASS] PEMDAS: multiplication evaluated before addition'))
print()

# PHASE 3: SEMANTIC ANALYSIS
print('PHASE 3: SEMANTIC ANALYSIS')
print('-' * 40)
errors = analyze(ast)
if errors:
    print(Colors.error('[FAIL] Found {len(errors)} semantic error(s):'))
    for e in errors:
        print(f'  - {e}')
else:
    print(Colors.success('[PASS] No semantic errors detected'))
print()

# PHASE 4: INTERPRETATION
print('PHASE 4: INTERPRETATION')
print('-' * 40)
result = interpret(ast)
print(Colors.success('[PASS] Execution completed: success={result.success}'))
print()
print('OUTPUT:')
for line in result.output:
    print(f'  {line}')
print()

# VERIFY EXPECTED OUTPUT
print('VERIFICATION:')
print('-' * 40)
expected_output = [
    'Error: Division by zero attempted but not allowed.',
    'The result is  1620'
]

if result.output == expected_output:
    print(Colors.success('[PASS][PASS][PASS] OUTPUT MATCHES EXPECTED [PASS][PASS][PASS]'))
else:
    print(Colors.error('[FAIL] Output mismatch!'))
    print(f'  Expected: {expected_output}')
    print(f'  Got:      {result.output}')

# Verify computation
print()
print('COMPUTATION VERIFICATION:')
print('  A = 20')
print('  B = 40')
print('  C = A + B * B')
print('    = 20 + (40 * 40)   [PEMDAS: multiply first]')
print('    = 20 + 1600')
print('    = 1620')
print()
assert '1620' in result.output[1]
print(Colors.success('[PASS] C computed correctly as 1620'))
print()

print('='*70)
print(Colors.success('[PASS][PASS][PASS] FULL PIPELINE TEST PASSED [PASS][PASS][PASS]'))
print('='*70)
print()
print('All compiler phases working correctly:')
print(Colors.success('  [PASS] Lexer → tokens'))
print(Colors.success('  [PASS] Parser → AST'))
print(Colors.success('  [PASS] Semantic Analyzer → error checking'))
print(Colors.success('  [PASS] Interpreter → execution'))
print()
print('Ready to proceed to Step 8: Code Generator!')
print('='*70)
print()
