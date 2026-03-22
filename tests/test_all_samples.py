"""E2E sample tests. See docs/DEVELOPER_NOTES.md"""
from pathlib import Path
from sarana import compile_and_run

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def _run(filename):
    path = SAMPLES_DIR / filename
    assert path.exists(), f"Sample file not found: {path}"
    return compile_and_run(path.read_text(encoding="utf-8"))


class TestSample1RequiredDemo:
    def test_success(self):
        r = _run("sample1.sa")
        assert r.success, r.get_all_errors()

    def test_no_semantic_errors(self):
        assert _run("sample1.sa").semantic_errors == []

    def test_expected_output(self):
        r = _run("sample1.sa")
        assert r.output[0] == "Error: Division by zero attempted but not allowed."
        assert "1620" in r.output[1]


class TestSample2ScopeBinding:
    def test_success(self):
        assert _run("sample2.sa").success

    def test_produces_output(self):
        assert len(_run("sample2.sa").output) >= 2


class TestSample3FunctionsLoops:
    def test_success(self):
        assert _run("sample3.sa").success

    def test_multiply_result(self):
        combined = " ".join(_run("sample3.sa").output)
        assert "42" in combined

    def test_produces_output(self):
        assert len(_run("sample3.sa").output) >= 5


class TestSample4BooleanLogic:
    def test_success(self):
        assert _run("sample4.sa").success

    def test_no_errors(self):
        assert _run("sample4.sa").get_all_errors() == []

    def test_short_circuit_works(self):
        combined = " ".join(_run("sample4.sa").output)
        assert "Short-circuit OR works!" in combined

    def test_grade_a_with_bonus(self):
        combined = " ".join(_run("sample4.sa").output)
        assert "A (with bonus)" in combined
