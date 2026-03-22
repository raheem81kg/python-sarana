"""Codegen tests. See docs/DEVELOPER_NOTES.md"""
import io
import sys
from sarana import compile_and_run


def gen(src):
    r = compile_and_run(src, generate_target_code=True, run_interpreter=False)
    assert r.generated_code, f"No code generated. Errors: {r.get_all_errors()}"
    return r.generated_code


def exec_output(python_code):
    buf = io.StringIO()
    old_out = sys.stdout
    sys.stdout = buf
    try:
        exec(python_code, {})  # noqa: S102
    finally:
        sys.stdout = old_out
    return [line for line in buf.getvalue().splitlines() if line]


def run_and_compare(src):
    r_interp = compile_and_run(src, generate_target_code=False, run_interpreter=True)
    r_gen = compile_and_run(src, generate_target_code=True, run_interpreter=False)
    gen_out = exec_output(r_gen.generated_code)
    return r_interp.output, gen_out


class TestTranslation:
    def test_bloom_to_assignment(self):
        assert "x = 5" in gen("bloom x = 5;")

    def test_echo_to_print(self):
        assert "print(" in gen('echo "hello";')

    def test_when_to_if(self):
        assert "if " in gen("bloom x = 1; when (x > 0) { echo x; }")

    def test_otherwise_to_else(self):
        code = gen("bloom x = 1; when (x > 0) { echo x; } otherwise { echo 0; }")
        assert "else:" in code

    def test_cycle_to_while(self):
        assert "while " in gen("bloom i = 0; cycle (i < 3) { bloom i = i + 1; }")

    def test_craft_to_def(self):
        assert "def add(a, b):" in gen("craft add(a, b) { return a + b; }")

    def test_try_ketch_to_try_except(self):
        code = gen("try { echo 1; } ketch { echo 0; }")
        assert "try:" in code and "except" in code

    def test_true_false_mapped(self):
        code = gen("bloom t = true; bloom f = false;")
        assert "True" in code and "False" in code


class TestGeneratedOutputMatches:
    def test_arithmetic(self):
        interp, gen_out = run_and_compare("bloom x = 2 + 3; echo x;")
        assert interp == gen_out

    def test_pemdas(self):
        src = "bloom A = 20; bloom B = 40; bloom C = A + B * B; echo C;"
        interp, gen_out = run_and_compare(src)
        assert interp == gen_out

    def test_function_call(self):
        src = "craft add(a, b) { return a + b; } bloom r = add(3, 4); echo r;"
        interp, gen_out = run_and_compare(src)
        assert interp == gen_out

    def test_loop(self):
        src = "bloom i = 0; cycle (i < 3) { echo i; bloom i = i + 1; }"
        interp, gen_out = run_and_compare(src)
        assert interp == gen_out


class TestRequiredSample:
    SAMPLE = (
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

    def test_generates_code(self):
        r = compile_and_run(self.SAMPLE, generate_target_code=True)
        assert r.generated_code

    def test_generated_matches_interpreter(self):
        interp, gen_out = run_and_compare(self.SAMPLE)
        assert interp == gen_out

    def test_expected_output(self):
        r = compile_and_run(self.SAMPLE)
        assert r.output[0] == "Error: Division by zero attempted but not allowed."
        assert "1620" in r.output[1]
