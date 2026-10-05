import json, logging, sys
from pathlib import Path
from utils.timestamps import utc_now
class F(logging.Formatter):
    def format(self, r):
        e = {"timestamp": utc_now(), "level": r.levelname, "message": r.getMessage()}
        if hasattr(r, "event_data") and r.event_data: e.update(r.event_data)
        return json.dumps(e, default=str)
def setup_logger(name, log_file=None, level=logging.INFO, console=True):
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(level)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8"); fh.setFormatter(F()); logger.addHandler(fh)
    if console:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")); logger.addHandler(ch)
    return logger
def log_event(logger, level, message, event_data=None):
    if event_data is None: event_data = {}
    event_data.setdefault("simulation", True)
    logger.log(level, message, extra={"event_data": event_data})
def read_jsonl(file_path):
    out = []
    if not file_path.exists(): return out
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try: out.append(json.loads(line))
                except: pass
    except: pass
    return out
