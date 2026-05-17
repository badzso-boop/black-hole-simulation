import pytest
from python.information_packet import InformationPacket


class TestInformationPacket:
    def test_hash_deterministic(self):
        """Ugyanaz a payload mindig ugyanazt a hash-t adja."""
        payload = {"uzenet": "teszt", "szam": 42}
        p1 = InformationPacket(payload)
        p2 = InformationPacket(payload)
        assert p1.hash_sha3 == p2.hash_sha3

    def test_different_payloads_different_hash(self):
        """Különböző payloadok különböző hash-t adnak."""
        p1 = InformationPacket({"a": 1})
        p2 = InformationPacket({"a": 2})
        assert p1.hash_sha3 != p2.hash_sha3

    def test_qubit_normalization(self):
        """A qubitek normáltak: |α|² + |β|² = 1."""
        packet = InformationPacket({"teszt": True})
        for q in packet.qubits:
            norm = abs(q.alpha) ** 2 + abs(q.beta) ** 2
            assert abs(norm - 1.0) < 1e-10, f"Qubit normálás hibás: {norm}"

    def test_von_neumann_entropy_non_negative(self):
        """Von Neumann entrópia nem negatív."""
        packet = InformationPacket({"x": list(range(100))})
        assert packet.entropy >= 0.0

    def test_entropy_zero_for_pure_state(self):
        """Tiszta |0⟩ állapotnál az entrópia nulla."""
        packet = InformationPacket.__pure_state_for_test__()
        assert abs(packet.entropy) < 1e-10

    def test_hash_is_64_hex_chars(self):
        """SHA3-256 hash 64 hex karakter."""
        p = InformationPacket({"adat": "valami"})
        assert len(p.hash_sha3) == 64
        assert all(c in "0123456789abcdef" for c in p.hash_sha3)

    def test_qubit_count_equals_sha3_bytes(self):
        """SHA3-256 = 32 byte → 32 qubit."""
        p = InformationPacket({"x": 1})
        assert len(p.qubits) == 32
