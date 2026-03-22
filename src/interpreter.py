# src/interpreter.py
# Sarana Language Interpreter — Phase 3 of the compiler pipeline.
#
# The interpreter walks the Abstract Syntax Tree (AST) and executes it,
# producing output. It's a tree-walking interpreter using the Visitor pattern.
#
# How it works:
#   - Each AST node type has a visit_NodeType() method
#   - visit() dispatches to the right method based on node class name
#   - Recursive: visiting BinaryOp visits its left and right children
#   - Environment: stores variables in a dict, supports nested scopes
#
# try/ketch handling:
#   - try_stack tracks active try blocks
#   - On error, execution jumps to the corresponding ketch block
#
# Public entry point:
#   interpret(ast: Program) -> InterpreterResult

from typing import Any, Callable, Optional, cast

from ast_nodes import Program
from errors import SaranaRuntimeError


# ===========================================================================
# Environment — variable storage with nested scope support
# ===========================================================================

class Environment:
    """
    Stores variables during program execution.
    
    Supports nested scopes: when a new scope is created (e.g. inside a
    function), it has a parent Environment. Variable lookups walk up the
    parent chain until found.
    
    Attributes:
        vars   (dict)        : name → value mapping for this scope
        parent (Environment) : outer scope (None for global scope)
    """
    
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
    
    def set(self, name, value):
        """Declare or update a variable in the current scope."""
        self.vars[name] = value
    
    def get(self, name):
        """
        Look up a variable by name.
        Walks up parent chain if not found in current scope.
        """
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise SaranaRuntimeError(
            f"Variable '{name}' used before being declared with 'bloom'",
            line=None  # line number would come from the Variable node
        )
    
    def exists(self, name):
        """Check if a variable exists in this scope or any parent scope."""
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.exists(name)
        return False


# ===========================================================================
# ReturnValue — signal to exit from a function early
# ===========================================================================

class ReturnValue(Exception):
    """
    Not a real error — used to implement 'return' statements.
    When a return statement executes, we raise ReturnValue(result).
    The craft function's executor catches it and returns the value.
    This lets 'return' work even from deep inside nested blocks.
    """
    
    def __init__(self, value):
        self.value = value


# ===========================================================================
# InterpreterResult — the output from running a program
# ===========================================================================

class InterpreterResult:
    """
    The result of interpreting a Sarana program.
    
    Attributes:
        output  (list[str]) : lines printed by 'echo' statements
        errors  (list[str]) : runtime errors that occurred (if any)
        success (bool)      : True if program ran without uncaught errors
    """
    
    def __init__(self, output, errors=None, success=True):
        self.output = output    # list of strings
        self.errors = errors if errors else []
        self.success = success


# ===========================================================================
# Interpreter — the main tree-walking executor
# ===========================================================================

class Interpreter:
    """
    Walks the AST and executes each node, maintaining:
      - env         : current variable environment
      - output      : list of strings echoed by the program
      - try_stack   : stack of (ketch_body, env) for active try blocks
    """
    
    def __init__(self):
        self.env = Environment()       # global scope
        self.output = []               # captured echo output
        self.try_stack = []            # for try/ketch exception handling
    
    def visit(self, node):
        method_name = f"visit_{node.__class__.__name__}"
        method: Optional[Callable[[Any], Any]] = getattr(
            self, method_name, None
        )
        if method is None:
            raise NotImplementedError(
                f"Interpreter has no visit method for {node.__class__.__name__}"
            )
        fn = cast(Callable[[Any], Any], method)
        return fn(node)
    
    # ═══════════════════════════════════════════════════════════════════════
    # Program and statements
    # ═══════════════════════════════════════════════════════════════════════
    
    def visit_Program(self, node):
        """Execute all top-level statements in order."""
        for stmt in node.statements:
            self.visit(stmt)
        # Program itself doesn't return a value
    
    def visit_BloomStatement(self, node):
        """
        bloom x = 5;
        Evaluate the right-hand side, store in environment.
        """
        value = self.visit(node.value)
        self.env.set(node.name, value)
    
    def visit_EchoStatement(self, node):
        """
        echo "Hello " name;
        Evaluate each expression, convert to string, print joined with spaces.
        """
        parts = []
        for expr in node.expressions:
            value = self.visit(expr)
            parts.append(self._to_string(value))
        self.output.append(' '.join(parts))
    
    def visit_TryKetchStatement(self, node):
        """
        try { ... } ketch { ... }
        Execute try_body. If ANY error occurs, jump to ketch_body.
        """
        # Push this ketch handler onto the stack
        self.try_stack.append((node.ketch_body, self.env))
        
        try:
            # Execute the try block
            for stmt in node.try_body:
                self.visit(stmt)
        except Exception:
            # An error occurred — execute the ketch block
            ketch_body, ketch_env = self.try_stack.pop()
            # Run ketch block in the same environment as try
            # (so variables declared in try are visible in ketch)
            saved_env = self.env
            self.env = ketch_env
            for stmt in ketch_body:
                self.visit(stmt)
            self.env = saved_env
            return  # don't re-raise
        
        # No error — just pop the handler
        self.try_stack.pop()
    
    def visit_WhenStatement(self, node):
        """
        when (condition) { ... } otherwise { ... }
        Evaluate condition. If true, execute then_body. Otherwise, otherwise_body.
        """
        condition_value = self.visit(node.condition)
        if self._is_truthy(condition_value):
            for stmt in node.then_body:
                self.visit(stmt)
        else:
            for stmt in node.otherwise_body:
                self.visit(stmt)
    
    def visit_CycleStatement(self, node):
        """
        cycle (i < 3) { ... }
        While condition is true, execute body.
        """
        while True:
            condition_value = self.visit(node.condition)
            if not self._is_truthy(condition_value):
                break
            for stmt in node.body:
                self.visit(stmt)
    
    def visit_CraftStatement(self, node):
        """
        craft add(a, b) { return a + b; }
        Store the function definition as a callable in the environment.
        """
        # Wrap the function definition in a SaranaFunction object
        func = SaranaFunction(node.name, node.params, node.body, self.env)
        self.env.set(node.name, func)
    
    def visit_ReturnStatement(self, node):
        """
        return x + 1;
        Evaluate the expression and signal return via exception.
        """
        value = self.visit(node.value)
        raise ReturnValue(value)
    
    def visit_ExpressionStatement(self, node):
        """
        Standalone expression used as a statement: add(10, 20);
        Just evaluate it (likely a function call for side effects).
        """
        self.visit(node.expression)
    
    # ═══════════════════════════════════════════════════════════════════════
    # Expressions
    # ═══════════════════════════════════════════════════════════════════════
    
    def visit_BinaryOp(self, node):
        """
        Arithmetic:  A + B * B
        Comparison:  x == y
        Logical:     a and b  (short-circuit; right side may be skipped)

        PEMDAS is already enforced by the AST shape.
        """
        op = node.operator

        # Short-circuit boolean ops — do not evaluate skipped side (e.g. x/0).
        if op == 'and':
            left = self.visit(node.left)
            if not self._is_truthy(left):
                return False
            right = self.visit(node.right)
            return self._is_truthy(right)
        if op == 'or':
            left = self.visit(node.left)
            if self._is_truthy(left):
                return True
            right = self.visit(node.right)
            return self._is_truthy(right)

        left = self.visit(node.left)
        right = self.visit(node.right)

        # Arithmetic
        if op == '+':
            return self._add(left, right)
        elif op == '-':
            return self._subtract(left, right)
        elif op == '*':
            return self._multiply(left, right)
        elif op == '/':
            return self._divide(left, right)
        elif op == '%':
            return self._modulo(left, right)
        
        # Comparison
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return self._less_than(left, right)
        elif op == '>':
            return self._greater_than(left, right)
        elif op == '<=':
            return self._less_equal(left, right)
        elif op == '>=':
            return self._greater_equal(left, right)
 
        else:
            raise SaranaRuntimeError(
                f"Unknown binary operator '{op}'",
                line=node.line
            )
    
    def visit_UnaryOp(self, node):
        """
        not flag
        -x
        """
        operand = self.visit(node.operand)
        
        if node.operator == 'not':
            return not self._is_truthy(operand)
        elif node.operator == '-':
            if isinstance(operand, (int, float)):
                return -operand
            raise SaranaRuntimeError(
                f"Cannot negate {type(operand).__name__}",
                line=node.line
            )
        else:
            raise SaranaRuntimeError(
                f"Unknown unary operator '{node.operator}'",
                line=node.line
            )
    
    def visit_Variable(self, node):
        """Look up variable value from environment."""
        return self.env.get(node.name)
    
    def visit_FunctionCall(self, node):
        """
        add(10, 20)
        Look up function in environment, evaluate arguments, call it.
        """
        func = self.env.get(node.name)
        
        if not isinstance(func, SaranaFunction):
            raise SaranaRuntimeError(
                f"'{node.name}' is not a function (it's a {type(func).__name__})",
                line=node.line
            )
        
        # Evaluate all arguments
        args = [self.visit(arg) for arg in node.arguments]
        
        # Check argument count
        if len(args) != len(func.params):
            raise SaranaRuntimeError(
                f"Function '{node.name}' expects {len(func.params)} arguments, got {len(args)}",
                line=node.line
            )
        
        # Create new environment for function body (closure + params)
        func_env = Environment(parent=func.closure)
        for param_name, arg_value in zip(func.params, args):
            func_env.set(param_name, arg_value)
        
        # Execute function body in the new environment
        saved_env = self.env
        self.env = func_env
        
        try:
            for stmt in func.body:
                self.visit(stmt)
            # No return statement → return None (null in Sarana)
            result = None
        except ReturnValue as ret:
            result = ret.value
        finally:
            self.env = saved_env
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════
    # Literals (leaf nodes — base cases for recursion)
    # ═══════════════════════════════════════════════════════════════════════
    
    def visit_Integer(self, node):
        return node.value
    
    def visit_Float(self, node):
        return node.value
    
    def visit_String(self, node):
        return node.value
    
    def visit_Boolean(self, node):
        return node.value
    
    def visit_Array(self, node):
        """Evaluate all elements and return as Python list."""
        return [self.visit(elem) for elem in node.elements]
    
    # ═══════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════
    
    def _to_string(self, value):
        """Convert any Sarana value to a string for echo output."""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            # Array: [1, 2, 3] → "[1, 2, 3]"
            items = ', '.join(self._to_string(item) for item in value)
            return f'[{items}]'
        elif value is None:
            return 'null'
        else:
            return str(value)
    
    def _is_truthy(self, value):
        """
        Python-style truthiness:
          false, 0, "", [], None → falsy
          everything else → truthy
        """
        if isinstance(value, bool):
            return value
        if value is None or value == 0 or value == "" or value == []:
            return False
        return True
    
    def _add(self, left, right):
        if isinstance(left, str) or isinstance(right, str):
            # String concatenation: "hi" + " there" → "hi there"
            return self._to_string(left) + self._to_string(right)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        raise SaranaRuntimeError(f"Cannot add {type(left).__name__} and {type(right).__name__}")
    
    def _subtract(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left - right
        raise SaranaRuntimeError(f"Cannot subtract {type(right).__name__} from {type(left).__name__}")
    
    def _multiply(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left * right
        # String repetition: "hi" * 3 → "hihihi"
        if isinstance(left, str) and isinstance(right, int):
            return left * right
        if isinstance(left, int) and isinstance(right, str):
            return right * left
        raise SaranaRuntimeError(f"Cannot multiply {type(left).__name__} and {type(right).__name__}")
    
    def _divide(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                raise SaranaRuntimeError("Division by zero")
            return left / right
        raise SaranaRuntimeError(f"Cannot divide {type(left).__name__} by {type(right).__name__}")
    
    def _modulo(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                raise SaranaRuntimeError("Modulo by zero")
            return left % right
        raise SaranaRuntimeError(f"Cannot compute {type(left).__name__} % {type(right).__name__}")
    
    def _less_than(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left < right
        raise SaranaRuntimeError(f"Cannot compare {type(left).__name__} < {type(right).__name__}")
    
    def _greater_than(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left > right
        raise SaranaRuntimeError(f"Cannot compare {type(left).__name__} > {type(right).__name__}")
    
    def _less_equal(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left <= right
        raise SaranaRuntimeError(f"Cannot compare {type(left).__name__} <= {type(right).__name__}")
    
    def _greater_equal(self, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left >= right
        raise SaranaRuntimeError(f"Cannot compare {type(left).__name__} >= {type(right).__name__}")


# ===========================================================================
# SaranaFunction — callable function object
# ===========================================================================

class SaranaFunction:
    """
    A user-defined Sarana function.
    
    Attributes:
        name    (str)        : function name (for error messages)
        params  (list[str])  : parameter names
        body    (list[Node]) : AST nodes in function body
        closure (Environment): environment where function was defined
                               (for closure/lexical scoping)
    """
    
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure  # captures variables from outer scope
    
    def __repr__(self):
        return f"<function {self.name}>"


# ===========================================================================
# Public entry point
# ===========================================================================

def interpret(ast: Program) -> InterpreterResult:
    """
    Execute a Sarana program AST and return the result.
    
    Args:
        ast: The Program node (root of the AST from the parser).
    
    Returns:
        InterpreterResult with:
          .output  — list of strings printed by 'echo' statements
          .errors  — list of error messages (if any)
          .success — True if program ran without uncaught errors
    
    Example:
        ast = parse('bloom x = 5; echo x;')
        result = interpret(ast)
        print(result.output)  # → ['5']
    """
    interp = Interpreter()
    
    try:
        interp.visit(ast)
        return InterpreterResult(
            output=interp.output,
            success=True
        )
    except SaranaRuntimeError as e:
        return InterpreterResult(
            output=interp.output,
            errors=[str(e)],
            success=False
        )
    except Exception as e:
        # Unexpected internal error
        return InterpreterResult(
            output=interp.output,
            errors=[f"Internal error: {e}"],
            success=False
        )
