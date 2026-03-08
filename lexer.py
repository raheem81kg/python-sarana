import re

try:
    import ply.lex as ply_lex
    from ply.lex import TOKEN
except ImportError as exc:
    raise ImportError("PLY is required. Install dependencies from requirements.txt.") from exc


class SourcePos(object):
    def __init__(self, idx, lineno, colno):
        self.idx = idx
        self.lineno = lineno
        self.colno = colno


class Token(object):
    def __init__(self, token_type, value, source_pos=None):
        self.token_type = token_type
        self.value = value
        self.source_pos = source_pos

    def gettokentype(self):
        return self.token_type

    def getstr(self):
        return self.value

    def getsourcepos(self):
        return self.source_pos

    def __repr__(self):
        return "Token(%r, %r)" % (self.token_type, self.value)


reserved = {
    "true": "BOOLEAN",
    "false": "BOOLEAN",
    "if": "IF",
    "else": "ELSE",
    "try": "TRY",
    "catch": "CATCH",
    "end": "END",
    "display": "DISPLAY",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "let": "LET",
    "for": "FOR",
    "while": "WHILE",
    "break": "BREAK",
    "continue": "CONTINUE",
    "match": "MATCH",
    "enum": "ENUM",
    "new": "NEW",
    "return": "RETURN",
    "type": "TYPE",
    "array": "TYPE_ARRAY",
    "dict": "TYPE_DICT",
    "int": "TYPE_INTEGER",
    "str": "TYPE_STRING",
    "float": "TYPE_FLOAT",
    "char": "TYPE_CHAR",
    "long": "TYPE_LONG",
    "double": "TYPE_DOUBLE",
    "record": "RECORD",
    "func": "FUNCTION",
    "fn": "LAMBDA",
    "priv": "PRIVATE",
    "mod": "MODULE",
    "trait": "TRAIT",
    "impl": "IMPLEMENT",
    "import": "IMPORT",
    "send": "SEND",
    "receive": "RECEIVE",
}


tokens = (
    "STRING",
    "INTEGER",
    "FLOAT",
    "IDENTIFIER",
    "BOOLEAN",
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "MOD",
    "DOT",
    "PIPE",
    "IF",
    "ELSE",
    "TRY",
    "CATCH",
    "DISPLAY",
    "COLON",
    "END",
    "AND",
    "OR",
    "NOT",
    "LET",
    "FOR",
    "WHILE",
    "BREAK",
    "CONTINUE",
    "MATCH",
    "ENUM",
    "NEW",
    "RETURN",
    "TYPE",
    "TYPE_ARRAY",
    "TYPE_DICT",
    "TYPE_INTEGER",
    "TYPE_STRING",
    "TYPE_FLOAT",
    "TYPE_CHAR",
    "TYPE_LONG",
    "TYPE_DOUBLE",
    "RECORD",
    "FUNCTION",
    "LAMBDA",
    "PRIVATE",
    "MODULE",
    "TRAIT",
    "IMPLEMENT",
    "IMPORT",
    "SEND",
    "RECEIVE",
    "LPAREN",
    "RPAREN",
    "ASSIGN",
    "EQ",
    "NE",
    "GTE",
    "LTE",
    "LT",
    "GT",
    "LBRACKET",
    "RBRACKET",
    "COMMA",
    "LBRACE",
    "RBRACE",
    "NEWLINE",
)


DISPLAY_TOKEN_TYPES = {
    "ASSIGN": "=",
    "EQ": "==",
    "NE": "!=",
    "GTE": ">=",
    "LTE": "<=",
    "GT": ">",
    "LT": "<",
    "LPAREN": "(",
    "RPAREN": ")",
    "LBRACKET": "[",
    "RBRACKET": "]",
    "LBRACE": "{",
    "RBRACE": "}",
    "COMMA": ",",
    "PIPE": "|",
    "DOT": ".",
    "MOD": "%",
}


t_PLUS = r"\+"
t_MINUS = r"-"
t_MUL = r"\*"
t_DIV = r"/"
t_MOD = r"%"
t_EQ = r"=="
t_NE = r"!="
t_GTE = r">="
t_LTE = r"<="
t_GT = r">"
t_LT = r"<"
t_ASSIGN = r"="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r"," 
t_PIPE = r"\|"
t_DOT = r"\."
t_COLON = r":"
t_ignore = " \t\r\f\v"

string_literal = r'("""(.|\n)*?""")|("[^"\n]*")|(\'[^\'\n]*\')'
identifier = r"[a-zA-Z_][a-zA-Z0-9_]*"


@TOKEN(string_literal)
def t_STRING(token):
    return token


def t_FLOAT(token):
    r"-?\d+\.\d+"
    return token


def t_INTEGER(token):
    r"-?\d+"
    return token


@TOKEN(identifier)
def t_IDENTIFIER(token):
    token.type = reserved.get(token.value, "IDENTIFIER")
    return token


def t_COMMENT(token):
    r"\#.*"
    pass


def t_NEWLINE(token):
    r"\n+"
    token.lexer.lineno += len(token.value)
    return token


def _find_column(source, lexpos):
    line_start = source.rfind("\n", 0, lexpos) + 1
    return (lexpos - line_start) + 1


def t_error(token):
    column = _find_column(token.lexer.lexdata, token.lexpos)
    raise SyntaxError("Unexpected character %r at line %s, column %s" % (token.value[0], token.lineno, column))


def build_lexer():
    return ply_lex.lex(module=__import__(__name__), reflags=re.DOTALL)


def _wrap_token(lexer, token):
    token_type = DISPLAY_TOKEN_TYPES.get(token.type, token.type)
    column = _find_column(lexer.lexdata, token.lexpos)
    return Token(token_type, token.value, SourcePos(token.lexpos, token.lineno, column))


def lex(source):
    lexer = build_lexer()
    lexer.input(source)
    result = []
    for token in lexer:
        result.append(_wrap_token(lexer, token))

    end_line = lexer.lineno
    end_col = _find_column(source, len(source)) if source else 1
    result.append(Token("$end", "$end", SourcePos(len(source), end_line, end_col)))
    return result
