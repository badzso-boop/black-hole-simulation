#!/usr/bin/env bash
set -e

echo "=== Fekete Lyuk Szimulátor — fejlesztői környezet beállítása ==="

# Rust ellenőrzés
if ! command -v cargo &> /dev/null; then
    echo "Rust telepítése..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# Python ellenőrzés
if ! command -v python3 &> /dev/null; then
    echo "HIBA: Python 3.11+ szükséges"
    exit 1
fi

# Maturin és Python függőségek
echo "Python függőségek telepítése..."
pip install maturin
maturin develop --manifest-path core/Cargo.toml --features python-ext
pip install -e '.[dev]'

# Ellenőrzés
echo "Rust tesztek futtatása..."
cargo test --manifest-path core/Cargo.toml --quiet

echo "Python tesztek futtatása..."
pytest python/tests/ -q

echo ""
echo "Kész! A fejlesztői környezet beállítva."
echo "  cargo test --manifest-path core/Cargo.toml   — Rust tesztek"
echo "  pytest python/tests/                          — Python tesztek"
echo "  cargo run --manifest-path bevy-app/Cargo.toml — 3D vizualizáció"
