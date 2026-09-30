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
#   NO_MPI=1  MPI nélkül: egyetlen lánc, alapból 16 szállal (lassabb, de mindig működik)
#   CHAINS=8 OMP_NUM_THREADS=4   párhuzamos láncok × szál/lánc (MPI-vel)
#   rootként (pl. WSL): OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 bash ...
# Folytatás megszakítás után: ugyanez a parancs (--resume).
# Haladás: a kimenet azonnal látszik; a láncok a chains/<modell>/ alatt nőnek.
# Elemzés:    python scripts/analyze_mcmc.py
set -euo pipefail
cd "$(dirname "$0")/.."
export COBAYA_PACKAGES_PATH="${COBAYA_PACKAGES_PATH:-$HOME/cobaya_packages}"
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1   # a tee mögött se pufferelje a kimenetet
CHAINS="${CHAINS:-8}"
which="${1:-both}"
# a projekt saját Pythonja, akkor is, ha a .venv nincs aktiválva
if [[ -z "${PYTHON:-}" ]]; then
  if [[ -x .venv/bin/python ]]; then PYTHON="$PWD/.venv/bin/python"; else PYTHON=python3; fi
fi
"$PYTHON" -c "import cobaya" 2>/dev/null || {
  echo "A cobaya nincs telepítve ehhez: $PYTHON — pip install -e '.[dev,thesis]' mpi4py"; exit 1; }

use_mpi=0
if [[ "${NO_MPI:-0}" != "1" ]] && command -v mpirun >/dev/null \
    && "$PYTHON" -c "import mpi4py" 2>/dev/null; then
  # WSL-ben az Open MPI indításkor néha elakad: 60 s-os próba két folyamattal
  echo "== MPI-próba (max 60 s)…"
  if timeout 60 mpirun --bind-to none -n 2 "$PYTHON" -c \
      "from mpi4py import MPI; MPI.COMM_WORLD.Barrier()" >/dev/null 2>&1; then
    use_mpi=1
    echo "   MPI rendben"
  else
    echo "   Az MPI nem indult el 60 s alatt. WSL-ben ezek szoktak segíteni:"
    echo "     export OMPI_MCA_btl_vader_single_copy_mechanism=none"
    echo "     export OMPI_MCA_btl_tcp_if_include=lo"
    echo "   (rootként: OMPI_ALLOW_RUN_AS_ROOT=1 OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1)"
    echo "   Vagy MPI nélkül: NO_MPI=1 bash scripts/run_mcmc.sh"
    exit 1
  fi
fi
if [[ $use_mpi == 1 ]]; then
  export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"   # 8 lánc × 4 szál = 32 a 5950X-en
else
  export OMP_NUM_THREADS="${OMP_NUM_THREADS:-16}"  # egy lánc: több szál
fi

run() {
  local name="$1"
  mkdir -p "chains/$name" runs/mcmc
  if [[ $use_mpi == 1 ]]; then
    echo "== $name: $CHAINS lánc × $OMP_NUM_THREADS szál, $(date -Is)"
    # --bind-to none: különben az Open MPI egy magra kötheti a láncot, és a 4 szála osztozik rajta
    mpirun --bind-to none -n "$CHAINS" "$PYTHON" -m cobaya run "scripts/cobaya/${name}_mcmc.yaml" --resume \
      2>&1 | tee -a "runs/mcmc/${name}.log"
  else
    echo "== $name: 1 lánc (MPI nélkül) × $OMP_NUM_THREADS szál, $(date -Is)"
    "$PYTHON" -m cobaya run "scripts/cobaya/${name}_mcmc.yaml" --resume 2>&1 | tee -a "runs/mcmc/${name}.log"
  fi
  echo "== $name: legjobb illesztés (minimize), $(date -Is)"
  "$PYTHON" -m cobaya run "scripts/cobaya/${name}_bestfit.yaml" --resume 2>&1 \
    | tee -a "runs/mcmc/${name}_bestfit.log"
}
case "$which" in
  lqc) run lqc ;;
  lcdm) run lcdm ;;
  both) run lcdm; run lqc ;;
  *) echo "használat: $0 [lqc|lcdm|both]"; exit 1 ;;
esac
