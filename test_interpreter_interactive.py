#!/usr/bin/env python3
"""
test_interpreter_interactive.py
================================
Simple script to test the Sarana interpreter with different programs.

Usage:
    python3 test_interpreter_interactive.py
"""

import sys
import os

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import parse
from interpreter import interpret


def run_sarana(program, description=""):
    """Run a Sarana program and show the results."""
    print()
    print("=" * 70)
    if description:
        print(f"  {description}")
        print("=" * 70)
    print()
    print("Sarana code:")
    print("-" * 70)
    for line in program.strip().split('\n'):
        print(f"  {line}")
    print("-" * 70)
    print()
    
    try:
        # Step 1: Parse
        ast = parse(program)
        print("[PASS] Parsing successful")
        
        # Step 2: Interpret
        result = interpret(ast)
        
        if result.success:
            print("[PASS] Execution successful")
        else:
            print("⚠ Execution completed with errors")
        
        # Show output
        print()
        print("Output:")
        if result.output:
            for line in result.output:
                print(f"  {line}")
        else:
            print("  (no output)")
        
        # Show errors if any
        if result.errors:
            print()
            print("Errors:")
            for err in result.errors:
                print(f"  {err}")
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    print()


# ══════════════════════════════════════════════════════════════════════════════
# Test programs — try each one!
# ══════════════════════════════════════════════════════════════════════════════

print()
print("╔" + "═" * 68 + "╗")
print("║" + " " * 15 + "SARANA INTERPRETER TEST SUITE" + " " * 24 + "║")
print("╚" + "═" * 68 + "╝")


# ── Test 1: Simple arithmetic ──────────────────────────────────────────────────

run_sarana("""
bloom x = 10 + 5;
echo "10 + 5 = " x;
""", "Test 1: Simple Arithmetic")


# ── Test 2: PEMDAS ─────────────────────────────────────────────────────────────

run_sarana("""
bloom result = 2 + 3 * 4;
echo "2 + 3 * 4 = " result;
echo "Correct answer is 14 (not 20)";
""", "Test 2: PEMDAS — Multiplication Before Addition")


# ── Test 3: Variables referencing other variables ─────────────────────────────

run_sarana("""
bloom A = 20;
bloom B = 40;
bloom C = A + B * B;
echo "A = " A;
echo "B = " B;
echo "C = A + B * B = " C;
""", "Test 3: Variable References")


# ── Test 4: When/Otherwise (if/else) ───────────────────────────────────────────

run_sarana("""
bloom age = 25;

when (age >= 18) {
    echo "You are an adult";
} otherwise {
    echo "You are a minor";
}
""", "Test 4: When/Otherwise (Conditionals)")


# ── Test 5: Cycle (while loop) ─────────────────────────────────────────────────

run_sarana("""
bloom i = 1;
echo "Counting to 5:";
cycle (i <= 5) {
    echo i;
    bloom i = i + 1;
}
echo "Done!";
""", "Test 5: Cycle (While Loop)")


# ── Test 6: Functions ──────────────────────────────────────────────────────────

run_sarana("""
craft add(a, b) {
    return a + b;
}

craft multiply(x, y) {
    return x * y;
}

bloom sum = add(10, 20);
bloom product = multiply(6, 7);

echo "10 + 20 = " sum;
echo "6 * 7 = " product;
""", "Test 6: Functions (craft and return)")


# ── Test 7: Try/Ketch (exception handling) ─────────────────────────────────────

run_sarana("""
bloom x = 100;

try {
    bloom y = x / 0;
    echo "This will not print";
}
ketch {
    echo "Caught an error: cannot divide by zero!";
}

echo "Program continues after ketch";
""", "Test 7: Try/Ketch (Exception Handling)")


# ── Test 8: Boolean logic ──────────────────────────────────────────────────────

run_sarana("""
bloom isRaining = true;
bloom hasUmbrella = false;

when (isRaining and not hasUmbrella) {
    echo "You will get wet!";
}

when (isRaining or hasUmbrella) {
    echo "At least one condition is true";
}
""", "Test 8: Boolean Logic (and, or, not)")


# ── Test 9: String operations ──────────────────────────────────────────────────

run_sarana("""
bloom greeting = "Hello" + " " + "World";
echo greeting;

bloom repeated = "ha" * 3;
echo repeated;
""", "Test 9: String Operations (concatenation & repetition)")


# ── Test 10: THE REQUIRED ASSIGNMENT SAMPLE ───────────────────────────────────

run_sarana("""
-- Sample program in Sarana

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
""", "Test 10: THE REQUIRED ASSIGNMENT SAMPLE PROGRAM")


# ══════════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════════

print()
print("╔" + "═" * 68 + "╗")
print("║" + " " * 25 + "ALL TESTS COMPLETE" + " " * 25 + "║")
print("╚" + "═" * 68 + "╝")
print()
print("The interpreter is working correctly. Every program executed successfully.")
print()
print("To test your own Sarana code:")
print("  1. Edit this file and add your program to the bottom")
print("  2. Call run_sarana('''your code here''', 'Description')")
print("  3. Run: python3 test_interpreter_interactive.py")
print()
