# src/parser.py
# Sarana Language Parser — Phase 2 of the compiler pipeline.
#
# The parser takes the flat list of tokens from the lexer and builds an
# Abstract Syntax Tree (AST).  It does two things simultaneously:
#   1. Validates that the token sequence follows Sarana's grammar rules
#   2. Builds the AST node tree that all later phases will work with
#
# Tool used: PLY (Python Lex-Yacc) yacc module — an LALR(1) parser generator.
# We write "production rules" as Python functions (p_* below), and PLY
# automatically builds the state machine that recognises the grammar.
#
# LALR(1) = Left-to-right scan, builds Leftmost derivation, 1 token lookahead.
# This handles all of Sarana's grammar without any ambiguity.
#
# Key concept — operator precedence (PEMDAS):
# The 'precedence' tuple below tells PLY which operators bind tighter.
# Higher position in the tuple = HIGHER precedence = evaluated FIRST.
# This is how A + B * B correctly becomes A + (B * B), not (A + B) * B.
#
# Public entry point:
#   parse(source_code: str) -> Program

import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

try:
    import ply.yacc as ply_yacc
except ImportError as exc:
    raise ImportError(
        "PLY is required. Run: pip install -r requirements.txt"
    ) from exc

from lexer import tokenize
import lexer as _lexer

tokens = _lexer.tokens
from ast_nodes import (
    Program, BloomStatement, EchoStatement, TryKetchStatement,
    WhenStatement, CycleStatement, CraftStatement, ReturnStatement,
    ExpressionStatement, BinaryOp, UnaryOp, Variable, FunctionCall,
    Integer, Float, String, Boolean, Array,
)
from errors import ParseError, UnexpectedEndError


# ===========================================================================
# Token stream bridge
# ===========================================================================
# PLY's yacc expects a lexer-like object with a token() method.
# Our tokenize() already gives us a clean list of Token objects.
# _TokenStream wraps that list so PLY's yacc can consume it.
# This lets us use our lexer's correct line numbers inside parser rules.

class _PLYToken:
    """A minimal PLY-compatible token object.
    Note: __slots__ is intentionally NOT used here — PLY's error handler
    dynamically sets a 'lexer' attribute on error tokens at runtime.
    """

    def __init__(self, tok):
        self.type    = tok.token_type   # e.g. 'BLOOM', 'INTEGER'
        self.value   = tok.value        # e.g. 'bloom', 42
        self.lineno  = tok.line         # line number from our tokenizer
        self.lexpos  = 0                # character position (not used here)


class _TokenStream:
    """
    Adapts our Token list to the interface PLY's yacc expects.

    PLY calls:
      stream.input(source)  — we ignore this (tokens already prepared)
      stream.token()        — we return the next token, or None at end
    """

    def __init__(self, token_list):
        self._tokens = iter(token_list)

    def input(self, s):
        pass   # no-op: tokens are already in self._tokens

    def token(self):
        """Return next PLY-compatible token, or None at end of input."""
        try:
            return _PLYToken(next(self._tokens))
        except StopIteration:
            return None   # PLY treats None as end of input


# ===========================================================================
# Operator precedence table  (PEMDAS + boolean logic)
# ===========================================================================
# Listed from LOWEST precedence (top) to HIGHEST precedence (bottom).
# PLY uses this to resolve shift/reduce conflicts automatically.
#
# Example: A + B * B
#   After reading A + B, lookahead is *.
#   * has higher precedence than + → PLY SHIFTS * → builds B*B first → correct.
#
# 'left'     = left-associative:  5 - 3 - 1 = (5 - 3) - 1 = 1  (not 5 - (3-1) = 3)
# 'right'    = right-associative: not not x = not (not x)
# 'nonassoc' = cannot be chained: a < b < c is a syntax error

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    (
        'nonassoc',
        'DOUBLE_EQUALS',
        'NOT_EQUALS',
        'LESS_THAN',
        'GREATER_THAN',
        'LESS_EQUAL',
        'GREATER_EQUAL',
    ),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS'),
)

# PLY requires the start symbol to be declared.
start = 'program'


# ===========================================================================
# Grammar rule:  program
# ===========================================================================
# A Sarana program is a list of zero or more statements.

def p_program(p):
    'program : statement_list'
    p[0] = Program(p[1])


# ===========================================================================
# Grammar rule:  statement_list
# ===========================================================================
# A list of statements.  Can be empty (e.g. inside an empty block {}).
# This is a standard left-recursive list rule — PLY handles left recursion
# efficiently (right recursion would use excessive memory).

def p_statement_list_empty(p):
    'statement_list : '
    p[0] = []   # empty list — no statements

def p_statement_list(p):
    'statement_list : statement_list statement'
    # Append each new statement to the list as we parse left-to-right
    p[0] = p[1] + [p[2]]


# ===========================================================================
# Grammar rules:  statements
# ===========================================================================
# Each statement type in Sarana has its own rule.

def p_statement_bloom(p):
    'statement : BLOOM IDENTIFIER ASSIGN expression SEMICOLON'
    # bloom x = 5;
    # p[1]=bloom  p[2]=x  p[3]==  p[4]=<expression node>  p[5]=;
    p[0] = BloomStatement(name=p[2], value=p[4], line=p.lineno(1))

def p_statement_echo(p):
    'statement : ECHO echo_exprs SEMICOLON'
    # echo "Hello" x;   or   echo result;
    # echo_exprs is a list of one or more expression nodes
    p[0] = EchoStatement(expressions=p[2], line=p.lineno(1))

def p_statement_try_ketch(p):
    'statement : TRY block KETCH block'
    # try { ... } ketch { ... }
    # block produces a list of statements
    p[0] = TryKetchStatement(try_body=p[2], ketch_body=p[4], line=p.lineno(1))

def p_statement_when(p):
    'statement : WHEN LPAREN expression RPAREN block when_else_tail'
    # when (x > 5) { ... }
    # optional: otherwise { ... }  and/or  otherwise when (..) { } chains
    p[0] = WhenStatement(
        condition=p[3],
        then_body=p[5],
        otherwise_body=p[6],
        line=p.lineno(1),
    )


def p_when_else_tail_empty(p):
    'when_else_tail :'
    p[0] = []


def p_when_else_tail_else_block(p):
    'when_else_tail : OTHERWISE block'
    p[0] = p[2]


def p_when_else_tail_else_if_chain(p):
    'when_else_tail : OTHERWISE WHEN LPAREN expression RPAREN block when_else_tail'
    inner = WhenStatement(
        condition=p[4],
        then_body=p[6],
        otherwise_body=p[7],
        line=p.lineno(2),
    )
    p[0] = [inner]

def p_statement_cycle(p):
    'statement : CYCLE LPAREN expression RPAREN block'
    # cycle (i < 3) { ... }
    p[0] = CycleStatement(condition=p[3], body=p[5], line=p.lineno(1))

def p_statement_craft_noparams(p):
    'statement : CRAFT IDENTIFIER LPAREN RPAREN block'
    # craft greet() { ... }
    p[0] = CraftStatement(name=p[2], params=[], body=p[5], line=p.lineno(1))

def p_statement_craft_params(p):
    'statement : CRAFT IDENTIFIER LPAREN param_list RPAREN block'
    # craft add(a, b) { ... }
    p[0] = CraftStatement(name=p[2], params=p[4], body=p[6], line=p.lineno(1))

def p_statement_return(p):
    'statement : RETURN expression SEMICOLON'
    # return a + b;
    p[0] = ReturnStatement(value=p[2], line=p.lineno(1))

def p_statement_expression(p):
    'statement : expression SEMICOLON'
    # Standalone expression used as a statement, most commonly a function call.
    # countdown(3);   or   add(x, y);
    p[0] = ExpressionStatement(expression=p[1], line=p.lineno(1))


# ===========================================================================
# Grammar rule:  block  (a { ... } section)
# ===========================================================================

def p_block(p):
    'block : LBRACE statement_list RBRACE'
    # { statement_list }
    # Returns the list of statements (not a separate Block node — the parent
    # statement stores the list directly in its body attribute).
    p[0] = p[2]


# ===========================================================================
# Grammar rule:  echo_exprs  (one or more expressions after 'echo')
# ===========================================================================
# echo "Hello " name;    ← two expressions printed together
# echo result;           ← one expression
#
# The left-recursive rule 'echo_exprs expression' collects all expressions
# before the semicolon.  PLY defaults to SHIFT on S/R conflicts, which
# correctly groups multi-term expressions (like x+y) as a single expression
# rather than splitting them across two echo_exprs entries.

def p_echo_exprs_single(p):
    'echo_exprs : expression'
    p[0] = [p[1]]

def p_echo_exprs_multi(p):
    'echo_exprs : echo_exprs expression'
    p[0] = p[1] + [p[2]]


# ===========================================================================
# Grammar rule:  param_list  (names in a craft definition)
# ===========================================================================
# craft add(a, b) { ... }  →  param_list = ['a', 'b']

def p_param_list_single(p):
    'param_list : IDENTIFIER'
    p[0] = [p[1]]

def p_param_list_multi(p):
    'param_list : param_list COMMA IDENTIFIER'
    p[0] = p[1] + [p[3]]


# ===========================================================================
# Grammar rule:  arg_list  (expressions in a function call)
# ===========================================================================
# add(10, x + 1)  →  arg_list = [Integer(10), BinaryOp(x, +, Integer(1))]

def p_arg_list_single(p):
    'arg_list : expression'
    p[0] = [p[1]]

def p_arg_list_multi(p):
    'arg_list : arg_list COMMA expression'
    p[0] = p[1] + [p[3]]


# ===========================================================================
# Grammar rules:  expressions
# ===========================================================================
# All binary operators (arithmetic, comparison, logical) share one rule.
# The 'precedence' table above resolves ALL ambiguity — PLY knows that
# * has higher precedence than + so A + B * B builds the correct tree.

def p_expression_binop(p):
    '''expression : expression PLUS          expression
                  | expression MINUS         expression
                  | expression MULTIPLY      expression
                  | expression DIVIDE        expression
                  | expression MODULO        expression
                  | expression DOUBLE_EQUALS expression
                  | expression NOT_EQUALS    expression
                  | expression LESS_THAN     expression
                  | expression GREATER_THAN  expression
                  | expression LESS_EQUAL    expression
                  | expression GREATER_EQUAL expression
                  | expression AND           expression
                  | expression OR            expression'''
    # p[2] is the operator token's VALUE — the actual symbol string: '+', '-', etc.
    p[0] = BinaryOp(left=p[1], operator=p[2], right=p[3], line=p.lineno(2))

def p_expression_not(p):
    'expression : NOT expression'
    # not flag   or   not (x > 5)
    p[0] = UnaryOp(operator='not', operand=p[2], line=p.lineno(1))

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    # Unary minus: -x   or   -5
    # %prec UMINUS tells PLY to use UMINUS precedence (highest) for this rule,
    # so -x+y is parsed as (-x)+y, not -(x+y).
    p[0] = UnaryOp(operator='-', operand=p[2], line=p.lineno(1))

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    # Parenthesised expression: (x + y) * z
    # The outer parentheses are discarded — they only affect structure via nesting.
    p[0] = p[2]

def p_expression_integer(p):
    'expression : INTEGER'
    # p[1] is already a Python int (lexer converted it)
    p[0] = Integer(value=p[1], line=p.lineno(1))

def p_expression_float(p):
    'expression : FLOAT'
    # p[1] is already a Python float (lexer converted it)
    p[0] = Float(value=p[1], line=p.lineno(1))

def p_expression_string(p):
    'expression : STRING'
    # p[1] is the string content without quotes (lexer stripped them)
    p[0] = String(value=p[1], line=p.lineno(1))

def p_expression_true(p):
    'expression : TRUE'
    p[0] = Boolean(value=True, line=p.lineno(1))

def p_expression_false(p):
    'expression : FALSE'
    p[0] = Boolean(value=False, line=p.lineno(1))

def p_expression_call_noargs(p):
    'expression : IDENTIFIER LPAREN RPAREN'
    # greet()   or   countdown()
    p[0] = FunctionCall(name=p[1], arguments=[], line=p.lineno(1))

def p_expression_call_args(p):
    'expression : IDENTIFIER LPAREN arg_list RPAREN'
    # add(10, 20)   or   multiply(a, b)
    p[0] = FunctionCall(name=p[1], arguments=p[3], line=p.lineno(1))

def p_expression_variable(p):
    'expression : IDENTIFIER'
    # A plain variable reference: x   or   result
    # NOTE: This rule MUST come AFTER the call rules — PLY tries longer
    # matches first (IDENTIFIER LPAREN beats plain IDENTIFIER).
    p[0] = Variable(name=p[1], line=p.lineno(1))

def p_expression_array_empty(p):
    'expression : LBRACKET RBRACKET'
    # []  — empty array
    p[0] = Array(elements=[], line=p.lineno(1))

def p_expression_array(p):
    'expression : LBRACKET arg_list RBRACKET'
    # [1, 2, 3]  or  ["a", "b"]
    p[0] = Array(elements=p[2], line=p.lineno(1))


# ===========================================================================
# Error handler
# ===========================================================================

def p_error(p):
    """Called by PLY when it encounters a token that doesn't fit any rule."""
    if p is None:
        # Reached end of input before the program was complete
        raise UnexpectedEndError()
    raise ParseError(
        f"Unexpected '{p.value}' — "
        f"check your syntax near this token (token type: {p.type})",
        line=p.lineno
    )


# ===========================================================================
# Build the PLY parser  (done once at import time)
# ===========================================================================
# write_tables=False  → don't generate parsetab.py cluttering the directory
# debug=False         → suppress debug output
# errorlog=NullLogger → suppress PLY's own printed warnings/notices

_parser = ply_yacc.yacc(
    module=sys.modules[__name__],
    write_tables=False,
    debug=False,
    errorlog=ply_yacc.NullLogger(),
)


# ===========================================================================
# Public entry point
# ===========================================================================

def parse(source_code: str) -> Program:
    """
    Parse a Sarana source code string and return the AST root node.

    Args:
        source_code: The full text of a .sara file (or any Sarana snippet).

    Returns:
        A Program node — the root of the Abstract Syntax Tree.
        Every statement in the source is a child of this node.

    Raises:
        LexError:   if the source contains an unrecognised character.
        ParseError: if the token sequence violates Sarana's grammar rules.
    """
    # Step 1: Tokenize (our lexer gives us correct line numbers)
    token_list = tokenize(source_code)

    # Step 2: Wrap in a stream adapter PLY's yacc can consume
    stream = _TokenStream(token_list)

    # Step 3: Run the LALR parser — builds and returns the AST
    # input=None tells PLY not to call stream.input() (we already have tokens)
    result = _parser.parse(input=None, lexer=stream)

    if result is None:
        # Empty source code — return an empty Program
        return Program(statements=[])

    return result


def get_ast_string(source_code: str) -> str:
    """
    Convenience function: parse source code and return the AST as a
    formatted, indented string for display in the UI or the project report.

    Args:
        source_code: Sarana source code string.

    Returns:
        Multi-line string showing the full AST tree.
    """
    ast = parse(source_code)
    return ast.rep()
