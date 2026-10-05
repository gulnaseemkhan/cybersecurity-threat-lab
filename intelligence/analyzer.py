import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.timestamps import utc_now
def run_analysis():
    inp = Path("analysis/data/normalized_intelligence.json")
    if not inp.exists(): return None
    try:
        with open(inp) as f: d = json.load(f)
    except: return None
    r = d.get("records", [])
    if not r: return None
    v = Counter(); c = set()
    for x in r:
        if x.get("vendor"): v[x["vendor"]] += 1
        if x.get("cve"): c.add(x["cve"])
    out = {"analyzed_at":utc_now(),"total":len(r),"cves":len(c),"top_vendors":v.most_common(10)}
    p = Path("analysis/data/intelligence_analysis.json")
    with open(p, "w") as f: json.dump(out, f, indent=2, default=str)
    return out
