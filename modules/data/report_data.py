from dataclasses import dataclass
from typing import Self

import pandas as pd

from modules.utils import format_number_to_currency

from .assignment_data import AssignedItemData, ParticipantData, SplitManager
from .receipt_data import AdditionalCharge


@dataclass
class PurchasedItemReportData:
    """Data report untuk satu item yang dibeli seseorang."""

    item_id: int
    name: str
    purchased_count: int
    unit_price: float

    @classmethod
    def from_item_assignment_data(cls, item_assignment: AssignedItemData) -> Self:
        return cls(
            item_id=item_assignment.item.id,
            name=item_assignment.item.name,
            purchased_count=item_assignment.assigned_count,
            unit_price=item_assignment.item.unit_price,
        )

    @property
    def total(self) -> float:
        return self.purchased_count * self.unit_price


@dataclass
class ParticipantReportData:
    """Data report untuk satu peserta."""

    participant_id: int
    name: str
    purchased_items: list[PurchasedItemReportData]
    purchased_subtotal: float   # total harga item saja
    purchased_total: float      # total akhir termasuk pajak/service proporsional
    charges_breakdown: list     # list biaya tambahan per orang
    @property
    def purchased_others(self) -> float:
        """Jumlah biaya tambahan (pajak, service, dll) yang ditanggung orang ini."""
        return self.purchased_total - self.purchased_subtotal

    @classmethod
    def from_assignment_data(
        cls,
        participant: ParticipantData,
        assigned_items: list[AssignedItemData],
        receipt_subtotal: float,
        receipt_total: float,
        additional_charges: list,  
    ) -> Self:
        purchased_items = [
            PurchasedItemReportData.from_item_assignment_data(it)
            for it in assigned_items
        ]
        subtotal = sum(it.total for it in purchased_items)

        # Rasio kontribusi orang ini terhadap total belanja
        ratio = (subtotal / receipt_subtotal) if receipt_subtotal > 0 else 0

        # Total akhir = proporsi dari total receipt
        total = ratio * receipt_total

        # Rincian biaya tambahan proporsional
        charges_breakdown = [
            (ch.name, ch.amount * ratio)
            for ch in additional_charges
        ]

        return cls(
            participant_id=participant.id,
            name=participant.name,
            purchased_items=purchased_items,
            purchased_subtotal=subtotal,
            purchased_total=total,
            charges_breakdown=charges_breakdown,
        )

    def to_dataframe_display(self) -> pd.DataFrame:
        rows = [
            {
                "Name": it.name,
                "Count": it.purchased_count,
                "Unit price": format_number_to_currency(it.unit_price),
                "Total": format_number_to_currency(it.total),
            }
            for it in self.purchased_items
        ]
        return pd.DataFrame(
            rows, columns=["Name", "Count", "Unit price", "Total"]
        ).set_index("Name")


@dataclass
class ReportData:
    """Data report lengkap untuk seluruh peserta."""

    participants_reports: list[ParticipantReportData]

    @classmethod
    def from_split_manager(cls, manager: SplitManager) -> Self:
        order_subtotal = manager.receipt_data.subtotal
        order_total = manager.receipt_data.total
        additional_charges = manager.receipt_data.additional_charges  

        return cls(
            participants_reports=[
                ParticipantReportData.from_assignment_data(
                    p,
                    manager.get_participant_items_assignment_list(p.id),
                    order_subtotal,
                    order_total,
                    additional_charges, 
                )
                for p in manager.get_all_participants()
            ],
        )
