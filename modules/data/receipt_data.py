from dataclasses import asdict, dataclass, field

import pandas as pd

from .base import IDGenerator


class ItemIDGenerator(IDGenerator):
    """Generator for item ID in the receipt."""
    pass


# class untuk biaya tambahan seperti pajak, service charge, dll
@dataclass
class AdditionalCharge:
    """Biaya tambahan di luar harga item (pajak, service charge, diskon, dll)."""
    name: str    # Contoh: "PPN 10%", "Service Charge", "Diskon Member"
    amount: float  # Positif untuk charge, negatif untuk diskon


@dataclass
class ItemData:
    """Item data from the receipt."""
    name: str
    count: int
    total_price: float

    id: int = field(default_factory=ItemIDGenerator.get)

    @property
    def unit_price(self) -> float:
        """Harga per unit item."""
        return self.total_price / self.count if self.count > 0 else self.total_price


@dataclass
class ReceiptData:
    """Receipt data from AI reading."""
    items: dict[int, ItemData]
    total: float
    # list biaya tambahan
    additional_charges: list = field(default_factory=list)  

    @property
    def subtotal(self) -> float:
        """Subtotal = jumlah total harga semua item, SEBELUM pajak/service/dll."""
        return sum(item.total_price for item in self.items.values())

    @property
    def total_additional_charges(self) -> float:
        """Total semua biaya tambahan (pajak, service, diskon, dll)."""
        return sum(ch.amount for ch in self.additional_charges)

    def to_items_df(self) -> pd.DataFrame:
        """Convert item data ke DataFrame untuk ditampilkan di UI."""
        return pd.DataFrame([asdict(item) for item in self.items.values()])

    # method untuk convert additional charges ke DataFrame
    def to_charges_df(self) -> pd.DataFrame:
        """Convert additional charges ke DataFrame untuk ditampilkan di UI."""
        if not self.additional_charges:
            return pd.DataFrame(columns=["name", "amount"])
        return pd.DataFrame([
            {"name": ch.name, "amount": ch.amount}
            for ch in self.additional_charges
        ])

    @classmethod
    def from_items_df(
        cls,
        items_df: pd.DataFrame,
        total: float,
        additional_charges: list | None = None,  
    ) -> "ReceiptData":
        """Build ReceiptData dari DataFrame hasil edit user.

        Args:
            items_df: DataFrame dengan kolom "name", "count", "total_price"
            total: total harga keseluruhan (sudah termasuk pajak dll)
            additional_charges: list AdditionalCharge (opsional)
        """
        items = [
            ItemData(
                name=row["name"],
                count=int(row["count"]),
                total_price=float(row["total_price"]),
            )
            for _, row in items_df.iterrows()
        ]
        return cls(
            items={it.id: it for it in items},
            total=total,
            additional_charges=additional_charges or [],
        )
