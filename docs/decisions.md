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

- messy (salon): backend/data/messy/messy1.csv
- messy (Taqueria): backend/data/messy/messy2.csv

## Forecasting setup

### 9. Only full weeks are kept (assumption)

- Decision: the weekly table keeps Monday to Sunday weeks only; the partial first and last weeks are dropped.

### 10. Baselines and backtest (brief, Section 5.2)

- Target: weekly net cash flow. Ending cash = opening balance + running total of net.
- Baselines: naive, 4-week moving average, seasonal naive (52 weeks back, or 4 weeks back when history is under a year).
- Backtest: 4 folds, 13-week test blocks stepping back in time, history never includes its own test block.

### 11. Validation is split in two (assumption)

- Row level (schema.py, parser.py): rejects bad dates, non-numeric and non-positive amounts. Unknown categories become `other` (Appendix A).
- File level (quality.py): duplicates, missing weeks, typo dates more than 3 years from the median, history length.
