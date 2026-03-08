try:
    import ply.yacc as ply_yacc
except ImportError as exc:
    raise ImportError("PLY is required. Install dependencies from requirements.txt.") from exc

from ast import *
from errors import *
import lexer

class ParserState(object):
    def __init__(self):
        self.variables = {}

tokens = lexer.tokens

precedence = (
    ("left", "FUNCTION"),
    ("left", "LET"),
    ("left", "ASSIGN"),
    ("left", "LBRACKET", "RBRACKET", "COMMA"),
    ("left", "IF", "TRY", "CATCH", "COLON", "ELSE", "END", "NEWLINE", "WHILE"),
    ("left", "AND", "OR"),
    ("left", "NOT"),
    ("left", "EQ", "NE", "GTE", "GT", "LT", "LTE"),
    ("left", "PLUS", "MINUS"),
    ("left", "MUL", "DIV"),
)

def p_main_program(p):
    "main : program"
    p[0] = p[1]

def p_program_statement(p):
    "program : statement_full"
    p[0] = Program(p[1])

def p_program_statement_program(p):
    "program : statement_full program"
    program = p[2]
    program.add_statement(p[1])
    p[0] = program

def p_block_expr(p):
    "block : statement_full"
    p[0] = Block(p[1])

def p_block_expr_block(p):
    "block : statement_full block"
    block = p[2]
    block.add_statement(p[1])
    p[0] = block

def p_statement_full_newline(p):
    "statement_full : statement NEWLINE"
    p[0] = p[1]

def p_statement_full_end(p):
    "statement_full : statement"
    p[0] = p[1]

def p_statement_expr(p):
    "statement : expression"
    p[0] = p[1]

def p_statement_assignment(p):
    "statement : LET IDENTIFIER ASSIGN expression"
    p[0] = Assignment(Variable(p[2]), p[4])

def p_statement_func(p):
    "statement : FUNCTION IDENTIFIER LPAREN arglist RPAREN COLON NEWLINE block END"
    p[0] = FunctionDeclaration(p[2], Array(p[4]), p[8])

def p_statement_func_noargs(p):
    "statement : FUNCTION IDENTIFIER LPAREN RPAREN COLON NEWLINE block END"
    p[0] = FunctionDeclaration(p[2], Null(), p[7])

def p_const_float(p):
    "const : FLOAT"
    p[0] = Float(float(p[1]))

def p_const_boolean(p):
    "const : BOOLEAN"
    p[0] = Boolean(True if p[1] == "true" else False)

def p_const_integer(p):
    "const : INTEGER"
    p[0] = Integer(int(p[1]))

def p_const_string(p):
    "const : STRING"
    p[0] = String(_parse_string_literal(p[1]))

def p_expression_const(p):
    "expression : const"
    p[0] = p[1]

def p_expression_array_single(p):
    "expression : LBRACKET expression RBRACKET"
    p[0] = Array(InnerArray([p[2]]))

def p_expression_array(p):
    "expression : LBRACKET expressionlist RBRACKET"
    p[0] = Array(p[2])

def p_expressionlist_single(p):
    "expressionlist : expression"
    p[0] = InnerArray([p[1]])

def p_expressionlist_trailing(p):
    "expressionlist : expression COMMA"
    p[0] = InnerArray([p[1]])

def p_expressionlist_many(p):
    "expressionlist : expression COMMA expressionlist"
    p[3].push(p[1])
    p[0] = p[3]

def p_arglist_single(p):
    "arglist : IDENTIFIER"
    p[0] = InnerArray([Variable(p[1])])

def p_arglist_trailing(p):
    "arglist : IDENTIFIER COMMA"
    p[0] = InnerArray([Variable(p[1])])

def p_arglist_many(p):
    "arglist : IDENTIFIER COMMA arglist"
    p[3].push(Variable(p[1]))
    p[0] = p[3]

def p_maplist_single(p):
    "maplist : expression COLON expression"
    p[0] = InnerDict({p[1]: p[3]})

def p_maplist_trailing(p):
    "maplist : expression COLON expression COMMA"
    p[0] = InnerDict({p[1]: p[3]})

def p_maplist_many(p):
    "maplist : expression COLON expression COMMA maplist"
    p[5].update(p[1], p[3])
    p[0] = p[5]

def p_expression_dict(p):
    "expression : LBRACE maplist RBRACE"
    p[0] = Dict(p[2])

def p_expression_array_index(p):
    "expression : expression LBRACKET expression RBRACKET"
    p[0] = Index(p[1], p[3])

def p_expression_if_single_line(p):
    "expression : IF expression COLON statement END"
    p[0] = If(condition=p[2], body=p[4])

def p_expression_if_else_single_line(p):
    "expression : IF expression COLON statement ELSE COLON statement END"
    p[0] = If(condition=p[2], body=p[4], else_body=p[7])

def p_expression_if(p):
    "expression : IF expression COLON NEWLINE block END"
    p[0] = If(condition=p[2], body=p[5])

def p_expression_if_else(p):
    "expression : IF expression COLON NEWLINE block ELSE COLON NEWLINE block END"
    p[0] = If(condition=p[2], body=p[5], else_body=p[9])

def p_expression_trycatch_single_line(p):
    "expression : TRY COLON statement CATCH COLON statement END"
    p[0] = TryCatch(p[3], p[6])

def p_expression_trycatch_plain(p):
    "expression : TRY NEWLINE block CATCH NEWLINE block END"
    p[0] = TryCatch(p[3], p[6])

def p_expression_trycatch(p):
    "expression : TRY COLON NEWLINE block CATCH COLON NEWLINE block END"
    p[0] = TryCatch(p[4], p[8])

def p_expression_while(p):
    "expression : WHILE expression COLON NEWLINE block END"
    p[0] = While(condition=p[2], body=p[5])

def p_expression_variable(p):
    "expression : IDENTIFIER"
    p[0] = Variable(p[1])

def p_expression_call_noargs(p):
    "expression : IDENTIFIER LPAREN RPAREN"
    p[0] = Call(p[1], InnerArray())

def p_expression_call_args(p):
    "expression : IDENTIFIER LPAREN expressionlist RPAREN"
    p[0] = Call(p[1], p[3])

def p_expression_not(p):
    "expression : NOT expression"
    p[0] = Not(p[2])

def p_expression_parens(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_plus(p):
    "expression : expression PLUS expression"
    p[0] = Add(p[1], p[3])

def p_expression_minus(p):
    "expression : expression MINUS expression"
    p[0] = Sub(p[1], p[3])

def p_expression_mul(p):
    "expression : expression MUL expression"
    p[0] = Mul(p[1], p[3])

def p_expression_div(p):
    "expression : expression DIV expression"
    p[0] = Div(p[1], p[3])

def p_expression_ne(p):
    "expression : expression NE expression"
    p[0] = NotEqual(p[1], p[3])

def p_expression_eq(p):
    "expression : expression EQ expression"
    p[0] = Equal(p[1], p[3])

def p_expression_gte(p):
    "expression : expression GTE expression"
    p[0] = GreaterThanEqual(p[1], p[3])

def p_expression_lte(p):
    "expression : expression LTE expression"
    p[0] = LessThanEqual(p[1], p[3])

def p_expression_gt(p):
    "expression : expression GT expression"
    p[0] = GreaterThan(p[1], p[3])

def p_expression_lt(p):
    "expression : expression LT expression"
    p[0] = LessThan(p[1], p[3])

def p_expression_and(p):
    "expression : expression AND expression"
    p[0] = And(p[1], p[3])

def p_expression_or(p):
    "expression : expression OR expression"
    p[0] = Or(p[1], p[3])

def p_error(token):
    if token is None:
        raise UnexpectedEndError()
    raise UnexpectedTokenError(lexer.DISPLAY_TOKEN_TYPES.get(token.type, token.type))

def _parse_string_literal(raw_value):
    if raw_value.startswith('"""') and raw_value.endswith('"""'):
        return raw_value[3:-3]
    if raw_value.startswith('"') and raw_value.endswith('"'):
        return raw_value[1:-1]
    if raw_value.startswith("'") and raw_value.endswith("'"):
        return raw_value[1:-1]
    return raw_value

state = ParserState()
parser = ply_yacc.yacc(
    module=__import__(__name__),
    start="main",
    write_tables=False,
    debug=False,
    errorlog=ply_yacc.NullLogger(),
)

def parse(code, state=state):
    del state
    return parser.parse(code, lexer=lexer.build_lexer())
