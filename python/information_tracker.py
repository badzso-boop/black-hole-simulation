"""Timeline-szintű információ-nyomkövetés a fekete lyuk szimulációhoz.

Feldolgozza a Rust szimulációból kapott teljes timeline-t és kiszámítja:
- Page-görbe (kumulatív sugárzási entrópia az idő függvényében)
- Él-sugárzás arányának fejlődése
- Thermality-score fejlődése
- Standard vs. Norbi összehasonlítás
"""
from __future__ import annotations
import numpy as np
from numpy.typing import NDArray


class InformationTracker:
    """Timeline-szintű információ-nyomkövetés.

    Bemenete: SimulationResults.timeline (Rust JSON kimenet deseriálva).
    Kimenet: Page-görbe, entrópia-fejlődés, Norbi vs. Standard összehasonlítás.
    """

    def process_timeline(
        self,
        timeline: list[dict],
        input_packet_entropy: float,
    ) -> dict:
        """Feldolgozza a teljes szimulációs timeline-t.

        Args:
            timeline: TimeStep dict-ek listája (JSON deserializáció)
            input_packet_entropy: Az InformationPacket Von Neumann entrópiája

        Returns:
            page_curve, information_recovery_per_step, total_recovered_bits,
            edge_fraction_evolution
        """
        page_curve = self.compute_page_curve(timeline)
        recovery_per_step = []
        edge_evolution = []

        for point in page_curve:
            ef = point["edge_fraction"]
            ts = point["thermality_score"]
            # Visszanyerhető bitek becslése (log2 skálán)
            max_bits = np.log2(1000.0)  # SPECTRUM_BINS = 1000
            recovered = max(ef * max_bits, (1.0 - np.exp(-ts)) * max_bits)
            recovery_per_step.append(float(recovered))
            edge_evolution.append(ef)

        total_recovered = float(np.mean(recovery_per_step)) if recovery_per_step else 0.0

        return {
            "page_curve": page_curve,
            "information_recovery_per_step": recovery_per_step,
            "total_recovered_bits": total_recovered,
            "edge_fraction_evolution": edge_evolution,
            "input_packet_entropy": input_packet_entropy,
        }

    @staticmethod
    def compute_page_curve(timeline: list[dict]) -> list[dict]:
        """Page-görbe kiszámítása a szimulációs timeline-ból.

        A Page-görbe a kisugárzott fotonok állapotának kumulatív entrópiája
        az idő függvényében:
        - Standard: monoton növekszik (információ elvész)
        - Norbi: lassabban nő, él-arány növekedésével az entrópia-gyarapodás csökken

        S_rad(t) = -sum_i p_i * ln(p_i)
        ahol p = kumulált intenzitások normalizálva (fotonszám-eloszlás)
        """
        cumulative = np.zeros(1000)
        result = []

        for step in timeline:
            spectrum = step.get("spectrum", {})
            intensities = np.array(spectrum.get("intensities", []), dtype=float)
            if len(intensities) == 0:
                continue

            # Kumulatív foton-intenzitás
            cumulative = cumulative + intensities[:1000] if len(intensities) >= 1000 \
                else cumulative + np.pad(intensities, (0, 1000 - len(intensities)))

            total = float(np.sum(cumulative))
            if total > 0.0:
                p = cumulative / total
                mask = p > 1e-300
                s_rad = float(-np.sum(p[mask] * np.log(p[mask])))
            else:
                s_rad = 0.0

            # BH entrópia
            s_bh = float(step.get("entropy", 0.0))

            # Spektrum metaadatok (az új Rust mezők)
            edge_fraction    = float(spectrum.get("edge_fraction", 0.0))
            thermality_score = float(spectrum.get("thermality_score", 0.0))

            result.append({
                "time":            float(step.get("time", 0.0)),
                "s_radiation":     s_rad,
                "s_bh":            s_bh,
                "s_total":         s_rad + s_bh,
                "edge_fraction":   edge_fraction,
                "thermality_score": thermality_score,
                "mass":            float(step.get("mass", 0.0)),
            })

        return result

    @staticmethod
    def compare_models(std_result: dict, norbi_result: dict) -> dict:
        """Standard vs. Norbi összehasonlítás az información-visszanyerés szempontjából.

        Kulcskérdések:
        - A Norbi spektrum termálitása nagyobb-e? (thermality_ratio > 1)
        - Van-e él-sugárzás? (norbi_avg_edge_fraction > 0)
        - Kevesebb entrópiát "veszt el" a Norbi? (information_advantage_norbi > 0)
        - Van-e Page-görbe visszafordulás Norbi módban?
        """
        std_curve   = std_result.get("page_curve", [])
        norbi_curve = norbi_result.get("page_curve", [])

        std_s_rad   = [p["s_radiation"] for p in std_curve]
        norbi_s_rad = [p["s_radiation"] for p in norbi_curve]

        # Csúcs-entrópia indexei
        std_peak_idx   = int(np.argmax(std_s_rad))   if std_s_rad   else 0
        norbi_peak_idx = int(np.argmax(norbi_s_rad)) if norbi_s_rad else 0

        # Átlagos thermality-score
        std_therm   = float(np.mean([p["thermality_score"] for p in std_curve]))   if std_curve   else 0.0
        norbi_therm = float(np.mean([p["thermality_score"] for p in norbi_curve])) if norbi_curve else 0.0

        # Átlagos él-arány (csak Norbi-ban nemzero)
        norbi_avg_edge = float(np.mean([p["edge_fraction"] for p in norbi_curve])) if norbi_curve else 0.0

        # Végső sugárzási entrópia
        std_final_s   = float(std_s_rad[-1])   if std_s_rad   else 0.0
        norbi_final_s = float(norbi_s_rad[-1]) if norbi_s_rad else 0.0

        # Page-görbe visszafordulás: csúcs nem az utolsó lépés
        n_norbi = len(norbi_s_rad)
        page_turnaround = (
            n_norbi > 2
            and norbi_peak_idx < n_norbi - 1
            and norbi_peak_idx > 0
        )

        return {
            "std_page_peak_step":          std_peak_idx,
            "norbi_page_peak_step":        norbi_peak_idx,
            "std_mean_thermality":         std_therm,
            "norbi_mean_thermality":       norbi_therm,
            "thermality_ratio":            norbi_therm / max(std_therm, 1e-300),
            "norbi_avg_edge_fraction":     norbi_avg_edge,
            "std_final_radiation_entropy": std_final_s,
            "norbi_final_radiation_entropy": norbi_final_s,
            "information_advantage_norbi": std_final_s - norbi_final_s,
            "page_curve_turnaround_norbi": page_turnaround,
        }
