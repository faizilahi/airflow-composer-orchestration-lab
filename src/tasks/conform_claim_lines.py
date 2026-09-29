"""conform_claim_lines — local worker callable."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"

PAYER_MAP = {
    "aetna": "AETNA",
    "uhc": "UHC",
    "bcbs": "BCBS",
    "cigna": "CIGNA",
    "medicare": "MEDICARE",
}


def _read_raw() -> pd.DataFrame:
    pq = OUT / "raw_claims.parquet"
    csv = OUT / "raw_claims.csv"
    if pq.exists():
        try:
            return pd.read_parquet(pq)
        except Exception:
            pass
    if csv.exists():
        return pd.read_csv(csv)
    raise FileNotFoundError("raw claims missing — run extract_raw_claims first")


def conform_claim_lines(**_) -> dict:
    df = _read_raw()
    df["payer_code"] = (
        df["payer_code"].astype(str).str.strip().str.lower().map(PAYER_MAP).fillna("OTHER")
    )
    df["encounter_id"] = df["encounter_id"].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA})
    df["paid_amount"] = pd.to_numeric(df["paid_amount"], errors="coerce")
    df["allowed_amount"] = pd.to_numeric(df["allowed_amount"], errors="coerce")
    df["service_date"] = pd.to_datetime(df["service_date"]).dt.date.astype(str)
    df["attribution_status"] = df["encounter_id"].apply(
        lambda x: "UNATTRIBUTED" if pd.isna(x) else "ATTRIBUTED"
    )

    out_path = OUT / "claim_lines_conformed.csv"
    df.to_csv(out_path, index=False)
    meta = {
        "task_id": "conform_claim_lines",
        "execution_mode": os.environ.get("EXECUTION_MODE", "local"),
        "row_count": int(len(df)),
        "attributed": int((df["attribution_status"] == "ATTRIBUTED").sum()),
        "unattributed": int((df["attribution_status"] == "UNATTRIBUTED").sum()),
        "output": str(out_path),
        "container_boundary": "PythonOperator on Airflow worker",
    }
    (OUT / "conform_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    print(conform_claim_lines())
