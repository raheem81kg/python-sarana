"""
components/sidebar.py
Renders the entire sidebar: sample picker, compiler options, LLM toggle,
language reference expanders, and the link to the Language Docs page.
Returns a dict of sidebar settings so Code_Editor.py can use them.
"""

from pathlib import Path

import streamlit as st

SAMPLE_OPTIONS = {
    "Custom Code": None,
    "Sample 1: Required Demo": "samples/sample1.sa",
    "Sample 2: Scope & Binding": "samples/sample2.sa",
    "Sample 3: Functions & Loops": "samples/sample3.sa",
    "Sample 4: Boolean Logic": "samples/sample4.sa",
}

DEFAULT_CODE = """-- Welcome to Sarana!

bloom x = 10;
bloom y = 20;
bloom sum = x + y;

echo "The sum is:" sum;

when (sum > 25) {
    echo "That is a big number!";
}
"""


def _load_sample(project_root: Path, rel_path: str) -> str:
    """Read a sample .sa file and return its text."""
    try:
        return (project_root / rel_path).read_text(encoding="utf-8")
    except OSError as exc:
        return f"-- Error loading sample: {exc}\n"


def _bump_editor(version_key: str) -> None:
    """Increment the editor version so st_ace remounts with fresh content."""
    st.session_state[version_key] = (
        int(st.session_state.get(version_key, 0)) + 1
    )


def render_sidebar(project_root: Path, editor_version_key: str) -> dict:
    """
    Draw the sidebar and return a settings dict with keys:
        run_interpreter  (bool)
        generate_code    (bool)
        enable_llm       (bool)
    """
    settings = {}

    with st.sidebar:

        # ── Sample programs ───────────────────────────────────────────
        st.markdown("### Sample Programs")
        if "code_editor" not in st.session_state:
            st.session_state.code_editor = DEFAULT_CODE

        selected = st.selectbox(
            "Choose a sample program:",
            list(SAMPLE_OPTIONS.keys()),
            label_visibility="collapsed",
            key="sample_dropdown",
        )

        # Only reload the editor when the selection actually changes.
        last_key = "last_loaded_sample_choice"
        if last_key not in st.session_state:
            st.session_state[last_key] = selected
        elif st.session_state[last_key] != selected:
            st.session_state[last_key] = selected
            if selected != "Custom Code":
                rel = SAMPLE_OPTIONS[selected]
                st.session_state.code_editor = _load_sample(project_root, rel)
                _bump_editor(editor_version_key)
                st.rerun()

        st.markdown("---")

        # ── Compiler options ──────────────────────────────────────────
        st.markdown("### Compiler Options")
        settings["run_interpreter"] = st.checkbox("Run Interpreter", value=True)
        settings["generate_code"] = st.checkbox("Generate Python Code", value=True)

        st.markdown("---")

        # ── LLM integration ───────────────────────────────────────────
        st.markdown("### LLM Integration")
        settings["enable_llm"] = st.checkbox("Enable Gemini Comparison", value=False)

        if settings["enable_llm"]:
            st.text_input(
                "Gemini API Key",
                type="password",
                key="gemini_api_key",
                help="Or set GEMINI_API_KEY in your environment.",
            )
            
            GEMINI_MODELS = {
                "gemini-2.5-flash": "Gemini 2.5 Flash (Price-performance, reasoning)",
                "gemini-2.5-flash-lite": "Gemini 2.5 Flash-Lite (Fastest, budget-friendly)",
                "gemini-2.5-flash-live": "Gemini 2.5 Flash Live Preview (Real-time agents)",
                "gemini-2.5-flash-tts": "Gemini 2.5 Flash TTS Preview (Text-to-speech)",
            }
            settings["gemini_model"] = st.selectbox(
                "Model",
                options=list(GEMINI_MODELS.keys()),
                format_func=lambda x: GEMINI_MODELS[x],
                index=0,
                help="Select the Gemini model for comparison",
            )

        st.markdown("---")

        # ── Language reference ────────────────────────────────────────
        st.markdown("### Language Reference")

        with st.expander("Keywords"):
            st.markdown("""
**Variables & Output:**
- `bloom` — Declare variable
- `echo` — Print output

**Control Flow:**
- `when` / `otherwise` — If / else
- `otherwise when` — Else-if chain
- `cycle` — While loop

**Functions:**
- `craft` — Define function
- `return` — Return value

**Error Handling:**
- `try` / `ketch` — Exception handling

**Boolean:**
- `true` / `false` — Booleans
- `and` / `or` / `not` — Logic (short-circuit)

**Comments:**
- `--` — Single-line comment
            """)

        with st.expander("Operators"):
            st.markdown("""
**Arithmetic (PEMDAS):**
`+` `-` `*` `/` `%`

**Comparison:**
`==` `!=` `<` `>` `<=` `>=`

**Assignment:** `=`

**Delimiters:** `{ }` blocks  `( )` expressions  `;` statements
            """)

        with st.expander("Quick Examples"):
            st.code(
                "-- Variables\nbloom x = 42;\n\n"
                "-- Output\necho x;\n\n"
                "-- Conditional\nwhen (x > 10) {\n    echo \"big\";\n}"
                " otherwise {\n    echo \"small\";\n}\n\n"
                "-- Loop\nbloom i = 0;\ncycle (i < 3) {\n    echo i;\n    bloom i = i + 1;\n}\n\n"
                "-- Function\ncraft add(a, b) {\n    return a + b;\n}\necho add(3, 4);",
                language="javascript",
            )

        st.page_link(
            "pages/Language_Docs.py",
            label="Full Language Reference",
            icon=":material/menu_book:",
        )

    return settings
