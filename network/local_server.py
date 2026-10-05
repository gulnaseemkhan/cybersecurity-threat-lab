import json, socket, sys, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging_utils import setup_logger, log_event
logger = setup_logger("network", Path("analysis/logs/network.log"))
class Server:
    def __init__(self, host="127.0.0.1", port=9000):
        if host not in {"127.0.0.1","localhost"}: raise ValueError("Must be localhost")
        self.host=host; self.port=port; self.running=False; self._s=None
    def _h(self, c, a):
        try:
            c.settimeout(5); d=b""
            while len(d)<65536:
                ch=c.recv(4096)
                if not ch: break
                d+=ch
            if d:
                log_event(logger,20,"Telemetry",event_data={"event_type":"TELEMETRY_RECEIVED","source":"SERVER","simulation":True})
                c.sendall(json.dumps({"status":"ok"}).encode())
        except: pass
        finally:
            try: c.close()
            except: pass
    def _loop(self):
        try:
            self._s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self._s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self._s.bind((self.host,self.port)); self._s.listen(5); self._s.settimeout(1)
            logger.info(f"Server on {self.host}:{self.port}")
            while self.running:
                try:
                    c,a=self._s.accept(); threading.Thread(target=self._h,args=(c,a),daemon=True).start()
                except socket.timeout: continue
                except: break
        except Exception as e: logger.error(str(e))
    def start(self):
        self.running=True; threading.Thread(target=self._loop,daemon=True).start(); time.sleep(0.5)
    def stop(self): self.running=False
