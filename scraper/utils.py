# src/utils.py
import os
import json
import time
import random
from typing import Any, Dict

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def atomic_write_json(path: str, obj: Any):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def atomic_append_lines(path: str, lines):
    ensure_parent = os.path.dirname(path)
    if ensure_parent:
        os.makedirs(ensure_parent, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip("\n") + "\n")

def jitter_backoff(attempt: int, base: float = 1.0, cap: float = 60.0):
    delay = min(cap, base * (2 ** attempt))
    delay = delay * (0.5 + random.random() * 0.5)  
    time.sleep(delay)
