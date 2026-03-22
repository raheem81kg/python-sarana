# src/lexer.py
# Sarana Language Lexer — Phase 1 of the compiler pipeline.
#
# The lexer (also called a tokenizer or scanner) reads raw Sarana source code
# and breaks it into a flat list of tokens.  Each token carries three pieces
# of information:
#   - token_type  : what kind of thing it is  (e.g. BLOOM, INTEGER, PLUS)
#   - value       : the exact text from the source  (e.g. "bloom", "42", "+")
#   - line        : which line it appears on  (for helpful error messages)
#
# Tool used: PLY (Python Lex-Yacc) — an industry-standard lexer/parser
# generator for Python.  It reads the t_* rules below and builds a
# finite-state automaton that scans the source string efficiently.
#
# Public entry point:
#   tokenize(source_code: str) -> list[Token]
#
# pylint: disable=invalid-name
# (PLY requires token rules named t_<TOKEN>, e.g. t_PLUS — not bare UPPER_CASE.)

import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from errors import LexError

try:
    import ply.lex as ply_lex
except ImportError as exc:
    raise ImportError(
        "PLY is required. Run: pip install -r requirements.txt"
    ) from exc


# Token  — the unit of output from the lexer
# ===========================================================================

class Token:
    """
    A single meaningful unit of Sarana source code.

    Attributes:
        token_type  (str)  : The category of this token, e.g. 'BLOOM', 'INTEGER'
        value       (any)  : The actual content — a string, int, or float
        line        (int)  : The source line number where this token appears
    """

    def __init__(self, token_type, value, line):
        self.token_type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.token_type!r}, {self.value!r}, line={self.line})"


# ===========================================================================
# Reserved keywords
# ===========================================================================
# These are Sarana's 14 keywords.  When the lexer matches a word like "bloom",
# it first checks this dictionary.  If found → keyword token type.
# If not found → plain IDENTIFIER (a variable or function name).
#
# CRITICAL: This lookup happens INSIDE t_IDENTIFIER below.
# Without it, "bloom" would be tokenized as an IDENTIFIER, not a keyword.

RESERVED = {
    'bloom':     'BLOOM',       # variable declaration  (replaces: let)
    'echo':      'ECHO',        # print/output          (replaces: display)
    'when':      'WHEN',        # if conditional        (replaces: if)
    'otherwise': 'OTHERWISE',   # else branch           (replaces: else)
    'cycle':     'CYCLE',       # while loop            (replaces: while)
    'craft':     'CRAFT',       # function definition   (replaces: func)
    'return':    'RETURN',      # return from function
    'try':       'TRY',         # try block
    'ketch':     'KETCH',       # catch exception       (replaces: catch)
    'true':      'TRUE',        # boolean true literal
    'false':     'FALSE',       # boolean false literal
    'and':       'AND',         # logical and
    'or':        'OR',          # logical or
    'not':       'NOT',         # logical not
}


# ===========================================================================
# Token type list — every token the lexer can produce
# ===========================================================================
# PLY requires this tuple.  Every token type that can ever appear in the
# output MUST be listed here.  Keywords are included via RESERVED above and
# added to this tuple at the bottom of this section.

tokens = (
    # --- Literals ---
    'IDENTIFIER',   # variable/function names: x, myVar, result
    'INTEGER',      # whole numbers: 42, 0, 100
    'FLOAT',        # decimal numbers: 3.14, 0.5
    'STRING',       # text in quotes: "hello", 'world'

    # --- Arithmetic operators ---
    'PLUS',         # +
    'MINUS',        # -
    'MULTIPLY',     # *
    'DIVIDE',       # /
    'MODULO',       # %

    # --- Comparison operators ---
    'DOUBLE_EQUALS',    # ==
    'NOT_EQUALS',       # !=
    'LESS_THAN',        # <
    'GREATER_THAN',     # >
    'LESS_EQUAL',       # <=
    'GREATER_EQUAL',    # >=

    # --- Assignment ---
    'ASSIGN',       # =  (single equals — assignment, NOT comparison)

    # --- Delimiters ---
    'LPAREN',       # (
    'RPAREN',       # )
    'LBRACE',       # {
    'RBRACE',       # }
    'LBRACKET',     # [
    'RBRACKET',     # ]
    'SEMICOLON',    # ;  (ends every statement in Sarana)
    'COMMA',        # ,  (separates function arguments)

) + tuple(RESERVED.values())
# ↑ This adds all 14 keyword token types to the tuple automatically.
# Result: BLOOM, ECHO, WHEN, OTHERWISE, CYCLE, CRAFT, RETURN, TRY, KETCH,
#         TRUE, FALSE, AND, OR, NOT


# ===========================================================================
# Whitespace — tell PLY to silently skip these characters
# ===========================================================================
# t_ignore is a special PLY variable.  Characters in this string are
# skipped WITHOUT producing any token.  We ignore spaces, tabs, carriage
# returns, form feeds, vertical tabs, AND newlines.
#
# We ignore newlines here because Sarana uses semicolons to end statements,
# not newlines.  Line numbers are computed separately from character position.

t_ignore = " \t\r\f\v\n"


# ===========================================================================
# Comment rule — skip everything from '--' to end of line
# ===========================================================================
# PLY tries FUNCTION rules before STRING rules.
# Among functions, longer docstring patterns are tried first.
# '--[^\n]*' is longer than '-' so this runs before the MINUS rule,
# ensuring '--' is never mistakenly tokenized as two MINUS tokens.

def t_COMMENT(t):
    r'--[^\n]*'
    # Return nothing → PLY discards this token.
    # The comment text is completely ignored.
    pass


# ===========================================================================
# Multi-character operators  (MUST be functions so they beat single-char ones)
# ===========================================================================
# PLY string rules are sorted by length, but functions always win over strings.
# Defining '==' as a function guarantees it is tried BEFORE '=' (string rule).

def t_DOUBLE_EQUALS(t):
    r'=='
    return t


def t_NOT_EQUALS(t):
    r'!='
    return t


def t_LESS_EQUAL(t):
    r'<='
    return t


def t_GREATER_EQUAL(t):
    r'>='
    return t


# ===========================================================================
# Single-character operators  (string rules — lower priority than functions)
# ===========================================================================

t_PLUS          = r'\+'    # backslash needed: + is special in regex
t_MINUS         = r'-'
t_MULTIPLY      = r'\*'    # backslash needed: * is special in regex
t_DIVIDE        = r'/'
t_MODULO        = r'%'
t_ASSIGN        = r'='
t_LESS_THAN     = r'<'
t_GREATER_THAN  = r'>'

# --- Delimiters ---
t_LPAREN        = r'\('    # backslash needed: ( is special in regex
t_RPAREN        = r'\)'
t_LBRACE        = r'\{'
t_RBRACE        = r'\}'
t_LBRACKET      = r'\['
t_RBRACKET      = r'\]'
t_SEMICOLON     = r';'
t_COMMA         = r','


# ===========================================================================
# Literals — STRING, FLOAT, INTEGER  (order matters!)
# ===========================================================================
# These MUST be functions so PLY respects their relative priority.
# FLOAT must be defined before INTEGER because '\d+\.\d+' is longer and
# more specific than '\d+'.  If INTEGER ran first, "3.14" would be tokenized
# as INTEGER("3"), DOT, INTEGER("14") — wrong!

def t_STRING(t):
    r'"[^"]*"|\'[^\']*\''
    # Strip the surrounding quotes from the value.
    # We store just the content: "hello" → hello
    t.value = t.value[1:-1]
    return t


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)    # convert from string "3.14" to Python float 3.14
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)      # convert from string "42" to Python int 42
    return t


# ===========================================================================
# Identifier + keyword lookup  (MUST come after STRING/FLOAT/INTEGER)
# ===========================================================================
# Matches any word: letters, digits, underscores (but can't START with a digit).
# After matching, checks RESERVED dict to see if it's a keyword.
# This is the standard PLY pattern for handling reserved words.

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = RESERVED.get(t.value, 'IDENTIFIER')
    return t


# ===========================================================================
# Error handler — called when no rule matches the current character
# ===========================================================================

def t_error(t):
    line = _line_at(t.lexer.lexdata, t.lexpos)
    raise LexError(
        f"Unrecognized character '{t.value[0]}' — "
        f"this character is not part of the Sarana language",
        line=line
    )


# ===========================================================================
# Helper — compute line number from character position
# ===========================================================================
# Because we ignore newlines in t_ignore, PLY's built-in lineno counter
# always stays at 1.  Instead, we compute the line number ourselves:
# count how many newline characters appear BEFORE position 'pos' in the
# source string, then add 1 (lines are 1-indexed).

def _line_at(source, pos):
    return source[:pos].count('\n') + 1


# ===========================================================================
# Public entry point
# ===========================================================================

def tokenize(source_code: str) -> list:
    """
    Convert a Sarana source code string into a list of Token objects.

    Args:
        source_code: The full text of a .sara file (or any Sarana snippet).

    Returns:
        A list of Token objects.  Each token has:
          .token_type  — the category  (e.g. 'BLOOM', 'INTEGER', 'PLUS')
          .value       — the content   (e.g. 'bloom', 42, '+')
          .line        — the line number in the source (1-indexed)

    Raises:
        LexError: if the source contains any character that Sarana doesn't
                  recognize (e.g. '@', '$', an unclosed string, etc.)
    """
    # Build a fresh PLY lexer using the rules defined in this module.
    # write_tables=False → don't generate lex.out file
    # errorlog=NullLogger() → suppress PLY's own printed warnings
    lexer = ply_lex.lex(
        module=sys.modules[__name__],
        errorlog=ply_lex.NullLogger(),
    )

    lexer.input(source_code)

    result = []
    for ply_token in lexer:
        # Compute real line number from character position (see _line_at above)
        line = _line_at(source_code, ply_token.lexpos)
        result.append(Token(ply_token.type, ply_token.value, line))

    return result
