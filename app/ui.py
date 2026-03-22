"""
ui.py
=====
Streamlit Web UI for Sarana Programming Language

This provides a professional web interface for the Sarana compiler
with color-coded messages and comprehensive compiler phase visualization.

Run with:
    streamlit run app/ui.py
"""

import sys
import os
from pathlib import Path
import base64
from datetime import datetime

import streamlit as st
import anthropic

# Add src to path before local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sarana import compile_and_run  # noqa: E402  # pylint: disable=import-error


# Project root (parent of app/) so samples/assets work no matter the cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Token table colours (keep legend and pandas styler in sync)
TOKEN_STYLE_KEYWORD = "background-color: #1e40af; color: #dbeafe"
TOKEN_STYLE_LITERAL = "background-color: #92400e; color: #fef3c7"
TOKEN_STYLE_IDENT = "background-color: #15803d; color: #dcfce7"
TOKEN_STYLE_OPERATOR = "background-color: #6b21a8; color: #f3e8ff"

# Default Claude model (override with env ANTHROPIC_MODEL if yours differs)
DEFAULT_LLM_MODEL = os.environ.get(
    "ANTHROPIC_MODEL",
    "claude-3-5-sonnet-20241022",
)

DEFAULT_EDITOR_CODE = """-- Welcome to Sarana!

bloom x = 10;
bloom y = 20;
bloom sum = x + y;

echo "The sum is:" sum;

when (sum > 25) {
    echo "That is a big number!";
}
"""

ACE_WIDGET_KEY = "sarana_ace_editor"
# Bump this when sample/clear loads new text so st_ace remounts (fresh `value`).
EDITOR_VERSION_KEY = "editor_widget_version"


def get_logo_base64():
    """Convert logo to base64 for embedding"""
    logo_file_path = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
    if logo_file_path.exists():
        with open(logo_file_path, "rb") as logo_file:
            return base64.b64encode(logo_file.read()).decode()
    return ""


def _bump_editor_widget():
    """New version = new st_ace instance so `value` updates (sample / clear)."""
    st.session_state[EDITOR_VERSION_KEY] = (
        int(st.session_state.get(EDITOR_VERSION_KEY, 0)) + 1
    )


def _anthropic_first_text_block(message) -> str:
    """First user-visible string from Anthropic `message.content` (typed as a union)."""
    if not getattr(message, "content", None):
        return ""
    block = message.content[0]
    chunk = getattr(block, "text", None)
    if isinstance(chunk, str):
        return chunk
    return str(block)


def render_code_editor(height_px: int) -> str:
    """Code editor with line numbers (streamlit-ace) or plain text_area."""
    try:
        from streamlit_ace import st_ace

        if EDITOR_VERSION_KEY not in st.session_state:
            st.session_state[EDITOR_VERSION_KEY] = 0

        current = st.session_state.get("code_editor", DEFAULT_EDITOR_CODE)
        ver = int(st.session_state[EDITOR_VERSION_KEY])
        # Unique key forces remount when sample changes (see _bump_editor_widget).
        ace_instance_key = f"{ACE_WIDGET_KEY}_v{ver}"
        edited = st_ace(
            value=current,
            language="plain_text",
            # Near-black surface (monokai reads brown; chaos is neutral black)
            theme="chaos",
            key=ace_instance_key,
            height=height_px,
            font_size=14,
            wrap=True,
            show_gutter=True,
            auto_update=True,
        )
        if edited is not None:
            st.session_state.code_editor = edited
        return st.session_state.get("code_editor", DEFAULT_EDITOR_CODE)
    except ImportError:
        code_text = st.text_area(
            "Enter your Sarana code:",
            height=height_px,
            key="code_editor",
            label_visibility="collapsed",
        )
        st.session_state.code_editor = code_text
        return code_text


# Page config
_icon = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
st.set_page_config(
    page_title="Sarana Language Playground",
    page_icon=str(_icon) if _icon.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with professional color coding
st.markdown(
    """
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        margin-bottom: 0;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Notice banners — rounded cards with soft shadow */
    .success-msg {
        padding: 1.1rem 1.35rem;
        background: linear-gradient(145deg, #ecfdf5 0%, #d1fae5 55%, #bbf7d0 100%);
        border: 1px solid rgba(22, 163, 74, 0.35);
        border-radius: 16px;
        margin: 1rem 0;
        color: #14532d;
        box-shadow: 0 6px 20px rgba(22, 163, 74, 0.12),
                    0 2px 6px rgba(0, 0, 0, 0.06);
    }

    .success-msg strong {
        color: #15803d;
    }

    .error-msg {
        padding: 1.1rem 1.35rem;
        background: linear-gradient(145deg, #fef2f2 0%, #fee2e2 50%, #fecaca 100%);
        border: 1px solid rgba(220, 38, 38, 0.35);
        border-radius: 16px;
        margin: 1rem 0;
        color: #7f1d1d;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.1),
                    0 2px 6px rgba(0, 0, 0, 0.06);
    }

    .error-msg strong {
        color: #991b1b;
    }

    .warning-msg {
        padding: 1.1rem 1.35rem;
        background: linear-gradient(145deg, #fffbeb 0%, #fef3c7 55%, #fde68a 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 16px;
        margin: 1rem 0;
        color: #78350f;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.12),
                    0 2px 6px rgba(0, 0, 0, 0.05);
    }

    .warning-msg strong {
        color: #92400e;
    }

    .info-msg {
        padding: 1.1rem 1.35rem;
        background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 55%, #bfdbfe 100%);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 16px;
        margin: 1rem 0;
        color: #1e3a8a;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.1),
                    0 2px 6px rgba(0, 0, 0, 0.05);
    }

    .info-msg strong {
        color: #1e40af;
    }

    /* Hint under “Code Editor” */
    .editor-hint {
        display: inline-block;
        padding: 0.45rem 0.9rem;
        margin: 0.35rem 0 0.75rem 0;
        font-size: 0.85rem;
        color: #cbd5e1;
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid #334155;
        border-radius: 999px;
    }

    /* Code editor (Ace iframe) outer chrome */
    iframe[title="streamlit_ace.streamlit_ace"] {
        border-radius: 14px !important;
    }

    div[data-testid="stIFrame"] {
        background: #000000 !important;
        border: 1px solid #334155;
        border-radius: 14px;
        overflow: hidden;
    }

    /* Compiler status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0 0.5rem;
    }

    .status-success {
        background-color: #dcfce7;
        color: #15803d;
    }

    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
    }

    .status-warning {
        background-color: #fef3c7;
        color: #92400e;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 8px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        background-color: #334155;
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid #475569;
        color: #e2e8f0;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #475569;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }

    /* Code blocks */
    .stCodeBlock {
        border-radius: 6px;
        border: 1px solid #e2e8f0;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }

    /* Section headers in tabs */
    .tab-section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Token table styling */
    .token-keyword { background-color: #1e40af; color: #dbeafe; }
    .token-literal { background-color: #92400e; color: #fef3c7; }
    .token-identifier { background-color: #15803d; color: #dcfce7; }
    .token-operator { background-color: #6b21a8; color: #f3e8ff; }
</style>
""",
    unsafe_allow_html=True,
)

# Header with logo and title on same line
st.markdown(
    """
<style>
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    margin-bottom: 1rem;
}
.logo-img {
    width: 80px !important;
    height: 80px !important;
    border-radius: 50% !important;
    object-fit: cover !important;
    border: 2px solid #3b82f6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    flex-shrink: 0;
}
.header-text {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.header-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0;
    line-height: 1.2;
}
.header-subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
    font-weight: 400;
}
</style>
""",
    unsafe_allow_html=True,
)

logo_path = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
headerSubtitle = (
    "A Caribbean-inspired programming language compiler with "
    "bloom, echo, when, and craft"
)
if logo_path.exists():
    logo_b64 = get_logo_base64()
    st.markdown(
        f"""
    <div class="header-container">
        <img src="data:image/png;base64,{logo_b64}" class="logo-img" />
        <div class="header-text">
            <div class="header-title">SARANA LANGUAGE PLAYGROUND</div>
            <div class="header-subtitle">{headerSubtitle}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="main-header">SARANA LANGUAGE PLAYGROUND</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="subtitle">{headerSubtitle}</div>',
        unsafe_allow_html=True,
    )

# Sidebar
with st.sidebar:
    st.markdown("### Sample Programs")

    sample_options = {
        "Custom Code": None,
        "Sample 1: Required Demo": "samples/sample1.sa",
        "Sample 2: Scope & Binding": "samples/sample2.sa",
        "Sample 3: Functions & Loops": "samples/sample3.sa",
        "Sample 4: Boolean Logic": "samples/sample4.sa",
    }

    if "code_editor" not in st.session_state:
        st.session_state.code_editor = DEFAULT_EDITOR_CODE

    selected_sample = st.selectbox(
        "Choose a sample program:",
        list(sample_options.keys()),
        label_visibility="collapsed",
        key="sample_dropdown",
    )

    # Load file when selection changes (paths from project root, not cwd)
    last_loaded = "last_loaded_sample_choice"
    if last_loaded not in st.session_state:
        st.session_state[last_loaded] = selected_sample
    elif st.session_state[last_loaded] != selected_sample:
        st.session_state[last_loaded] = selected_sample
        if selected_sample != "Custom Code":
            rel = sample_options[selected_sample]
            full_path = PROJECT_ROOT / rel
            try:
                st.session_state.code_editor = full_path.read_text(encoding="utf-8")
            except OSError as exc:
                st.session_state.code_editor = (
                    f"-- Error loading {full_path.name}: {exc}\n"
                )
            _bump_editor_widget()
            st.rerun()
        # Custom Code: keep current editor contents

    st.markdown("---")
    st.markdown("### Compiler Options")

    run_interpreter = st.checkbox("Run Interpreter", value=True)
    generate_code = st.checkbox("Generate Python Code", value=True)

    st.markdown("---")
    st.markdown("### LLM Integration")

    enable_llm = st.checkbox("Enable Claude Comparison", value=False)

    if enable_llm:
        st.text_input(
            "Anthropic API Key",
            type="password",
            key="anthropic_api_key",
            help=(
                "Or set ANTHROPIC_API_KEY in the environment. "
                "Optional: ANTHROPIC_MODEL for model id."
            ),
        )

    st.markdown("---")
    st.markdown("### Language Reference")

    with st.expander("Keywords"):
        st.markdown("""
**Variables & Output:**
- `bloom` - Declare variable
- `echo` - Print output

**Control Flow:**
- `when` / `otherwise` - If/else
- `cycle` - While loop

**Functions:**
- `craft` - Define function
- `return` - Return value

**Error Handling:**
- `try` / `ketch` - Exception handling

**Boolean:**
- `true` / `false` - Booleans
- `and` / `or` / `not` - Logic operators
        """)

    with st.expander("Operators"):
        st.markdown("""
**Arithmetic:**
`+` `-` `*` `/` `%`

**Comparison:**
`==` `!=` `<` `>` `<=` `>=`

**Assignment:**
`=`

**Comments:**
`--` (single line)
        """)

# Main editor
st.markdown("### Code Editor")
st.caption(
    "Editor shows line numbers when `streamlit-ace` is installed "
    "(pip install streamlit-ace)."
)

code = render_code_editor(height_px=280)

# Control buttons
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_button = st.button(
        "Run Sarana",
        type="primary",
        use_container_width=True,
    )
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state.code_editor = ""
    _bump_editor_widget()
    st.rerun()

# Compilation and results
if run_button and code.strip():
    with st.spinner("Compiling..."):
        result = compile_and_run(
            code, generate_target_code=generate_code, run_interpreter=run_interpreter
        )

    # Status banner
    if result.success:
        status_html = f"""
        <div class="success-msg">
            <strong>COMPILATION SUCCESSFUL</strong><br>
            Phase: {result.phase_reached} | Tokens: {len(result.tokens)} |
            Semantic Issues: {len(result.semantic_errors)}
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
    else:
        error_count = len(result.get_all_errors())
        status_html = f"""
        <div class="error-msg">
            <strong>COMPILATION FAILED</strong><br>
            Phase: {result.phase_reached} | Errors: {error_count}
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

    # Display errors
    all_errors = result.get_all_errors()
    if all_errors:
        with st.expander("Errors & Warnings", expanded=True):
            for error in all_errors:
                error_html = f'<div class="error-msg">{error}</div>'
                st.markdown(error_html, unsafe_allow_html=True)

    # Results tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Output",
            "Tokens",
            "AST",
            "Semantic Analysis",
            "Generated Code",
            "LLM Comparison",
        ]
    )

    # TAB 1: Output
    with tab1:
        header = '<div class="tab-section-header">Program Output</div>'
        st.markdown(header, unsafe_allow_html=True)

        if run_interpreter:
            if result.output:
                info_msg = (
                    '<div class="info-msg"><strong>Interpreter Output:</strong></div>'
                )
                st.markdown(info_msg, unsafe_allow_html=True)
                for line in result.output:
                    st.code(line, language=None)
            elif result.interpreter_success:
                success_msg = (
                    '<div class="success-msg">'
                    "Program executed successfully with no output</div>"
                )
                st.markdown(success_msg, unsafe_allow_html=True)
            else:
                warning_msg = (
                    '<div class="warning-msg">'
                    "Program execution failed or produced no output</div>"
                )
                st.markdown(warning_msg, unsafe_allow_html=True)

            if result.runtime_errors:
                st.markdown("**Runtime Errors:**")
                for error in result.runtime_errors:
                    error_html = f'<div class="error-msg">{error}</div>'
                    st.markdown(error_html, unsafe_allow_html=True)
        else:
            info_msg = (
                '<div class="info-msg">'
                "Interpreter disabled. Enable in sidebar to see output."
                "</div>"
            )
            st.markdown(info_msg, unsafe_allow_html=True)

    # TAB 2: Tokens
    with tab2:
        header = '<div class="tab-section-header">Lexical Analysis - Token Stream</div>'
        st.markdown(header, unsafe_allow_html=True)

        st.markdown("""
**What are tokens?** Tokens are the basic building blocks of the
language, produced by the lexer (lexical analyzer). Each token
represents a meaningful unit like a keyword, identifier, operator,
or literal.
        """)

        if result.tokens:
            import pandas as pd

            token_data = {
                "Token Type": [t.token_type for t in result.tokens],
                "Value": [str(t.value) for t in result.tokens],
                "Line": [t.line for t in result.tokens],
            }

            df = pd.DataFrame(token_data)

            def highlight_tokens(row):
                token_type = row["Token Type"]
                keywords = [
                    "BLOOM",
                    "ECHO",
                    "WHEN",
                    "OTHERWISE",
                    "CYCLE",
                    "CRAFT",
                    "RETURN",
                    "TRY",
                    "KETCH",
                ]
                literals = ["INTEGER", "FLOAT", "STRING", "TRUE", "FALSE"]
                operators = ["PLUS", "MINUS", "MULTIPLY", "DIVIDE", "MODULO", "ASSIGN"]

                if token_type in keywords:
                    return [TOKEN_STYLE_KEYWORD] * len(row)
                elif token_type in literals:
                    return [TOKEN_STYLE_LITERAL] * len(row)
                elif token_type == "IDENTIFIER":
                    return [TOKEN_STYLE_IDENT] * len(row)
                elif token_type in operators:
                    return [TOKEN_STYLE_OPERATOR] * len(row)
                else:
                    return [""] * len(row)

            styled_df = df.style.apply(highlight_tokens, axis=1)
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=260,
            )

            st.markdown(f"**Total Tokens:** {len(result.tokens)}")

            # Legend (same colours as the styled table rows)
            st.markdown("**Color Legend:**")
            col1, col2, col3, col4 = st.columns(4)
            chip = "padding: 4px 10px; border-radius: 4px; display: inline-block;"
            col1.markdown(
                f'<span style="{TOKEN_STYLE_KEYWORD}; {chip}">Keywords</span>',
                unsafe_allow_html=True,
            )
            col2.markdown(
                f'<span style="{TOKEN_STYLE_LITERAL}; {chip}">Literals</span>',
                unsafe_allow_html=True,
            )
            col3.markdown(
                f'<span style="{TOKEN_STYLE_IDENT}; {chip}">Identifiers</span>',
                unsafe_allow_html=True,
            )
            col4.markdown(
                f'<span style="{TOKEN_STYLE_OPERATOR}; {chip}">Operators</span>',
                unsafe_allow_html=True,
            )
        else:
            warning = '<div class="warning-msg">No tokens generated</div>'
            st.markdown(warning, unsafe_allow_html=True)

    # TAB 3: AST
    with tab3:
        header = (
            '<div class="tab-section-header">'
            "Syntax Analysis - Abstract Syntax Tree</div>"
        )
        st.markdown(header, unsafe_allow_html=True)

        st.markdown("""
**What is an AST?** The Abstract Syntax Tree is a tree
representation of the program's structure. It shows how the parser
understands your code according to the grammar rules.
        """)

        if result.ast_string:
            st.code(result.ast_string, language=None)

            st.markdown("---")
            info_msg = (
                '<div class="info-msg"><strong>Key Observations:'
                "</strong><br>"
                "- Root node is Program containing all statements<br>"
                "- Operators show PEMDAS structure<br>"
                "- Each node corresponds to a grammar rule</div>"
            )
            st.markdown(info_msg, unsafe_allow_html=True)
        else:
            warning = '<div class="warning-msg">No AST generated</div>'
            st.markdown(warning, unsafe_allow_html=True)

    # TAB 4: Semantic Analysis
    with tab4:
        header = (
            '<div class="tab-section-header">'
            "Semantic Analysis - Static Error Detection</div>"
        )
        st.markdown(header, unsafe_allow_html=True)

        st.markdown("""
**What is semantic analysis?** This phase checks for errors that
are syntactically correct but semantically invalid:
- Using undefined variables
- Type mismatches
- Division by zero
- Calling undefined functions
        """)

        if result.semantic_errors:
            count = len(result.semantic_errors)
            warning = (
                f'<div class="warning-msg"><strong>'
                f"Found {count} semantic issue(s):</strong></div>"
            )
            st.markdown(warning, unsafe_allow_html=True)
            for i, error in enumerate(result.semantic_errors, 1):
                error_html = f'<div class="error-msg">{i}. {error}</div>'
                st.markdown(error_html, unsafe_allow_html=True)
        else:
            success = (
                '<div class="success-msg">No semantic errors found. '
                "Your code is semantically valid.</div>"
            )
            st.markdown(success, unsafe_allow_html=True)

    # TAB 5: Generated Code
    with tab5:
        header = (
            '<div class="tab-section-header">'
            "Target Code Generation - Python Output</div>"
        )
        st.markdown(header, unsafe_allow_html=True)

        st.markdown("""
**What is code generation?** This is the compiler's final phase,
which translates the Sarana AST into executable Python code.
        """)

        if generate_code and result.generated_code:
            st.code(result.generated_code, language="python")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fileName = f"sarana_generated_{timestamp}.py"
            st.download_button(
                label="Download Python Code",
                data=result.generated_code,
                file_name=fileName,
                mime="text/x-python",
            )

            st.markdown("---")
            st.markdown("**Translation Examples:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Sarana**")
                st.code("bloom x = 5;", language=None)
                st.code("echo x;", language=None)
                st.code("when (x > 0) { }", language=None)
            with col2:
                st.markdown("**Python**")
                st.code("x = 5", language="python")
                st.code("print(x)", language="python")
                st.code("if (x > 0):", language="python")
        else:
            InfoMsg = (
                '<div class="info-msg">'
                "Code generation disabled. "
                "Enable in sidebar to see Python output.</div>"
            )
            st.markdown(InfoMsg, unsafe_allow_html=True)

    # TAB 6: LLM Comparison
    with tab6:
        headerMsg = (
            '<div class="tab-section-header">'
            "LLM Comparison - Claude vs Sarana Compiler</div>"
        )
        st.markdown(headerMsg, unsafe_allow_html=True)

        st.markdown("""
**Compiler (Deterministic) vs LLM (Probabilistic)**

This comparison shows how a traditional compiler differs from
an LLM. The compiler follows exact rules and always produces
the same output. The LLM interprets code probabilistically.
        """)

        api_key_resolved = (
            st.session_state.get("anthropic_api_key") or ""
        ).strip() or os.environ.get("ANTHROPIC_API_KEY", "").strip()

        if enable_llm and api_key_resolved:
            st.caption(f"Model: `{DEFAULT_LLM_MODEL}` (set ANTHROPIC_MODEL to change).")
            if st.button("Run Claude Comparison"):
                try:
                    with st.spinner("Asking Claude..."):
                        client = anthropic.Anthropic(api_key=api_key_resolved)

                        prompt = (
                            f"""You are executing a program """
                            f"""written in Sarana.

Keyword Mappings:
- bloom = variable declaration
- echo = print
- when = if
- otherwise = else
- cycle = while
- craft = function
- return = return
- try/ketch = try/catch
- true/false = booleans
- and/or/not = logical operators

Execute this program and show ONLY the output:

{code}

Output:"""
                        )

                        message = client.messages.create(
                            model=DEFAULT_LLM_MODEL,
                            max_tokens=1024,
                            messages=[{"role": "user", "content": prompt}],
                        )

                        llm_output = _anthropic_first_text_block(message)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Sarana Compiler (Deterministic)**")
                        st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                        if result.output:
                            for line in result.output:
                                st.code(line, language=None)
                        else:
                            st.text("(no output)")
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.caption("Always exact - follows grammar rules precisely")

                    with col2:
                        st.markdown("**Claude (Probabilistic)**")
                        st.markdown('<div class="info-msg">', unsafe_allow_html=True)
                        st.code(llm_output, language=None)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.caption("Best guess - interprets code probabilistically")

                except Exception as e:  # pylint: disable=broad-except
                    errMsg = str(e).replace("<", "&lt;")
                    errHtml = (
                        f'<div class="error-msg">Error calling Claude API: {errMsg}</div>'
                    )
                    st.markdown(errHtml, unsafe_allow_html=True)
        else:
            infoMsg = (
                '<div class="info-msg">Enable <strong>Claude Comparison</strong> '
                "in the sidebar and enter your API key, or set the environment "
                "variable <code>ANTHROPIC_API_KEY</code> before starting "
                "Streamlit.</div>"
            )
            st.markdown(infoMsg, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #64748b; padding: 2rem 0;">'
    "<strong>Sarana Programming Language</strong><br>"
    "CIT4004 Analysis of Programming Languages | "
    "University of Technology, Jamaica<br>"
    "<em>A Caribbean-inspired language with bloom, echo, craft, and more</em>"
    "</div>",
    unsafe_allow_html=True,
)
