import json, sys, time, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.timestamps import utc_now
from utils.logging_utils import setup_logger
logger = setup_logger("intel", Path("analysis/logs/analyzer.log"))
URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
def run_collection():
    logger.info("Collecting CISA KEV")
    h = {"User-Agent": "CyberLab/1.0"}
    for i in range(3):
        try:
            req = urllib.request.Request(URL, headers=h)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            out = Path("analysis/data/threat_intelligence.json"); out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w") as f:
                json.dump({"source":"CISA_KEV","collected_at":utc_now(),"data":data}, f, indent=2, default=str)
            return out
        except Exception as e:
            logger.warning(f"Try {i+1}: {e}"); time.sleep(5)
    return None
