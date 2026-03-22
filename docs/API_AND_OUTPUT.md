# API (LLM) and `output/` folder

## Anthropic / Claude API (web UI)

1. **Where:** `app/Code_Editor.py` — sidebar checkbox “Enable Claude Comparison” and optional API key field.
2. **Flow:**
   - Your Sarana source is compiled locally with `compile_and_run()` (lexer → parser → semantic → interpreter/codegen). That result is **deterministic**.
   - If LLM is enabled, the same source text is sent to **Anthropic’s HTTP API** with a prompt asking the model to predict or simulate output.
   - The UI shows **compiler output** next to **model text** so you can compare formal execution vs. probabilistic answers (course requirement).
3. **Secrets:** Use env var `ANTHROPIC_API_KEY`, or paste in the UI (session only). Never commit keys. Optional: `ANTHROPIC_MODEL` for model id.
4. **Dependency:** `anthropic` package (`requirements.txt`).

