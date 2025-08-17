# Parse ONLY the Parquet and compute per-trace insights with real Levels from metadata.
# Usage:
#   python parse_traces.py --parquet /path/trace_insights.parquet \
#                          --metadata /path/metadata.sorted.jsonl \
#                          --out insights_extraction/validation_trace_insights
import os, json, argparse, re
import polars as pl

TRACK_ROLES = {"planner", "search", "evaluator", "writer", "judge"}
ROLE_KEYWORDS = {
    "planner":   ["planner", "planning"],
    "search":    ["search", "retriev", "browser", "crawl", "scrape", "serp", "web.run", "bing", "google"],
    "evaluator": ["evaluator", "evaluation", "grader", "critic", "reviewer", "scorer", "rater"],
    "writer":    ["writer", "compose", "draft", "synthes"],
    "judge":     ["judge", "arbiter", "referee", "final judge"],
}

def args_():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet",  required=True)
    ap.add_argument("--metadata", required=True, help="metadata.sorted.jsonl with task_id and Level")
    ap.add_argument("--out",      default="insights_extraction/validation_trace_insights")
    return ap.parse_args()

def parse_json_attr(x):
    if x is None or x == "":
        return {}
    if isinstance(x, dict):
        return x
    if isinstance(x, (bytes, bytearray)):
        try:
            return json.loads(x.decode("utf-8", "ignore"))
        except Exception:
            return {}
    try:
        return json.loads(x)
    except Exception:
        return {}

def flatten(d, prefix=""):
    for k, v in (d or {}).items():
        kk = f"{prefix}.{k}"[1:] if prefix else k
        if isinstance(v, dict):
            yield from flatten(v, kk)
        else:
            yield (kk.lower(), v)

def first_num(m, keys):
    for k in keys:
        v = m.get(k)
        if v is None: continue
        if isinstance(v, (int, float)): return int(v)
        if isinstance(v, str):
            try: return int(float(v))
            except Exception: pass
    return None

def extract_token_tuple(attrs_obj):
    a = parse_json_attr(attrs_obj)
    m = dict(flatten(a))

    def get_nested_num(d, path):
        cur = d
        for key in path:
            if not isinstance(cur, dict) or key not in cur: return None
            cur = cur[key]
        if isinstance(cur, (int, float)): return int(cur)
        if isinstance(cur, str):
            try: return int(float(cur))
            except Exception: return None
        return None

    total = first_num(m, [
        "usage.total_tokens","gen_ai.usage.total_tokens",
        "response.usage.total_tokens","response.model_usage.total_tokens",
        "model.usage.total_tokens","token_usage.total","tokens_total"
    ])
    inp = first_num(m, ["usage.input_tokens","gen_ai.usage.input_tokens",
                        "response.usage.input_tokens","token_usage.prompt","input_tokens"]) or 0
    out = first_num(m, ["usage.output_tokens","gen_ai.usage.output_tokens",
                        "response.usage.output_tokens","token_usage.completion","output_tokens"]) or 0
    reasoning = (
        get_nested_num(a, ["response","usage","output_tokens_details","reasoning_tokens"]) or
        get_nested_num(a, ["gen_ai","usage","output_tokens_details","reasoning_tokens"]) or
        get_nested_num(a, ["usage","output_tokens_details","reasoning_tokens"]) or
        get_nested_num(a, ["response","model_usage","output_tokens_details","reasoning_tokens"]) or
        first_num(m, [
            "usage.output_tokens_details.reasoning_tokens",
            "gen_ai.usage.output_tokens_details.reasoning_tokens",
            "response.usage.output_tokens_details.reasoning_tokens",
            "response.model_usage.output_tokens_details.reasoning_tokens",
        ]) or 0
    )
    if total is None: total = inp + out
    return int(total or 0), int(inp), int(out), int(reasoning or 0)

def norm_role_value(s: str) -> str:
    s = (s or "").lower()
    for role, pats in ROLE_KEYWORDS.items():
        if any(p in s for p in pats):
            return role
    return "unknown"

def detect_role_self(attrs: dict, texts: list[str]) -> str:
    for k in ["agent_role","role","agent","agent_name","agent_type","component","module","span_type"]:
        v = attrs.get(k)
        if isinstance(v, str):
            r = norm_role_value(v)
            if r != "unknown": return r
    for v in texts:
        if isinstance(v, str):
            r = norm_role_value(v)
            if r != "unknown": return r
    return "unknown"

def to_dt(df: pl.DataFrame, col: str) -> pl.DataFrame:
    if col in df.columns and df[col].dtype == pl.Utf8:
        return df.with_columns(pl.col(col).str.strptime(pl.Datetime, strict=False).alias(col))
    return df

def normalize_level(x) -> str:
    s = str(x).strip().lower()
    if s in {"1","l1","level1","level 1"}: return "L1"
    if s in {"2","l2","level2","level 2"}: return "L2"
    if s in {"3","l3","level3","level 3"}: return "L3"
    return "UNKNOWN"

def main():
    a = args_()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)

    # ---- Load parquet ----
    df = pl.read_parquet(a.parquet).with_row_index("row_idx")

    for c in ["trace_id","span_id","parent_span_id","attributes","message"]:
        if c not in df.columns:
            raise RuntimeError(f"Missing required column: {c}")

    # Timestamps / duration
    for c in ("start_timestamp","end_timestamp"):
        df = to_dt(df, c)
    if "end_timestamp" in df.columns and df["end_timestamp"].dtype == pl.Datetime and df["start_timestamp"].dtype == pl.Datetime:
        df = df.with_columns([
            (pl.col("end_timestamp") - pl.col("start_timestamp")).dt.total_milliseconds().alias("span_duration_ms"),
            pl.col("end_timestamp").alias("span_end"),
        ])
    else:
        dur_ms_col = None
        for cand in ("duration_ms","duration_millis"):
            if cand in df.columns: dur_ms_col = cand; break
        if dur_ms_col is None and "duration_ns" in df.columns:
            df = df.with_columns((pl.col("duration_ns")/1_000_000).alias("duration_ms")); dur_ms_col = "duration_ms"
        if dur_ms_col is None and "duration" in df.columns:
            df = df.with_columns(
                pl.when(pl.col("duration") > 10_000_000_000).then(pl.col("duration")/1_000_000).otherwise(pl.col("duration")/1_000).alias("duration_ms")
            ); dur_ms_col = "duration_ms"
        if dur_ms_col is None:
            raise RuntimeError("No usable end/duration columns.")
        df = df.with_columns(pl.col(dur_ms_col).alias("span_duration_ms"))

    # Responses API detection
    msg_expr = pl.col("message").cast(pl.Utf8, strict=False).str.to_lowercase().str.contains("responses api", literal=True)
    attr_expr = pl.col("attributes").map_elements(
        lambda x: "responses api" in str(parse_json_attr(x).get("logfire.msg_template","")).lower(),
        return_dtype=pl.Boolean
    )
    df = df.with_columns((msg_expr | attr_expr).alias("is_responses_api"))

    # Self role
    text_keys = [c for c in ["name","span_name","message","otel_scope_name","resource_service_name","service_name"] if c in df.columns]
    df = df.with_columns(
        pl.struct(["attributes", *text_keys]).map_elements(
            lambda s: detect_role_self(parse_json_attr(s.get("attributes")), [s.get(k) for k in text_keys]),
            return_dtype=pl.Utf8
        ).alias("role_self")
    )

    # Resolve role by ancestor walk
    span_ids   = df.get_column("span_id").to_list()
    parent_ids = df.get_column("parent_span_id").to_list()
    roles_self = df.get_column("role_self").to_list()
    parent_map = dict(zip(span_ids, parent_ids))
    role_self_map = dict(zip(span_ids, roles_self))
    def resolve_role(span_id):
        cur = span_id
        for _ in range(5):
            r = role_self_map.get(cur)
            if r in TRACK_ROLES: return r
            cur = parent_map.get(cur)
            if not cur: break
        return "unknown"
    df = df.with_columns(pl.col("span_id").map_elements(resolve_role, return_dtype=pl.Utf8).alias("role"))

    # ---- Map trace_id -> task_id (from first row message) ----
    # First message per trace (guaranteed to include "OpenAI Agents trace: GAIA <uuid>")
    first_rows = (
        df.select(["trace_id","row_idx","message"])
          .sort(["trace_id","row_idx"])
          .group_by("trace_id")
          .agg([
              pl.first("row_idx").alias("first_row_idx"),
              pl.first("message").alias("first_message"),
          ])
          .with_columns(
              pl.col("first_message")
                .cast(pl.Utf8, strict=False)
                .str.extract(r"GAIA\s+([0-9a-fA-F-]{36})", 1)
                .alias("task_id_msg")
          )
    )

    # Fallback: try to grab task_id from first row's attributes if regex failed
    if "attributes" in df.columns:
        first_attrs = (
            df.select(["trace_id","row_idx","attributes"])
              .sort(["trace_id","row_idx"])
              .group_by("trace_id")
              .agg([pl.first("attributes").alias("first_attrs")])
        )
        first_rows = first_rows.join(first_attrs, on="trace_id", how="left").with_columns(
            pl.col("first_attrs").map_elements(
                lambda x: dict(flatten(parse_json_attr(x))).get("task_id") or
                          dict(flatten(parse_json_attr(x))).get("gaia.task_id") or None,
                return_dtype=pl.Utf8
            ).alias("task_id_attr")
        ).with_columns(
            pl.when(pl.col("task_id_msg").is_not_null()).then(pl.col("task_id_msg"))
              .otherwise(pl.col("task_id_attr")).alias("task_id")
        )
    else:
        first_rows = first_rows.rename({"task_id_msg":"task_id"})

    # ---- Load metadata and attach real Level ----
    try:
        meta = pl.read_ndjson(a.metadata)
    except Exception:
        # Fallback simple loader
        rows = []
        with open(a.metadata, "r", encoding="utf-8") as f:
            for line in f:
                try: rows.append(json.loads(line))
                except Exception: pass
        meta = pl.DataFrame(rows)
    for req in ("task_id","Level"):
        if req not in meta.columns:
            raise RuntimeError(f"metadata missing '{req}' field")
    meta = meta.with_columns(pl.col("Level").map_elements(normalize_level, return_dtype=pl.Utf8).alias("question_level"))

    traces = (
        first_rows.select(["trace_id","first_row_idx","task_id"])
                  .join(meta.select(["task_id","question_level"]), on="task_id", how="left")
                  .sort("first_row_idx")
                  .with_row_index("trace_rank", offset=1)
    )

    # Sanity: ensure we resolved all levels
    missing = traces.filter(pl.col("question_level").is_null() | (pl.col("question_level")=="UNKNOWN")).height
    if missing:
        raise RuntimeError(f"Could not resolve Level for {missing} trace(s) — check metadata/task_id extraction.")

    # ---- Tokens ONLY from Responses API spans ----
    df_resp = df.filter(pl.col("is_responses_api")).with_columns([
        pl.col("attributes").map_elements(lambda x: extract_token_tuple(x)[0], return_dtype=pl.Int64).alias("tokens_total"),
        pl.col("attributes").map_elements(lambda x: extract_token_tuple(x)[1], return_dtype=pl.Int64).alias("input_tokens"),
        pl.col("attributes").map_elements(lambda x: extract_token_tuple(x)[2], return_dtype=pl.Int64).alias("output_tokens"),
        pl.col("attributes").map_elements(lambda x: extract_token_tuple(x)[3], return_dtype=pl.Int64).alias("reasoning_tokens"),
    ])
    # search: reasoning = 0
    df_resp = df_resp.with_columns(
        pl.when(pl.col("role")=="search").then(pl.lit(0)).otherwise(pl.col("reasoning_tokens")).alias("reasoning_tokens")
    )

    # (1) Aggregated token usage per trace
    agg_tokens_trace = (df_resp.group_by("trace_id")
        .agg([
            pl.col("tokens_total").sum().alias("tokens_total"),
            pl.col("input_tokens").sum().alias("tokens_input_total"),
            pl.col("output_tokens").sum().alias("tokens_output_total"),
            pl.col("reasoning_tokens").sum().alias("tokens_reasoning_total"),
        ])
    )

    # (2) Per-role token usage
    df_resp_roles = df_resp.filter(pl.col("role").is_in(list(TRACK_ROLES)))
    def pivot_role(df_in: pl.DataFrame, value: str, suffix: str) -> pl.DataFrame:
        out = (df_in.group_by(["trace_id","role"])
               .agg(pl.col(value).sum().alias(value))
               .pivot(index="trace_id", on="role", values=value)
               .fill_null(0))
        for r in TRACK_ROLES:
            if r not in out.columns:
                out = out.with_columns(pl.lit(0).alias(r))
        return out.rename({r: f"{r}_{suffix}" for r in TRACK_ROLES})
    role_tot  = pivot_role(df_resp_roles, "tokens_total",     "tokens_total")
    role_inp  = pivot_role(df_resp_roles, "input_tokens",     "input_tokens")
    role_out  = pivot_role(df_resp_roles, "output_tokens",    "output_tokens")
    role_reas = pivot_role(df_resp_roles, "reasoning_tokens", "tokens_reasoning")

    # (3) Total duration per trace
    trace_bounds = (df.group_by("trace_id")
        .agg([
            pl.col("start_timestamp").min().alias("trace_start"),
            pl.col("end_timestamp").max().alias("trace_end"),
            pl.len().alias("span_count"),
        ])
        .with_columns((pl.col("trace_end") - pl.col("trace_start")).dt.total_milliseconds().alias("trace_total_duration_ms"))
    )

    # (4) Per-role duration
    df_roles = df.filter(pl.col("role").is_in(list(TRACK_ROLES)))
    dur_role = (df_roles.group_by(["trace_id","role"])
        .agg(pl.col("span_duration_ms").sum().alias("role_duration_ms"))
        .pivot(index="trace_id", on="role", values="role_duration_ms")
        .fill_null(0))
    for r in TRACK_ROLES:
        if r not in dur_role.columns:
            dur_role = dur_role.with_columns(pl.lit(0).alias(r))
    dur_role = dur_role.rename({
        "planner":"planner_duration_ms",
        "search":"search_duration_ms",
        "evaluator":"evaluator_duration_ms",
        "writer":"writer_duration_ms",
        "judge":"judge_duration_ms",
    })

    # ---- Merge on ALL traces with real Levels ----
    summary = (traces.select(["trace_id","trace_rank","question_level"])
        .join(trace_bounds,     on="trace_id", how="left")
        .join(agg_tokens_trace, on="trace_id", how="left")
        .join(role_tot,         on="trace_id", how="left")
        .join(role_inp,         on="trace_id", how="left")
        .join(role_out,         on="trace_id", how="left")
        .join(role_reas,        on="trace_id", how="left")
        .join(dur_role,         on="trace_id", how="left")
        .sort("trace_rank")
    )

    # Fill numeric nulls with 0
    num_cols = [c for c in summary.columns if c.endswith("_ms") or "token" in c]
    summary = summary.with_columns([pl.col(c).fill_null(0) for c in num_cols])

    # ---- Write ----
    summary.write_parquet(f"{a.out}.parquet")
    summary.write_csv(f"{a.out}.csv")

    # Sanity
    n_tr = traces.height
    print(f"Unique traces found: {n_tr}")
    print(f"Levels: {summary.select(pl.col('question_level')).unique().to_series().to_list()}")
    print(f"Wrote {a.out}.parquet and {a.out}.csv")

if __name__ == "__main__":
    main()
