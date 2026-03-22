"""Parser tests. See docs/DEVELOPER_NOTES.md"""
import pytest
from parser import parse  # pyright: ignore[reportDeprecated]
from ast_nodes import (
    Program, BloomStatement, EchoStatement, WhenStatement,
    CycleStatement, CraftStatement, ReturnStatement,
    TryKetchStatement, BinaryOp, Integer, Float, String,
    Boolean,
)
from errors import ParseError


def first_stmt(src):
    ast = parse(src)
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 1
    return ast.statements[0]


class TestBloom:
    def test_integer_value(self):
        stmt = first_stmt("bloom x = 42;")
        assert isinstance(stmt, BloomStatement)
        assert stmt.name == "x"
        assert isinstance(stmt.value, Integer)
        assert stmt.value.value == 42

    def test_float_value(self):
        stmt = first_stmt("bloom pi = 3.14;")
        assert isinstance(stmt.value, Float)

    def test_string_value(self):
        stmt = first_stmt('bloom s = "hello";')
        assert isinstance(stmt.value, String)

    def test_expression_value(self):
        stmt = first_stmt("bloom z = x + 1;")
        assert isinstance(stmt.value, BinaryOp)


class TestPrecedence:
    def test_mult_before_add(self):
        stmt = first_stmt("bloom c = a + b * b;")
        top = stmt.value
        assert isinstance(top, BinaryOp)
        assert top.operator == "+"
        assert isinstance(top.right, BinaryOp)
        assert top.right.operator == "*"

    def test_parens_override(self):
        stmt = first_stmt("bloom c = (a + b) * b;")
        top = stmt.value
        assert isinstance(top, BinaryOp)
        assert top.operator == "*"
        assert isinstance(top.left, BinaryOp)
        assert top.left.operator == "+"


class TestEcho:
    def test_echo_string(self):
        stmt = first_stmt('echo "hi";')
        assert isinstance(stmt, EchoStatement)
        assert len(stmt.expressions) == 1

    def test_echo_multi_expr(self):
        stmt = first_stmt('echo "result is " x;')
        assert isinstance(stmt, EchoStatement)
        assert len(stmt.expressions) == 2


class TestWhen:
    def test_when_only(self):
        stmt = first_stmt("when (x > 0) { echo x; }")
        assert isinstance(stmt, WhenStatement)
        assert stmt.otherwise_body == []

    def test_when_otherwise(self):
        stmt = first_stmt("when (x > 0) { echo x; } otherwise { echo 0; }")
        assert isinstance(stmt, WhenStatement)
        assert len(stmt.otherwise_body) >= 1

    def test_else_if_chain(self):
        src = (
            "when (x > 10) { echo x; }"
            " otherwise when (x > 5) { echo x; }"
            " otherwise { echo 0; }"
        )
        stmt = first_stmt(src)
        assert isinstance(stmt, WhenStatement)
        assert isinstance(stmt.otherwise_body[0], WhenStatement)


class TestCycle:
    def test_cycle(self):
        stmt = first_stmt("cycle (i < 3) { echo i; }")
        assert isinstance(stmt, CycleStatement)
        assert isinstance(stmt.condition, BinaryOp)
        assert stmt.condition.operator == "<"


class TestCraft:
    def test_no_params(self):
        stmt = first_stmt("craft greet() { echo 1; }")
        assert isinstance(stmt, CraftStatement)
        assert stmt.name == "greet"
        assert stmt.params == []

    def test_with_params(self):
        stmt = first_stmt("craft add(a, b) { return a + b; }")
        assert isinstance(stmt, CraftStatement)
        assert stmt.params == ["a", "b"]

    def test_return(self):
        ast = parse("craft f() { return 42; }")
        ret = ast.statements[0].body[0]
        assert isinstance(ret, ReturnStatement)
        assert isinstance(ret.value, Integer)


class TestTryKetch:
    def test_try_ketch(self):
        stmt = first_stmt("try { echo 1; } ketch { echo 0; }")
        assert isinstance(stmt, TryKetchStatement)
        assert len(stmt.try_body) >= 1
        assert len(stmt.ketch_body) >= 1


class TestBooleans:
    def test_true_false(self):
        stmt = first_stmt("bloom f = true;")
        assert isinstance(stmt.value, Boolean)
        assert stmt.value.value is True

    def test_not(self):
        stmt = first_stmt("bloom f = not true;")
        from ast_nodes import UnaryOp
        assert isinstance(stmt.value, UnaryOp)
        assert stmt.value.operator == "not"


class TestParseErrors:
    def test_missing_semicolon(self):
        with pytest.raises(Exception):
            parse("bloom x = 5")

    def test_missing_identifier(self):
        with pytest.raises(ParseError):
            parse("bloom = 5;")


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

    def test_parses_to_program(self):
        ast = parse(self.SAMPLE)
        assert isinstance(ast, Program)
        assert len(ast.statements) == 5

    def test_c_pemdas(self):
        bloom_c = parse(self.SAMPLE).statements[2]
        assert isinstance(bloom_c.value, BinaryOp)
        assert bloom_c.value.operator == "+"
        assert bloom_c.value.right.operator == "*"
