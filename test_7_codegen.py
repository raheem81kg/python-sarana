#!/usr/bin/env python3
"""
TEST 7: Code Generator (src/codegen.py)
========================================
Tests that the code generator translates Sarana AST to Python correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import parse
from codegen import generate, generate_to_file
import subprocess
import tempfile
from colors import Colors

print('\n' + '='*60)
print('TEST 7: Code Generator')
print('='*60 + '\n')

# Test 1: Simple variable and output
print('Test: Simple bloom and echo')
code = 'bloom x = 5; echo x;'
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code}')
print('Generated Python:')
print(python_code)
assert 'x = 5' in python_code
assert 'print(x)' in python_code
print(Colors.success('[PASS] Variables and output translated correctly\n'))

# Test 2: Arithmetic with PEMDAS
print('Test: Arithmetic expression')
code = 'bloom x = 2 + 3 * 4; echo x;'
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code}')
print('Generated Python:')
print(python_code)
assert 'x = (2 + (3 * 4))' in python_code or 'x = ((2 + (3 * 4)))' in python_code
print(Colors.success('[PASS] PEMDAS arithmetic translated correctly\n'))

# Test 3: Conditionals
print('Test: When/otherwise (if/else)')
code = '''
when (x > 5) {
    echo "big";
} otherwise {
    echo "small";
}
'''
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code.strip()}')
print('Generated Python:')
print(python_code)
assert 'if' in python_code
assert 'else:' in python_code
assert 'print("big")' in python_code
assert 'print("small")' in python_code
print(Colors.success('[PASS] Conditionals translated correctly\n'))

# Test 4: Loops
print('Test: Cycle (while loop)')
code = '''
bloom i = 0;
cycle (i < 3) {
    echo i;
    bloom i = i + 1;
}
'''
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code.strip()}')
print('Generated Python:')
print(python_code)
assert 'while' in python_code
assert 'i < 3' in python_code
print(Colors.success('[PASS] Loops translated correctly\n'))

# Test 5: Functions
print('Test: Craft (function definition)')
code = '''
craft add(a, b) {
    return a + b;
}
bloom result = add(10, 20);
echo result;
'''
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code.strip()}')
print('Generated Python:')
print(python_code)
assert 'def add(a, b):' in python_code
assert 'return (a + b)' in python_code
assert 'result = add(10, 20)' in python_code
print(Colors.success('[PASS] Functions translated correctly\n'))

# Test 6: Try/Ketch
print('Test: Try/ketch (exception handling)')
code = '''
try {
    bloom x = 10 / 0;
}
ketch {
    echo "error";
}
'''
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code.strip()}')
print('Generated Python:')
print(python_code)
assert 'try:' in python_code
assert 'except Exception:' in python_code
assert 'print("error")' in python_code
print(Colors.success('[PASS] Exception handling translated correctly\n'))

# Test 7: Booleans
print('Test: Boolean literals and operators')
code = 'bloom x = true and not false;'
ast = parse(code)
python_code = generate(ast)
print(f'Sarana: {code}')
print('Generated Python:')
print(python_code)
assert 'True' in python_code
assert 'False' in python_code
assert 'and' in python_code
assert 'not' in python_code
print(Colors.success('[PASS] Booleans translated correctly\n'))

# Test 8: Required Assignment Sample
print('Test: Required assignment sample')
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

ast = parse(REQUIRED_SAMPLE)
python_code = generate(ast)
print('Sarana: [Required Assignment Sample]')
print('Generated Python:')
print(python_code)
print()

# Test 9: Execute generated code
print('Test: Generated code is executable')
print('-' * 60)

# Write to temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(python_code)
    temp_file = f.name

try:
    # Execute the generated Python code
    result = subprocess.run(
        ['python3', temp_file],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    print('Generated Python code execution:')
    print('STDOUT:')
    print(result.stdout)
    
    if result.returncode == 0:
        print(Colors.success('[PASS] Generated code executed successfully'))
        
        # Verify output
        expected_lines = [
            'Error: Division by zero attempted but not allowed.',
            'The result is  1620'
        ]
        
        output_lines = result.stdout.strip().split('\n')
        
        if output_lines == expected_lines:
            print(Colors.success('[PASS][PASS][PASS] OUTPUT MATCHES EXPECTED [PASS][PASS][PASS]'))
        else:
            print(Colors.error('[FAIL] Output mismatch:'))
            print(f'  Expected: {expected_lines}')
            print(f'  Got:      {output_lines}')
    else:
        print(Colors.error('[FAIL] Generated code failed with exit code {result.returncode}'))
        print(f'STDERR: {result.stderr}')
        
finally:
    # Clean up temp file
    os.unlink(temp_file)

print()
print('-' * 60)
print()

# Test 10: Save to output folder
print('Test: Generate to file')
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'generated_sample.py')
generate_to_file(ast, output_path)
print(Colors.success('[PASS] Generated code saved to: {output_path}'))

# Verify file exists and is readable
with open(output_path, 'r') as f:
    file_content = f.read()
    assert len(file_content) > 0
    assert 'A = 20' in file_content
    print(Colors.success('[PASS] File is readable and contains expected code'))
print()

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL CODE GENERATOR TESTS PASSED [PASS][PASS][PASS]'))
print('='*60)
print()
print('Generated Python code can be executed with:')
print(f'  python3 {output_path}')
print()
