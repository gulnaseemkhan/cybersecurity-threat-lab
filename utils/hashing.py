import hashlib
from pathlib import Path
def calculate_sha256(p):
    if not p.exists() or not p.is_file(): return None
    h = hashlib.sha256()
    try:
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(8192), b""): h.update(c)
        return h.hexdigest()
    except: return None
def save_hash(p, d):
    fh = calculate_sha256(p)
    if fh is None: return None
    d.mkdir(parents=True, exist_ok=True)
    hf = d / (p.name + ".sha256")
    try:
        with open(hf, "w") as f: f.write(f"{fh}  {p.name}\n")
        return hf
    except: return None
def compare_hashes(a, b):
    return bool(a and b and a.lower() == b.lower())
