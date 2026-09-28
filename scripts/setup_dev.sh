#!/usr/bin/env bash
# Fejlesztői környezet egy lépésben: Rust + Python virtualenv + a Rust mag
# lefordítása Python-modulként + tesztek.
#
# Előfeltétel (Debian/Ubuntu): sudo apt install -y git curl build-essential python3 python3-venv
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Fekete Lyuk Szimulátor — fejlesztői környezet ==="

# C fordító/linker (a Rust és a maturin build ezt használja)
if ! command -v cc &> /dev/null; then
    echo "HIBA: nincs C fordító (cc). Telepítsd: sudo apt install -y build-essential"
    exit 1
fi

# Rust (rustup)
if ! command -v cargo &> /dev/null; then
    echo "Rust telepítése (rustup)..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # shellcheck disable=SC1091
    source "$HOME/.cargo/env"
fi
echo "Rust: $(rustc --version)"

# Python ≥ 3.11
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "HIBA: Python 3.11 vagy újabb kell (van: $(python3 --version 2>&1))"
    exit 1
fi

# Virtualenv (a rendszer-Pythonba a PEP 668 miatt nem telepítünk)
if [ ! -x .venv/bin/python3 ]; then
    echo "Virtualenv létrehozása (.venv)..."
    python3 -m venv .venv || {
        echo "HIBA: a venv modul hiányzik. Telepítsd: sudo apt install -y python3-venv"
        exit 1
    }
fi
PY=.venv/bin/python3

echo "A Rust mag fordítása + Python függőségek (az első fordítás néhány perc)..."
unset CONDA_PREFIX
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -e '.[dev]'

echo "Rust tesztek..."
cargo test --manifest-path core/Cargo.toml --quiet

echo "Python tesztek..."
"$PY" -m pytest python/tests/ -q

echo ""
echo "Kész! Használat:"
echo "  source .venv/bin/activate"
echo "  python -m python --list-objects"
echo "  python -m python --object sgr-a --output output/sgr-a.json"
