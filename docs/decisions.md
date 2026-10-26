## Stack decisions

### 1. Frontend: Vue 3 + Vite (2026-10-25)

- Decision: Vue 3 with Vite

### 2. Backend: FastAPI (Python) (2026-10-25)

- Decision: FastAPI

### 3. LLM provider: Groq, openai/gpt-oss-20b (2026-10-25)

- Decision: Groq free tier with openai/gpt-oss-20b behind a provider interface.
- Fallbacks: Claude API, then Ollama.

### 4. Python 3.12 in a .venv (2026-10-25)

## Data decisions

### 5. Template settings format (assumption)

- Decision: one "# key=value" line per setting at the top of the CSV (4 lines).

### 6. Synthetic data design (assumptions)

- Window: 2025-01-01 to 2026-06-30 (18 months).
- Supply/inventory purchases are a share of the previous 7 days of sales.
- All amounts are invented: (list three examples, e.g. subsidy, commercial payment, rent)
- Each business uses seed (42) so daily noise is not correlated.

### 7. Opening cash and cushion (assumption, to revisit)

- Values are placeholders, not tuned.

### 8. Messy files

- messy (salon): \_\_\_\_ (list the damage)
