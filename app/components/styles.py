import streamlit as st


# Token row colours — used by both the table styler and the colour legend chips.
TOKEN_STYLE_KEYWORD = "background-color: #1e40af; color: #dbeafe"
TOKEN_STYLE_LITERAL = "background-color: #92400e; color: #fef3c7"
TOKEN_STYLE_IDENT = "background-color: #15803d; color: #dcfce7"
TOKEN_STYLE_OPERATOR = "background-color: #6b21a8; color: #f3e8ff"


def render_styles() -> None:
    """Inject all custom CSS into the page."""
    st.markdown(
        """
<style>
    #MainMenu {visibility: hidden;}
    footer    {visibility: hidden;}

    /* ── Page header ────────────────────────────────────────────── */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1rem;
    }
    .logo-img {
        width: 80px; height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0,0,0,.1);
        flex-shrink: 0;
    }
    .header-text    { display: flex; flex-direction: column; gap: .25rem; }
    .header-title   { font-size: 2rem; font-weight: 700; color: #1e3a8a;
                      margin: 0; line-height: 1.2; }
    .header-subtitle{ color: #64748b; font-size: .9rem; margin: 0; }

    /* ── Notice banners ─────────────────────────────────────────── */
    .success-msg, .error-msg, .warning-msg, .info-msg {
        padding: 1.1rem 1.35rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,.06);
    }
    .success-msg {
        background: linear-gradient(145deg,#ecfdf5,#d1fae5,#bbf7d0);
        border: 1px solid rgba(22,163,74,.35);
        color: #14532d;
    }
    .error-msg {
        background: linear-gradient(145deg,#fef2f2,#fee2e2,#fecaca);
        border: 1px solid rgba(220,38,38,.35);
        color: #7f1d1d;
    }
    .warning-msg {
        background: linear-gradient(145deg,#fffbeb,#fef3c7,#fde68a);
        border: 1px solid rgba(245,158,11,.4);
        color: #78350f;
    }
    .info-msg {
        background: linear-gradient(145deg,#eff6ff,#dbeafe,#bfdbfe);
        border: 1px solid rgba(59,130,246,.35);
        color: #1e3a8a;
    }

    /* ── Code editor chrome ─────────────────────────────────────── */
    .editor-hint {
        display: inline-block;
        padding: .45rem .9rem;
        font-size: .85rem; color: #cbd5e1;
        background: rgba(30,41,59,.85);
        border: 1px solid #334155; border-radius: 999px;
        margin: .35rem 0 .75rem;
    }
    iframe[title="streamlit_ace.streamlit_ace"] { border-radius: 14px !important; }
    div[data-testid="stIFrame"] {
        background: #000 !important;
        border: 1px solid #334155; border-radius: 14px; overflow: hidden;
    }

    /* ── Tabs ───────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background-color: #1e293b;
        padding: 8px; border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px; background-color: #334155;
        border-radius: 6px; font-weight: 500;
        border: 1px solid #475569; color: #e2e8f0;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #475569; }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important; border-color: #3b82f6 !important;
    }

    /* ── Misc ───────────────────────────────────────────────────── */
    .tab-section-header {
        font-size: 1.25rem; font-weight: 600; color: #1e293b;
        margin: 1.5rem 0 1rem; padding-bottom: .5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .token-keyword    { background-color:#1e40af; color:#dbeafe; }
    .token-literal    { background-color:#92400e; color:#fef3c7; }
    .token-identifier { background-color:#15803d; color:#dcfce7; }
    .token-operator   { background-color:#6b21a8; color:#f3e8ff; }
</style>
""",
        unsafe_allow_html=True,
    )
