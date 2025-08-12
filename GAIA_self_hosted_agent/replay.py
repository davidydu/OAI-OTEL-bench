import torch
import torch.nn.functional as F

# --- global registry to capture data ---
capture_registry = []

def _capture_and_forward(fn_name, orig_fn, *args, **kwargs):
    # run original fn
    out = orig_fn(*args, **kwargs)

    # store input/output in registry; convert to CPU
    def to_cpu(t):
        return t.detach().cpu() if torch.is_tensor(t) else t

    capture_registry.append({
        "op": fn_name,
        "inputs": [to_cpu(x) for x in args],
        "kwargs": {k: to_cpu(v) for k, v in kwargs.items()},
        "outputs": to_cpu(out),
    })

# Use records directly, or convert to a DataFrame/JSON
prompt_df = pd.DataFrame(records)
# save as json
prompt_df.to_json("GAIA_self_hosted_agent/parsed_traces.json", orient="records", indent=2)
print(prompt_df.head())
