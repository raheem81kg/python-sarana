"""
components/header.py
Renders the page header: circular logo inline with the title.
"""

import base64
from pathlib import Path

import streamlit as st


def render_header(project_root: Path) -> None:
    """Show the Sarana logo + title + subtitle at the top of the page."""
    logo_path = project_root / "assets" / "NoBackgroundLogo.PNG"
    subtitle = (
        "A Caribbean-inspired programming language "
        "with bloom, echo, when, and craft"
    )

    if logo_path.exists():
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(
            f"""
<div class="header-container">
    <img src="data:image/png;base64,{logo_b64}" class="logo-img" />
    <div class="header-text">
        <div class="header-title">SARANA LANGUAGE PLAYGROUND</div>
        <div class="header-subtitle">{subtitle}</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="header-title">SARANA LANGUAGE PLAYGROUND</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="header-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )
