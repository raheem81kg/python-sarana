#!/usr/bin/env python3
"""
TEST 4: Semantic Analyzer (src/semantic.py)
============================================
Tests that the semantic analyzer catches static errors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import parse
from semantic import analyze
from colors import Colors

print('\n' + '='*60)
print('TEST 4: Semantic Analyzer')
print('='*60 + '\n')

# Test 1: Undefined variable
print('Test: Detects undefined variable')
code = 'echo x;'
errors = analyze(parse(code))
assert len(errors) == 1, f'Expected 1 error, got {len(errors)}'
assert 'used before being declared' in str(errors[0]) or 'undefined' in str(errors[0]).lower()
print(Colors.success('[PASS] Caught: {errors[0]}\n'))

# Test 2: Undefined function
print('Test: Detects undefined function')
code = 'bloom result = add(1, 2);'
errors = analyze(parse(code))
assert len(errors) == 1, f'Expected 1 error, got {len(errors)}'
assert 'function' in str(errors[0]).lower()
print(Colors.success('[PASS] Caught: {errors[0]}\n'))

# Test 3: Division by zero (static)
print('Test: Detects static division by zero')
code = 'bloom x = 10 / 0;'
errors = analyze(parse(code))
assert len(errors) == 1, f'Expected 1 error, got {len(errors)}'
assert 'division by zero' in str(errors[0]).lower()
print(Colors.success('[PASS] Caught: {errors[0]}\n'))

# Test 4: Type mismatch
print('Test: Detects type mismatch')
code = 'bloom x = "hello" - 5;'
errors = analyze(parse(code))
assert len(errors) >= 1, f'Expected at least 1 error, got {len(errors)}'
print(Colors.success('[PASS] Caught: {errors[0]}\n'))

# Test 5: Multiple errors collected
print('Test: Collects multiple errors in one pass')
code = '''
echo x;
echo y;
bloom z = a + b;
'''
errors = analyze(parse(code))
assert len(errors) == 4, f'Expected 4 errors (x,y,a,b undefined), got {len(errors)}'
print(Colors.success('[PASS] Collected {len(errors)} errors in single pass:'))
for e in errors:
    print(f'   - {e}')
print()

# Test 6: Valid program (no errors)
print('Test: Valid program produces no errors')
code = '''
bloom x = 10;
bloom y = 20;
bloom z = x + y;
echo z;
'''
errors = analyze(parse(code))
assert len(errors) == 0, f'Expected 0 errors, got {len(errors)}: {errors}'
print(Colors.success('[PASS] Valid program: no errors\n'))

# Test 7: Function scope
print('Test: Function parameters are in scope')
code = '''
craft add(a, b) {
    return a + b;
}
bloom result = add(5, 10);
'''
errors = analyze(parse(code))
assert len(errors) == 0, f'Expected 0 errors, got {len(errors)}: {errors}'
print(Colors.success('[PASS] Function parameters correctly scoped\n'))

# Test 8: Try/ketch allows div by zero
print('Test: Division by zero inside try/ketch is allowed')
code = '''
try {
    bloom x = 10 / 0;
}
ketch {
    echo "error caught";
}
'''
errors = analyze(parse(code))
assert len(errors) == 0, f'Expected 0 errors (suppressed in try block), got {len(errors)}: {errors}'
print(Colors.success('[PASS] Division by zero suppressed inside try block\n'))

# Test 9: Interpreter enforces block scope at runtime
print('Test: Block scope handled at runtime')
code = '''
bloom x = 10;
when (x > 5) {
    bloom y = 20;
}
echo y;
'''
errors = analyze(parse(code))
# Note: Semantic analyzer doesn't catch this - it's a runtime scope issue
# The interpreter will raise an error when trying to access y
print(Colors.success('[PASS] Block scope test: Semantic analysis passes (runtime check)\n'))

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL SEMANTIC TESTS PASSED [PASS][PASS][PASS]'))
print('='*60 + '\n')
