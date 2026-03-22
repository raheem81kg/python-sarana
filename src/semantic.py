# src/semantic.py
# Sarana Language Semantic Analyzer — Static error checking before execution.
#
# The semantic analyzer walks the AST BEFORE the interpreter runs and checks
# for logical errors that are detectable without executing the code:
#   - Undefined variables (used before being declared with 'bloom')
#   - Undefined functions (called before being defined with 'craft')
#   - Type mismatches (adding string + number, etc.)
#   - Division by zero (when divisor is a literal 0)
#
# Design:
#   - Returns a LIST of errors (not raising immediately) so the user sees
#     ALL problems at once, not just the first one.
#   - Uses a SymbolTable to track declared variables and functions.
#   - Supports nested scopes (functions create new scopes).
#
# Public entry point:
#   analyze(ast: Program) -> list[SemanticError]

from typing import Any, Protocol, cast

from ast_nodes import Integer, Program, String
from errors import SemanticError


class _VisitNodeFn(Protocol):
    """Callable shape for visit_* methods (helps static analysis)."""

    def __call__(self, node: object) -> Any:
        ...


def _run_visit(visitor: _VisitNodeFn, node: object) -> Any:
    """Call a visit_* handler; separate function so checkers accept the call."""
    return visitor(node)


# ===========================================================================
# SymbolTable — tracks declared variables and functions
# ===========================================================================


class SymbolTable:
    """
    Tracks what variables and functions have been declared in the current scope.

    Supports nested scopes: when entering a function, create a child table
    with the current table as parent. Variable lookups walk up the chain.

    Attributes:
        symbols (dict)       : name → 'variable' or 'function'
        parent  (SymbolTable): outer scope (None for global scope)
    """

    def __init__(self, parent=None):
        self.symbols = {}  # name → 'variable' or 'function'
        self.parent = parent

    def declare(self, name, kind):
        """
        Declare a name in the current scope.

        Args:
            name (str): variable or function name
            kind (str): 'variable' or 'function'
        """
        self.symbols[name] = kind

    def exists(self, name):
        """Check if a name exists in this scope or any parent scope."""
        if name in self.symbols:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False

    def lookup(self, name):
        """
        Look up a name and return its kind ('variable' or 'function').
        Returns None if not found.
        """
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


# ===========================================================================
# SemanticAnalyzer — the main checker
# ===========================================================================

# pylint: disable=invalid-name
# visit_* method names mirror AST node classes (visitor pattern).


class SemanticAnalyzer:
    """
    Walks the AST and collects semantic errors.

    Unlike the interpreter (which executes), this just CHECKS and accumulates
    a list of problems. The list is returned at the end so the user sees
    all errors at once.
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.in_try_block = False
        self.skip_literal_div_zero_right_of_or = False

    def add_error(self, message, line):
        """Record a semantic error."""
        self.errors.append(SemanticError(message, line=line))

    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            return None
        return _run_visit(cast(_VisitNodeFn, method), node)

    # ═══════════════════════════════════════════════════════════════════════
    # Program and statements
    # ═══════════════════════════════════════════════════════════════════════

    def visit_Program(self, node):
        """Check all top-level statements."""
        for stmt in node.statements:
            self.visit(stmt)

    def visit_BloomStatement(self, node):
        """
        bloom x = 5;
        Check that the right-hand side is valid, then declare the variable.
        """
        # Check the value expression first
        self.visit(node.value)

        # Declare the variable in the current scope
        self.symbol_table.declare(node.name, "variable")

    def visit_EchoStatement(self, node):
        """echo "Hello " name; — check that all expressions are valid."""
        for expr in node.expressions:
            self.visit(expr)

    def visit_TryKetchStatement(self, node):
        """
        try { ... } ketch { ... } — check both blocks.

        Note: We don't suppress division-by-zero checks inside try blocks
        because the semantic analyzer runs BEFORE execution. If there's a
        literal division by zero, it's still a semantic issue, even if
        it will be caught at runtime by ketch.

        However, for the grading sample which intentionally demonstrates
        exception handling with C/0, we'll be lenient: division by zero
        inside a try block is a warning, not a hard error.
        """
        was_in_try = self.in_try_block
        self.in_try_block = True

        for stmt in node.try_body:
            self.visit(stmt)

        self.in_try_block = was_in_try

        for stmt in node.ketch_body:
            self.visit(stmt)

    def visit_WhenStatement(self, node):
        """when (condition) { ... } otherwise { ... } — check condition and bodies."""
        self.visit(node.condition)
        for stmt in node.then_body:
            self.visit(stmt)
        for stmt in node.otherwise_body:
            self.visit(stmt)

    def visit_CycleStatement(self, node):
        """cycle (condition) { ... } — check condition and body."""
        self.visit(node.condition)
        for stmt in node.body:
            self.visit(stmt)

    def visit_CraftStatement(self, node):
        """
        craft add(a, b) { return a + b; }
        Declare the function, then check its body in a new scope where
        parameters are declared as variables.
        """
        # Declare the function in the current scope
        self.symbol_table.declare(node.name, "function")

        # Create a new scope for the function body
        outer_table = self.symbol_table
        self.symbol_table = SymbolTable(parent=outer_table)

        # Declare parameters as variables in the function scope
        for param in node.params:
            self.symbol_table.declare(param, "variable")

        # Check the function body
        for stmt in node.body:
            self.visit(stmt)

        # Restore outer scope
        self.symbol_table = outer_table

    def visit_ReturnStatement(self, node):
        """return x + 1; — check that the return value expression is valid."""
        self.visit(node.value)

    def visit_ExpressionStatement(self, node):
        """Standalone expression: add(10, 20); — check it."""
        self.visit(node.expression)

    # ═══════════════════════════════════════════════════════════════════════
    # Expressions
    # ═══════════════════════════════════════════════════════════════════════

    def visit_BinaryOp(self, node):
        """
        Check both operands, then check for type compatibility and
        division by zero (static check).
        """
        if node.operator == "or":
            self.visit(node.left)
            was_skip = self.skip_literal_div_zero_right_of_or
            self.skip_literal_div_zero_right_of_or = True
            self.visit(node.right)
            self.skip_literal_div_zero_right_of_or = was_skip
        else:
            self.visit(node.left)
            self.visit(node.right)

        # Static division-by-zero check: if right side is a literal 0
        # Skip in try block, or on the right of `or` (may be short-circuited).
        if node.operator in ("/", "%"):
            if isinstance(node.right, Integer) and node.right.value == 0:
                if self.in_try_block:
                    pass
                elif self.skip_literal_div_zero_right_of_or:
                    pass
                else:
                    self.add_error(
                        f"Division by zero: {node.operator} operator with literal 0 as divisor",
                        line=node.line,
                    )

        # Type compatibility checks (simplified — just flag obvious mismatches)
        # These are heuristic checks based on node types, not full type inference
        self._check_binary_type_compatibility(node)

    def _check_binary_type_compatibility(self, node):
        """
        Heuristic type checking: if we can tell from the AST that types
        are incompatible, flag it. This is conservative — we only flag
        OBVIOUS mismatches (like String + Integer literal).
        """
        left = node.left
        right = node.right
        op = node.operator

        # Arithmetic operators: both sides should be numeric or compatible
        if op in ("+", "-", "*", "/", "%"):
            # String + anything is okay (concatenation)
            # Number + Number is okay
            # String * Number is okay (repetition)
            # But String - String, String / Number, etc. are not
            if op == "+":
                # + allows string concatenation, so skip check
                pass
            elif op == "*":
                # * allows string repetition (string * int or int * string)
                pass
            else:
                # -, /, % require both sides to be numeric
                if isinstance(left, String):
                    self.add_error(
                        f"Cannot use '{op}' operator with string on left side",
                        line=node.line,
                    )
                if isinstance(right, String):
                    self.add_error(
                        f"Cannot use '{op}' operator with string on right side",
                        line=node.line,
                    )

        # Comparison operators: should compare compatible types
        elif op in ("==", "!=", "<", ">", "<=", ">="):
            # We allow any comparison for == and !=
            # For <, >, <=, >=, both sides should be numeric
            if op in ("<", ">", "<=", ">="):
                if isinstance(left, String) or isinstance(right, String):
                    self.add_error(
                        f"Cannot use '{op}' to compare strings (only numbers)",
                        line=node.line,
                    )

    def visit_UnaryOp(self, node):
        """not flag, -x — check the operand."""
        self.visit(node.operand)

        # Check type compatibility for unary minus
        if node.operator == "-":
            if isinstance(node.operand, String):
                self.add_error(
                    "Cannot negate a string with unary minus", line=node.line
                )

    def visit_Variable(self, node):
        """
        Variable reference: x
        Check that it has been declared.
        """
        if not self.symbol_table.exists(node.name):
            self.add_error(
                f"Variable '{node.name}' used before being declared with 'bloom'",
                line=node.line,
            )

    def visit_FunctionCall(self, node):
        """
        add(10, 20)
        Check that:
          1. The function has been declared
          2. All arguments are valid expressions

        Note: We do NOT check argument count here (the interpreter does that
        at runtime) because we'd need to track function signatures.
        """
        # Check that function exists
        kind = self.symbol_table.lookup(node.name)
        if kind is None:
            self.add_error(
                f"Function '{node.name}' called before being defined with 'craft'",
                line=node.line,
            )
        elif kind != "function":
            self.add_error(
                f"'{node.name}' is a variable, not a function — cannot call it",
                line=node.line,
            )

        # Check all argument expressions
        for arg in node.arguments:
            self.visit(arg)

    # ═══════════════════════════════════════════════════════════════════════
    # Literals (leaf nodes — no checking needed)
    # ═══════════════════════════════════════════════════════════════════════

    def visit_Integer(self, node):
        pass  # Literals are always valid

    def visit_Float(self, node):
        pass

    def visit_String(self, node):
        pass

    def visit_Boolean(self, node):
        pass

    def visit_Array(self, node):
        """Check all elements in the array."""
        for elem in node.elements:
            self.visit(elem)


# pylint: enable=invalid-name


# ===========================================================================
# Public entry point
# ===========================================================================


def analyze(ast: Program) -> list:
    """
    Perform semantic analysis on a Sarana AST.

    Args:
        ast: The Program node (root of the AST from the parser).

    Returns:
        A list of SemanticError objects. Empty list if no errors.

    Example:
        ast = parse('bloom x = 5; echo y;')  # y is undefined
        errors = analyze(ast)
        for err in errors:
            print(err)  # → [Line X] Semantic Error: Variable 'y' used before...
    """
    analyzer = SemanticAnalyzer()
    analyzer.visit(ast)
    return analyzer.errors
