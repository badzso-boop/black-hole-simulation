"""Qiskit kvantum szimuláció — hash qubitek."""
from __future__ import annotations

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    HAS_QISKIT = True
except ImportError:
    HAS_QISKIT = False

from python.information_packet import Qubit


class QuantumSimulator:
    """Kvantum áramkör a hash qubitek szimulálásához."""

    def __init__(self, qubits: list[Qubit]) -> None:
        self.qubits = qubits
        self.n = min(len(qubits), 8)  # max 8 qubit a szimulációban

    def build_circuit(self) -> object | None:
        """Qiskit kvantum áramkör felépítése."""
        if not HAS_QISKIT:
            return None
        import math
        qc = QuantumCircuit(self.n, self.n)
        for i, q in enumerate(self.qubits[: self.n]):
            theta = 2 * math.acos(abs(q.alpha))
            qc.ry(theta, i)
        qc.measure(range(self.n), range(self.n))
        return qc

    def run(self, shots: int = 1024) -> dict | None:
        """Szimuláció futtatása."""
        if not HAS_QISKIT:
            return None
        qc = self.build_circuit()
        if qc is None:
            return None
        sim = AerSimulator()
        job = sim.run(qc, shots=shots)
        return job.result().get_counts()
