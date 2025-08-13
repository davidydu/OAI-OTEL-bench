# Generates research-grade charts from the per-trace parquet
# Constraints: no seaborn, one chart per figure, no custom colors.

import os
import math
import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PARQUET = os.getenv("TRACE_SUMMARY_PARQUET", "insights_extraction/trace_insights.parquet")
OUTDIR  = os.getenv("OUTDIR", "insights_extraction/figs")
os.makedirs(OUTDIR, exist_ok=True)

# ---------- Global style (no custom colors) ----------
plt.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

def savefig(path): 
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()

def fmt_int(ax): 
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
def fmt_pct(ax): 
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))

# ---------- Load & order ----------
df = pl.read_parquet(PARQUET)

LEVELS = ["L1", "L2", "L3"]
df = (
    df.with_columns([
        pl.col("question_level").cast(pl.Utf8),
        pl.col("question_level")
          .map_elements(lambda s: 1 if s=="L1" else (2 if s=="L2" else (3 if s=="L3" else 999)), return_dtype=pl.Int64)
          .alias("_lvl")
    ])
    .sort(["_lvl", "trace_rank"])
)

# Roles present (filter to columns that actually exist)
ROLES = ["planner","search","evaluator","writer","judge"]
def existing(cols): 
    cols = [c for c in cols if c in df.columns]
    return cols

TOK_TCOLS = existing([f"{r}_tokens_total"     for r in ROLES])
TOK_RCOLS = existing([f"{r}_tokens_reasoning" for r in ROLES])
DUR_COLS  = existing([f"{r}_duration_ms"      for r in ROLES])

# Basic fields
HAS_TOTAL_TOK = "tokens_total" in df.columns
HAS_TRACE_MS  = "trace_total_duration_ms" in df.columns

# ---------- Aggregates ----------
# Per-level totals (for stacked totals)
agg_exprs = []
if HAS_TOTAL_TOK: agg_exprs.append(pl.col("tokens_total").sum().alias("tokens_total_sum"))
agg_exprs += [pl.col(c).sum().alias(c) for c in TOK_TCOLS + TOK_RCOLS + DUR_COLS]
if HAS_TRACE_MS: agg_exprs.append(pl.col("trace_total_duration_ms").sum().alias("trace_ms_sum"))
agg_exprs.append(pl.len().alias("num_traces"))

agg_tot = df.group_by("question_level").agg(agg_exprs).sort("question_level").to_pandas().set_index("question_level")

# Per-level medians (more robust than sums when counts differ)
med_exprs = []
if HAS_TOTAL_TOK: med_exprs.append(pl.col("tokens_total").median().alias("tokens_total_median"))
med_exprs += [pl.col(c).median().alias(c+"_median") for c in TOK_TCOLS + DUR_COLS]
if HAS_TRACE_MS: med_exprs.append(pl.col("trace_total_duration_ms").median().alias("trace_ms_median"))
agg_med = df.group_by("question_level").agg(med_exprs).sort("question_level").to_pandas().set_index("question_level")

# Convenience pandas frames keyed by LEVELS order
agg_tot = agg_tot.reindex(LEVELS)
agg_med = agg_med.reindex(LEVELS)

# ---------- Chart 1: Tokens by role per level (stacked totals) ----------
if TOK_TCOLS:
    plt.figure(figsize=(7.2, 4.4))
    bottom = np.zeros(len(LEVELS))
    for c in TOK_TCOLS:
        vals = agg_tot[c].values
        plt.bar(LEVELS, vals, bottom=bottom, label=c.replace("_tokens_total",""))
        bottom = bottom + vals
    tot = bottom
    for i, t in enumerate(tot):
        plt.text(i, t, f"{int(t):,}", ha="center", va="bottom", fontsize=9)
    plt.title("Tokens by Role per Level (totals)")
    plt.xlabel("Question Level")
    plt.ylabel("Total Tokens")
    fmt_int(plt.gca())
    plt.legend(title="Role", ncol=min(3, len(TOK_TCOLS)))
    savefig(os.path.join(OUTDIR, "tokens_by_role_per_level_totals.png"))

# ---------- Chart 2: Tokens by role per level (normalized shares) ----------
if TOK_TCOLS:
    plt.figure(figsize=(7.2, 4.4))
    totals = agg_tot[TOK_TCOLS].sum(axis=1).values
    bottom = np.zeros(len(LEVELS))
    for c in TOK_TCOLS:
        share = np.divide(agg_tot[c].values, totals, out=np.zeros_like(totals, dtype=float), where=totals>0) * 100
        plt.bar(LEVELS, share, bottom=bottom, label=c.replace("_tokens_total",""))
        bottom = bottom + share
    plt.title("Token Share by Role per Level (normalized)")
    plt.xlabel("Question Level")
    plt.ylabel("Share (%)")
    fmt_pct(plt.gca())
    plt.legend(title="Role", ncol=min(3, len(TOK_TCOLS)))
    savefig(os.path.join(OUTDIR, "tokens_by_role_per_level_share.png"))

# ---------- Chart 3: Duration by role per level (stacked totals, minutes) ----------
if DUR_COLS:
    plt.figure(figsize=(7.2, 4.4))
    bottom = np.zeros(len(LEVELS))
    for c in DUR_COLS:
        vals_min = agg_tot[c].values / 1000.0 / 60.0
        plt.bar(LEVELS, vals_min, bottom=bottom, label=c.replace("_duration_ms",""))
        bottom = bottom + vals_min
    tot = bottom
    for i, t in enumerate(tot):
        plt.text(i, t, f"{t:,.1f} min", ha="center", va="bottom", fontsize=9)
    plt.title("Duration by Role per Level (totals, minutes)")
    plt.xlabel("Question Level")
    plt.ylabel("Total Minutes")
    fmt_int(plt.gca())
    plt.legend(title="Role", ncol=min(3, len(DUR_COLS)))
    savefig(os.path.join(OUTDIR, "duration_by_role_per_level_minutes.png"))

# ---------- Chart 4: Duration share by role (normalized, minutes) ----------
if DUR_COLS:
    plt.figure(figsize=(7.2, 4.4))
    totals_min = agg_tot[DUR_COLS].sum(axis=1).values / 1000.0 / 60.0
    bottom = np.zeros(len(LEVELS))
    for c in DUR_COLS:
        share = np.divide((agg_tot[c].values / 1000.0 / 60.0), totals_min, out=np.zeros_like(totals_min, dtype=float), where=totals_min>0) * 100
        plt.bar(LEVELS, share, bottom=bottom, label=c.replace("_duration_ms",""))
        bottom = bottom + share
    plt.title("Duration Share by Role per Level (normalized)")
    plt.xlabel("Question Level")
    plt.ylabel("Share (%)")
    fmt_pct(plt.gca())
    plt.legend(title="Role", ncol=min(3, len(DUR_COLS)))
    savefig(os.path.join(OUTDIR, "duration_by_role_per_level_share.png"))

# ---------- Chart 5: Reasoning vs non-reasoning (reasoning roles only) ----------
reason_roles_total = [r+"_tokens_total" for r in ["planner","evaluator","writer","judge"] if r+"_tokens_total" in agg_tot.columns]
reason_roles_reason = [r+"_tokens_reasoning" for r in ["planner","evaluator","writer","judge"] if r+"_tokens_reasoning" in agg_tot.columns]
if reason_roles_total and reason_roles_reason:
    reason_total = agg_tot[reason_roles_total].sum(axis=1).values
    reason_reason = agg_tot[reason_roles_reason].sum(axis=1).values
    reason_other = np.clip(reason_total - reason_reason, 0, None)
    plt.figure(figsize=(7.0, 4.2))
    plt.bar(LEVELS, reason_other, label="non-reasoning")
    plt.bar(LEVELS, reason_reason, bottom=reason_other, label="reasoning")
    for i, (a,b) in enumerate(zip(reason_other, reason_reason)):
        plt.text(i, a+b, f"{int(a+b):,}", ha="center", va="bottom", fontsize=9)
    plt.title("Reasoning vs Non-Reasoning Tokens (planner/evaluator/writer/judge)")
    plt.xlabel("Question Level"); plt.ylabel("Tokens")
    fmt_int(plt.gca())
    plt.legend()
    savefig(os.path.join(OUTDIR, "reasoning_vs_other_tokens_per_level.png"))

# ---------- Chart 6: Tokens vs Duration per trace (scatter, log axes + medians) ----------
if HAS_TOTAL_TOK and HAS_TRACE_MS:
    tp = df.select(["question_level","tokens_total","trace_total_duration_ms"]).to_pandas()
    tp["duration_s"] = tp["trace_total_duration_ms"] / 1000.0

    plt.figure(figsize=(7.0, 4.6))
    eps = 1e-3
    for lvl in LEVELS:
        sub = tp[tp["question_level"] == lvl]
        if not sub.empty:
            sc = plt.scatter(sub["duration_s"] + eps, sub["tokens_total"] + eps,
                            label=lvl, s=12, alpha=0.7)
            col = sc.get_facecolor()[0]  # color used for this level

            # Median lines (same color as points)
            med_x = np.median(sub["duration_s"])
            med_y = np.median(sub["tokens_total"])
            plt.axvline(med_x + eps, linestyle="--", linewidth=1, color=col)
            plt.axhline(med_y + eps, linestyle="--", linewidth=1, color=col)

    plt.xscale("log"); plt.yscale("log")
    plt.title("Tokens vs Duration per Trace (log scale; medians dashed)")
    plt.xlabel("Duration (s, log)"); plt.ylabel("Tokens (log)")
    plt.legend(title="Level")
    savefig(os.path.join(OUTDIR, "tokens_vs_duration_scatter_log.png"))

# ---------- Chart 7: Boxplots — duration by level (seconds, log y) ----------
if HAS_TRACE_MS:
    d = df.select(["question_level","trace_total_duration_ms"]).to_pandas()
    d["duration_s"] = d["trace_total_duration_ms"] / 1000.0
    data = [d[d["question_level"]==lvl]["duration_s"].values for lvl in LEVELS]
    plt.figure(figsize=(6.8, 4.2))
    plt.boxplot(data, labels=LEVELS, showfliers=False)
    plt.yscale("log")
    plt.title("Trace Duration by Level (boxplot, log scale)")
    plt.xlabel("Question Level"); plt.ylabel("Duration (s, log)")
    savefig(os.path.join(OUTDIR, "duration_boxplot_log.png"))

# ---------- Chart 8: Throughput — tokens per minute (boxplot) ----------
if HAS_TOTAL_TOK and HAS_TRACE_MS:
    tpm = df.select(["question_level","tokens_total","trace_total_duration_ms"]).to_pandas()
    tpm["tokens_per_min"] = tpm["tokens_total"] / (tpm["trace_total_duration_ms"]/1000.0/60.0).replace(0, np.nan)
    data = [tpm[tpm["question_level"]==lvl]["tokens_per_min"].dropna().values for lvl in LEVELS]
    plt.figure(figsize=(6.8, 4.2))
    plt.boxplot(data, labels=LEVELS, showfliers=False)
    plt.title("Throughput by Level (tokens per minute)")
    plt.xlabel("Question Level"); plt.ylabel("Tokens / minute")
    fmt_int(plt.gca())
    savefig(os.path.join(OUTDIR, "throughput_tokens_per_min_boxplot.png"))

print("Saved figures in", OUTDIR)
