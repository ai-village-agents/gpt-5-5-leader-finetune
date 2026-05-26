#!/usr/bin/env python3
"""List Tinker-supported models without printing secrets."""
from __future__ import annotations
import os
import sys

if not os.environ.get("TINKER_API_KEY"):
    print("FAIL: TINKER_API_KEY is not present; run via bash -ic or source ~/.bashrc without printing the key")
    sys.exit(1)

try:
    import tinker
except Exception as exc:
    print(f"FAIL: import tinker failed: {exc}")
    sys.exit(1)

client = tinker.ServiceClient()
caps = client.get_server_capabilities()
models = getattr(caps, "supported_models", None) or getattr(caps, "models", None) or []
print(f"models_count: {len(models)}")
for model in models:
    name = getattr(model, "model_name", None) or getattr(model, "name", None) or getattr(model, "id", None) or str(model)
    ctx = getattr(model, "max_context_length", None)
    if ctx is None:
        print(name)
    else:
        print(f"{name}\tctx={ctx}")
