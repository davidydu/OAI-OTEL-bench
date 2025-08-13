from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, torch.nn.functional as F
from functools import wraps

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-30B-A3B-Thinking-2507")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-30B-A3B-Thinking-2507")

def replay_call(system_prompt, user_msg):
    prompt = f"<s>[SYSTEM]{system_prompt}[/SYSTEM]\n[USER]{user_msg}[/USER]\n[ASSISTANT]"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    out = model.generate(**inputs, max_new_tokens=500)
    return tokenizer.decode(out[0], skip_special_tokens=True)

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
    return out

# --- patch functions ---
orig_bmm = torch.bmm
orig_matmul = torch.matmul
orig_sdpa = F.scaled_dot_product_attention

def patched_bmm(*args, **kwargs):
    return _capture_and_forward("bmm", orig_bmm, *args, **kwargs)

def patched_matmul(*args, **kwargs):
    return _capture_and_forward("matmul", orig_matmul, *args, **kwargs)

def patched_sdpa(*args, **kwargs):
    return _capture_and_forward("sdpa", orig_sdpa, *args, **kwargs)

torch.bmm = patched_bmm
torch.matmul = patched_matmul
F.scaled_dot_product_attention = patched_sdpa
