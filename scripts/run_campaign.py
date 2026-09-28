#!/usr/bin/env python3
"""Szimulációs kampány: minden fontos futás egyben, naplózva.

Használat (a repó gyökeréből, aktivált .venv-vel):
    python scripts/run_campaign.py [--id AZONOSÍTÓ] [--jobs N]

Kimenet:
    runs/<id>/logs/<futás>.log      parancs, stdout/stderr, kilépési kód, idő, csúcs-RAM
    runs/<id>/system.txt            gép, verziók
    runs/<id>/tests.log             Rust + Python tesztcsomag
    runs/<id>/campaign.json         a futások listája mérésekkel
    output/campaign/<id>/*.json     a teljes eredmények (gitignore-olt, ~1.3 MB/db;
                                    a szimuláció determinisztikus, újra előállítható)
Az elemzés: python scripts/analyze_campaign.py runs/<id>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
M_SUN = 1.98847e30
M_PLANCK = 2.176434e-8


def campaign() -> list[tuple[str, str, list[str]]]:
    """(csoport, név, CLI-argumentumok)"""
    runs: list[tuple[str, str, list[str]]] = []
    # A. valódi fekete lyukak, mindkét belső modellel
    for obj in ["sgr-a", "m87", "cyg-x1", "gw250114", "gw150914", "pbh-today"]:
        for norbi in ["false", "true"]:
            runs.append(("catalog", f"{obj}_norbi-{norbi}", ["--object", obj, "--norbi-mode", norbi]))
    # B. tömeg-scan a mai CMB-ben és vákuumban
    masses = [2 * M_PLANCK, 1e-6, 1.0, 1e3, 1e6, 1e9, 1e11, 5.1e11, 1e12, 1e15, 1e18,
              1e20, 1e22, 5e22, 7e22, 1e23, 1e25, M_SUN]
    for m in masses:
        runs.append(("mass_cmb", f"m{m:.3g}", ["--mass", repr(m)]))
    for m in masses[:12]:
        runs.append(("mass_vacuum", f"m{m:.3g}", ["--mass", repr(m), "--cmb-temperature", "0"]))
    # C. spin-scan egy primordiális fekete lyukra, két emissziós modellel
    for model in ["MacGibbon", "PageGammaGraviton"]:
        for a in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99, 0.999]:
            runs.append(("spin", f"{model}_a{a}", ["--mass", "1e12", "--spin", str(a),
                                                     "--emission-model", model, "--steps", "300"]))
    # D. emissziós modellek összevetése a ma elpárolgó tömegen
    for model in ["MacGibbon", "PageGammaGraviton", "PhotonBlackbody"]:
        runs.append(("emission", model, ["--mass", "5.1e11", "--emission-model", model]))
    # E. környezet-szcenáriók
    runs += [
        ("environment", "pbh_asteroid_infall",
         ["--mass", "1e12", "--norbi-mode", "true", "--infall", "1e17:1e12:aszteroida"]),
        ("environment", "pbh_two_infalls",
         ["--mass", "1e12", "--infall", "5e16:5e11:kicsi", "--infall", "2e18:2e12:nagy"]),
        ("environment", "stellar_bondi_eddington_100myr",
         ["--mass", repr(10 * M_SUN), "--accretion", "bondi", "--gas-density", "1e-10",
          "--max-time", "3.15576e15"]),
        ("environment", "stellar_disk_spinup_from_0",
         ["--mass", repr(10 * M_SUN), "--accretion", "constant", "--accretion-rate", "1e22",
          "--disk-accretion", "--cmb-temperature", "0", "--max-time", "1.9e10", "--steps", "300"]),
        ("environment", "sun_in_vacuum_10gyr",
         ["--mass", repr(M_SUN), "--cmb-temperature", "0", "--max-time", "3.15576e17"]),
    ]
    # F. konvergencia a lépésszámban
    for steps in [25, 50, 100, 400, 1000]:
        runs.append(("convergence", f"steps{steps}", ["--mass", "1e12", "--steps", str(steps)]))
    return runs


def run_one(py: str, out_dir: Path, log_dir: Path, group: str, name: str,
            args: list[str]) -> dict[str, Any]:
    run_id = f"{group}__{name}"
    out = out_dir / f"{run_id}.json"
    cmd = [py, "-m", "python", *args, "--output", str(out.relative_to(ROOT))]
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    stdout, stderr = proc.communicate()
    wall = time.perf_counter() - t0
    rec = {"id": run_id, "group": group, "name": name, "args": args,
           "exit_code": proc.returncode, "wall_s": round(wall, 3), "output": str(out.relative_to(ROOT))}
    log = [f"$ {' '.join(shlex.quote(c) for c in cmd[1:])}", f"# kilépési kód: {proc.returncode}",
           f"# falióra-idő: {wall:.3f} s", "", "## stdout", stdout.rstrip(), "", "## stderr",
           stderr.rstrip(), ""]
    (log_dir / f"{run_id}.log").write_text("\n".join(log))
    return rec


def measure_peak_rss(py: str, args: list[str], out: Path) -> float:
    """Egy futás csúcs-RSS-e (MB) os.wait4-gyel — a gyermek saját rusage-e."""
    pid = os.fork()
    if pid == 0:
        os.chdir(ROOT)
        fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.execv(py, [py, "-m", "python", *args, "--output", str(out)])
    _, _, usage = os.wait4(pid, 0)
    return usage.ru_maxrss / 1024.0


def system_info(py: str) -> str:
    def sh(cmd: str) -> str:
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT).stdout.strip()
        except OSError as e:
            return f"({e})"

    cpu = sh("lscpu | sed -n 's/^Model name:[[:space:]]*//p'")
    mem = sh("free -h | awk '/^Mem:/{print $2}'")
    return "\n".join([
        f"dátum:     {dt.datetime.now(dt.UTC).isoformat(timespec='seconds')}",
        f"os:        {sh('. /etc/os-release && echo $PRETTY_NAME')} ({platform.release()})",
        f"cpu:       {cpu}",
        f"magok:     {os.cpu_count()}",
        f"memória:   {mem}",
        f"python:    {sh(py + ' --version')}",
        f"rustc:     {sh('rustc --version')}",
        f"commit:    {sh('git rev-parse --short HEAD')} ({sh('git log -1 --format=%s')[:90]})",
    ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", default=dt.datetime.now(dt.UTC).date().isoformat())
    ap.add_argument("--jobs", type=int, default=1, help="párhuzamos futások (alap: 1, a futási idő méréséhez)")
    ap.add_argument("--skip-tests", action="store_true")
    a = ap.parse_args()

    # repó-relatív útvonalak, hogy a naplókban ne legyen gépfüggő abszolút útvonal
    py = ".venv/bin/python3" if (ROOT / ".venv").exists() else sys.executable
    run_dir = ROOT / "runs" / a.id
    log_dir = run_dir / "logs"
    out_dir = ROOT / "output" / "campaign" / a.id
    log_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "system.txt").write_text(system_info(py) + "\n")
    print((run_dir / "system.txt").read_text())

    if not a.skip_tests:
        print("Tesztcsomag…")
        parts = []
        for title, cmd in [("Rust", "cargo test --manifest-path core/Cargo.toml --quiet"),
                           ("Python", f"{py} -m pytest python/tests -q")]:
            t0 = time.perf_counter()
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
            parts.append(f"## {title}: `{cmd}` — kilépési kód {r.returncode}, "
                         f"{time.perf_counter() - t0:.1f} s\n\n{(r.stdout + r.stderr).strip()}\n")
        (run_dir / "tests.log").write_text("\n".join(parts))

    runs = campaign()
    print(f"{len(runs)} futás, {a.jobs} párhuzamosan…")
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        records = list(ex.map(lambda r: run_one(py, out_dir, log_dir, *r), runs))
    total = time.perf_counter() - t0
    for r in records:
        mark = "ok " if r["exit_code"] == 0 else "HIBA"
        print(f"  [{mark}] {r['id']:<55} {r['wall_s']:6.2f} s")

    # csúcs-RAM néhány jellemző futásra (os.wait4 → a gyermek saját rusage-e)
    rss = {}
    for key, args in [("sgr-a", ["--object", "sgr-a"]), ("m87_norbi", ["--object", "m87", "--norbi-mode", "true"]),
                      ("spin_pbh_300", ["--mass", "1e12", "--spin", "0.99", "--steps", "300"])]:
        rss[key] = round(measure_peak_rss(py, args, out_dir / f"_rss_{key}.json"), 1)
        (out_dir / f"_rss_{key}.json").unlink(missing_ok=True)

    meta = {"id": a.id, "jobs": a.jobs, "total_wall_s": round(total, 2), "peak_rss_mb": rss,
            "runs": records}
    (run_dir / "campaign.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    failed = [r["id"] for r in records if r["exit_code"] != 0]
    print(f"Kész: {total:.1f} s, csúcs-RAM {rss}, hibás: {failed or 'nincs'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
