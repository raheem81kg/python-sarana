#!/usr/bin/env python3
"""
TEST 3: Parser (src/parser.py)
===============================
Tests that the parser correctly builds AST from tokens.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import parse, get_ast_string
from errors import ParseError
from colors import Colors

print('\n' + '='*60)
print('TEST 3: Parser')
print('='*60 + '\n')

# Test 1: PEMDAS
print('Test: PEMDAS — 2 + 3 * 4 should parse as 2 + (3 * 4)')
ast = parse('bloom x = 2 + 3 * 4;')
expr = ast.statements[0].value
assert expr.operator == '+', 'Root should be +'
assert expr.right.operator == '*', 'Right child should be *'
print(Colors.success('[PASS] PEMDAS: multiplication has higher precedence than addition\n'))

print('Test: Parentheses override PEMDAS — (2 + 3) * 4')
ast = parse('bloom x = (2 + 3) * 4;')
expr = ast.statements[0].value
assert expr.operator == '*', 'Root should be *'
assert expr.left.operator == '+', 'Left child should be +'
print(Colors.success('[PASS] Parentheses correctly override precedence\n'))

# Test 2: All statement types
print('Test: All statement types parse correctly')
tests = [
    ('bloom x = 5;', 'BloomStatement'),
    ('echo "hi";', 'EchoStatement'),
    ('when (true) {}', 'WhenStatement'),
    ('cycle (i < 10) {}', 'CycleStatement'),
    ('craft add(a, b) { return a + b; }', 'CraftStatement'),
    ('return 42;', 'ReturnStatement'),
    ('try {} ketch {}', 'TryKetchStatement'),
]

for code, expected_type in tests:
    ast = parse(code)
    actual_type = ast.statements[0].__class__.__name__
    assert expected_type in actual_type, f'Expected {expected_type}, got {actual_type}'
    print(Colors.success('[PASS] {expected_type:20} <- {code}'))
print()

# Test 3: AST string generation
print('Test: AST string representation')
code = 'bloom x = 5; echo x;'
ast_str = get_ast_string(code)
assert 'Program' in ast_str
assert 'BloomStatement' in ast_str
assert 'EchoStatement' in ast_str
print(Colors.success('[PASS] get_ast_string() generates readable AST'))
print('\nAST Preview:')
print(ast_str[:200] + '...\n')

# Test 4: Error detection
print('Test: ParseError on syntax error')
try:
    parse('bloom = 5;')  # missing variable name
    assert False, 'Should have raised ParseError'
except ParseError as e:
    print(Colors.success('[PASS] ParseError on "bloom = 5;": {e}\n'))

try:
    parse('bloom x = ;')  # missing expression
    assert False, 'Should have raised ParseError'
except ParseError as e:
    print(Colors.success('[PASS] ParseError on "bloom x = ;": {e}\n'))

# Test 5: Complex program
print('Test: Complex program with nested structures')
code = '''
craft factorial(n) {
    when (n <= 1) {
        return 1;
    } otherwise {
        return n * factorial(n - 1);
    }
}

bloom result = factorial(5);
echo result;
'''
ast = parse(code)
assert len(ast.statements) == 3, f'Expected 3 statements, got {len(ast.statements)}'
print(Colors.success('[PASS] Complex program parsed successfully'))
print(f'  - {len(ast.statements)} top-level statements')
print(f'  - Nested when/otherwise inside function')
print()

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL PARSER TESTS PASSED [PASS][PASS][PASS]'))
print('='*60 + '\n')
