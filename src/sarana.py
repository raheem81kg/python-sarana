"""
sarana.py
=========
Main Entry Point for Sarana Compiler

This module ties all compiler phases together and provides a unified API
for compiling and running Sarana programs.

Usage:
    # As a module (used by UI):
    from sarana import compile_and_run
    result = compile_and_run(source_code)
    
    # As a command-line tool:
    python sarana.py program.sara
    python sarana.py program.sara --output generated.py

Architecture:
    Source Code
        ↓
    [Lexer] → Tokens
        ↓
    [Parser] → AST
        ↓
    [Semantic Analyzer] → Error checking
        ↓
    ├─→ [Interpreter] → Execution output
    └─→ [Code Generator] → Python source code
"""

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

_SRC = Path(__file__).resolve().parent
_UTILS = _SRC.parent / "utils"

for _p in (str(_SRC), str(_UTILS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _load_parser():
    name = "_sarana_parser"
    spec = importlib.util.spec_from_file_location(name, _SRC / "parser.py")
    mod = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError("Cannot load parser.py")
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_parser = _load_parser()
parse = _parser.parse

from colors import Colors  # noqa: E402
from errors import (  # noqa: E402
    LexError,
    ParseError,
    SaranaRuntimeError,
    UnexpectedEndError,
    UnexpectedTokenError,
)
from lexer import Token, tokenize  # noqa: E402
from semantic import analyze  # noqa: E402
from interpreter import interpret  # noqa: E402
from codegen import generate  # noqa: E402


class CompilationResult:
    """
    Encapsulates the results from all compiler phases.
    
    This class provides a structured way to access results from
    lexing, parsing, semantic analysis, interpretation, and code generation.
    """
    
    def __init__(self):
        # Phase 1: Lexical Analysis
        self.tokens: List[Token] = []
        self.lex_errors: List[str] = []
        
        # Phase 2: Syntax Analysis
        self.ast = None
        self.ast_string: str = ""
        self.parse_errors: List[str] = []
        
        # Phase 3: Semantic Analysis
        self.semantic_errors: List[str] = []
        
        # Phase 4a: Interpretation
        self.output: List[str] = []
        self.runtime_errors: List[str] = []
        self.interpreter_success: bool = False
        
        # Phase 4b: Code Generation
        self.generated_code: str = ""
        self.codegen_errors: List[str] = []
        
        # Overall status
        self.success: bool = False
        self.phase_reached: str = ""  # "lexer", "parser", "semantic", "complete"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for easy JSON serialization or UI display.
        
        Returns:
            dict: All results as a dictionary
        """
        return {
            # Tokens
            "tokens": [
                {
                    "type": t.token_type,
                    "value": t.value,
                    "line": t.line
                }
                for t in self.tokens
            ],
            
            # AST
            "ast": self.ast_string,
            
            # Errors
            "lex_errors": self.lex_errors,
            "parse_errors": self.parse_errors,
            "semantic_errors": self.semantic_errors,
            "runtime_errors": self.runtime_errors,
            "codegen_errors": self.codegen_errors,
            
            # Output
            "output": self.output,
            "generated_code": self.generated_code,
            
            # Status
            "success": self.success,
            "phase_reached": self.phase_reached,
            "interpreter_success": self.interpreter_success
        }
    
    def has_errors(self) -> bool:
        """Check if any errors occurred during compilation."""
        return (
            len(self.lex_errors) > 0 or
            len(self.parse_errors) > 0 or
            len(self.semantic_errors) > 0 or
            len(self.runtime_errors) > 0 or
            len(self.codegen_errors) > 0
        )
    
    def get_all_errors(self) -> List[str]:
        """Get all errors from all phases."""
        return (
            self.lex_errors +
            self.parse_errors +
            self.semantic_errors +
            self.runtime_errors +
            self.codegen_errors
        )


def compile_and_run(
    source_code: str,
    generate_target_code: bool = True,
    run_interpreter: bool = True,
    output_file: Optional[str] = None
) -> CompilationResult:
    """
    Main compilation function that runs all compiler phases.
    
    This is the primary API for compiling Sarana programs. It runs the
    lexer, parser, semantic analyzer, and optionally the interpreter
    and code generator.
    
    Args:
        source_code: Sarana source code as a string
        generate_target_code: If True, generate Python code (default: True)
        run_interpreter: If True, run the interpreter (default: True)
        output_file: If provided, save generated code to this file
        
    Returns:
        CompilationResult: Object containing results from all phases
        
    Example:
        >>> from sarana import compile_and_run
        >>> result = compile_and_run('bloom x = 5; echo x;')
        >>> if result.success:
        >>>     print("Output:", result.output)
        >>>     print("Generated:", result.generated_code)
    """
    result = CompilationResult()
    
    # ═════════════════════════════════════════════════════════════════════
    # PHASE 1: LEXICAL ANALYSIS
    # ═════════════════════════════════════════════════════════════════════
    try:
        result.tokens = tokenize(source_code)
        result.phase_reached = "lexer"
        
    except LexError as e:
        result.lex_errors.append(str(e))
        result.phase_reached = "lexer"
        return result
    
    except Exception as e:
        result.lex_errors.append(f"Unexpected lexer error: {e}")
        return result
    
    # ═════════════════════════════════════════════════════════════════════
    # PHASE 2: SYNTAX ANALYSIS
    # ═════════════════════════════════════════════════════════════════════
    try:
        result.ast = parse(source_code)
        result.ast_string = result.ast.rep()
        result.phase_reached = "parser"
        
    except (ParseError, UnexpectedEndError, UnexpectedTokenError) as e:
        result.parse_errors.append(str(e))
        result.phase_reached = "parser"
        return result
    
    except Exception as e:
        result.parse_errors.append(f"Unexpected parser error: {e}")
        return result
    
    # ═════════════════════════════════════════════════════════════════════
    # PHASE 3: SEMANTIC ANALYSIS
    # ═════════════════════════════════════════════════════════════════════
    try:
        semantic_errors = analyze(result.ast)
        result.semantic_errors = [str(e) for e in semantic_errors]
        result.phase_reached = "semantic"
        
        # Don't stop on semantic errors — continue to code generation
        # (semantic errors are warnings, not fatal)
        
    except Exception as e:
        result.semantic_errors.append(f"Unexpected semantic analyzer error: {e}")
        # Continue anyway
    
    # ═════════════════════════════════════════════════════════════════════
    # PHASE 4a: INTERPRETATION (Optional)
    # ═════════════════════════════════════════════════════════════════════
    if run_interpreter:
        try:
            interp_result = interpret(result.ast)
            result.output = interp_result.output
            result.runtime_errors = interp_result.errors
            result.interpreter_success = interp_result.success
            
        except SaranaRuntimeError as e:
            result.runtime_errors.append(str(e))
            result.interpreter_success = False
            
        except Exception as e:
            result.runtime_errors.append(f"Unexpected runtime error: {e}\n{traceback.format_exc()}")
            result.interpreter_success = False
    
    # ═════════════════════════════════════════════════════════════════════
    # PHASE 4b: CODE GENERATION (Optional)
    # ═════════════════════════════════════════════════════════════════════
    if generate_target_code:
        try:
            result.generated_code = generate(result.ast)
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(result.generated_code)
            
        except Exception as e:
            result.codegen_errors.append(f"Code generation error: {e}\n{traceback.format_exc()}")
    
    # ═════════════════════════════════════════════════════════════════════
    # FINAL STATUS
    # ═════════════════════════════════════════════════════════════════════
    result.phase_reached = "complete"
    
    # Success if we made it through all phases without fatal errors
    # (semantic errors are non-fatal warnings)
    result.success = (
        len(result.lex_errors) == 0 and
        len(result.parse_errors) == 0
    )
    
    return result


def compile_file(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> CompilationResult:
    """
    Compile a Sarana source file.
    
    Args:
        input_file: Path to .sara source file
        output_file: Optional path for generated Python code
        verbose: If True, print detailed progress
        
    Returns:
        CompilationResult: Compilation results
    """
    if verbose:
        print(Colors.info("Reading: ") + input_file)
    
    # Read source file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        result = CompilationResult()
        result.lex_errors.append(f"File not found: {input_file}")
        return result
    except Exception as e:
        result = CompilationResult()
        result.lex_errors.append(f"Error reading file: {e}")
        return result
    
    # Determine output file name if not provided
    if output_file is None and input_file.endswith('.sa'):
        output_file = input_file.replace('.sa', '.py')
    
    if verbose:
        print(Colors.info("Compiling..."))
    
    # Compile
    result = compile_and_run(
        source_code,
        generate_target_code=True,
        run_interpreter=True,
        output_file=output_file
    )
    
    if verbose:
        print(Colors.success("Phase reached: ") + result.phase_reached)
        
        if result.has_errors():
            print(Colors.warning("\nErrors found:"))
            for error in result.get_all_errors():
                print(Colors.error(f"   {error}"))
        
        if result.output:
            print(Colors.info("\nOutput:"))
            for line in result.output:
                print(f"   {line}")
        
        if result.generated_code and output_file:
            print(Colors.success(f"\nGenerated code saved to: {output_file}"))
    
    return result


def main():
    """
    Command-line interface for the Sarana compiler.
    
    Usage:
        python sarana.py program.sara
        python sarana.py program.sara --output generated.py
        python sarana.py program.sara --verbose
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sarana Programming Language Compiler',
        epilog='Example: python sarana.py hello.sa'
    )
    
    parser.add_argument(
        'input',
        help='Input .sa source file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output .py file (default: input.py)',
        default=None
    )
    
    parser.add_argument(
        '-v', '--verbose',
        help='Print detailed compilation info',
        action='store_true'
    )
    
    parser.add_argument(
        '--no-run',
        help='Generate code but do not run interpreter',
        action='store_true'
    )
    
    parser.add_argument(
        '--ast-only',
        help='Only print the AST and exit',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Compile the file
    result = compile_file(
        args.input,
        output_file=args.output,
        verbose=args.verbose
    )
    
    # AST-only mode
    if args.ast_only:
        if result.ast_string:
            print(result.ast_string)
        sys.exit(0 if result.success else 1)
    
    # Print output
    if not args.verbose and result.output:
        for line in result.output:
            print(line)
    
    # Print errors
    if result.has_errors():
        print(Colors.error("\nCompilation failed with errors:"), file=sys.stderr)
        for error in result.get_all_errors():
            print(Colors.error(f"  {error}"), file=sys.stderr)
        sys.exit(1)
    
    # Success
    if not args.verbose:
        if args.output or (args.input.endswith('.sa')):
            output_name = args.output or args.input.replace('.sa', '.py')
            print(Colors.success(f"\nCompiled successfully: {output_name}"))
    
    sys.exit(0)


if __name__ == '__main__':
    main()
