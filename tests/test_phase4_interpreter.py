"""Interpreter tests. See docs/DEVELOPER_NOTES.md"""
from sarana import compile_and_run


def run(src):
    r = compile_and_run(src, generate_target_code=False, run_interpreter=True)
    return r.output, r.success


def output(src):
    lines, _ = run(src)
    return lines


class TestArithmetic:
    def test_addition(self):
        assert output("bloom x = 2 + 3; echo x;") == ["5"]

    def test_subtraction(self):
        assert output("bloom x = 10 - 4; echo x;") == ["6"]

    def test_multiplication(self):
        assert output("bloom x = 3 * 4; echo x;") == ["12"]

    def test_integer_division(self):
        out = output("bloom x = 10 / 4; echo x;")
        assert out == ["2.5"] or out == ["2"]

    def test_modulo(self):
        assert output("bloom x = 10 % 3; echo x;") == ["1"]

    def test_pemdas_mult_first(self):
        src = "bloom A = 20; bloom B = 40; bloom C = A + B * B; echo C;"
        assert output(src) == ["1620"]

    def test_parens_override(self):
        assert output("bloom x = (2 + 3) * 4; echo x;") == ["20"]

    def test_negative_unary(self):
        assert output("bloom x = -5; echo x;") == ["-5"]


class TestVariables:
    def test_declare_and_use(self):
        src = "bloom x = 10; bloom y = x * 2; echo y;"
        assert output(src) == ["20"]

    def test_reassignment(self):
        src = "bloom i = 0; bloom i = i + 1; echo i;"
        assert output(src) == ["1"]


class TestEcho:
    def test_string(self):
        assert output('echo "hello";') == ["hello"]

    def test_multi_expr(self):
        src = 'echo "result: " 42;'
        joined = " ".join(output(src))
        assert "result:" in joined and "42" in joined

    def test_integer(self):
        assert output("echo 99;") == ["99"]


class TestConditionals:
    def test_when_true(self):
        src = 'bloom x = 10; when (x > 5) { echo "big"; }'
        assert output(src) == ["big"]

    def test_when_false(self):
        src = 'bloom x = 1; when (x > 5) { echo "big"; }'
        assert output(src) == []

    def test_otherwise(self):
        src = 'bloom x = 1; when (x > 5) { echo "big"; } otherwise { echo "small"; }'
        assert output(src) == ["small"]

    def test_else_if_chain(self):
        src = (
            "bloom score = 85;\n"
            'when (score >= 90) { echo "A"; }'
            ' otherwise when (score >= 80) { echo "B"; }'
            ' otherwise { echo "C"; }'
        )
        assert output(src) == ["B"]


class TestCycles:
    def test_basic_loop(self):
        src = "bloom i = 0; cycle (i < 3) { echo i; bloom i = i + 1; }"
        assert output(src) == ["0", "1", "2"]

    def test_loop_not_entered(self):
        src = "bloom i = 5; cycle (i < 3) { echo i; bloom i = i + 1; }"
        assert output(src) == []


class TestFunctions:
    def test_no_params(self):
        src = 'craft greet() { echo "hi"; } greet();'
        assert output(src) == ["hi"]

    def test_with_params(self):
        src = "craft add(a, b) { return a + b; } bloom r = add(3, 4); echo r;"
        assert output(src) == ["7"]

    def test_recursive_countdown(self):
        src = (
            "craft countdown(n) {\n"
            "    cycle (n > 0) { echo n; bloom n = n - 1; }\n"
            "}\n"
            "countdown(3);\n"
        )
        assert output(src) == ["3", "2", "1"]

    def test_function_scope(self):
        src = (
            "bloom outer = 99;\n"
            "craft f() { bloom inner = 1; return inner; }\n"
            "bloom r = f();\n"
            "echo outer;\n"
        )
        assert output(src) == ["99"]


class TestTryKetch:
    def test_ketch_triggered(self):
        src = 'try { bloom d = 1 / 0; } ketch { echo "caught"; }'
        assert output(src) == ["caught"]

    def test_ketch_not_triggered(self):
        src = 'try { bloom x = 5; } ketch { echo "caught"; }'
        assert output(src) == []

    def test_required_sample(self):
        src = (
            "bloom A = 20;\n"
            "bloom B = 40;\n"
            "bloom C = A + B * B;\n"
            "try {\n"
            "    bloom D = C / 0;\n"
            "}\n"
            "ketch {\n"
            '    echo "Error: Division by zero attempted but not allowed.";\n'
            "}\n"
            'echo "The result is " C;\n'
        )
        out = output(src)
        assert out[0] == "Error: Division by zero attempted but not allowed."
        assert "1620" in out[1]


class TestBooleans:
    def test_and_true(self):
        assert output('when (true and true) { echo "yes"; }') == ["yes"]

    def test_and_false(self):
        assert output('when (true and false) { echo "yes"; }') == []

    def test_or(self):
        assert output('when (false or true) { echo "yes"; }') == ["yes"]

    def test_not(self):
        assert output('when (not false) { echo "yes"; }') == ["yes"]

    def test_short_circuit_or(self):
        src = 'bloom x = 10; when (x > 5 or x / 0 > 1) { echo "ok"; }'
        out, success = run(src)
        assert "ok" in out
        assert success
