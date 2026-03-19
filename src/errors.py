# src/errors.py
# Custom error classes for the Sarana language compiler.
#
# Design principle:
#   - LexError, ParseError, SaranaRuntimeError are RAISED immediately —
#     they stop execution at the point the problem is found.
#   - SemanticError is COLLECTED into a list by the semantic analyzer —
#     this way the user sees ALL semantic problems at once, not just the first.
#
# Every error carries a line number so the user knows exactly where to look.


class SaranaError(Exception):
    """Base class for all Sarana compiler and runtime errors."""

    def __init__(self, message, line=None):
        self.message = message
        self.line = line

    def __str__(self):
        if self.line is not None:
            return f"[Line {self.line}] {self.message}"
        return self.message


# ---------------------------------------------------------------------------
# Phase 1 — Lexer errors
# ---------------------------------------------------------------------------

class LexError(SaranaError):
    """
    Raised by the lexer when it encounters a character or sequence it cannot
    turn into a valid token.

    Examples:
        bloom x = @5;        ← '@' is not a valid character in Sarana
        bloom msg = "hello;  ← string was opened but never closed
    """

    def __init__(self, message, line=None):
        super().__init__(f"Lexical Error: {message}", line)


# ---------------------------------------------------------------------------
# Phase 2 — Parser errors
# ---------------------------------------------------------------------------

class ParseError(SaranaError):
    """
    Raised by the parser when the token stream does not match the grammar rules.

    Examples:
        bloom = 5;            ← missing variable name after 'bloom'
        when x > 5 echo x;   ← missing parentheses around condition
        bloom x = 5           ← missing semicolon at end of statement
    """

    def __init__(self, message, line=None):
        super().__init__(f"Syntax Error: {message}", line)


class UnexpectedEndError(ParseError):
    """
    Raised when the parser reaches the end of the source code
    before a statement or block is complete.

    Example:
        bloom x = (5 +    ← expression never finished
    """

    def __init__(self, line=None):
        super().__init__("Unexpected end of input — did you forget a closing ';' or '}'?", line)


class UnexpectedTokenError(ParseError):
    """
    Raised when the parser encounters a valid token but in a place
    where it does not belong according to the grammar.

    Example:
        bloom 5 = x;   ← '5' is valid as a number but not as a variable name
    """

    def __init__(self, token, line=None):
        self.token = token
        super().__init__(f"Unexpected token '{token}'", line)


# ---------------------------------------------------------------------------
# Phase 3 — Semantic errors (collected, not raised immediately)
# ---------------------------------------------------------------------------

class SemanticError(SaranaError):
    """
    Represents a single semantic problem found during semantic analysis.

    Unlike LexError and ParseError which stop compilation immediately,
    SemanticErrors are collected into a list so the user sees ALL
    problems at once.

    Examples:
        echo y;              ← 'y' was never declared with 'bloom'
        bloom x = "hi" * 2; ← can't multiply a string by a number
        bloom z = 10 / 0;   ← division by zero (detected statically)
        add(1, 2);           ← 'add' was never defined with 'craft'
    """

    def __init__(self, message, line=None):
        super().__init__(f"Semantic Error: {message}", line)


# ---------------------------------------------------------------------------
# Phase 4 — Runtime errors (raised during interpretation)
# ---------------------------------------------------------------------------

class SaranaRuntimeError(SaranaError):
    """
    Raised by the interpreter when something goes wrong during program execution.
    This is separate from SemanticError because some problems (like division by
    zero with a variable divisor) can only be detected while the program is running.

    Examples:
        bloom x = 0;
        bloom y = 10 / x;   ← x is 0 but we only know that at runtime

    Note: Division by zero with a *literal* 0 is caught at semantic analysis time.
          Division by zero with a *variable* that happens to be 0 is caught here.
    """

    def __init__(self, message, line=None):
        super().__init__(f"Runtime Error: {message}", line)


# ---------------------------------------------------------------------------
# Legacy error (kept for compatibility with existing code during transition)
# ---------------------------------------------------------------------------

class ImmutableError(SaranaError):
    """
    Raised when attempting to reassign a variable that was already declared.
    In the original python-braid, variables were immutable (could only be set once).
    Sarana allows reassignment via bloom, so this may be relaxed later.
    """

    def __init__(self, name, line=None):
        self.name = name
        super().__init__(f"Cannot reassign variable '{name}' — it was already declared", line)


class LogicError(SaranaError):
    """
    Generic error for internal logic violations (kept for compatibility).
    Prefer the more specific error types above in new code.
    """

    def __init__(self, message, line=None):
        super().__init__(f"Logic Error: {message}", line)
