"""v3 placeholder — HKLL rekonstrukció (Hamilton-Kabat-Lifschytz-Lowe 2006)."""
from __future__ import annotations


class HKLLReconstruction:
    """Bulk lokalitás és kvantumhibajavítás az AdS/CFT keretrendszerben."""

    def __init__(self, bulk_field: str = "scalar") -> None:
        self.bulk_field = bulk_field

    def reconstruct_bulk_operator(self, boundary_data: list[float]) -> list[float]:
        """v3.0-ban kerül implementálásra."""
        raise NotImplementedError("HKLL rekonstrukció v3.0-ban")
