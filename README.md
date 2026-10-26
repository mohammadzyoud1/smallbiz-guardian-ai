# SmallBiz Guardian AI

> SmallBiz Guardian AI is an educational planning tool. It is not financial, legal, or tax advice.
> A free, mobile-friendly web app where an immigrant-, women-, or low-income-owned small
> business uploads a simple sales and expense spreadsheet and gets a 13-week cash-flow forecast, early
> warnings about financial vulnerabilities, three adjustable (what if )scenarios, and a plain-language explanation
> from an AI agent that only speaks from the numbers.

All testing uses synthetic financial records. No real business data is used.

## What is in the repo

| Folder         | Contents                                                         |
| -------------- | ---------------------------------------------------------------- |
| backend        | Python code: data generator, validator, MLflow logging           |
| data/templates | template v1 (CSV and XLSX) with a filled example                 |
| data/synthetic | Six clean synthetic businesses (18 months of daily transactions) |
| data/messy     | Two deliberately broken files for testing the validator          |
| docs           | decisions.md and later the model card                            |
| tests          | pytest checks on the data files                                  |
| frontend       | Vue 3 dashboard                                                  |

## Run it

    pip install pip install numpy pandas openpyxl python-dotenv groq mlflow ruff pytest
    python backend/make_synthetic.py
    python backend/validate.py
    pytest

## Planned stack

Python, pandas, scikit-learn, MLflow, FastAPI, Docker, GitHub Actions, Vue 3, LLM tool-calling agent (Groq).
