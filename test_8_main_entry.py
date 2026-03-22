#!/usr/bin/env python3
"""
TEST 8: Main Entry Point (src/sarana.py)
=========================================
Tests the unified API that ties all compiler phases together.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sarana import compile_and_run, compile_file, CompilationResult
from colors import Colors

print('\n' + '='*60)
print('TEST 8: Main Entry Point')
print('='*60 + '\n')

# Test 1: Simple program through full pipeline
print('Test 1: Complete compilation pipeline')
code = 'bloom x = 5; echo x;'
result = compile_and_run(code)

assert result.success, "Compilation should succeed"
assert len(result.tokens) > 0, "Should have tokens"
assert result.ast is not None, "Should have AST"
assert len(result.semantic_errors) == 0, "Should have no semantic errors"
assert result.output == ['5'], f"Expected ['5'], got {result.output}"
assert 'x = 5' in result.generated_code, "Should generate x = 5"
assert 'print(x)' in result.generated_code, "Should generate print(x)"
print(Colors.success('[PASS] Full pipeline works correctly\n'))

# Test 2: Lexer error handling
print('Test 2: Lexer error handling')
code_with_lex_error = 'bloom x = @5;'
result = compile_and_run(code_with_lex_error)

assert not result.success, "Should fail due to lex error"
assert len(result.lex_errors) > 0, "Should have lex errors"
assert result.phase_reached == "lexer", "Should stop at lexer"
print(Colors.success('[PASS] Lex error caught: {result.lex_errors[0]}\n'))

# Test 3: Parser error handling
print('Test 3: Parser error handling')
code_with_parse_error = 'bloom = 5;'  # missing variable name
result = compile_and_run(code_with_parse_error)

assert not result.success, "Should fail due to parse error"
assert len(result.parse_errors) > 0, "Should have parse errors"
assert result.phase_reached == "parser", "Should stop at parser"
print(Colors.success('[PASS] Parse error caught: {result.parse_errors[0]}\n'))

# Test 4: Semantic error (non-fatal)
print('Test 4: Semantic error detection')
code_with_semantic_error = 'echo x;'  # undefined variable
result = compile_and_run(code_with_semantic_error)

assert result.success, "Should succeed (semantic errors are warnings)"
assert len(result.semantic_errors) > 0, "Should have semantic errors"
assert result.phase_reached == "complete", "Should reach completion"
print(Colors.success('[PASS] Semantic error detected: {result.semantic_errors[0]}\n'))

# Test 5: Runtime error handling
print('Test 5: Runtime error handling')
code_with_runtime_error = 'bloom x = 10 / 0;'
result = compile_and_run(code_with_runtime_error)

assert not result.interpreter_success, "Interpreter should fail"
assert len(result.runtime_errors) > 0, "Should have runtime errors"
# But code generation should still work
assert 'x = (10 / 0)' in result.generated_code, "Should still generate code"
print(Colors.success('[PASS] Runtime error caught: {result.runtime_errors[0][:50]}...\n'))

# Test 6: PEMDAS in full pipeline
print('Test 6: PEMDAS arithmetic')
code = 'bloom C = 20 + 40 * 40; echo C;'
result = compile_and_run(code)

assert result.success, "Should compile successfully"
assert result.output == ['1620'], f"Expected ['1620'], got {result.output}"
assert '(20 + (40 * 40))' in result.generated_code, "Should preserve PEMDAS"
print(Colors.success('[PASS] PEMDAS: 20 + 40*40 = 1620 [PASS]\n'))

# Test 7: Required assignment sample
print('Test 7: Required assignment sample')
REQUIRED_SAMPLE = """-- Sample program in Sarana

bloom A = 20;
bloom B = 40;
bloom C = A + B * B;

try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}

echo "The result is " C;
"""

result = compile_and_run(REQUIRED_SAMPLE)

assert result.success, "Required sample should compile"
assert len(result.semantic_errors) == 0, "Should have no semantic errors"
assert result.interpreter_success, "Should execute successfully"
expected_output = [
    'Error: Division by zero attempted but not allowed.',
    'The result is  1620'
]
assert result.output == expected_output, f"Expected {expected_output}, got {result.output}"
print(Colors.success('[PASS] Required sample compiles and runs correctly\n'))

# Test 8: to_dict() method
print('Test 8: Result serialization')
result_dict = result.to_dict()

assert 'tokens' in result_dict, "Should have tokens key"
assert 'ast' in result_dict, "Should have ast key"
assert 'output' in result_dict, "Should have output key"
assert 'generated_code' in result_dict, "Should have generated_code key"
assert 'success' in result_dict, "Should have success key"
assert result_dict['success'] == True, "Success should be True"
print(Colors.success('[PASS] Result serializes to dict correctly\n'))

# Test 9: Code generation can be disabled
print('Test 9: Optional code generation')
result = compile_and_run('bloom x = 5;', generate_target_code=False)

assert result.success, "Should succeed"
assert result.generated_code == "", "Should not generate code"
print(Colors.success('[PASS] Code generation can be disabled\n'))

# Test 10: Interpreter can be disabled
print('Test 10: Optional interpretation')
result = compile_and_run('bloom x = 5; echo x;', run_interpreter=False)

assert result.success, "Should succeed"
assert len(result.output) == 0, "Should not produce output"
assert len(result.generated_code) > 0, "Should still generate code"
print(Colors.success('[PASS] Interpretation can be disabled\n'))

# Test 11: File compilation
print('Test 11: File compilation')

# Create a temporary test file
test_file = 'test_temp.sara'
with open(test_file, 'w') as f:
    f.write('bloom x = 42;\necho x;')

try:
    result = compile_file(test_file, output_file='test_temp.py', verbose=False)
    
    assert result.success, "File compilation should succeed"
    assert os.path.exists('test_temp.py'), "Output file should be created"
    
    # Read generated file
    with open('test_temp.py', 'r') as f:
        generated = f.read()
    
    assert 'x = 42' in generated, "Generated file should contain x = 42"
    print(Colors.success('[PASS] File compilation works correctly\n'))
    
finally:
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists('test_temp.py'):
        os.remove('test_temp.py')

print('='*60)
print(Colors.success('[PASS][PASS][PASS] ALL MAIN ENTRY POINT TESTS PASSED [PASS][PASS][PASS]'))
print('='*60)
print()
print('The unified API successfully:')
print(Colors.success('  [PASS] Runs all compiler phases in order'))
print(Colors.success('  [PASS] Handles errors from each phase gracefully'))
print(Colors.success('  [PASS] Provides structured results for UI consumption'))
print(Colors.success('  [PASS] Supports file I/O for command-line use'))
print(Colors.success('  [PASS] Allows optional phases (interpret, codegen)'))
print()
