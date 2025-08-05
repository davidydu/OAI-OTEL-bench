import pandas as pd, json, numpy as np

# Load the trace file
df = pd.read_parquet("GAIA_self_hosted_agent/logfire_sample_traces.parquet")

# Spans tagged with LLMs
llm_spans = df[df["tags"].apply(lambda x: "LLM" in x if isinstance(x, (list, np.ndarray)) else False)]

records = []
for _, row in llm_spans.iterrows():
    attr = json.loads(row["attributes"])
    # system prompt lives in request_data['messages']
    system_prompt = next((m["content"] for m in attr.get("request_data", {}).get("messages", [])
                          if m.get("role") == "system"), "")
    user_inputs   = [m["content"] for m in attr.get("input", []) if m.get("role") == "user"]
    model_outputs = [m["content"] for m in attr.get("output", [])]
    model_reasoning_content = [m["reasoning_content"] for m in attr.get("output", [])]
    records.append({
        "system_prompt": system_prompt,
        "inputs": user_inputs,
        "outputs": model_outputs,
        "reasoning": model_reasoning_content
    })

# Use records directly, or convert to a DataFrame/JSON
prompt_df = pd.DataFrame(records)
# save as json
prompt_df.to_json("GAIA_self_hosted_agent/parsed_traces.json", orient="records", indent=2)
print(prompt_df.head())
