"""
Code_Editor.py
==============
Main Streamlit page for the Sarana Language Playground.

This file is the orchestrator — it is intentionally short.
All rendering logic lives in app/components/:
    styles.py   — CSS injection
    header.py   — page header (logo + title)
    sidebar.py  — sidebar controls and sample loader
    results.py  — the six result tabs shown after compilation
"""

import os
import sys
from pathlib import Path

import streamlit as st

# Ensure src/ modules are importable from anywhere.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sarana import compile_and_run  # noqa: E402  # pylint: disable=import-error

from components.styles import render_styles
from components.header import render_header
from components.sidebar import render_sidebar, DEFAULT_CODE
from components.results import (
    render_status_banner,
    tab_output,
    tab_tokens,
    tab_ast,
    tab_semantic,
    tab_codegen,
    tab_llm,
)

# ── Constants ────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_LLM_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

ACE_WIDGET_KEY = "sarana_ace_editor"
EDITOR_VERSION_KEY = "editor_widget_version"
# Clear runs next run before widgets bind; avoids mutating key "code_editor" after text_area.
CLEAR_EDITOR_NEXT_KEY = "_sarana_clear_editor_next"
# Store compilation result to persist across reruns (e.g., when using AI features)
COMPILATION_RESULT_KEY = "_sarana_compilation_result"
COMPILATION_CODE_KEY = "_sarana_compilation_code"


# ── Helpers defined first so they can be called below ────────────────────────

def _bump_editor_version() -> None:
    """Increment the version counter so st_ace remounts with fresh content."""
    st.session_state[EDITOR_VERSION_KEY] = (
        int(st.session_state.get(EDITOR_VERSION_KEY, 0)) + 1
    )


def _render_editor(height_px: int) -> str:
    """Render the code editor. Uses st_ace (line numbers) when available."""
    try:
        from streamlit_ace import st_ace  # optional dependency

        if EDITOR_VERSION_KEY not in st.session_state:
            st.session_state[EDITOR_VERSION_KEY] = 0

        current = st.session_state.get("code_editor", DEFAULT_CODE)
        ver = int(st.session_state[EDITOR_VERSION_KEY])

        edited = st_ace(
            value=current,
            language="plain_text",
            theme="chaos",          # near-black, neutral background
            key=f"{ACE_WIDGET_KEY}_v{ver}",
            height=height_px,
            font_size=14,
            wrap=True,
            show_gutter=True,       # line numbers on the left
            auto_update=True,
        )
        # Ace widget key is not "code_editor"; safe to mirror text for sample/clear logic.
        if edited is not None:
            st.session_state["code_editor"] = edited
        return st.session_state.get("code_editor", DEFAULT_CODE)

    except ImportError:
        # Do not assign session_state["code_editor"] here: Streamlit owns that key
        # when key="code_editor" is used — use the widget return value only.
        return st.text_area(
            "Enter your Sarana code:",
            height=height_px,
            key="code_editor",
            label_visibility="collapsed",
        )


# ── Page configuration ────────────────────────────────────────────────────────
# set_page_config must be the very first Streamlit call.
_icon = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
st.set_page_config(
    page_title="Sarana Language Playground",
    page_icon=str(_icon) if _icon.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize session state for persistence across pages ─────────────────────
# Ensure API key persists when navigating between pages
if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")

# ── CSS ───────────────────────────────────────────────────────────────────────
render_styles()

# ── Header ────────────────────────────────────────────────────────────────────
render_header(PROJECT_ROOT)

# Clear must run before any widget with key "code_editor" is created.
if st.session_state.pop(CLEAR_EDITOR_NEXT_KEY, False):
    st.session_state["code_editor"] = ""
    _bump_editor_version()

# ── Sidebar ───────────────────────────────────────────────────────────────────
settings = render_sidebar(PROJECT_ROOT, EDITOR_VERSION_KEY)

# ── Code editor ───────────────────────────────────────────────────────────────
st.markdown("### Code Editor")
st.caption(
    "Line numbers are shown when `streamlit-ace` is installed "
    "(pip install streamlit-ace)."
)
code = _render_editor(height_px=280)

# ── Run / Clear buttons ───────────────────────────────────────────────────────
col_run, col_clear, _ = st.columns([1, 1, 4])
with col_run:
    run_button = st.button("Run Sarana", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear", use_container_width=True):
        st.session_state[CLEAR_EDITOR_NEXT_KEY] = True
        # Clear compilation results too
        st.session_state.pop(COMPILATION_RESULT_KEY, None)
        st.session_state.pop(COMPILATION_CODE_KEY, None)
        st.rerun()

# ── Compilation and results ───────────────────────────────────────────────────
# Compile when Run button is clicked, or use stored result on reruns
result = None
try:
    if run_button and code.strip():
        with st.spinner("Compiling..."):
            result = compile_and_run(
                code,
                generate_target_code=settings["generate_code"],
                run_interpreter=settings["run_interpreter"],
            )
        # Store result in session state for persistence across reruns
        st.session_state[COMPILATION_RESULT_KEY] = result
        st.session_state[COMPILATION_CODE_KEY] = code
        result = st.session_state[COMPILATION_RESULT_KEY]
    elif COMPILATION_RESULT_KEY in st.session_state:
        # Use stored result on reruns (e.g., when AI buttons are clicked)
        result = st.session_state[COMPILATION_RESULT_KEY]

    # Display results if we have them
    if result:
        render_status_banner(result)

        t1, t2, t3, t4, t5, t6 = st.tabs(
            ["Output", "Tokens", "AST", "Semantic Analysis", "Generated Code", "AI Assistant"]
        )
        with t1:
            tab_output(result, settings["run_interpreter"])
        with t2:
            tab_tokens(result)
        with t3:
            tab_ast(result)
        with t4:
            tab_semantic(result)
        with t5:
            tab_codegen(result, settings["generate_code"])
        with t6:
            tab_llm(
                result,
                code,
                settings["enable_llm"],
                settings.get("gemini_model", DEFAULT_LLM_MODEL),
            )
except Exception as e:
    st.error(f"Error displaying results: {e}")
    import traceback
    st.code(traceback.format_exc())

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#64748b; padding:2rem 0;">'
    "<strong>Sarana Programming Language</strong>"
    "</div>",
    unsafe_allow_html=True,
)
