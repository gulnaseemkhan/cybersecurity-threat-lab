import os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.hashing import calculate_sha256
from utils.logging_utils import setup_logger, log_event
from utils.timestamps import utc_now
logger = setup_logger("monitor", Path("analysis/logs/monitor.log"))
LAB = Path("lab_data")
class PM:
    def __init__(self):
        self.known=set(); self._init=False
    def scan(self):
        ev=[]
        try: cur={int(e) for e in os.listdir("/proc") if e.isdigit()}
        except: return ev
        if not self._init:
            self.known=cur; self._init=True; return ev
        for p in cur-self.known:
            try:
                c=Path(f"/proc/{p}/cmdline").read_text(errors="replace").replace("\x00"," ").strip()
                if c:
                    e={"timestamp":utc_now(),"event_type":"PROCESS_OBSERVED","source":"MONITOR","simulation":True,"pid":p,"cmdline":c[:200]}
                    ev.append(e); log_event(logger,20,"Proc",event_data=e)
            except: pass
        self.known=cur; return ev
class FM:
    def __init__(self):
        self.state={}; self._init=False
    def _s(self):
        f={}
        for fp in LAB.rglob("*"):
            if fp.is_file():
                try:
                    st=fp.stat(); f[str(fp)]={"m":st.st_mtime,"s":st.st_size,"h":calculate_sha256(fp)}
                except: pass
        return f
    def scan(self):
        ev=[]; cur=self._s()
        if not self._init:
            self.state=cur; self._init=True; return ev
        cp=set(cur.keys()); kp=set(self.state.keys())
        for p in cp-kp:
            e={"timestamp":utc_now(),"event_type":"FILE_CREATE_DETECTED","source":"MONITOR","simulation":True,"path":p}
            ev.append(e); log_event(logger,20,"Created",event_data=e)
        for p in kp-cp:
            e={"timestamp":utc_now(),"event_type":"FILE_DELETE_DETECTED","source":"MONITOR","simulation":True,"path":p}
            ev.append(e); log_event(logger,20,"Deleted",event_data=e)
        for p in cp&kp:
            if self.state[p]["m"]!=cur[p]["m"] or self.state[p]["s"]!=cur[p]["s"]:
                e={"timestamp":utc_now(),"event_type":"FILE_MODIFICATION_DETECTED","source":"MONITOR","simulation":True,"path":p,"hash_changed":self.state[p]["h"]!=cur[p]["h"]}
                ev.append(e); log_event(logger,20,"Modified",event_data=e)
        self.state=cur; return ev
def run_monitor():
    pm=PM(); fm=FM(); logger.info("MONITOR STARTED")
    try:
        while True:
            pm.scan(); fm.scan(); time.sleep(3)
    except KeyboardInterrupt: logger.info("Stopped")
