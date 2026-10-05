import json, logging, random, subprocess, sys, time, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.hashing import calculate_sha256
from utils.logging_utils import setup_logger, log_event
from utils.timestamps import utc_now
logger = setup_logger("simulator", Path("analysis/logs/simulator.log"))
class SimulationEngine:
    def __init__(self, max_events=50):
        self.lab_dir = Path("lab_data"); self.max_events = max_events; self.events = []
        self.simulation_id = str(uuid.uuid4())[:8]
        self.lab_dir.mkdir(parents=True, exist_ok=True)
    def _e(self, et, **kw):
        return {"event_id": str(uuid.uuid4()), "timestamp": utc_now(), "event_type": et, "source": "SIMULATOR", "simulation": True, "simulation_id": self.simulation_id, **kw}
    def _log(self, e):
        log_event(logger, logging.INFO, f"Simulated: {e['event_type']}", event_data=e); self.events.append(e)
    def create_file(self):
        fp = self.lab_dir / f"simulation_{random.randint(1000,9999)}.txt"
        c = f"SIMULATION FILE\n{utc_now()}\n{self.simulation_id}\n"
        try:
            fp.write_text(c, encoding="utf-8")
            e = self._e("FILE_CREATE", path=str(fp), size=len(c), sha256=calculate_sha256(fp))
        except Exception as ex: e = self._e("ERROR", message=str(ex))
        self._log(e); return e
    def modify_file(self):
        ex = list(self.lab_dir.glob("*.txt"))
        if not ex: return self.create_file()
        fp = random.choice(ex); old = calculate_sha256(fp)
        try:
            with open(fp, "a", encoding="utf-8") as f: f.write(f"Mod: {utc_now()}\n")
            new = calculate_sha256(fp)
            e = self._e("FILE_MODIFY", path=str(fp), old_sha256=old, new_sha256=new, hash_changed=old!=new)
        except Exception as ex2: e = self._e("ERROR", message=str(ex2))
        self._log(e); return e
    def read_file(self):
        ex = list(self.lab_dir.glob("*.txt"))
        if not ex:
            self.create_file(); ex = list(self.lab_dir.glob("*.txt"))
        if not ex: return self._e("ERROR", message="No file")
        fp = random.choice(ex)
        try:
            c = fp.read_text(encoding="utf-8"); e = self._e("FILE_READ", path=str(fp), bytes_read=len(c))
        except Exception as ex2: e = self._e("ERROR", message=str(ex2))
        self._log(e); return e
    def calculate_hash(self):
        ex = list(self.lab_dir.glob("*.txt"))
        if not ex:
            self.create_file(); ex = list(self.lab_dir.glob("*.txt"))
        if not ex: return self._e("ERROR", message="No file")
        fp = random.choice(ex); e = self._e("HASH_CALCULATED", path=str(fp), sha256=calculate_sha256(fp))
        self._log(e); return e
    def spawn_process(self):
        cmd = [sys.executable, "-c", "print('SIM')"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            e = self._e("PROCESS_SPAWNED", command=" ".join(cmd), return_code=r.returncode)
        except Exception as ex: e = self._e("ERROR", message=str(ex))
        self._log(e); return e
    def send_telemetry(self):
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3); s.connect(("127.0.0.1", 9000))
                s.sendall(json.dumps({"event":"SIM","simulation":True}).encode())
            e = self._e("NETWORK_TELEMETRY", destination="127.0.0.1:9000")
        except Exception as ex: e = self._e("NETWORK_TELEMETRY_FAILED", error=str(ex))
        self._log(e); return e
    def run_simulation(self, n=None):
        if n is None: n = self.max_events
        logger.info(f"Starting sim {self.simulation_id} ({n} events)")
        gens = [(self.create_file,3),(self.modify_file,2),(self.read_file,2),(self.calculate_hash,2),(self.spawn_process,1),(self.send_telemetry,1)]
        w = []
        for g, wt in gens: w.extend([g]*wt)
        for _ in range(n):
            g = random.choice(w)
            try: g(); time.sleep(random.uniform(0.05, 0.2))
            except Exception as ex: logger.error(str(ex))
        return self.events
