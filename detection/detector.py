import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from detection.rules import evaluate_rules
from utils.logging_utils import setup_logger, log_event
from utils.timestamps import utc_now
logger = setup_logger("detection", Path("analysis/logs/detection.log"))
_c = 0
def _nid():
    global _c; _c += 1; return f"ALERT-{_c:04d}"
def _load(f):
    ev = []
    if not f.exists(): return ev
    try:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line: continue
                try:
                    e = json.loads(line)
                    if "event_type" in e: ev.append(e)
                except: pass
    except: pass
    return ev
def run_detection():
    logger.info("DETECTION STARTED")
    events = _load(Path("analysis/logs/simulator.log")) + _load(Path("analysis/logs/monitor.log"))
    if not events: return None
    alerts = []
    for e in events:
        for r in evaluate_rules(e):
            a = {"alert_id": _nid(), "timestamp": utc_now(), "rule_id": r.rule_id, "severity": r.severity, "description": r.description, "event": e, "simulation": True, "action": r.action}
            alerts.append(a)
            log_event(logger, 20, f"Alert {r.rule_id}", event_data=a)
    out = Path("analysis/data/alerts.json"); out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump({"generated_at": utc_now(), "count": len(alerts), "simulation": True, "alerts": alerts}, f, indent=2, default=str)
    return alerts
