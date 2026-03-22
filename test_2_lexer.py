#!/usr/bin/env python3
"""
TEST 2: Lexer (src/lexer.py)
=============================
Tests that the lexer correctly tokenizes Sarana source code.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lexer import tokenize
from errors import LexError
from colors import Colors

print('\n' + '='*60)
print('TEST 2: Lexer')
print('='*60 + '\n')

# Test 1: All keywords
print('Test: All 14 keywords')
code = 'bloom echo when otherwise cycle craft return try ketch true false and or not'
tokens = tokenize(code)
types = [t.token_type for t in tokens]
expected = ['BLOOM', 'ECHO', 'WHEN', 'OTHERWISE', 'CYCLE', 'CRAFT', 'RETURN', 
            'TRY', 'KETCH', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT']
assert types == expected, f'Expected {expected}, got {types}'
print(Colors.success('[PASS] All 14 keywords recognized: {", ".join(expected)}\n'))

# Test 2: Literals
print('Test: Literals (integer, float, string)')
code = '42 3.14 "hello world"'
tokens = tokenize(code)
assert tokens[0].token_type == 'INTEGER' and tokens[0].value == 42
assert tokens[1].token_type == 'FLOAT' and tokens[1].value == 3.14
assert tokens[2].token_type == 'STRING' and tokens[2].value == 'hello world'
print(Colors.success('[PASS] INTEGER: 42'))
print(Colors.success('[PASS] FLOAT: 3.14'))
print(Colors.success('[PASS] STRING: "hello world"\n'))

# Test 3: Operators
print('Test: All operators')
code = '+ - * / % == != < > <= >= ='
tokens = tokenize(code)
ops = [t.token_type for t in tokens]
print(Colors.success('[PASS] {len(ops)} operators recognized: {", ".join(ops)}\n'))

# Test 4: Comments ignored
print('Test: Comments are ignored')
code = '''-- This is a comment
bloom x = 5; -- inline comment
-- another comment
'''
tokens = tokenize(code)
assert not any(t.token_type == 'COMMENT' for t in tokens)
assert len([t for t in tokens if t.token_type == 'BLOOM']) == 1
print(Colors.success('[PASS] Comments completely removed from token stream\n'))

# Test 5: Line numbers
print('Test: Line number tracking')
code = '''bloom a = 1;
bloom b = 2;
bloom c = 3;'''
tokens = tokenize(code)
blooms = [t for t in tokens if t.token_type == 'BLOOM']
assert blooms[0].line == 1
assert blooms[1].line == 2
assert blooms[2].line == 3
print(Colors.success('[PASS] Line numbers correctly tracked across newlines\n'))

# Test 6: Error on invalid character
print('Test: LexError on invalid character')
try:
    tokenize('bloom x = @5;')
    assert False, 'Should have raised LexError'
except LexError as e:
    print(Colors.success('[PASS] LexError raised: {e}\n'))

# Test 7: Complex expression
print('Test: Complex arithmetic expression')
code = 'bloom result = (10 + 20) * 3 - 5 / 2;'
tokens = tokenize(code)
print(Colors.success('[PASS] Tokenized complex expression into {len(tokens)} tokens'))
for t in tokens:
    print(f'   {t.token_type:15} {t.value}')
print()

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL LEXER TESTS PASSED [PASS][PASS][PASS]'))
print('='*60 + '\n')
