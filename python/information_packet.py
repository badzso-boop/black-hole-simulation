"""A beeső „üzenet" (payload) azonosítása.

A korábbi változat a SHA3-hash bájtjait szorzatállapotú qubitekbe kódolta, és
ennek "Neumann-entrópiáját" számolta — de egy tiszta szorzatállapot Neumann-
entrópiája 0; az ott kiszámolt érték a mérési valószínűségek Shannon-entrópiája
volt, félrevezető néven. Itt a payload csak azonosít: a hash adja a
determinisztikus véletlenmagot a toy modellhez és az üzenet bitjeit.

A Hayden–Preskill-mérőszám (a referencia-qubittel vett kölcsönös információ)
minden lehetséges üzenetre felső korlátot ad a visszanyerhetőségre — így a
konkrét payload tartalma nem befolyásolja, hogy visszanyerhető-e.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


class InformationPacket:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self._raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
        self.hash_sha3 = hashlib.sha3_256(self._raw).hexdigest()

    @property
    def seed(self) -> int:
        """Determinisztikus 64 bites véletlenmag a hash-ből."""
        return int(self.hash_sha3[:16], 16)

    def message_bits(self, k: int) -> list[int]:
        """Az üzenet első k bitje (a hash-ből)."""
        value = int(self.hash_sha3, 16)
        return [(value >> (255 - i)) & 1 for i in range(k)]
