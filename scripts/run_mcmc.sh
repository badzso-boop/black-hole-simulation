#!/usr/bin/env bash
# WP5c: teljes Planck-MCMC a hibrid LQC-spektrummal (és a ΛCDM-referencia) — a Ryzen 5950X-re.
#
# Egyszeri előkészítés (a repó gyökeréből, aktivált .venv-vel):
#   sudo apt install openmpi-bin libopenmpi-dev        # MPI a párhuzamos láncokhoz
#   pip install -e '.[dev,thesis]' mpi4py
#   cobaya-install planck_2018_lowl.TT planck_2018_lowl.EE \
#       planck_2018_highl_plik.TTTEEE_lite_native -p ~/cobaya_packages   # ~19 MB
#
# Futtatás:   bash scripts/run_mcmc.sh [lqc|lcdm|both]   (alapértelmezés: both)
# Folytatás megszakítás után: ugyanez a parancs (--resume).
# Elemzés:    python scripts/analyze_mcmc.py
set -euo pipefail
cd "$(dirname "$0")/.."
export COBAYA_PACKAGES_PATH="${COBAYA_PACKAGES_PATH:-$HOME/cobaya_packages}"
CHAINS="${CHAINS:-8}"                       # párhuzamos láncok (MPI-folyamatok)
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"  # szál láncónként (8 × 4 = 32 a 5950X-en)
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
which="${1:-both}"
run() {
  local name="$1"
  mkdir -p "chains/$name" runs/mcmc
  echo "== $name: $CHAINS lánc × $OMP_NUM_THREADS szál, $(date -Is)"
  if command -v mpirun >/dev/null && python -c "import mpi4py" 2>/dev/null; then
    mpirun -n "$CHAINS" cobaya-run "scripts/cobaya/${name}_mcmc.yaml" --resume \
      2>&1 | tee -a "runs/mcmc/${name}.log"
  else
    echo "   (nincs MPI/mpi4py: egyetlen lánc)"
    cobaya-run "scripts/cobaya/${name}_mcmc.yaml" --resume 2>&1 | tee -a "runs/mcmc/${name}.log"
  fi
  echo "== $name: legjobb illesztés (minimize), $(date -Is)"
  cobaya-run "scripts/cobaya/${name}_bestfit.yaml" --resume 2>&1 | tee -a "runs/mcmc/${name}_bestfit.log"
}
case "$which" in
  lqc) run lqc ;;
  lcdm) run lcdm ;;
  both) run lcdm; run lqc ;;
  *) echo "használat: $0 [lqc|lcdm|both]"; exit 1 ;;
esac
