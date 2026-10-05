from dataclasses import dataclass
from typing import Callable, Dict, Any
@dataclass
class Rule:
    rule_id: str; severity: str; description: str; condition: Callable; action: str
DETECTION_RULES=[
    Rule("RULE-FILE-001","LOW","New file created",lambda e: e.get("event_type") in ("FILE_CREATE","FILE_CREATE_DETECTED"),"Review file"),
    Rule("RULE-FILE-002","MEDIUM","File hash changed",lambda e: e.get("hash_changed") is True,"Compare hashes"),
    Rule("RULE-PROC-001","LOW","New process observed",lambda e: e.get("event_type") in ("PROCESS_SPAWNED","PROCESS_OBSERVED"),"Review process"),
    Rule("RULE-PROC-002","HIGH","Suspicious process",lambda e: e.get("event_type")=="PROCESS_SPAWNED" and any(p in e.get("cmdline","").lower() for p in ["cmd.exe","powershell","/dev/tcp/","bash -i","netcat"]),"Sandbox review"),
    Rule("RULE-NET-001","LOW","Localhost telemetry",lambda e: e.get("event_type") in ("NETWORK_TELEMETRY","TELEMETRY_RECEIVED"),"Verify source"),
]
def evaluate_rules(e):
    return [r for r in DETECTION_RULES if _safe(r.condition, e)]
def _safe(c, e):
    try: return c(e)
    except: return False
