#!/usr/bin/env bash
# A Planck 2018 CMB-teljesítményspektrumok letöltése a data/planck/ mappába, ellenőrzőösszeggel.
set -euo pipefail
cd "$(dirname "$0")/../data/planck"
BASE="https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams"
for f in COM_PowerSpect_CMB-TT-full_R3.01.txt \
         COM_PowerSpect_CMB-TT-binned_R3.01.txt \
         COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt; do
    echo "letöltés: $f"
    curl -fsSL -o "$f" "$BASE/$f"
done
sha256sum -c SHA256SUMS
