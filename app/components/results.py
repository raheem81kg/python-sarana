"""
components/results.py
Renders all six result tabs after the user runs a Sarana program.

Each tab function receives the CompilationResult and any extra settings
it needs, then draws its section of the UI independently.
"""

import os
from datetime import datetime

import streamlit as st

from components.styles import (
    TOKEN_STYLE_IDENT,
    TOKEN_STYLE_KEYWORD,
    TOKEN_STYLE_LITERAL,
    TOKEN_STYLE_OPERATOR,
)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _banner(css_class: str, content: str) -> None:
    """Render a coloured notice banner."""
    st.markdown(
        f'<div class="{css_class}">{content}</div>',
        unsafe_allow_html=True,
    )


def _section(title: str) -> None:
    """Render a tab section header."""
    st.markdown(
        f'<div class="tab-section-header">{title}</div>',
        unsafe_allow_html=True,
    )


# ── Status banner (shown above the tabs) ─────────────────────────────────────

def render_status_banner(result) -> None:
    """Green success or red failure banner shown right after compilation."""
    if result.success:
        _banner(
            "success-msg",
            f"<strong>COMPILATION SUCCESSFUL</strong><br>"
            f"Phase: {result.phase_reached} | "
            f"Tokens: {len(result.tokens)} | "
            f"Semantic Issues: {len(result.semantic_errors)}",
        )
    else:
        error_count = len(result.get_all_errors())
        _banner(
            "error-msg",
            f"<strong>COMPILATION FAILED</strong><br>"
            f"Phase: {result.phase_reached} | Errors: {error_count}",
        )

    # Show every collected error below the status banner.
    all_errors = result.get_all_errors()
    if all_errors:
        with st.expander("Errors & Warnings", expanded=True):
            for err in all_errors:
                _banner("error-msg", err)


# ── Individual tab renderers ─────────────────────────────────────────────────

def tab_output(result, run_interpreter: bool) -> None:
    """Tab 1 — interpreter output."""
    _section("Program Output")

    if not run_interpreter:
        _banner("info-msg", "Interpreter disabled. Enable in sidebar to see output.")
        return

    if result.output:
        _banner("info-msg", "<strong>Interpreter Output:</strong>")
        for line in result.output:
            st.code(line, language=None)
    elif result.interpreter_success:
        _banner("success-msg", "Program executed successfully with no output.")
    else:
        _banner("warning-msg", "Program execution failed or produced no output.")

    if result.runtime_errors:
        st.markdown("**Runtime Errors:**")
        for err in result.runtime_errors:
            _banner("error-msg", err)


def tab_tokens(result) -> None:
    """Tab 2 — token stream from the lexer."""
    import pandas as pd

    _section("Lexical Analysis - Token Stream")
    st.markdown(
        "Tokens are the smallest meaningful units produced by the lexer.  "
        "Each token has a **type**, **value**, and **line number**."
    )

    if not result.tokens:
        _banner("warning-msg", "No tokens generated.")
        return

    keywords = {
        "BLOOM", "ECHO", "WHEN", "OTHERWISE", "CYCLE",
        "CRAFT", "RETURN", "TRY", "KETCH",
    }
    literals = {"INTEGER", "FLOAT", "STRING", "TRUE", "FALSE"}
    operators = {"PLUS", "MINUS", "MULTIPLY", "DIVIDE", "MODULO", "ASSIGN"}

    def highlight(row):
        tt = row["Token Type"]
        if tt in keywords:
            return [TOKEN_STYLE_KEYWORD] * len(row)
        if tt in literals:
            return [TOKEN_STYLE_LITERAL] * len(row)
        if tt == "IDENTIFIER":
            return [TOKEN_STYLE_IDENT] * len(row)
        if tt in operators:
            return [TOKEN_STYLE_OPERATOR] * len(row)
        return [""] * len(row)

    df = pd.DataFrame({
        "Token Type": [t.token_type for t in result.tokens],
        "Value": [str(t.value) for t in result.tokens],
        "Line": [t.line for t in result.tokens],
    })
    
    st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True, height=260)
    st.markdown(f"**Total Tokens:** {len(result.tokens)}")

    # Colour legend chips that match the table.
    chip = "padding:4px 10px; border-radius:4px; display:inline-block;"
    st.markdown("**Color Legend:**")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<span style="{TOKEN_STYLE_KEYWORD};{chip}">Keywords</span>',    unsafe_allow_html=True)
    c2.markdown(f'<span style="{TOKEN_STYLE_LITERAL};{chip}">Literals</span>',    unsafe_allow_html=True)
    c3.markdown(f'<span style="{TOKEN_STYLE_IDENT};{chip}">Identifiers</span>',   unsafe_allow_html=True)
    c4.markdown(f'<span style="{TOKEN_STYLE_OPERATOR};{chip}">Operators</span>',  unsafe_allow_html=True)


def tab_ast(result) -> None:
    """Tab 3 — Abstract Syntax Tree."""
    _section("Syntax Analysis - Abstract Syntax Tree")
    st.markdown(
        "The **AST** is a tree that shows how the parser understood your code. "
        "Each node maps to a grammar rule."
    )

    if result.ast_string:
        st.code(result.ast_string, language=None)
        _banner(
            "info-msg",
            "<strong>Key Observations:</strong><br>"
            "- Root node is Program containing all statements<br>"
            "- Operators reflect PEMDAS precedence<br>"
            "- Each node corresponds to a grammar rule",
        )
    else:
        _banner("warning-msg", "No AST generated.")


def tab_semantic(result) -> None:
    """Tab 4 — semantic analysis errors."""
    _section("Semantic Analysis - Static Error Detection")
    st.markdown(
        "This phase catches errors that are **syntactically correct but logically wrong**: "
        "undefined variables, type mismatches, division by zero, unknown functions."
    )

    if result.semantic_errors:
        count = len(result.semantic_errors)
        _banner("warning-msg", f"<strong>Found {count} semantic issue(s):</strong>")
        for i, err in enumerate(result.semantic_errors, 1):
            _banner("error-msg", f"{i}. {err}")
    else:
        _banner("success-msg", "No semantic errors found. Your code is semantically valid.")


def tab_codegen(result, generate_code: bool) -> None:
    """Tab 5 — generated Python code."""
    _section("Target Code Generation - Python Output")
    st.markdown(
        "The final compiler phase translates the Sarana AST into **executable Python**."
    )

    if not generate_code or not result.generated_code:
        _banner("info-msg", "Code generation disabled. Enable in sidebar to see Python output.")
        return

    st.code(result.generated_code, language="python")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="Download Python Code",
        data=result.generated_code,
        file_name=f"sarana_generated_{timestamp}.py",
        mime="text/x-python",
    )

    st.markdown("---")
    st.markdown("**Translation Examples:**")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Sarana**")
        st.code("bloom x = 5;",    language=None)
        st.code("echo x;",         language=None)
        st.code("when (x > 0) { }", language=None)
    with col2:
        st.markdown("**Python**")
        st.code("x = 5",       language="python")
        st.code("print(x)",    language="python")
        st.code("if (x > 0):", language="python")


def tab_llm(result, code: str, enable_llm: bool, default_model: str) -> None:
    """Tab 6 — Enhanced Gemini AI Assistant with multiple analysis modes."""
    from components.ai_assistant import create_ai_assistant

    _section("AI Assistant - Powered by Gemini")

    st.markdown(
        "### Sarana AI Assistant\n"
        "Get AI-powered insights about your code including execution comparison, "
        "explanations, error analysis, and optimization suggestions."
    )

    api_key = (
        st.session_state.get("gemini_api_key") or ""
    ).strip() or os.environ.get("GEMINI_API_KEY", "").strip()

    if not enable_llm or not api_key:
        _banner(
            "info-msg",
            "Enable <strong>Gemini AI Assistant</strong> in the sidebar "
            "and enter your API key, or set <code>GEMINI_API_KEY</code> "
            "before starting Streamlit.",
        )
        return

    try:
        assistant = create_ai_assistant(api_key=api_key, model_name=default_model)
    except ImportError as exc:
        _banner(
            "error-msg",
            f"{exc}<br>"
            "From the project root run: <code>pip install google-generativeai</code>",
        )
        return
    
    st.caption(f"Model: `{default_model}` (set GEMINI_MODEL to change)")
    
    # AI Mode Selection
    ai_mode = st.radio(
        "Select AI Analysis Mode:",
        options=[
            "execution_comparison",
            "code_explanation", 
            "error_analysis",
            "optimization",
            "generate_example"
        ],
        format_func=lambda x: {
            "execution_comparison": "Execution Comparison (Compiler vs AI)",
            "code_explanation": "Code Explanation",
            "error_analysis": "Error Analysis & Fixes",
            "optimization": "Optimization Suggestions",
            "generate_example": "Generate Example Code",
        }.get(x, x),
        horizontal=True,
        key="ai_mode_radio"
    )

    # Render appropriate UI based on mode
    if ai_mode == "execution_comparison":
        _render_execution_comparison(assistant, result, code)
    elif ai_mode == "code_explanation":
        _render_code_explanation(assistant, code)
    elif ai_mode == "error_analysis":
        _render_error_analysis(assistant, result, code)
    elif ai_mode == "optimization":
        _render_optimization(assistant, code)
    elif ai_mode == "generate_example":
        _render_example_generator(assistant)


def _render_execution_comparison(assistant, result, code: str) -> None:
    """Render the execution comparison UI."""
    st.markdown("---")
    st.markdown("#### Execution Comparison")
    st.markdown(
        "Compare the deterministic compiler output with Gemini's probabilistic interpretation. "
        "This demonstrates the difference between formal compilation and AI reasoning."
    )

    if not st.button("Run Comparison", use_container_width=True, key="run_comparison"):
        return

    try:
        with st.spinner("Gemini is analyzing your code..."):
            ai_result = assistant.compare_with_compiler(
                code=code,
                compiler_output=result.output or [],
                compiler_generated_code=result.generated_code if result.generated_code else None
            )

        if not ai_result.success:
            _banner("error-msg", f"AI Analysis Failed: {ai_result.error_message}")
            return

        # Display comparison results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sarana Compiler (Deterministic)**")
            if result.output:
                for line in result.output:
                    st.code(line, language=None)
            else:
                st.caption("(no output)")
            st.caption("Follows exact grammar rules.")
            
            if result.generated_code:
                with st.expander("Generated Python Code"):
                    st.code(result.generated_code, language="python")

        with col2:
            st.markdown("**Gemini AI (Probabilistic)**")

            # Parse AI response to extract output and reasoning sections
            import re
            
            # Look for the section markers
            output_section_match = re.search(
                r'=== OUTPUT SECTION ===\s*\n?(.*?)\n?(?:=== REASONING SECTION ===|$)',
                ai_result.content,
                re.DOTALL | re.IGNORECASE
            )
            
            reasoning_section_match = re.search(
                r'=== REASONING SECTION ===\s*\n?(.*?)$',
                ai_result.content,
                re.DOTALL | re.IGNORECASE
            )
            
            if output_section_match:
                ai_output = output_section_match.group(1).strip()
                # Remove any markdown code block wrapping if present
                ai_output = re.sub(r'^```\s*\n?', '', ai_output)
                ai_output = re.sub(r'\n?```\s*$', '', ai_output)
            else:
                # Fallback: try to extract from old format or use raw
                ai_output_match = re.search(
                    r'```\n?(.*?)\n?```',
                    ai_result.content,
                    re.DOTALL
                )
                if ai_output_match:
                    ai_output = ai_output_match.group(1).strip()
                else:
                    ai_output = ai_result.content.strip()
            
            # Display AI output line by line like compiler
            if ai_output:
                for line in ai_output.split('\n'):
                    if line.strip():
                        st.code(line, language=None)
            else:
                st.caption("(no output)")
            st.caption("Interpreted by the AI model.")
            
            # Display reasoning in expander
            if reasoning_section_match:
                with st.expander("AI reasoning / notes"):
                    st.markdown(reasoning_section_match.group(1).strip())

        # Analysis summary - compare outputs directly in UI
        st.markdown("---")
        
        # Normalize outputs for comparison (collapse multiple spaces to single)
        import re
        def normalize_line(line):
            # Collapse multiple whitespace to single space, strip ends
            return re.sub(r'\s+', ' ', line.strip())
        
        compiler_lines = [normalize_line(line) for line in (result.output or []) if line.strip()]
        ai_lines = [normalize_line(line) for line in ai_output.split('\n') if line.strip()]
        
        # Check for match
        is_match = compiler_lines == ai_lines
        
        if is_match:
            st.success("MATCH: AI execution matches compiler output exactly.")
        else:
            st.warning("DIFFER: AI interpretation differs from compiler.")

            with st.expander("Difference details", expanded=True):
                col_diff1, col_diff2 = st.columns(2)
                with col_diff1:
                    st.markdown("**Compiler lines:**")
                    for i, line in enumerate(compiler_lines, 1):
                        st.text(f"{i}. {line}")
                with col_diff2:
                    st.markdown("**AI lines:**")
                    for i, line in enumerate(ai_lines[:len(compiler_lines)+5], 1):
                        st.text(f"{i}. {line}")
        
        with st.expander("Analysis details"):
            if ai_result.tokens_used:
                st.caption(f"Tokens used: {ai_result.tokens_used:,}")
            st.markdown(f"- Compiler output lines: {len(compiler_lines)}")
            st.markdown(f"- AI output lines: {len(ai_lines)}")
            st.markdown(f"- Match: {'Yes' if is_match else 'No'}")

    except Exception as exc:
        _banner("error-msg", f"Error: {str(exc).replace('<', '&lt;')}")


def _render_code_explanation(assistant, code: str) -> None:
    """Render the code explanation UI."""
    st.markdown("---")
    st.markdown("#### Code Explanation")
    st.markdown("Get a detailed breakdown of what your code does and how it works.")

    if not st.button("Explain Code", use_container_width=True, key="explain_code"):
        return

    try:
        with st.spinner("Gemini is analyzing your code..."):
            ai_result = assistant.explain_code(code)

        if not ai_result.success:
            _banner("error-msg", f"Analysis Failed: {ai_result.error_message}")
            return

        st.markdown(ai_result.content)

        if ai_result.tokens_used:
            st.caption(f"Tokens used: {ai_result.tokens_used:,}")

    except Exception as exc:
        _banner("error-msg", f"Error: {str(exc).replace('<', '&lt;')}")


def _render_error_analysis(assistant, result, code: str) -> None:
    """Render the error analysis UI."""
    st.markdown("---")
    st.markdown("#### Error Analysis & Fixes")
    
    # Collect all errors
    all_errors = result.get_all_errors()
    
    if not all_errors:
        st.success("No errors detected. Your code compiled successfully.")
        st.markdown(
            "Your code has no errors. You can still run error analysis "
            "on the semantic warnings if any exist."
        )
        errors_to_analyze = result.semantic_errors or []
        phase = "semantic"
    else:
        errors_to_analyze = all_errors
        phase = result.phase_reached if not result.success else "semantic"
        st.error(f"Found {len(all_errors)} error(s) in phase: {phase}")

    if not errors_to_analyze:
        st.info("No errors or warnings to analyze.")
        return

    # Show errors
    with st.expander("Errors/Warnings to Analyze", expanded=True):
        for i, err in enumerate(errors_to_analyze, 1):
            st.error(f"{i}. {err}")

    if not st.button("Analyze & Fix", use_container_width=True, key="analyze_errors"):
        return

    try:
        with st.spinner("Gemini is analyzing errors..."):
            ai_result = assistant.analyze_errors(
                code=code,
                error_messages=errors_to_analyze,
                compilation_phase=phase
            )

        if not ai_result.success:
            _banner("error-msg", f"Analysis Failed: {ai_result.error_message}")
            return

        st.markdown(ai_result.content)

        if ai_result.tokens_used:
            st.caption(f"Tokens used: {ai_result.tokens_used:,}")

    except Exception as exc:
        _banner("error-msg", f"Error: {str(exc).replace('<', '&lt;')}")


def _render_optimization(assistant, code: str) -> None:
    """Render the optimization suggestions UI."""
    st.markdown("---")
    st.markdown("#### Optimization Suggestions")
    st.markdown("Get AI-powered recommendations to improve your code.")

    if not st.button("Get Suggestions", use_container_width=True, key="get_optimizations"):
        return

    try:
        with st.spinner("Gemini is analyzing for optimizations..."):
            ai_result = assistant.suggest_optimizations(code)

        if not ai_result.success:
            _banner("error-msg", f"Analysis Failed: {ai_result.error_message}")
            return

        st.markdown(ai_result.content)

        if ai_result.tokens_used:
            st.caption(f"Tokens used: {ai_result.tokens_used:,}")

    except Exception as exc:
        _banner("error-msg", f"Error: {str(exc).replace('<', '&lt;')}")


def _render_example_generator(assistant) -> None:
    """Render the example generator UI."""
    st.markdown("---")
    st.markdown("#### Generate Example Code")
    st.markdown("Generate Sarana code examples for learning and reference.")

    col1, col2 = st.columns(2)
    
    with col1:
        concept = st.selectbox(
            "Concept to demonstrate:",
            options=[
                "variables_and_arithmetic",
                "conditionals",
                "loops",
                "functions",
                "recursion",
                "exception_handling",
                "arrays",
                "boolean_logic",
                "scope_and_binding",
                "short_circuit_evaluation"
            ],
            format_func=lambda x: x.replace("_", " ").title(),
            key="example_concept"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty level:",
            options=["beginner", "intermediate", "advanced"],
            index=0,
            key="example_difficulty"
        )

    if not st.button("Generate Example", use_container_width=True, key="generate_example"):
        return

    try:
        with st.spinner("Gemini is generating an example..."):
            ai_result = assistant.generate_example(
                concept=concept.replace("_", " "),
                difficulty=difficulty
            )

        if not ai_result.success:
            _banner("error-msg", f"Generation Failed: {ai_result.error_message}")
            return

        st.markdown(ai_result.content)

        if ai_result.tokens_used:
            st.caption(f"Tokens used: {ai_result.tokens_used:,}")

        # Add to editor button
        st.markdown("---")
        if st.button("Copy to Editor", key="copy_example"):
            # Extract code from markdown code blocks
            import re
            code_match = re.search(r'```sarana\n(.*?)\n```', ai_result.content, re.DOTALL)
            if code_match:
                st.session_state["code_editor"] = code_match.group(1)
                st.success("Example copied to editor! Click 'Run Sarana' to execute.")
                st.rerun()
            else:
                st.warning("Could not extract code from response. Please copy manually.")

    except Exception as exc:
        _banner("error-msg", f"Error: {str(exc).replace('<', '&lt;')}")
