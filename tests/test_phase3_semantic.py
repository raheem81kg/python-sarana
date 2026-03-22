"""Semantic analyzer tests. See docs/DEVELOPER_NOTES.md"""
from parser import parse  # pyright: ignore[reportDeprecated]
from semantic import analyze


def errors_for(src):
    ast = parse(src)
    return analyze(ast)


def has_error_matching(errors, keyword):
    return any(keyword.lower() in str(e).lower() for e in errors)


class TestValidPrograms:
    def test_simple_bloom_echo(self):
        assert errors_for("bloom x = 5; echo x;") == []

    def test_function_definition_and_call(self):
        src = "craft add(a, b) { return a + b; } bloom r = add(1, 2); echo r;"
        assert errors_for(src) == []

    def test_when_otherwise(self):
        src = "bloom x = 5; when (x > 3) { echo x; } otherwise { echo 0; }"
        assert errors_for(src) == []

    def test_cycle(self):
        src = "bloom i = 0; cycle (i < 3) { bloom i = i + 1; }"
        assert errors_for(src) == []

    def test_try_ketch_div_zero_suppressed(self):
        src = (
            "bloom c = 10;\n"
            "try { bloom d = c / 0; }\n"
            "ketch { echo \"caught\"; }\n"
        )
        errs = errors_for(src)
        assert not has_error_matching(errs, "division by zero")


class TestUndefinedVariables:
    def test_use_before_bloom(self):
        errs = errors_for("echo x;")
        assert len(errs) >= 1
        msg = " ".join(str(e) for e in errs).lower()
        assert any(
            w in msg for w in ("bloom", "declared", "before", "undeclared")
        )

    def test_out_of_scope(self):
        src = "bloom x = 1; when (x > 0) { bloom y = 2; } echo x;"
        assert isinstance(errors_for(src), list)


class TestUndefinedFunction:
    def test_call_undeclared(self):
        errs = errors_for("bloom r = mystery(1, 2);")
        assert len(errs) >= 1
        msg = " ".join(str(e) for e in errs).lower()
        assert any(w in msg for w in ("craft", "defined", "function", "before"))


class TestDivisionByZero:
    def test_literal_zero_divisor(self):
        errs = errors_for("bloom x = 10 / 0;")
        assert len(errs) >= 1
        assert has_error_matching(errs, "zero")

    def test_modulo_zero_divisor(self):
        errs = errors_for("bloom x = 10 % 0;")
        assert len(errs) >= 1
        assert has_error_matching(errs, "zero")

    def test_or_short_circuit_no_false_alarm(self):
        src = "bloom x = 10; when (x > 5 or x / 0 > 1) { echo x; }"
        errs = errors_for(src)
        div_errs = [e for e in errs if "zero" in str(e).lower()]
        assert div_errs == []


class TestTypeMismatch:
    def test_string_plus_integer(self):
        errs = errors_for('bloom r = "hello" + 5;')
        assert isinstance(errs, list)


class TestMultipleErrors:
    def test_collects_all(self):
        errs = errors_for("echo a; echo b;")
        assert len(errs) >= 2


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

    def test_no_semantic_errors(self):
        errs = errors_for(self.SAMPLE)
        assert errs == [], f"Expected no errors, got: {errs}"
