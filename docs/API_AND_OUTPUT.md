# API (LLM) and `output/` folder

## Anthropic / Claude API (web UI)

1. **Where:** `app/Code_Editor.py` — sidebar checkbox “Enable Claude Comparison” and optional API key field.
2. **Flow:**
   - Your Sarana source is compiled locally with `compile_and_run()` (lexer → parser → semantic → interpreter/codegen). That result is **deterministic**.
   - If LLM is enabled, the same source text is sent to **Anthropic’s HTTP API** with a prompt asking the model to predict or simulate output.
   - The UI shows **compiler output** next to **model text** so you can compare formal execution vs. probabilistic answers (course requirement).
3. **Secrets:** Use env var `ANTHROPIC_API_KEY`, or paste in the UI (session only). Never commit keys. Optional: `ANTHROPIC_MODEL` for model id.
4. **Dependency:** `anthropic` package (`requirements.txt`).

There is no separate “Sarana API server” — the only external API is Anthropic’s.

## `output/` directory

Default place to save **generated Python** when you ask the CLI/UI to write a file (e.g. `python3 src/sarana.py program.sa --output output/program.py`). It keeps generated `.py` files out of `src/` and samples. It may be empty until you generate something; `.gitignore` can ignore its contents if you prefer.

## Why `colors.py` stays under `src/` (not `assets/`)

- **`assets/`** is for static files the **browser** uses (e.g. PNG logos in Streamlit).
- **`colors.py`** is **Python code** (ANSI escape sequences for the **terminal**). Moving it to `assets/` would break normal `from colors import Colors` unless you hacked `sys.path`. Keep it next to `sarana.py`.

## `from ast_nodes import *` — what was wrong

- Linters and Pyright **cannot tell** which names exist → false “undefined” warnings.
- It pollutes the namespace and hides typos.
- **Fix:** use explicit imports (`from ast_nodes import Program, BinaryOp, ...`).

## `return visitor(node)` warnings

`getattr(self, "visit_Foo", ...)` is typed as `Any`, so some tools say “not callable”. **Fix:** assign to a variable typed as `Callable` and use `typing.cast`, or call through a local after an `assert callable(...)`.
