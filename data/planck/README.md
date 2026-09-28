# Planck 2018 (PR3) CMB power spectra

Downloaded 2026-09-28 from the Planck Legacy Archive mirror at IRSA:
`https://irsa.ipac.caltech.edu/data/Planck/release_3/ancillary-data/cosmoparams/`
(re-download with `bash scripts/fetch_planck_data.sh`; checksums in `SHA256SUMS`).

| File | Content |
|---|---|
| `COM_PowerSpect_CMB-TT-full_R3.01.txt` | unbinned TT spectrum: ℓ, D_ℓ [μK²], −ΔD_ℓ, +ΔD_ℓ (asymmetric errors at low ℓ) |
| `COM_PowerSpect_CMB-TT-binned_R3.01.txt` | binned TT spectrum (includes a best-fit column) |
| `COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt` | best-fit ΛCDM theory D_ℓ (TT, TE, EE, BB, PP) |

D_ℓ = ℓ(ℓ+1)C_ℓ/2π. Acknowledgement required when used: *"Based on observations
obtained with Planck (http://www.esa.int/Planck), an ESA science mission with
instruments and contributions directly funded by ESA Member States, NASA, and Canada."*
Reference: Planck Collaboration 2018 V/VI, A&A 641, A5/A6 (2020).
