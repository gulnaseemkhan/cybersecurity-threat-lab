#!/usr/bin/env python3
import argparse, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
def _cfg():
    p = Path("config/config.json")
    if not p.exists(): return {}
    try:
        with open(p) as f: return json.load(f)
    except: return {}
def _dirs():
    for d in ["lab_data","analysis/data","analysis/hashes","analysis/logs","analysis/pcap","analysis/reports"]:
        Path(d).mkdir(parents=True, exist_ok=True)
def ck(c):
    print("="*50); print("ENVIRONMENT CHECK"); print("="*50)
    v = sys.version_info; print(f"Python: {v.major}.{v.minor}.{v.micro}")
    import platform; print(f"OS: {platform.system()}")
    for d in ["lab_data","analysis","config"]:
        print(f"  {'OK' if Path(d).exists() else 'MISS'}: {d}/")
def sm(c):
    from simulator.simulator import SimulationEngine
    print("\n=== SIMULATION ===")
    e = SimulationEngine()
    ev = e.run_simulation(c.get("simulation",{}).get("max_events",50))
    print(f"\n[OK] {len(ev)} events. ID: {e.simulation_id}")
def mon(c):
    from monitor.monitor import run_monitor
    print("\n=== MONITOR (Ctrl+C) ===")
    run_monitor()
def srv(c):
    from network.local_server import Server
    import time
    print("\n=== SERVER 127.0.0.1:9000 ===")
    s = Server(); s.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: s.stop()
def intel(c):
    from intelligence.scraper import run_collection
    from intelligence.normalizer import run_normalization
    print("\n=== INTEL ===")
    r = run_collection()
    if r:
        print(f"[OK] {r}")
        n = run_normalization()
        if n: print(f"[OK] {n}")
    else: print("[FAIL]")
def ana(c):
    from intelligence.analyzer import run_analysis
    print("\n=== ANALYZE ===")
    r = run_analysis()
    if r: print(f"[OK] Records: {r['total']}, CVEs: {r['cves']}")
    else: print("[FAIL]")
def det(c):
    from detection.detector import run_detection
    print("\n=== DETECT ===")
    a = run_detection()
    if a: print(f"[OK] {len(a)} alerts")
    else: print("[FAIL]")
def rep(c):
    from reporting.report import generate_report
    print("\n=== REPORT ===")
    r = generate_report()
    if r: print(f"[OK] {r}")
    else: print("[FAIL]")
def all_(c):
    print("\n=== COMPLETE WORKFLOW ==="); ck(c)
    print("\n[1] SIMULATE"); sm(c)
    print("\n[2] INTEL"); intel(c)
    print("\n[3] ANALYZE"); ana(c)
    print("\n[4] DETECT"); det(c)
    print("\n[5] REPORT"); rep(c)
    print("\n[OK] DONE")
def main():
    p = argparse.ArgumentParser()
    for f in ["check","simulate","monitor","server","collect-intel","analyze","detect","report","all"]:
        p.add_argument(f"--{f}", action="store_true")
    a = p.parse_args()
    if not any(vars(a).values()): p.print_help(); return 0
    _dirs(); c = _cfg()
    if a.check: ck(c)
    elif a.simulate: sm(c)
    elif a.monitor: mon(c)
    elif a.server: srv(c)
    elif getattr(a, "collect_intel"): intel(c)
    elif a.analyze: ana(c)
    elif a.detect: det(c)
    elif a.report: rep(c)
    elif a.all: all_(c)
    return 0
if __name__ == "__main__":
    sys.exit(main())
