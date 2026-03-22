"""Lexer tests. See docs/DEVELOPER_NOTES.md"""
import pytest
from lexer import tokenize
from errors import LexError


def tok_types(src):
    return [t.token_type for t in tokenize(src)]

def tok_values(src):
    return [t.value for t in tokenize(src)]


class TestKeywords:
    def test_bloom(self):
        assert "BLOOM" in tok_types("bloom x = 5;")

    def test_echo(self):
        assert "ECHO" in tok_types("echo x;")

    def test_when_otherwise(self):
        types = tok_types("when (a) { } otherwise { }")
        assert "WHEN" in types
        assert "OTHERWISE" in types

    def test_cycle(self):
        assert "CYCLE" in tok_types("cycle (i < 3) { }")

    def test_craft_return(self):
        types = tok_types("craft f() { return 1; }")
        assert "CRAFT" in types
        assert "RETURN" in types

    def test_try_ketch(self):
        types = tok_types("try { } ketch { }")
        assert "TRY" in types
        assert "KETCH" in types

    def test_booleans(self):
        types = tok_types("true false")
        assert "TRUE" in types
        assert "FALSE" in types

    def test_boolean_ops(self):
        types = tok_types("a and b or not c")
        assert "AND" in types
        assert "OR" in types
        assert "NOT" in types


class TestLiterals:
    def test_integer(self):
        toks = tokenize("42")
        assert toks[0].token_type == "INTEGER"
        assert toks[0].value == 42

    def test_float(self):
        toks = tokenize("3.14")
        assert toks[0].token_type == "FLOAT"
        assert abs(toks[0].value - 3.14) < 1e-9

    def test_string_double_quote(self):
        toks = tokenize('"hello"')
        assert toks[0].token_type == "STRING"
        assert toks[0].value == "hello"

    def test_string_single_quote(self):
        toks = tokenize("'world'")
        assert toks[0].token_type == "STRING"
        assert toks[0].value == "world"

    def test_identifier(self):
        toks = tokenize("myVar")
        assert toks[0].token_type == "IDENTIFIER"
        assert toks[0].value == "myVar"


class TestOperators:
    def test_arithmetic(self):
        src = "a + b - c * d / e % f"
        types = tok_types(src)
        for expected in ("PLUS", "MINUS", "MULTIPLY", "DIVIDE", "MODULO"):
            assert expected in types

    def test_comparison(self):
        src = "a == b != c < d > e <= f >= g"
        types = tok_types(src)
        for expected in (
            "DOUBLE_EQUALS", "NOT_EQUALS", "LESS_THAN", "GREATER_THAN",
            "LESS_EQUAL", "GREATER_EQUAL",
        ):
            assert expected in types

    def test_assign(self):
        assert "ASSIGN" in tok_types("x = 5")

    def test_delimiters(self):
        src = "( ) { } [ ] ; ,"
        types = tok_types(src)
        for expected in (
            "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET",
            "SEMICOLON", "COMMA",
        ):
            assert expected in types


class TestComments:
    def test_comment_ignored(self):
        types = tok_types("-- this is a comment\nbloom x = 1;")
        assert "COMMENT" not in types
        assert "BLOOM" in types

    def test_inline_comment(self):
        toks = tokenize("bloom x = 5; -- declare x")
        assert all(t.token_type != "COMMENT" for t in toks)


class TestLineNumbers:
    def test_line_numbers(self):
        src = "bloom a = 1;\nbloom b = 2;\n"
        toks = tokenize(src)
        bloom_lines = [t.line for t in toks if t.token_type == "BLOOM"]
        assert bloom_lines == [1, 2]


class TestLexErrors:
    def test_invalid_char(self):
        with pytest.raises(LexError):
            tokenize("bloom x = @;")

    def test_unclosed_string(self):
        with pytest.raises(Exception):
            tokenize('"unclosed')


class TestRequiredSample:
    def test_sample1_tokenizes(self):
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
        toks = tokenize(src)
        assert len(toks) > 0
        keywords = {t.token_type for t in toks}
        for kw in ("BLOOM", "TRY", "KETCH", "ECHO"):
            assert kw in keywords, f"Expected keyword {kw}"
