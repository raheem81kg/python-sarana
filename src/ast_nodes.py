# src/ast_nodes.py
# Abstract Syntax Tree (AST) node definitions for the Sarana language.
#
# After the lexer produces a flat list of tokens, the parser uses these
# classes to build a TREE that captures the structure and meaning of the
# program.  Every statement, expression, and operator in Sarana has its
# own node class here.
#
# How the tree is used:
#   - Parser       → builds the tree from tokens
#   - Semantic     → walks the tree to check for errors (undefined vars, etc.)
#   - Interpreter  → walks the tree to execute the program
#   - Code gen     → walks the tree to emit Python source code
#
# Every node has a rep(indent) method that returns a readable indented-tree
# string.  This is used in the UI's "AST" tab and in the project report.
#
# Design:
#   - Nodes store ONLY the data they need (no bloat)
#   - No eval() here — execution is the interpreter's job
#   - BinaryOp and UnaryOp use a string operator ('+'  '-'  '*'  etc.)
#     rather than separate Add/Sub/Mul classes — simpler and cleaner



# Base class
# ===========================================================================

class Node:
    """Base class for all Sarana AST nodes."""

    def rep(self, indent=0):
        """
        Return a human-readable indented string representation of this node
        and all its children.  Each level of nesting is indented by 2 spaces.

        Example output for:  bloom C = A + B * B;

            BloomStatement 'C'
              BinaryOp '+'
                Variable 'A'
                BinaryOp '*'
                  Variable 'B'
                  Variable 'B'
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement rep()"
        )

    def _pad(self, indent):
        """Return the indentation prefix string for a given depth."""
        return "  " * indent



# Program — the root node
# ===========================================================================

class Program(Node):
    """
    The root of the entire AST.  Holds the ordered list of all top-level
    statements in the .sara file.

    Attributes:
        statements  (list[Node])  : Every statement in the program, in order.
    """

    def __init__(self, statements):
        self.statements = statements   # list of statement nodes

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}Program"]
        for stmt in self.statements:
            lines.append(stmt.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"Program({len(self.statements)} statements)"



# Statements
# ===========================================================================

class BloomStatement(Node):
    """
    Variable declaration.

    Sarana syntax:   bloom x = 5;
                     bloom result = add(10, 20);

    Attributes:
        name   (str)   : The variable name  (e.g. 'x', 'result')
        value  (Node)  : The expression assigned to it
        line   (int)   : Source line number (for error messages)
    """

    def __init__(self, name, value, line=None):
        self.name = name
        self.value = value
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}BloomStatement '{self.name}'"]
        lines.append(self.value.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"BloomStatement(name={self.name!r})"


class EchoStatement(Node):
    """
    Print/output statement.  Can print multiple expressions on one line.

    Sarana syntax:   echo "Hello!";
                     echo "The result is " C;   ← two expressions, printed together

    Attributes:
        expressions  (list[Node])  : One or more expressions to print.
        line         (int)         : Source line number.
    """

    def __init__(self, expressions, line=None):
        self.expressions = expressions   # list — could be just one item
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}EchoStatement"]
        for expr in self.expressions:
            lines.append(expr.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"EchoStatement({len(self.expressions)} expressions)"


class TryKetchStatement(Node):
    """
    Exception handling block.

    Sarana syntax:
        try {
            bloom D = C / 0;
        }
        ketch {
            echo "Error!";
        }

    If ANY statement inside 'try' raises an error at runtime, execution
    immediately jumps to the 'ketch' block.

    Attributes:
        try_body    (list[Node])  : Statements inside the try block.
        ketch_body  (list[Node])  : Statements inside the ketch block.
        line        (int)         : Source line number.
    """

    def __init__(self, try_body, ketch_body, line=None):
        self.try_body = try_body      # list of statements
        self.ketch_body = ketch_body  # list of statements
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}TryKetchStatement"]
        lines.append(f"{self._pad(indent+1)}try:")
        for stmt in self.try_body:
            lines.append(stmt.rep(indent + 2))
        lines.append(f"{self._pad(indent+1)}ketch:")
        for stmt in self.ketch_body:
            lines.append(stmt.rep(indent + 2))
        return "\n".join(lines)

    def __repr__(self):
        return "TryKetchStatement"


class WhenStatement(Node):
    """
    Conditional statement (if / else).

    Sarana syntax:
        when (x > 5) {
            echo "big";
        } otherwise {
            echo "small";
        }

    The 'otherwise' block is optional.

    Attributes:
        condition       (Node)       : The boolean expression to test.
        then_body       (list[Node]) : Statements run when condition is true.
        otherwise_body  (list[Node]) : Statements run when condition is false.
                                       Empty list if no 'otherwise'.
        line            (int)        : Source line number.
    """

    def __init__(self, condition, then_body, otherwise_body=None, line=None):
        self.condition = condition
        self.then_body = then_body
        self.otherwise_body = otherwise_body if otherwise_body is not None else []
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}WhenStatement"]
        lines.append(f"{self._pad(indent+1)}condition:")
        lines.append(self.condition.rep(indent + 2))
        lines.append(f"{self._pad(indent+1)}then:")
        for stmt in self.then_body:
            lines.append(stmt.rep(indent + 2))
        if self.otherwise_body:
            lines.append(f"{self._pad(indent+1)}otherwise:")
            for stmt in self.otherwise_body:
                lines.append(stmt.rep(indent + 2))
        return "\n".join(lines)

    def __repr__(self):
        return "WhenStatement"


class CycleStatement(Node):
    """
    While loop.

    Sarana syntax:
        cycle (i < 3) {
            echo i;
            bloom i = i + 1;
        }

    Executes the body repeatedly as long as the condition is true.

    Attributes:
        condition  (Node)       : Boolean expression checked before each iteration.
        body       (list[Node]) : Statements inside the loop.
        line       (int)        : Source line number.
    """

    def __init__(self, condition, body, line=None):
        self.condition = condition
        self.body = body   # list of statements
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}CycleStatement"]
        lines.append(f"{self._pad(indent+1)}condition:")
        lines.append(self.condition.rep(indent + 2))
        lines.append(f"{self._pad(indent+1)}body:")
        for stmt in self.body:
            lines.append(stmt.rep(indent + 2))
        return "\n".join(lines)

    def __repr__(self):
        return "CycleStatement"


class CraftStatement(Node):
    """
    Function definition.

    Sarana syntax:
        craft add(a, b) {
            return a + b;
        }

    Attributes:
        name    (str)        : The function name (e.g. 'add').
        params  (list[str])  : Parameter names (e.g. ['a', 'b']).
        body    (list[Node]) : Statements inside the function body.
        line    (int)        : Source line number.
    """

    def __init__(self, name, params, body, line=None):
        self.name = name
        self.params = params   # list of strings (parameter names)
        self.body = body       # list of statement nodes
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        param_str = ", ".join(self.params)
        lines = [f"{pad}CraftStatement '{self.name}' ({param_str})"]
        for stmt in self.body:
            lines.append(stmt.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"CraftStatement(name={self.name!r}, params={self.params})"


class ReturnStatement(Node):
    """
    Return from a function.

    Sarana syntax:   return a + b;

    Attributes:
        value  (Node)  : The expression to return.
        line   (int)   : Source line number.
    """

    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}ReturnStatement"]
        lines.append(self.value.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return "ReturnStatement"


class ExpressionStatement(Node):
    """
    A standalone expression used as a statement (most commonly a function call).

    Sarana syntax:   countdown(3);

    Attributes:
        expression  (Node)  : The expression being evaluated.
        line        (int)   : Source line number.
    """

    def __init__(self, expression, line=None):
        self.expression = expression
        self.line = line

    def rep(self, indent=0):
        return self.expression.rep(indent)

    def __repr__(self):
        return f"ExpressionStatement({self.expression!r})"



# Expressions — things that produce a value
# ===========================================================================

class BinaryOp(Node):
    """
    An operation with two operands: arithmetic, comparison, or logical.

    Sarana syntax:   A + B * B     x == y     flag and not other

    We use a single BinaryOp class with an 'operator' string rather than
    separate Add/Sub/Mul classes.  This is simpler and the operator string
    makes the AST display self-explanatory.

    Operators:
        Arithmetic:   +  -  *  /  %
        Comparison:   ==  !=  <  >  <=  >=
        Logical:      and  or

    Attributes:
        left      (Node)  : Left operand.
        operator  (str)   : The operator symbol (e.g. '+', '==', 'and').
        right     (Node)  : Right operand.
        line      (int)   : Source line number.
    """

    def __init__(self, left, operator, right, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}BinaryOp '{self.operator}'"]
        lines.append(self.left.rep(indent + 1))
        lines.append(self.right.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"BinaryOp({self.left!r} {self.operator} {self.right!r})"


class UnaryOp(Node):
    """
    An operation with one operand.

    Sarana syntax:   not flag     -x

    Operators:
        not   (logical negation)
        -     (arithmetic negation)

    Attributes:
        operator  (str)   : 'not' or '-'
        operand   (Node)  : The expression being negated.
        line      (int)   : Source line number.
    """

    def __init__(self, operator, operand, line=None):
        self.operator = operator
        self.operand = operand
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}UnaryOp '{self.operator}'"]
        lines.append(self.operand.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand!r})"


class Variable(Node):
    """
    A reference to a variable — anywhere a variable NAME is used in an expression.

    Sarana syntax:   echo x;      bloom y = x + 1;

    Attributes:
        name  (str)  : The variable name.
        line  (int)  : Source line number.
    """

    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def rep(self, indent=0):
        return f"{self._pad(indent)}Variable '{self.name}'"

    def __repr__(self):
        return f"Variable({self.name!r})"


class FunctionCall(Node):
    """
    A call to a named function.

    Sarana syntax:   add(10, 20)     countdown(3)     multiply(a, b)

    Attributes:
        name       (str)        : The function name.
        arguments  (list[Node]) : Expressions passed as arguments.
        line       (int)        : Source line number.
    """

    def __init__(self, name, arguments, line=None):
        self.name = name
        self.arguments = arguments   # list of expression nodes
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}FunctionCall '{self.name}'"]
        for arg in self.arguments:
            lines.append(arg.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"FunctionCall(name={self.name!r}, args={len(self.arguments)})"



# Literals — leaf nodes that hold actual values
# ===========================================================================
# Literals are 'leaf' nodes — they have no children.  They just hold a value.

class Integer(Node):
    """
    A whole number literal.

    Sarana syntax:   42     0     100

    Attributes:
        value  (int)  : The integer value.
        line   (int)  : Source line number.
    """

    def __init__(self, value, line=None):
        self.value = int(value)
        self.line = line

    def rep(self, indent=0):
        return f"{self._pad(indent)}Integer {self.value}"

    def __repr__(self):
        return f"Integer({self.value})"


class Float(Node):
    """
    A decimal number literal.

    Sarana syntax:   3.14     0.5     100.0

    Attributes:
        value  (float)  : The float value.
        line   (int)    : Source line number.
    """

    def __init__(self, value, line=None):
        self.value = float(value)
        self.line = line

    def rep(self, indent=0):
        return f"{self._pad(indent)}Float {self.value}"

    def __repr__(self):
        return f"Float({self.value})"


class String(Node):
    """
    A text string literal.

    Sarana syntax:   "hello"     "Error: Division by zero"

    Attributes:
        value  (str)  : The string content WITHOUT surrounding quotes.
                        (The lexer already stripped the quotes.)
        line   (int)  : Source line number.
    """

    def __init__(self, value, line=None):
        self.value = str(value)
        self.line = line

    def rep(self, indent=0):
        return f'{self._pad(indent)}String "{self.value}"'

    def __repr__(self):
        return f"String({self.value!r})"


class Boolean(Node):
    """
    A boolean literal.

    Sarana syntax:   true     false

    Attributes:
        value  (bool)  : True or False.
        line   (int)   : Source line number.
    """

    def __init__(self, value, line=None):
        self.value = bool(value)
        self.line = line

    def rep(self, indent=0):
        return f"{self._pad(indent)}Boolean {'true' if self.value else 'false'}"

    def __repr__(self):
        return f"Boolean({self.value})"


class Array(Node):
    """
    An array literal.

    Sarana syntax:   [1, 2, 3]     ["a", "b"]     []

    Attributes:
        elements  (list[Node])  : The expressions that make up the array.
        line      (int)         : Source line number.
    """

    def __init__(self, elements, line=None):
        self.elements = elements   # list of expression nodes
        self.line = line

    def rep(self, indent=0):
        pad = self._pad(indent)
        lines = [f"{pad}Array"]
        for elem in self.elements:
            lines.append(elem.rep(indent + 1))
        return "\n".join(lines)

    def __repr__(self):
        return f"Array({len(self.elements)} elements)"
