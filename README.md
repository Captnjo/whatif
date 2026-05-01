# whatif

Streamlit toy: $1M today vs $10/pushup for life, both invested at x%/year.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## What it models

- **Scenario A:** lump sum invested on day 1, compounded monthly.
- **Scenario B:** earn `$/pushup × pushups/day` on active days, contribute monthly to the same portfolio.

Editable in the sidebar: annual return, lump-sum size, pushups/day, $/pushup, rest days, current age, life expectancy. Includes a crossover age and a sensitivity sweep across return rates.

## Caveats

Nominal dollars only — no inflation, taxes, or withdrawals. Use the return knob as a real-return proxy if you want to think in today's dollars.
