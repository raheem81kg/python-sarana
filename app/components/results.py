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
    """Tab 6 — Gemini LLM comparison."""
    import google.generativeai as genai  # local import keeps top-level Code_Editor clean

    _section("LLM Comparison - Gemini vs Sarana Compiler")
    st.markdown(
        "**Compiler (Deterministic) vs LLM (Probabilistic)** — "
        "The compiler follows exact grammar rules.  "
        "Gemini interprets code probabilistically."
    )

    api_key = (
        st.session_state.get("gemini_api_key") or ""
    ).strip() or os.environ.get("GEMINI_API_KEY", "").strip()

    if not enable_llm or not api_key:
        _banner(
            "info-msg",
            "Enable <strong>Gemini Comparison</strong> in the sidebar "
            "and enter your API key, or set <code>GEMINI_API_KEY</code> "
            "before starting Streamlit.",
        )
        return

    st.caption(f"Model: `{default_model}` (set GEMINI_MODEL to change)")

    if not st.button("Run Gemini Comparison"):
        return

    try:
        with st.spinner("Asking Gemini..."):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(default_model)
            prompt = (
                "You are executing a program written in Sarana.\n\n"
                "Keyword Mappings:\n"
                "- bloom = variable declaration\n"
                "- echo = print\n"
                "- when = if\n"
                "- otherwise = else\n"
                "- cycle = while\n"
                "- craft = function\n"
                "- return = return\n"
                "- try/ketch = try/catch\n"
                "- true/false = booleans\n"
                "- and/or/not = logical operators\n\n"
                f"Execute this program and show ONLY the output:\n\n{code}\n\nOutput:"
            )
            response = model.generate_content(prompt)
            llm_text = response.text

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Sarana Compiler (Deterministic)**")
            _banner("success-msg", "")
            for line in (result.output or ["(no output)"]):
                st.code(line, language=None)
            st.caption("Always exact — follows grammar rules precisely")
        with col2:
            st.markdown("**Gemini (Probabilistic)**")
            _banner("info-msg", "")
            st.code(llm_text, language=None)
            st.caption("Best guess — interprets code probabilistically")

    except Exception as exc:  # pylint: disable=broad-except
        _banner("error-msg", f"Error calling Gemini API: {str(exc).replace('<', '&lt;')}")


def _first_text_block(response) -> str:
    """Extract text from a Gemini API response."""
    if hasattr(response, "text"):
        return response.text
    return str(response)
