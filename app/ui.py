"""
ui.py
=====
Streamlit Web UI for Sarana Programming Language

This provides a professional web interface for the Sarana compiler
with color-coded messages and comprehensive compiler phase visualization.

Run with:
    streamlit run app/ui.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sarana import compile_and_run
import anthropic
from datetime import datetime


def get_logo_base64():
    """Convert logo to base64 for embedding"""
    logo_path = Path("assets/NoBackgroundLogo.PNG")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# Page config
st.set_page_config(
    page_title="Sarana Language Playground",
    page_icon="assets/NoBackgroundLogo.PNG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with professional color coding
st.markdown("""
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
    
    /* Success messages - Green */
    .success-msg {
        padding: 1rem 1.5rem;
        background-color: #dcfce7;
        border-left: 4px solid #16a34a;
        border-radius: 4px;
        margin: 1rem 0;
        color: #14532d;
    }
    
    .success-msg strong {
        color: #15803d;
    }
    
    /* Error messages - Red */
    .error-msg {
        padding: 1rem 1.5rem;
        background-color: #fee2e2;
        border-left: 4px solid #dc2626;
        border-radius: 4px;
        margin: 1rem 0;
        color: #7f1d1d;
    }
    
    .error-msg strong {
        color: #991b1b;
    }
    
    /* Warning messages - Yellow/Orange */
    .warning-msg {
        padding: 1rem 1.5rem;
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 4px;
        margin: 1rem 0;
        color: #78350f;
    }
    
    .warning-msg strong {
        color: #92400e;
    }
    
    /* Info messages - Blue */
    .info-msg {
        padding: 1rem 1.5rem;
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        margin: 1rem 0;
        color: #1e3a8a;
    }
    
    .info-msg strong {
        color: #1e40af;
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
    .token-keyword { background-color: #dbeafe; }
    .token-literal { background-color: #fef3c7; }
    .token-identifier { background-color: #dcfce7; }
    .token-operator { background-color: #f3e8ff; }
</style>
""", unsafe_allow_html=True)

# Header with logo and title on same line
st.markdown("""
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
""", unsafe_allow_html=True)

logo_path = Path("assets/NoBackgroundLogo.PNG")
_header_subtitle = (
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
            <div class="header-subtitle">{_header_subtitle}</div>
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
        f'<div class="subtitle">{_header_subtitle}</div>',
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
        "Sample 4: Boolean Logic": "samples/sample4.sa"
    }
    
    selected_sample = st.selectbox(
        "Choose a sample program:",
        list(sample_options.keys()),
        label_visibility="collapsed"
    )
    
    if selected_sample != "Custom Code":
        sample_path = sample_options[selected_sample]
        try:
            with open(sample_path, 'r') as f:
                sample_code = f.read()
        except:
            sample_code = "-- Error loading sample file"
    else:
        sample_code = """-- Welcome to Sarana!

bloom x = 10;
bloom y = 20;
bloom sum = x + y;

echo "The sum is:" sum;

when (sum > 25) {
    echo "That is a big number!";
}
"""
    
    st.markdown("---")
    st.markdown("### Compiler Options")
    
    run_interpreter = st.checkbox("Run Interpreter", value=True)
    generate_code = st.checkbox("Generate Python Code", value=True)
    
    st.markdown("---")
    st.markdown("### LLM Integration")
    
    enable_llm = st.checkbox("Enable Claude Comparison", value=False)
    
    if enable_llm:
        api_key = st.text_input("Anthropic API Key", type="password")
        if api_key:
            st.session_state['anthropic_key'] = api_key
    
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

code = st.text_area(
    "Enter your Sarana code:",
    value=sample_code,
    height=300,
    key="code_editor",
    label_visibility="collapsed"
)

# Control buttons
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_button = st.button("Run Sarana", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("Clear", use_container_width=True)

if clear_button:
    st.session_state.code_editor = ""
    st.rerun()

# Compilation and results
if run_button and code.strip():
    with st.spinner("Compiling..."):
        result = compile_and_run(
            code,
            generate_target_code=generate_code,
            run_interpreter=run_interpreter
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
                st.markdown(f'<div class="error-msg">{error}</div>', unsafe_allow_html=True)
    
    # Results tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Output",
        "Tokens", 
        "AST",
        "Semantic Analysis",
        "Generated Code",
        "LLM Comparison"
    ])
    
    # TAB 1: Output
    with tab1:
        st.markdown('<div class="tab-section-header">Program Output</div>', unsafe_allow_html=True)
        
        if run_interpreter:
            if result.output:
                st.markdown('<div class="info-msg"><strong>Interpreter Output:</strong></div>', unsafe_allow_html=True)
                for line in result.output:
                    st.code(line, language=None)
            elif result.interpreter_success:
                st.markdown('<div class="success-msg">Program executed successfully with no output</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-msg">Program execution failed or produced no output</div>', unsafe_allow_html=True)
            
            if result.runtime_errors:
                st.markdown("**Runtime Errors:**")
                for error in result.runtime_errors:
                    st.markdown(f'<div class="error-msg">{error}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-msg">Interpreter disabled. Enable in sidebar to see output.</div>', unsafe_allow_html=True)
    
    # TAB 2: Tokens
    with tab2:
        st.markdown('<div class="tab-section-header">Lexical Analysis - Token Stream</div>', unsafe_allow_html=True)
        
        st.markdown("""
**What are tokens?** Tokens are the basic building blocks of the language,
produced by the lexer (lexical analyzer). Each token represents a meaningful
unit like a keyword, identifier, operator, or literal.
        """)
        
        if result.tokens:
            import pandas as pd
            
            token_data = {
                "Token Type": [t.token_type for t in result.tokens],
                "Value": [str(t.value) for t in result.tokens],
                "Line": [t.line for t in result.tokens]
            }
            
            df = pd.DataFrame(token_data)
            
            def highlight_tokens(row):
                token_type = row['Token Type']
                if token_type in ['BLOOM', 'ECHO', 'WHEN', 'OTHERWISE', 'CYCLE', 'CRAFT', 'RETURN', 'TRY', 'KETCH']:
                    return ['background-color: #dbeafe'] * len(row)
                elif token_type in ['INTEGER', 'FLOAT', 'STRING', 'TRUE', 'FALSE']:
                    return ['background-color: #fef3c7'] * len(row)
                elif token_type == 'IDENTIFIER':
                    return ['background-color: #dcfce7'] * len(row)
                elif token_type in ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', 'ASSIGN']:
                    return ['background-color: #f3e8ff'] * len(row)
                else:
                    return [''] * len(row)
            
            st.dataframe(df.style.apply(highlight_tokens, axis=1), use_container_width=True, height=400)
            
            st.markdown(f"**Total Tokens:** {len(result.tokens)}")
            
            # Legend
            st.markdown("**Color Legend:**")
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown('<span style="background-color: #dbeafe; padding: 2px 8px; border-radius: 3px;">Keywords</span>', unsafe_allow_html=True)
            col2.markdown('<span style="background-color: #fef3c7; padding: 2px 8px; border-radius: 3px;">Literals</span>', unsafe_allow_html=True)
            col3.markdown('<span style="background-color: #dcfce7; padding: 2px 8px; border-radius: 3px;">Identifiers</span>', unsafe_allow_html=True)
            col4.markdown('<span style="background-color: #f3e8ff; padding: 2px 8px; border-radius: 3px;">Operators</span>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-msg">No tokens generated</div>', unsafe_allow_html=True)
    
    # TAB 3: AST
    with tab3:
        st.markdown('<div class="tab-section-header">Syntax Analysis - Abstract Syntax Tree</div>', unsafe_allow_html=True)
        
        st.markdown("""
**What is an AST?** The Abstract Syntax Tree is a tree representation of
the program's structure. It shows how the parser understands your code
according to the grammar rules.
        """)
        
        if result.ast_string:
            st.code(result.ast_string, language=None)
            
            st.markdown("---")
            st.markdown('<div class="info-msg"><strong>Key Observations:</strong><br>' +
                       '- Root node is Program containing all statements<br>' +
                       '- Operators show PEMDAS structure<br>' +
                       '- Each node corresponds to a grammar rule</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-msg">No AST generated</div>', unsafe_allow_html=True)
    
    # TAB 4: Semantic Analysis
    with tab4:
        st.markdown('<div class="tab-section-header">Semantic Analysis - Static Error Detection</div>', unsafe_allow_html=True)
        
        st.markdown("""
**What is semantic analysis?** This phase checks for errors that are
syntactically correct but semantically invalid:
- Using undefined variables
- Type mismatches
- Division by zero
- Calling undefined functions
        """)
        
        if result.semantic_errors:
            st.markdown(f'<div class="warning-msg"><strong>Found {len(result.semantic_errors)} semantic issue(s):</strong></div>', unsafe_allow_html=True)
            for i, error in enumerate(result.semantic_errors, 1):
                st.markdown(f'<div class="error-msg">{i}. {error}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-msg">No semantic errors found. Your code is semantically valid.</div>', unsafe_allow_html=True)
    
    # TAB 5: Generated Code
    with tab5:
        st.markdown('<div class="tab-section-header">Target Code Generation - Python Output</div>', unsafe_allow_html=True)
        
        st.markdown("""
**What is code generation?** This is the compiler's final phase, which
translates the Sarana AST into executable Python code.
        """)
        
        if generate_code and result.generated_code:
            st.code(result.generated_code, language="python")
            
            st.download_button(
                label="Download Python Code",
                data=result.generated_code,
                file_name=f"sarana_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                mime="text/x-python"
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
            st.markdown('<div class="info-msg">Code generation disabled. Enable in sidebar to see Python output.</div>', unsafe_allow_html=True)
    
    # TAB 6: LLM Comparison
    with tab6:
        st.markdown('<div class="tab-section-header">LLM Comparison - Claude vs Sarana Compiler</div>', unsafe_allow_html=True)
        
        st.markdown("""
**Compiler (Deterministic) vs LLM (Probabilistic)**

This comparison shows how a traditional compiler differs from an LLM.
The compiler follows exact rules and always produces the same output.
The LLM interprets code probabilistically.
        """)
        
        if enable_llm and 'anthropic_key' in st.session_state:
            if st.button("Run Claude Comparison"):
                try:
                    with st.spinner("Asking Claude..."):
                        client = anthropic.Anthropic(api_key=st.session_state['anthropic_key'])
                        
                        prompt = f"""You are executing a program written in Sarana.

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
                        
                        message = client.messages.create(
                            model="claude-sonnet-4-20250514",
                            max_tokens=1024,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        
                        llm_output = message.content[0].text
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Sarana Compiler (Deterministic)**")
                        st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                        if result.output:
                            for line in result.output:
                                st.code(line, language=None)
                        else:
                            st.text("(no output)")
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.caption("Always exact - follows grammar rules precisely")
                    
                    with col2:
                        st.markdown("**Claude (Probabilistic)**")
                        st.markdown('<div class="info-msg">', unsafe_allow_html=True)
                        st.code(llm_output, language=None)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.caption("Best guess - interprets code probabilistically")
                    
                except Exception as e:
                    st.markdown(f'<div class="error-msg">Error calling Claude API: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-msg">Enable LLM comparison in the sidebar and enter your Anthropic API key.</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem 0;">
    <strong>Sarana Programming Language</strong><br>
    CIT4004 Analysis of Programming Languages | University of Technology, Jamaica<br>
    <em>A Caribbean-inspired language with bloom, echo, craft, and more</em>
</div>
""", unsafe_allow_html=True)
