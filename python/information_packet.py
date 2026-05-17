from __future__ import annotations
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class Qubit:
    alpha: complex
    beta: complex

    def is_normalized(self) -> bool:
        return abs(abs(self.alpha) ** 2 + abs(self.beta) ** 2 - 1.0) < 1e-10


class InformationPacket:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self._raw = json.dumps(payload, sort_keys=True).encode()
        self.hash_sha3 = hashlib.sha3_256(self._raw).hexdigest()
        self.qubits = self._encode_qubits()
        self.entropy = self._von_neumann_entropy()

    def _encode_qubits(self) -> list[Qubit]:
        """SHA3 hash bytejait kvantum állapotokba kódolja. Minden byte → 1 qubit."""
        qubits = []
        for byte in hashlib.sha3_256(self._raw).digest():
            theta = (byte / 255.0) * math.pi
            alpha = complex(math.cos(theta / 2), 0)
            beta = complex(math.sin(theta / 2), 0)
            qubits.append(Qubit(alpha=alpha, beta=beta))
        return qubits

    def _von_neumann_entropy(self) -> float:
        """Von Neumann entrópia a qubit sűrűségmátrixból."""
        total = 0.0
        for q in self.qubits:
            p0 = abs(q.alpha) ** 2
            p1 = abs(q.beta) ** 2
            if p0 > 0:
                total -= p0 * math.log2(p0)
            if p1 > 0:
                total -= p1 * math.log2(p1)
        return total / len(self.qubits) if self.qubits else 0.0

    @classmethod
    def __pure_state_for_test__(cls) -> InformationPacket:
        """Tesztsegéd: tiszta |0⟩ állapot (S=0)."""
        inst = cls.__new__(cls)
        inst.payload = {}
        inst.hash_sha3 = "0" * 64
        inst.qubits = [Qubit(alpha=complex(1, 0), beta=complex(0, 0))]
        inst.entropy = 0.0
        return inst
