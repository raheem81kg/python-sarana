#!/usr/bin/env python3
"""
TEST 5: Interpreter (src/interpreter.py)
=========================================
Tests that the interpreter executes Sarana programs correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import parse
from interpreter import interpret
from colors import Colors

print('\n' + '='*60)
print('TEST 5: Interpreter')
print('='*60 + '\n')

# Test 1: Arithmetic
print('Test: Basic arithmetic')
result = interpret(parse('bloom x = 10 + 5; echo x;'))
assert result.output == ['15'], f'Expected ["15"], got {result.output}'
print(Colors.success('[PASS] 10 + 5 = 15\n'))

result = interpret(parse('bloom x = 6 * 7; echo x;'))
assert result.output == ['42'], f'Expected ["42"], got {result.output}'
print(Colors.success('[PASS] 6 * 7 = 42\n'))

result = interpret(parse('bloom x = 2 + 3 * 4; echo x;'))
assert result.output == ['14'], f'Expected ["14"], got {result.output}'
print(Colors.success('[PASS] PEMDAS: 2 + 3*4 = 14\n'))

# Test 2: Variables
print('Test: Variable declarations and references')
code = '''
bloom x = 5;
bloom y = 10;
bloom z = x + y;
echo z;
'''
result = interpret(parse(code))
assert result.output == ['15'], f'Expected ["15"], got {result.output}'
print(Colors.success('[PASS] Variable arithmetic: 5 + 10 = 15\n'))

# Test 3: Conditionals
print('Test: When/otherwise conditionals')
result = interpret(parse('when (5 > 3) { echo "yes"; }'))
assert result.output == ['yes']
print(Colors.success('[PASS] When true branch executes\n'))

result = interpret(parse('when (5 < 3) { echo "no"; } otherwise { echo "yes"; }'))
assert result.output == ['yes']
print(Colors.success('[PASS] Otherwise branch executes\n'))

# Test 4: Loops
print('Test: Cycle (while) loops')
code = '''
bloom i = 0;
cycle (i < 3) {
    echo i;
    bloom i = i + 1;
}
'''
result = interpret(parse(code))
assert result.output == ['0', '1', '2'], f'Expected ["0","1","2"], got {result.output}'
print(Colors.success('[PASS] Cycle loop: 0, 1, 2\n'))

# Test 5: Functions
print('Test: Function definition and calls')
code = '''
craft add(a, b) {
    return a + b;
}
bloom x = add(10, 20);
echo x;
'''
result = interpret(parse(code))
assert result.output == ['30'], f'Expected ["30"], got {result.output}'
print(Colors.success('[PASS] Function call: add(10, 20) = 30\n'))

# Test 6: Try/Ketch
print('Test: Exception handling with try/ketch')
code = '''
try {
    bloom x = 10 / 0;
}
ketch {
    echo "error caught";
}
echo "program continues";
'''
result = interpret(parse(code))
assert result.output == ['error caught', 'program continues']
assert result.success == True
print(Colors.success('[PASS] Try/ketch catches division by zero'))
print(Colors.success('[PASS] Program continues after ketch\n'))

# Test 7: Booleans
print('Test: Boolean operations')
result = interpret(parse('bloom x = true and false; echo x;'))
assert result.output == ['false']
print(Colors.success('[PASS] true AND false = false\n'))

result = interpret(parse('bloom x = not true; echo x;'))
assert result.output == ['false']
print(Colors.success('[PASS] NOT true = false\n'))

result = interpret(parse('bloom x = true or false; echo x;'))
assert result.output == ['true']
print(Colors.success('[PASS] true OR false = true\n'))

# Test 8: Strings
print('Test: String operations')
result = interpret(parse('bloom x = "hello" + " world"; echo x;'))
assert result.output == ['hello world']
print(Colors.success('[PASS] String concatenation: "hello" + " world"\n'))

result = interpret(parse('bloom x = "ha" * 3; echo x;'))
assert result.output == ['hahaha']
print(Colors.success('[PASS] String repetition: "ha" * 3 = "hahaha"\n'))

# Test 9: Multiple echo arguments
print('Test: Echo with multiple arguments')
result = interpret(parse('echo "The answer is" 42;'))
assert result.output == ['The answer is 42']
print(Colors.success('[PASS] echo "The answer is" 42 -> "The answer is 42"\n'))

# Test 10: Nested scopes
print('Test: Nested function scopes')
code = '''
bloom x = 100;
craft outer() {
    bloom y = 50;
    craft inner() {
        return x + y;
    }
    return inner();
}
bloom result = outer();
echo result;
'''
result = interpret(parse(code))
assert result.output == ['150']
print(Colors.success('[PASS] Nested scopes: inner function sees outer variables\n'))

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL INTERPRETER TESTS PASSED [PASS][PASS][PASS]'))
print('='*60 + '\n')
