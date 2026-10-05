import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.timestamps import utc_now
def run_normalization():
    inp = Path("analysis/data/threat_intelligence.json")
    if not inp.exists(): return None
    try:
        with open(inp) as f: d = json.load(f)
    except: return None
    records = []
    for v in d.get("data", {}).get("vulnerabilities", []):
        if not isinstance(v, dict): continue
        records.append({"source":"CISA_KEV","cve":v.get("cveID",""),"vendor":v.get("vendorProject",""),"product":v.get("product",""),"title":v.get("vulnerabilityName",""),"published":v.get("dateAdded",""),"severity":"HIGH","collected_at":utc_now()})
    out = Path("analysis/data/normalized_intelligence.json")
    with open(out, "w") as f:
        json.dump({"record_count":len(records),"records":records}, f, indent=2, default=str)
    return out
