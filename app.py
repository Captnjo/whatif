"""$1M today vs $10/pushup for life — invested at x% per year."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="$1M vs $10/pushup", layout="wide")
st.title(r"\$1M Today vs \$10 per Pushup for Life")
st.caption("Both portfolios stay invested at the same annual return.")

with st.sidebar:
    st.header("Assumptions")
    annual_return_pct = st.slider("Annual return (%)", 0.0, 20.0, 7.0, 0.1)
    annual_return = annual_return_pct / 100

    st.subheader("Lump sum")
    lump_sum = st.number_input(
        "Day-1 amount ($)", min_value=0, value=1_000_000, step=100_000, format="%d"
    )

    st.subheader("Pushups")
    pushups_per_day = st.number_input("Pushups per day", min_value=0, value=50, step=5)
    dollars_per_pushup = st.number_input(
        "$ per pushup", min_value=0.0, value=10.0, step=0.5
    )
    rest_days_per_week = st.slider("Rest days per week", 0, 7, 0)

    st.subheader("Time horizon")
    current_age = st.number_input("Current age", min_value=0, max_value=120, value=30)
    life_expectancy = st.number_input(
        "Life expectancy", min_value=current_age + 1, max_value=120, value=85
    )

years = life_expectancy - current_age
n_months = years * 12
months = np.arange(0, n_months + 1)
r_monthly = (1 + annual_return) ** (1 / 12) - 1

# Scenario A — lump sum compounded monthly
scenario_a = lump_sum * (1 + r_monthly) ** months

# Scenario B — monthly contributions from pushup income
active_days_per_week = 7 - rest_days_per_week
days_per_month = active_days_per_week * 52 / 12
monthly_contribution = pushups_per_day * dollars_per_pushup * days_per_month

if r_monthly > 0:
    scenario_b = monthly_contribution * (((1 + r_monthly) ** months - 1) / r_monthly)
else:
    scenario_b = monthly_contribution * months

# Headline metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Lump sum at end", f"${scenario_a[-1]:,.0f}")
    st.caption(f"${lump_sum:,.0f} compounded for {years} years")
with col2:
    total_pushups = pushups_per_day * active_days_per_week * 52 * years
    total_contributed = total_pushups * dollars_per_pushup
    st.metric("Pushups at end", f"${scenario_b[-1]:,.0f}")
    st.caption(
        f"{total_pushups:,.0f} pushups · ${total_contributed:,.0f} contributed"
    )
with col3:
    diff = scenario_b[-1] - scenario_a[-1]
    winner = "Pushups" if diff > 0 else "Lump sum"
    st.metric(f"{winner} win by", f"${abs(diff):,.0f}")
    ratio = scenario_b[-1] / scenario_a[-1] if scenario_a[-1] else float("inf")
    st.caption(f"Pushups / Lump sum = {ratio:.2f}×")

# Time-series chart
ages = current_age + months / 12

ctrl1, ctrl2 = st.columns([3, 1])
with ctrl1:
    zoom_years = st.slider(
        "Zoom (years from now)",
        min_value=0.0,
        max_value=float(years),
        value=(0.0, float(years)),
        step=0.5,
    )
with ctrl2:
    log_scale = st.toggle("Log scale", value=False)
    preset = st.selectbox(
        "Preset", ["Custom", "1y", "5y", "10y", "20y", "All"], index=0,
        label_visibility="collapsed",
    )

if preset != "Custom":
    if preset == "All":
        zoom_years = (0.0, float(years))
    else:
        n = float(preset.rstrip("y"))
        zoom_years = (0.0, min(n, float(years)))

mask = (ages >= current_age + zoom_years[0]) & (ages <= current_age + zoom_years[1])
ages_z = ages[mask]
a_z = scenario_a[mask]
b_z = scenario_b[mask]

if log_scale:
    chart_df = pd.DataFrame(
        {
            "Lump sum ($1M day 1)": np.log10(np.maximum(a_z, 1)),
            "Pushups ($10 each)": np.log10(np.maximum(b_z, 1)),
        },
        index=pd.Index(ages_z, name="Age"),
    )
    st.caption("y-axis: log10(portfolio value $)")
else:
    chart_df = pd.DataFrame(
        {
            "Lump sum ($1M day 1)": a_z,
            "Pushups ($10 each)": b_z,
        },
        index=pd.Index(ages_z, name="Age"),
    )
    st.caption(
        f"Window: age {ages_z[0]:.1f} → {ages_z[-1]:.1f} "
        f"({zoom_years[1] - zoom_years[0]:.1f} years)"
    )

st.line_chart(chart_df, height=420)

# Crossover
crossover_idx = np.where(scenario_b >= scenario_a)[0]
if len(crossover_idx):
    m = int(crossover_idx[0])
    cross_age = current_age + m / 12
    st.success(
        f"Pushup portfolio overtakes lump sum at age **{cross_age:.1f}** "
        f"({m / 12:.1f} years in)."
    )
else:
    st.warning("Pushup portfolio never catches the lump sum in this horizon.")

# Sensitivity sweep
with st.expander("Sensitivity to annual return"):
    rates = np.arange(0.0, 0.151, 0.005)
    a_final = lump_sum * (1 + rates) ** years
    rm = (1 + rates) ** (1 / 12) - 1
    with np.errstate(divide="ignore", invalid="ignore"):
        b_final = np.where(
            rm > 0,
            monthly_contribution * (((1 + rm) ** n_months - 1) / np.where(rm > 0, rm, 1)),
            monthly_contribution * n_months,
        )
    sens_df = pd.DataFrame(
        {"Lump sum": a_final, "Pushups": b_final},
        index=pd.Index((rates * 100).round(2), name="Annual return (%)"),
    )
    st.line_chart(sens_df, height=300)
    st.caption(
        "Higher return rates favor whichever side has more capital earlier. "
        "The lump sum dominates at high returns; pushups dominate when returns are modest "
        "and the contribution stream is large."
    )
