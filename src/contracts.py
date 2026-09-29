"""Data contracts shared by conform + gate tasks."""
from __future__ import annotations

from dataclasses import dataclass

REQUIRED_CLAIM_COLUMNS = (
    "claim_line_id",
    "encounter_id",
    "payer_code",
    "service_date",
    "allowed_amount",
    "paid_amount",
    "cpt_code",
)

PAYER_CANONICAL = {"AETNA", "UHC", "BCBS", "CIGNA", "MEDICARE", "OTHER"}


@dataclass(frozen=True)
class GateThresholds:
    max_orphan_rate: float = 0.02
    max_null_paid: int = 0
    min_rows: int = 1


def validate_columns(columns: list[str]) -> list[str]:
    return [c for c in REQUIRED_CLAIM_COLUMNS if c not in columns]
