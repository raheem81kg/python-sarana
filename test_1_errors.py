#!/usr/bin/env python3
"""
TEST 1: Error Classes (src/errors.py)
======================================
Tests that all custom error classes format correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from errors import LexError, ParseError, SemanticError, SaranaRuntimeError
from colors import Colors

print('\n' + '='*60)
print('TEST 1: Error Classes')
print('='*60 + '\n')

# Test 1: LexError
e = LexError('Unexpected character @', line=5)
print(f'LexError: {e}')
assert '[Line 5]' in str(e), 'LexError should include line number'
assert 'Lexical Error' in str(e), 'LexError should include error type'
print(Colors.success('[PASS] LexError formats correctly\n'))

# Test 2: ParseError
e = ParseError('Expected semicolon', line=12)
print(f'ParseError: {e}')
assert '[Line 12]' in str(e), 'ParseError should include line number'
assert 'Syntax Error' in str(e), 'ParseError should include error type'
print(Colors.success('[PASS] ParseError formats correctly\n'))

# Test 3: SemanticError
e = SemanticError('Undefined variable "x"', line=8)
print(f'SemanticError: {e}')
assert '[Line 8]' in str(e), 'SemanticError should include line number'
assert 'Semantic Error' in str(e), 'SemanticError should include error type'
print(Colors.success('[PASS] SemanticError formats correctly\n'))

# Test 4: SaranaRuntimeError
e = SaranaRuntimeError('Division by zero', line=20)
print(f'SaranaRuntimeError: {e}')
assert '[Line 20]' in str(e), 'SaranaRuntimeError should include line number'
assert 'Runtime Error' in str(e), 'SaranaRuntimeError should include error type'
print(Colors.success('[PASS] SaranaRuntimeError formats correctly\n'))

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL ERROR TESTS PASSED [PASS][PASS][PASS]'))
print('='*60 + '\n')
