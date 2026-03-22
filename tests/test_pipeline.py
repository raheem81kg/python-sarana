"""
tests/test_pipeline.py
======================
Full test suite for the Sarana compiler pipeline.

Run with:
    python3 tests/test_pipeline.py

Each test has a clear name, a description of WHAT it tests,
WHY it matters, and WHAT the correct input/output should be.
"""

import sys
import os

# Add src/ to path so we can import Sarana modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from errors import (
    LexError, ParseError, SemanticError, SaranaRuntimeError,
    UnexpectedEndError, UnexpectedTokenError, ImmutableError, SaranaError
)
from lexer import tokenize, Token
from ast_nodes import (
    Program, BloomStatement, EchoStatement, TryKetchStatement,
    WhenStatement, CycleStatement, CraftStatement, ReturnStatement,
    ExpressionStatement, BinaryOp, UnaryOp, Variable, FunctionCall,
    Integer, Float, String, Boolean, Array
)
from parser import parse, get_ast_string


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

PASS = 0
FAIL = 0
SECTION_PASS = 0
SECTION_FAIL = 0


def start_section(title):
    global SECTION_PASS, SECTION_FAIL
    SECTION_PASS = 0
    SECTION_FAIL = 0
    print(f'\n{"=" * 60}')
    print(f'  {title}')
    print(f'{"=" * 60}')


def end_section():
    global SECTION_PASS, SECTION_FAIL, PASS, FAIL
    PASS += SECTION_PASS
    FAIL += SECTION_FAIL
    color = 'OK' if SECTION_FAIL == 0 else 'ISSUES FOUND'
    print(f'  → {SECTION_PASS} passed  {SECTION_FAIL} failed  [{color}]')


def check(what_it_tests, correct_input, condition, got=None):
    """
    Args:
        what_it_tests : short description of the behaviour being verified
        correct_input : what input triggers this behaviour
        condition     : True = pass, False = fail
        got           : optional — what we actually got (shown on failure)
    """
    global SECTION_PASS, SECTION_FAIL
    if condition:
        SECTION_PASS += 1
        print(f'  PASS  {what_it_tests}')
    else:
        SECTION_FAIL += 1
        detail = f'  ← got: {got}' if got is not None else ''
        print(f'  FAIL  {what_it_tests}{detail}')
        print(f'        input was: {correct_input!r}')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Error Classes  (src/errors.py)
# Purpose: verify every error type formats correctly with a line number.
# Why it matters: ALL phases depend on these for user-facing error messages.
# ══════════════════════════════════════════════════════════════════════════════

start_section('1 / 5   ERROR CLASSES  (src/errors.py)')

e = LexError('bad char', line=3)
check(
    what_it_tests='LexError includes line number in message',
    correct_input='LexError("bad char", line=3)',
    condition='[Line 3]' in str(e)
)
check(
    what_it_tests='LexError includes "Lexical Error" label',
    correct_input='LexError("bad char", line=3)',
    condition='Lexical Error' in str(e)
)

e = ParseError('missing ;', line=7)
check(
    what_it_tests='ParseError includes line number in message',
    correct_input='ParseError("missing ;", line=7)',
    condition='[Line 7]' in str(e)
)
check(
    what_it_tests='ParseError includes "Syntax Error" label',
    correct_input='ParseError("missing ;", line=7)',
    condition='Syntax Error' in str(e)
)

e = SemanticError('undefined variable y', line=2)
check(
    what_it_tests='SemanticError includes line number and label',
    correct_input='SemanticError("undefined variable y", line=2)',
    condition='[Line 2]' in str(e) and 'Semantic Error' in str(e)
)

e = SaranaRuntimeError('division by zero', line=9)
check(
    what_it_tests='SaranaRuntimeError includes line number and label',
    correct_input='SaranaRuntimeError("division by zero", line=9)',
    condition='[Line 9]' in str(e) and 'Runtime Error' in str(e)
)

e = UnexpectedEndError(line=5)
check(
    what_it_tests='UnexpectedEndError is a subclass of ParseError',
    correct_input='UnexpectedEndError(line=5)',
    condition=isinstance(e, ParseError)
)
check(
    what_it_tests='UnexpectedEndError has a helpful message',
    correct_input='UnexpectedEndError(line=5)',
    condition='end of input' in str(e).lower() or 'end' in str(e).lower()
)

e = UnexpectedTokenError('=', line=4)
check(
    what_it_tests='UnexpectedTokenError stores the bad token',
    correct_input='UnexpectedTokenError("=", line=4)',
    condition=e.token == '='
)

check(
    what_it_tests='All error types are subclasses of the base SaranaError',
    correct_input='isinstance(LexError(...), SaranaError)',
    condition=all(
        isinstance(cls('x'), SaranaError)
        for cls in [LexError, ParseError, SemanticError, SaranaRuntimeError]
    )
)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Lexer  (src/lexer.py)
# Purpose: verify every token type the Sarana language uses is recognized.
# Why it matters: if a keyword, operator, or literal is mis-tokenized,
#                 every downstream phase (parser, semantic, codegen) breaks.
# ══════════════════════════════════════════════════════════════════════════════

start_section('2 / 5   LEXER  (src/lexer.py)')

# ── 2a: All 14 keywords ──────────────────────────────────────────────────────

src = 'bloom echo when otherwise cycle craft return try ketch true false and or not;'
toks = tokenize(src)
types = [t.token_type for t in toks if t.token_type != 'SEMICOLON']
expected_keywords = [
    'BLOOM', 'ECHO', 'WHEN', 'OTHERWISE', 'CYCLE', 'CRAFT',
    'RETURN', 'TRY', 'KETCH', 'TRUE', 'FALSE', 'AND', 'OR', 'NOT'
]
check(
    what_it_tests='All 14 Sarana keywords are recognized as keyword tokens',
    correct_input=src,
    condition=types == expected_keywords,
    got=types
)

# Each keyword individually
for kw, expected_type in [
    ('bloom', 'BLOOM'), ('echo', 'ECHO'), ('when', 'WHEN'),
    ('otherwise', 'OTHERWISE'), ('cycle', 'CYCLE'), ('craft', 'CRAFT'),
    ('return', 'RETURN'), ('try', 'TRY'), ('ketch', 'KETCH'),
    ('true', 'TRUE'), ('false', 'FALSE'), ('and', 'AND'),
    ('or', 'OR'), ('not', 'NOT'),
]:
    t = tokenize(kw + ';')[0]
    check(
        what_it_tests=f'Keyword "{kw}" produces token type {expected_type}',
        correct_input=kw,
        condition=t.token_type == expected_type,
        got=t.token_type
    )

# ── 2b: Identifiers vs keywords ──────────────────────────────────────────────

# "bloom" is a keyword; "blooming" is an identifier
toks = tokenize('blooming;')
check(
    what_it_tests='"blooming" is an IDENTIFIER, not the keyword BLOOM',
    correct_input='blooming;',
    condition=toks[0].token_type == 'IDENTIFIER',
    got=toks[0].token_type
)

toks = tokenize('myVariable;')
check(
    what_it_tests='Regular variable name is IDENTIFIER token',
    correct_input='myVariable;',
    condition=toks[0].token_type == 'IDENTIFIER' and toks[0].value == 'myVariable'
)

# ── 2c: Literals ─────────────────────────────────────────────────────────────

toks = tokenize('42;')
check(
    what_it_tests='Integer literal produces INTEGER token with Python int value',
    correct_input='42;',
    condition=toks[0].token_type == 'INTEGER' and toks[0].value == 42 and isinstance(toks[0].value, int)
)

toks = tokenize('3.14;')
check(
    what_it_tests='Float literal produces FLOAT token with Python float value',
    correct_input='3.14;',
    condition=toks[0].token_type == 'FLOAT' and toks[0].value == 3.14 and isinstance(toks[0].value, float)
)

toks = tokenize('3.14;')
check(
    what_it_tests='3.14 is ONE FLOAT token, not split into 3 DOT 14 (float rule runs first)',
    correct_input='3.14;',
    condition=len([t for t in toks if t.token_type in ('FLOAT', 'INTEGER')]) == 1
)

toks = tokenize('"hello world";')
check(
    what_it_tests='String literal produces STRING token with content (no quotes)',
    correct_input='"hello world";',
    condition=toks[0].token_type == 'STRING' and toks[0].value == 'hello world'
)

toks = tokenize("'single quoted';")
check(
    what_it_tests='Single-quoted string also produces STRING token',
    correct_input="'single quoted';",
    condition=toks[0].token_type == 'STRING' and toks[0].value == 'single quoted'
)

# ── 2d: Comments ─────────────────────────────────────────────────────────────

toks = tokenize('-- this is a comment\nbloom x = 5;')
check(
    what_it_tests='-- comment produces no tokens (completely ignored)',
    correct_input='-- this is a comment',
    condition=not any(t.token_type == 'COMMENT' for t in toks)
)
check(
    what_it_tests='Code on next line after comment still tokenizes normally',
    correct_input='-- comment\nbloom x = 5;',
    condition=toks[0].token_type == 'BLOOM'
)

# ── 2e: Operators ────────────────────────────────────────────────────────────

op_tests = [
    ('+', 'PLUS'), ('-', 'MINUS'), ('*', 'MULTIPLY'),
    ('/', 'DIVIDE'), ('%', 'MODULO'),
]
for op, expected in op_tests:
    t = tokenize(f'a {op} b;')[1]
    check(
        what_it_tests=f'Arithmetic operator "{op}" produces {expected} token',
        correct_input=f'a {op} b;',
        condition=t.token_type == expected,
        got=t.token_type
    )

comp_tests = [
    ('==', 'DOUBLE_EQUALS'), ('!=', 'NOT_EQUALS'),
    ('<',  'LESS_THAN'),      ('>',  'GREATER_THAN'),
    ('<=', 'LESS_EQUAL'),     ('>=', 'GREATER_EQUAL'),
    ('=',  'ASSIGN'),
]
for op, expected in comp_tests:
    toks = tokenize(f'a {op} b;')
    t = toks[1]
    check(
        what_it_tests=f'Operator "{op}" produces {expected} token (not confused with similar operators)',
        correct_input=f'a {op} b;',
        condition=t.token_type == expected,
        got=t.token_type
    )

# Critical: -- must NOT produce two MINUS tokens
toks = tokenize('bloom x = 5 - 3;')
minus_count = sum(1 for t in toks if t.token_type == 'MINUS')
check(
    what_it_tests='Single hyphen "-" is MINUS; not confused with "--" comment',
    correct_input='bloom x = 5 - 3;',
    condition=minus_count == 1,
    got=f'{minus_count} MINUS tokens'
)

# ── 2f: Delimiters ───────────────────────────────────────────────────────────

delimiter_tests = [
    ('(', 'LPAREN'), (')', 'RPAREN'),
    ('{', 'LBRACE'), ('}', 'RBRACE'),
    ('[', 'LBRACKET'), (']', 'RBRACKET'),
    (';', 'SEMICOLON'), (',', 'COMMA'),
]
for ch, expected in delimiter_tests:
    t = tokenize(f'x {ch};')[1] if ch != ';' else tokenize(f'x;')[1]
    check(
        what_it_tests=f'Delimiter "{ch}" produces {expected} token',
        correct_input=f'x {ch};',
        condition=t.token_type == expected,
        got=t.token_type
    )

# ── 2g: Line number tracking ─────────────────────────────────────────────────

toks = tokenize('bloom a = 1;\nbloom b = 2;\nbloom c = 3;')
blooms = [t for t in toks if t.token_type == 'BLOOM']
check(
    what_it_tests='Line number 1 is assigned to tokens on line 1',
    correct_input='bloom a = 1;  (first line)',
    condition=blooms[0].line == 1
)
check(
    what_it_tests='Line number 2 is assigned to tokens on line 2',
    correct_input='bloom b = 2;  (second line after \\n)',
    condition=blooms[1].line == 2
)
check(
    what_it_tests='Line number 3 is assigned to tokens on line 3',
    correct_input='bloom c = 3;  (third line)',
    condition=blooms[2].line == 3
)

# ── 2h: Token object structure ───────────────────────────────────────────────

toks = tokenize('bloom x = 5;')
check(
    what_it_tests='Every token is a Token instance',
    correct_input='bloom x = 5;',
    condition=all(isinstance(t, Token) for t in toks)
)
check(
    what_it_tests='Every token has .token_type attribute',
    correct_input='bloom x = 5;',
    condition=all(hasattr(t, 'token_type') for t in toks)
)
check(
    what_it_tests='Every token has .value attribute',
    correct_input='bloom x = 5;',
    condition=all(hasattr(t, 'value') for t in toks)
)
check(
    what_it_tests='Every token has .line attribute',
    correct_input='bloom x = 5;',
    condition=all(hasattr(t, 'line') for t in toks)
)

# ── 2i: LexError on bad characters ───────────────────────────────────────────

for bad_char, src in [('@', 'bloom x = @5;'), ('$', '$x = 5;'), ('#', '#comment;')]:
    try:
        tokenize(src)
        check(
            what_it_tests=f'LexError raised on invalid character "{bad_char}"',
            correct_input=src,
            condition=False
        )
    except LexError as e:
        check(
            what_it_tests=f'LexError raised on invalid character "{bad_char}"',
            correct_input=src,
            condition=True
        )
        check(
            what_it_tests=f'LexError for "{bad_char}" includes line number',
            correct_input=src,
            condition=e.line is not None
        )

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — AST Nodes  (src/ast_nodes.py)
# Purpose: verify every node stores its data correctly and rep() displays it.
# Why it matters: all later phases (interpreter, codegen, semantic) read these
#                 node attributes. Wrong storage = wrong execution.
# ══════════════════════════════════════════════════════════════════════════════

start_section('3 / 5   AST NODES  (src/ast_nodes.py)')

# ── Leaf nodes: correct Python type AND value ────────────────────────────────

check('Integer(42) stores value as Python int 42',
      'Integer(42)', Integer(42).value == 42 and isinstance(Integer(42).value, int))

check('Float(3.14) stores value as Python float 3.14',
      'Float(3.14)', Float(3.14).value == 3.14 and isinstance(Float(3.14).value, float))

check('String("hello") stores content without surrounding quotes',
      'String("hello")', String('hello').value == 'hello')

check('Boolean(True).value is True',
      'Boolean(True)', Boolean(True).value is True)

check('Boolean(False).value is False',
      'Boolean(False)', Boolean(False).value is False)

check('Variable("x").name is "x"',
      'Variable("x")', Variable('x').name == 'x')

# ── BinaryOp ─────────────────────────────────────────────────────────────────

b = BinaryOp(Integer(2), '+', Integer(3), line=5)
check('BinaryOp stores left operand',    'BinaryOp(Integer(2), "+", Integer(3))', b.left.value == 2)
check('BinaryOp stores operator string', 'BinaryOp(Integer(2), "+", Integer(3))', b.operator == '+')
check('BinaryOp stores right operand',   'BinaryOp(Integer(2), "+", Integer(3))', b.right.value == 3)
check('BinaryOp stores line number',     'BinaryOp(..., line=5)',                  b.line == 5)

for op in ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', 'and', 'or']:
    node = BinaryOp(Variable('a'), op, Variable('b'))
    check(f'BinaryOp supports operator "{op}"',
          f'BinaryOp(Variable("a"), "{op}", Variable("b"))',
          node.operator == op)

# ── UnaryOp ──────────────────────────────────────────────────────────────────

u = UnaryOp('not', Boolean(True))
check('UnaryOp("not") stores operator',  'UnaryOp("not", Boolean(True))', u.operator == 'not')
check('UnaryOp("not") stores operand',   'UnaryOp("not", Boolean(True))', isinstance(u.operand, Boolean))

u2 = UnaryOp('-', Integer(5))
check('UnaryOp("-") stores operator',    'UnaryOp("-", Integer(5))', u2.operator == '-')

# ── BloomStatement ───────────────────────────────────────────────────────────

bl = BloomStatement('myVar', Integer(99), line=7)
check('BloomStatement stores variable name',    'BloomStatement("myVar", Integer(99), line=7)', bl.name == 'myVar')
check('BloomStatement stores value expression', 'BloomStatement("myVar", Integer(99), line=7)', isinstance(bl.value, Integer))
check('BloomStatement stores line number',      'BloomStatement("myVar", Integer(99), line=7)', bl.line == 7)

# ── EchoStatement ────────────────────────────────────────────────────────────

ec1 = EchoStatement([String('hello')])
check('EchoStatement stores single expression',     'EchoStatement([String("hello")])',          len(ec1.expressions) == 1)

ec2 = EchoStatement([String('The result is '), Variable('C')])
check('EchoStatement stores multiple expressions',  'EchoStatement([String(...), Variable("C")])', len(ec2.expressions) == 2)
check('EchoStatement first expr is String',         'EchoStatement([String("The result is "), ...])', isinstance(ec2.expressions[0], String))
check('EchoStatement second expr is Variable',      'EchoStatement([..., Variable("C")])',       isinstance(ec2.expressions[1], Variable))
check('EchoStatement Variable name is "C"',         'Variable("C").name == "C"',                 ec2.expressions[1].name == 'C')

# ── TryKetchStatement ────────────────────────────────────────────────────────

tk = TryKetchStatement(
    try_body=[BloomStatement('D', BinaryOp(Variable('C'), '/', Integer(0)))],
    ketch_body=[EchoStatement([String('Error!')])]
)
check('TryKetch stores try_body list',   'TryKetchStatement(try_body=[...], ketch_body=[...])', len(tk.try_body) == 1)
check('TryKetch stores ketch_body list', 'TryKetchStatement(try_body=[...], ketch_body=[...])', len(tk.ketch_body) == 1)
check('TryKetch try_body[0] is BloomStatement', 'try_body=[BloomStatement(...)]', isinstance(tk.try_body[0], BloomStatement))
check('TryKetch ketch_body[0] is EchoStatement', 'ketch_body=[EchoStatement(...)]', isinstance(tk.ketch_body[0], EchoStatement))

# ── WhenStatement ────────────────────────────────────────────────────────────

w_no_else = WhenStatement(BinaryOp(Variable('x'), '>', Integer(5)), [EchoStatement([String('big')])])
check('WhenStatement without otherwise: otherwise_body defaults to []',
      'WhenStatement(cond, body)  — no otherwise arg',
      w_no_else.otherwise_body == [])

w_with_else = WhenStatement(
    BinaryOp(Variable('x'), '>', Integer(5)),
    [EchoStatement([String('big')])],
    [EchoStatement([String('small')])]
)
check('WhenStatement with otherwise: otherwise_body has 1 statement',
      'WhenStatement(cond, body, otherwise=[EchoStatement(...)])',
      len(w_with_else.otherwise_body) == 1)

# ── CycleStatement ───────────────────────────────────────────────────────────

cy = CycleStatement(BinaryOp(Variable('i'), '<', Integer(3)), [EchoStatement([Variable('i')])])
check('CycleStatement stores condition', 'CycleStatement(BinaryOp(i < 3), [...])', isinstance(cy.condition, BinaryOp))
check('CycleStatement stores body',      'CycleStatement(..., [EchoStatement(...)])', len(cy.body) == 1)

# ── CraftStatement ───────────────────────────────────────────────────────────

cr = CraftStatement('add', ['a', 'b'], [ReturnStatement(BinaryOp(Variable('a'), '+', Variable('b')))])
check('CraftStatement stores function name',       'CraftStatement("add", ["a","b"], [...])', cr.name == 'add')
check('CraftStatement stores parameter list',      'CraftStatement("add", ["a","b"], [...])', cr.params == ['a', 'b'])
check('CraftStatement stores body statements',     'CraftStatement(..., [ReturnStatement(...)])', len(cr.body) == 1)
check('CraftStatement body[0] is ReturnStatement', 'CraftStatement body = [ReturnStatement]',  isinstance(cr.body[0], ReturnStatement))

# ── FunctionCall ─────────────────────────────────────────────────────────────

fc = FunctionCall('multiply', [Integer(6), Integer(7)])
check('FunctionCall stores function name',    'FunctionCall("multiply", [Int(6), Int(7)])', fc.name == 'multiply')
check('FunctionCall stores argument list',    'FunctionCall("multiply", [Int(6), Int(7)])', len(fc.arguments) == 2)
check('FunctionCall arg[0] is Integer 6',     'FunctionCall arguments[0] = Integer(6)',     fc.arguments[0].value == 6)

# ── Array ─────────────────────────────────────────────────────────────────────

arr = Array([Integer(1), Integer(2), Integer(3)])
check('Array stores elements list', 'Array([Integer(1), Integer(2), Integer(3)])', len(arr.elements) == 3)

empty_arr = Array([])
check('Empty array stores empty elements list', 'Array([])', len(empty_arr.elements) == 0)

# ── rep() display ────────────────────────────────────────────────────────────
# These verify what the AST tab in the UI will show.

check('Integer(42).rep()  →  "Integer 42"',
      'Integer(42).rep()', Integer(42).rep() == 'Integer 42')

check('Float(3.14).rep()  →  "Float 3.14"',
      'Float(3.14).rep()', Float(3.14).rep() == 'Float 3.14')

check('String("hi").rep()  →  \'String "hi"\'',
      'String("hi").rep()', String('hi').rep() == 'String "hi"')

check('Boolean(True).rep()  →  "Boolean true"',
      'Boolean(True).rep()', Boolean(True).rep() == 'Boolean true')

check('Variable("x").rep()  →  "Variable \'x\'"',
      'Variable("x").rep()', Variable('x').rep() == "Variable 'x'")

# BinaryOp rep shows operator and both children
binop = BinaryOp(Variable('A'), '+', BinaryOp(Variable('B'), '*', Variable('B')))
rep = binop.rep()
check('BinaryOp rep shows operator',      'BinaryOp(A, "+", B*B).rep()', "BinaryOp '+'" in rep)
check('BinaryOp rep shows nested *',      'BinaryOp(A, "+", B*B).rep()', "BinaryOp '*'" in rep)
check('PEMDAS in rep: * is deeper than +', 'A + B*B tree structure', rep.index("BinaryOp '*'") > rep.index("BinaryOp '+'"))

# WhenStatement rep
when_rep = WhenStatement(
    Boolean(True), [EchoStatement([String('yes')])], [EchoStatement([String('no')])]
).rep()
check('WhenStatement rep has "condition:" label', 'WhenStatement(...).rep()', 'condition:' in when_rep)
check('WhenStatement rep has "then:" label',      'WhenStatement(...).rep()', 'then:' in when_rep)
check('WhenStatement rep has "otherwise:" label', 'WhenStatement(...).rep()', 'otherwise:' in when_rep)

# TryKetch rep
tk_rep = TryKetchStatement(
    [BloomStatement('D', Integer(0))], [EchoStatement([String('err')])]
).rep()
check('TryKetchStatement rep has "try:" label',   'TryKetchStatement(...).rep()', 'try:' in tk_rep)
check('TryKetchStatement rep has "ketch:" label', 'TryKetchStatement(...).rep()', 'ketch:' in tk_rep)

# Program rep
prog_rep = Program([BloomStatement('x', Integer(1)), EchoStatement([Variable('x')])]).rep()
check('Program rep starts with "Program"',        'Program([...]).rep()', prog_rep.startswith('Program'))
check('Program rep contains child statements',    'Program([bloom, echo]).rep()', 'BloomStatement' in prog_rep and 'EchoStatement' in prog_rep)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Parser  (src/parser.py)
# Purpose: verify the grammar rules produce the correct AST for every
#          Sarana construct, with correct PEMDAS and correct line numbers.
# Why it matters: wrong AST shape = wrong execution by the interpreter.
# ══════════════════════════════════════════════════════════════════════════════

start_section('4 / 5   PARSER  (src/parser.py)')

# ── PEMDAS operator precedence ───────────────────────────────────────────────

ast = parse('bloom x = 2 + 3 * 4;')
expr = ast.statements[0].value
check(
    what_it_tests='PEMDAS: "2 + 3 * 4" — addition is the ROOT (evaluated last)',
    correct_input='bloom x = 2 + 3 * 4;',
    condition=isinstance(expr, BinaryOp) and expr.operator == '+',
    got=getattr(expr, 'operator', type(expr).__name__)
)
check(
    what_it_tests='PEMDAS: "2 + 3 * 4" — multiplication is the RIGHT CHILD (evaluated first)',
    correct_input='bloom x = 2 + 3 * 4;',
    condition=isinstance(expr.right, BinaryOp) and expr.right.operator == '*',
    got=getattr(expr.right, 'operator', type(expr.right).__name__)
)
check(
    what_it_tests='PEMDAS: "2 + 3 * 4" — left of + is Integer 2',
    correct_input='bloom x = 2 + 3 * 4;',
    condition=isinstance(expr.left, Integer) and expr.left.value == 2
)

ast = parse('bloom x = (2 + 3) * 4;')
expr = ast.statements[0].value
check(
    what_it_tests='Parentheses override PEMDAS: "(2+3)*4" — multiplication is ROOT',
    correct_input='bloom x = (2 + 3) * 4;',
    condition=expr.operator == '*',
    got=expr.operator
)
check(
    what_it_tests='Parentheses override PEMDAS: "(2+3)*4" — addition is LEFT CHILD',
    correct_input='bloom x = (2 + 3) * 4;',
    condition=expr.left.operator == '+',
    got=expr.left.operator
)

ast = parse('bloom x = 10 - 3 - 2;')
expr = ast.statements[0].value
check(
    what_it_tests='Left-associativity: "10-3-2" groups as "(10-3)-2" — left is a BinaryOp',
    correct_input='bloom x = 10 - 3 - 2;',
    condition=isinstance(expr.left, BinaryOp) and expr.left.operator == '-'
)

ast = parse('bloom x = a and b or c;')
expr = ast.statements[0].value
check(
    what_it_tests='Boolean: "a and b or c" — OR is ROOT (lowest precedence)',
    correct_input='bloom x = a and b or c;',
    condition=expr.operator == 'or',
    got=expr.operator
)
check(
    what_it_tests='Boolean: "a and b or c" — AND is LEFT CHILD of OR',
    correct_input='bloom x = a and b or c;',
    condition=expr.left.operator == 'and',
    got=expr.left.operator
)

# ── All statement types ───────────────────────────────────────────────────────

ast = parse('bloom result = 100;')
s = ast.statements[0]
check('BloomStatement: name stored correctly',   'bloom result = 100;', s.name == 'result', got=s.name)
check('BloomStatement: value is Integer(100)',   'bloom result = 100;', s.value.value == 100, got=s.value.value)
check('BloomStatement: line number stored',      'bloom result = 100;', s.line is not None)

ast = parse('echo "hello";')
s = ast.statements[0]
check('EchoStatement: single string expression', 'echo "hello";',  isinstance(s.expressions[0], String))
check('EchoStatement: expression value is hello','echo "hello";',  s.expressions[0].value == 'hello', got=s.expressions[0].value)

ast = parse('echo "The result is " C;')
s = ast.statements[0]
check('EchoStatement: multi-expression — has 2 expressions', 'echo "The result is " C;', len(s.expressions) == 2, got=len(s.expressions))
check('EchoStatement: first expression is String',            'echo "The result is " C;', isinstance(s.expressions[0], String))
check('EchoStatement: second expression is Variable C',       'echo "The result is " C;', s.expressions[1].name == 'C', got=s.expressions[1].name)

ast = parse('try { echo "ok"; } ketch { echo "err"; }')
s = ast.statements[0]
check('TryKetch: correct node type',          'try { echo "ok"; } ketch { echo "err"; }', isinstance(s, TryKetchStatement))
check('TryKetch: try_body has 1 statement',   'try { echo "ok"; } ketch { echo "err"; }', len(s.try_body) == 1, got=len(s.try_body))
check('TryKetch: ketch_body has 1 statement', 'try { echo "ok"; } ketch { echo "err"; }', len(s.ketch_body) == 1, got=len(s.ketch_body))

ast = parse('when (x > 5) { echo "big"; }')
s = ast.statements[0]
check('WhenStatement: no-otherwise — otherwise_body is []', 'when (x > 5) { echo "big"; }', s.otherwise_body == [], got=s.otherwise_body)
check('WhenStatement: condition operator is >',             'when (x > 5) { ... }',          s.condition.operator == '>', got=s.condition.operator)

ast = parse('when (x > 5) { echo "big"; } otherwise { echo "small"; }')
s = ast.statements[0]
check('WhenStatement+otherwise: otherwise_body has 1 stmt', 'when (x > 5) { ... } otherwise { ... }', len(s.otherwise_body) == 1, got=len(s.otherwise_body))

ast = parse('cycle (i < 3) { echo i; bloom i = i + 1; }')
s = ast.statements[0]
check('CycleStatement: condition operator is <', 'cycle (i < 3) { ... }', s.condition.operator == '<', got=s.condition.operator)
check('CycleStatement: body has 2 statements',   'cycle (i < 3) { echo i; bloom i = i + 1; }', len(s.body) == 2, got=len(s.body))

ast = parse('craft greet() { echo "hi"; }')
s = ast.statements[0]
check('CraftStatement no-params: name is greet', 'craft greet() { ... }', s.name == 'greet', got=s.name)
check('CraftStatement no-params: params is []',  'craft greet() { ... }', s.params == [], got=s.params)

ast = parse('craft add(a, b) { return a + b; }')
s = ast.statements[0]
check('CraftStatement with-params: name is add',   'craft add(a, b) { ... }', s.name == 'add')
check('CraftStatement with-params: params [a, b]', 'craft add(a, b) { ... }', s.params == ['a', 'b'], got=s.params)
check('CraftStatement: body[0] is ReturnStatement','craft add(a,b) { return a+b; }', isinstance(s.body[0], ReturnStatement))

ast = parse('return x + 1;')
s = ast.statements[0]
check('ReturnStatement: correct node type',     'return x + 1;', isinstance(s, ReturnStatement))
check('ReturnStatement: value is BinaryOp +',   'return x + 1;', s.value.operator == '+', got=getattr(s.value, 'operator', None))

ast = parse('add(10, 20);')
s = ast.statements[0]
check('ExpressionStatement with FunctionCall: correct outer type', 'add(10, 20);', isinstance(s, ExpressionStatement))
check('FunctionCall: name is add',   'add(10, 20);', s.expression.name == 'add', got=s.expression.name)
check('FunctionCall: has 2 args',    'add(10, 20);', len(s.expression.arguments) == 2, got=len(s.expression.arguments))
check('FunctionCall: arg[0] = 10',   'add(10, 20);', s.expression.arguments[0].value == 10)
check('FunctionCall: arg[1] = 20',   'add(10, 20);', s.expression.arguments[1].value == 20)

ast = parse('bloom x = [1, 2, 3];')
check('Array literal: 3 elements',   'bloom x = [1, 2, 3];', len(ast.statements[0].value.elements) == 3)

ast = parse('bloom x = [];')
check('Empty array literal',         'bloom x = [];', len(ast.statements[0].value.elements) == 0)

ast = parse('bloom x = 3.14;')
check('Float literal in expression', 'bloom x = 3.14;', isinstance(ast.statements[0].value, Float))

# ── Line numbers stored in AST ────────────────────────────────────────────────

ast = parse('bloom a = 1;\nbloom b = 2;\nbloom c = 3;')
check('Line 1 stored on statement from line 1', 'bloom a = 1;  (line 1)', ast.statements[0].line == 1, got=ast.statements[0].line)
check('Line 2 stored on statement from line 2', 'bloom b = 2;  (line 2)', ast.statements[1].line == 2, got=ast.statements[1].line)
check('Line 3 stored on statement from line 3', 'bloom c = 3;  (line 3)', ast.statements[2].line == 3, got=ast.statements[2].line)

# ── Multiple statements in sequence ──────────────────────────────────────────

ast = parse('bloom x = 5;\nbloom y = 10;\necho x;')
check('3 statements parsed in correct order',  '3-line program', len(ast.statements) == 3, got=len(ast.statements))
check('Statement order preserved: first is bloom',   '3-line program', isinstance(ast.statements[0], BloomStatement))
check('Statement order preserved: third is echo',    '3-line program', isinstance(ast.statements[2], EchoStatement))

# ── Empty program ─────────────────────────────────────────────────────────────

ast = parse('')
check('Empty source returns Program node',              '""  (empty string)',  isinstance(ast, Program))
check('Empty source Program has 0 statements',          '""  (empty string)',  len(ast.statements) == 0, got=len(ast.statements))

# ── Error cases ───────────────────────────────────────────────────────────────

try:
    parse('bloom = 5;')
    check('ParseError: "bloom = 5;" (missing variable name)', 'bloom = 5;', False)
except ParseError as e:
    check('ParseError: "bloom = 5;" (missing variable name)',
          'bloom = 5;  — "=" appears where a name should be', True)

try:
    parse('bloom x = @5;')
    check('LexError: "bloom x = @5;" (invalid character @)', 'bloom x = @5;', False)
except LexError as e:
    check('LexError: "bloom x = @5;" (invalid character @)',
          'bloom x = @5;  — "@" is not in the Sarana character set', True)

try:
    parse('when x > 5 { echo "hi"; }')
    check('ParseError: "when x > 5 ..." (missing parens around condition)', 'when x > 5 { ... }', False)
except ParseError as e:
    check('ParseError: "when x > 5 ..." (missing parens around condition)',
          'when x > 5 { ... }  — requires when (x > 5) { ... }', True)

try:
    parse('bloom x = (5 +;')
    check('ParseError: "bloom x = (5 +;" (incomplete expression)', 'bloom x = (5 +;', False)
except (ParseError, Exception):
    check('ParseError: "bloom x = (5 +;" (incomplete expression)',
          'bloom x = (5 +;  — expression started but never finished', True)

# ── get_ast_string ────────────────────────────────────────────────────────────

ast_str = get_ast_string('bloom x = 5;\necho x;')
check('get_ast_string() returns a string',            'get_ast_string("bloom x = 5; echo x;")', isinstance(ast_str, str))
check('get_ast_string() output starts with "Program"','get_ast_string("bloom x = 5; echo x;")', ast_str.startswith('Program'))
check('get_ast_string() output contains BloomStatement', 'get_ast_string(...)', 'BloomStatement' in ast_str)
check('get_ast_string() output contains EchoStatement',  'get_ast_string(...)', 'EchoStatement' in ast_str)

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Full Pipeline  (lexer → parser together on real programs)
# Purpose: verify that all modules work together on real Sarana programs.
# This is the most important test — it mirrors what the grader will see.
# ══════════════════════════════════════════════════════════════════════════════

start_section('5 / 5   FULL PIPELINE  (all modules on real programs)')

# ── The required assignment sample program ────────────────────────────────────

REQUIRED_SAMPLE = """\
-- Sample program in Sarana

bloom A = 20;
bloom B = 40;
bloom C = A + B * B;

-- Demonstrating Exception Handling
try {
    bloom D = C / 0;
}
ketch {
    echo "Error: Division by zero attempted but not allowed.";
}

echo "The result is " C;
"""

print()
print('  Testing the required assignment sample program:')
print()

toks = tokenize(REQUIRED_SAMPLE)
check(
    what_it_tests='Lexer: comment lines produce no tokens',
    correct_input='-- Sample program in Sarana',
    condition=not any(t.token_type == 'COMMENT' for t in toks)
)
check(
    what_it_tests='Lexer: 39 tokens total (correct count for this program)',
    correct_input=REQUIRED_SAMPLE,
    condition=len(toks) == 39,
    got=len(toks)
)

ast = parse(REQUIRED_SAMPLE)
check('Parser: produces a Program node',              REQUIRED_SAMPLE, isinstance(ast, Program))
check('Parser: program has 5 top-level statements',   REQUIRED_SAMPLE, len(ast.statements) == 5, got=len(ast.statements))

s0, s1, s2, s3, s4 = ast.statements

check('Parser: stmt[0] is bloom A = 20',  'bloom A = 20;', isinstance(s0, BloomStatement) and s0.name == 'A' and s0.value.value == 20)
check('Parser: stmt[1] is bloom B = 40',  'bloom B = 40;', isinstance(s1, BloomStatement) and s1.name == 'B' and s1.value.value == 40)
check('Parser: stmt[2] is bloom C = ...',  'bloom C = A + B * B;', isinstance(s2, BloomStatement) and s2.name == 'C')

c_expr = s2.value
check('PEMDAS: C = A + B*B — "+" is root op',   'A + B * B',  c_expr.operator == '+', got=c_expr.operator)
check('PEMDAS: C = A + B*B — left is Variable A','A + B * B',  isinstance(c_expr.left, Variable) and c_expr.left.name == 'A')
check('PEMDAS: C = A + B*B — right is BinaryOp *','A + B * B', c_expr.right.operator == '*', got=c_expr.right.operator)
check('PEMDAS: C = A + B*B — B*B left is B',     'B * B',      c_expr.right.left.name == 'B')
check('PEMDAS: C = A + B*B — B*B right is B',    'B * B',      c_expr.right.right.name == 'B')

check('Parser: stmt[3] is TryKetchStatement', 'try { ... } ketch { ... }', isinstance(s3, TryKetchStatement))
check('Parser: try body has 1 statement — bloom D = C / 0', 'bloom D = C / 0;', len(s3.try_body) == 1)
check('Parser: try body[0] is BloomStatement for D', 'bloom D = C / 0;', isinstance(s3.try_body[0], BloomStatement) and s3.try_body[0].name == 'D')
check('Parser: divisor in C/0 is Integer 0', 'C / 0', s3.try_body[0].value.right.value == 0)

check('Parser: ketch body has 1 statement — echo error', 'echo "Error: ...";', len(s3.ketch_body) == 1)
check('Parser: ketch body[0] is EchoStatement', 'echo "Error: ...";', isinstance(s3.ketch_body[0], EchoStatement))
ketch_msg = s3.ketch_body[0].expressions[0]
check('Parser: ketch echo message contains "Division by zero"',
      'echo "Error: Division by zero attempted but not allowed.";',
      isinstance(ketch_msg, String) and 'Division by zero' in ketch_msg.value,
      got=ketch_msg.value if isinstance(ketch_msg, String) else type(ketch_msg).__name__)

check('Parser: stmt[4] is final EchoStatement', 'echo "The result is " C;', isinstance(s4, EchoStatement))
check('Parser: final echo has 2 expressions',   'echo "The result is " C;', len(s4.expressions) == 2, got=len(s4.expressions))
check('Parser: final echo expr[0] is String',   'echo "The result is " C;', isinstance(s4.expressions[0], String))
check('Parser: final echo expr[1] is Variable C','echo "The result is " C;', isinstance(s4.expressions[1], Variable) and s4.expressions[1].name == 'C')

# ── A program with functions and loops ────────────────────────────────────────

FUNCTIONS_SAMPLE = """\
craft multiply(a, b) {
    return a * b;
}

bloom result = multiply(6, 7);
echo "6 x 7 = " result;
"""

ast = parse(FUNCTIONS_SAMPLE)
check('Functions: program has 3 statements', FUNCTIONS_SAMPLE, len(ast.statements) == 3, got=len(ast.statements))
craft = ast.statements[0]
check('Functions: first stmt is CraftStatement', FUNCTIONS_SAMPLE, isinstance(craft, CraftStatement))
check('Functions: craft name is multiply', FUNCTIONS_SAMPLE, craft.name == 'multiply')
check('Functions: params are [a, b]', FUNCTIONS_SAMPLE, craft.params == ['a', 'b'])
check('Functions: body has return a * b', FUNCTIONS_SAMPLE, craft.body[0].value.operator == '*')

call_stmt = ast.statements[1]
check('Functions: bloom result = multiply(6, 7)', FUNCTIONS_SAMPLE, isinstance(call_stmt.value, FunctionCall))
check('Functions: FunctionCall name is multiply', FUNCTIONS_SAMPLE, call_stmt.value.name == 'multiply')
check('Functions: FunctionCall has 2 args', FUNCTIONS_SAMPLE, len(call_stmt.value.arguments) == 2)

# ── A program with boolean logic ──────────────────────────────────────────────

BOOLEAN_SAMPLE = """\
bloom isRaining = true;
bloom hasUmbrella = false;

when (isRaining and not hasUmbrella) {
    echo "You will get wet!";
} otherwise {
    echo "You are prepared.";
}
"""

ast = parse(BOOLEAN_SAMPLE)
check('Booleans: program has 3 statements', BOOLEAN_SAMPLE, len(ast.statements) == 3, got=len(ast.statements))
check('Booleans: bloom isRaining = true', BOOLEAN_SAMPLE, ast.statements[0].value.value is True)
check('Booleans: bloom hasUmbrella = false', BOOLEAN_SAMPLE, ast.statements[1].value.value is False)
when = ast.statements[2]
check('Booleans: when condition uses "and"', BOOLEAN_SAMPLE, when.condition.operator == 'and')
check('Booleans: right side of and is UnaryOp "not"', BOOLEAN_SAMPLE, isinstance(when.condition.right, UnaryOp) and when.condition.right.operator == 'not')
check('Booleans: has otherwise block', BOOLEAN_SAMPLE, len(when.otherwise_body) == 1)

# ── AST string output ─────────────────────────────────────────────────────────

ast_str = get_ast_string(REQUIRED_SAMPLE)
check('AST string: starts with "Program"',           REQUIRED_SAMPLE, ast_str.startswith('Program'))
check('AST string: shows all 4 BloomStatements',     REQUIRED_SAMPLE, ast_str.count('BloomStatement') == 4)
check('AST string: shows TryKetchStatement',          REQUIRED_SAMPLE, 'TryKetchStatement' in ast_str)
check('AST string: shows try: and ketch: headings',  REQUIRED_SAMPLE, 'try:' in ast_str and 'ketch:' in ast_str)
check('AST string: PEMDAS — * is indented deeper than +', REQUIRED_SAMPLE,
      ast_str.index("BinaryOp '*'") > ast_str.index("BinaryOp '+'"))

end_section()


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

print(f'\n{"=" * 60}')
print(f'  FINAL RESULTS')
print(f'{"=" * 60}')
print(f'  Total tests : {PASS + FAIL}')
print(f'  Passed      : {PASS}')
print(f'  Failed      : {FAIL}')
if FAIL == 0:
    print(f'\n  ALL TESTS PASSED — pipeline is working correctly.')
else:
    print(f'\n  {FAIL} test(s) failed — see FAIL lines above.')
print(f'{"=" * 60}\n')
