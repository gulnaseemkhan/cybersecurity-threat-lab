import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.timestamps import utc_now, utc_now_compact
def _load(p):
    if not p.exists(): return None
    try:
        with open(p) as f: return json.load(f)
    except: return None
def generate_report():
    sim = []
    if Path("analysis/logs/simulator.log").exists():
        with open("analysis/logs/simulator.log") as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    if "event_type" in e: sim.append(e)
                except: pass
    alerts = []
    ad = _load(Path("analysis/data/alerts.json"))
    if ad: alerts = ad.get("alerts", [])
    et = Counter(e.get("event_type","?") for e in sim)
    rules = Counter(a.get("rule_id","?") for a in alerts)
    L = ["# Cybersecurity Threat Lab - Report", "", f"Generated: {utc_now()}", "", "> SIMULATION ONLY", "", "## Summary", f"- Simulated Events: {len(sim)}", f"- Total Alerts: {len(alerts)}", "", "## Event Types", ""]
    for t, c in sorted(et.items()): L.append(f"- {t}: {c}")
    L += ["", "## Alerts by Rule", ""]
    for r, c in sorted(rules.items()): L.append(f"- {r}: {c}")
    L += ["", "## Note", "All events are SIMULATED. Localhost only. Not real malware."]
    out_dir = Path("analysis/reports"); out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"report_{utc_now_compact()}.md"
    p.write_text("\n".join(L), encoding="utf-8")
    return p
