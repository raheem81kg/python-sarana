"""
pages/Language_Docs.py
=======================
Full Sarana language reference — rendered as a dedicated Streamlit page.

Streamlit auto-discovers all files inside app/pages/ and adds them to the
sidebar navigation automatically. Navigate back to the main playground via
the sidebar link.
"""

# import sys
import base64
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Page config — must come first
_icon = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
st.set_page_config(
    page_title="Sarana Language Reference",
    page_icon=str(_icon) if _icon.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Shared CSS (keep in sync with ui.py)
st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .doc-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        padding: 1rem 0 0.25rem 0;
    }
    .doc-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .section-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    code {
        background: #1e293b;
        color: #7dd3fc;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.88rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Logo helper
def get_logo_b64() -> str:
    logo_path = PROJECT_ROOT / "assets" / "NoBackgroundLogo.PNG"
    if logo_path.exists():
        return base64.b64encode(logo_path.read_bytes()).decode()
    return ""


logo_b64 = get_logo_b64()
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" '
    f'style="width:52px;height:52px;border-radius:50%;object-fit:cover;'
    f'margin-right:14px;vertical-align:middle;" />'
    if logo_b64
    else ""
)

st.markdown(
    f"""
<div style="display:flex;align-items:center;margin-bottom:0.25rem;">
    {logo_html}
    <span class="doc-header">Sarana Language Reference</span>
</div>
<p class="doc-subtitle">
    CIT4004 — Analysis of Programming Languages &nbsp;|&nbsp;
    University of Technology, Jamaica &nbsp;|&nbsp; Semester 2, 2025/2026
</p>
""",
    unsafe_allow_html=True,
)

st.divider()

# Load and render LANGUAGE_DOCS.md (root first, then docs/ fallback)
_docs_candidates = (
    PROJECT_ROOT / "LANGUAGE_DOCS.md",
    PROJECT_ROOT / "docs" / "LANGUAGE_DOCS.md",
)
docs_path = next((p for p in _docs_candidates if p.exists()), None)
if docs_path is not None:
    content = docs_path.read_text(encoding="utf-8")

    # Split into sections by h2 headings so each becomes a collapsible section
    import re

    # Find all top-level sections (## heading)
    sections = re.split(r"(?m)^(## .+)$", content)

    # sections[0] is anything before the first ##
    preamble = sections[0].strip()
    if preamble:
        st.markdown(preamble)

    # Pair up headings with their content
    pairs = list(zip(sections[1::2], sections[2::2]))

    # First 3 sections open by default, rest collapsed
    for i, (heading, body) in enumerate(pairs):
        title = heading.lstrip("#").strip()
        with st.expander(title, expanded=(i < 3)):
            st.markdown(body.strip())
else:
    st.error(
        "LANGUAGE_DOCS.md was not found. Add it at the project root "
        f"(expected: {_docs_candidates[0]}) or under docs/."
    )

st.divider()
st.caption(
    "Sarana is built with Python 3 and PLY (Python Lex-Yacc). "
    "Return to the playground using the sidebar navigation."
)
