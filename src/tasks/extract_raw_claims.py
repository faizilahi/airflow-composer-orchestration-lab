"""extract_raw_claims — pod-eligible extract callable."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LANDING = ROOT / "data" / "landing"
OUT = ROOT / "output"


def extract_raw_claims(logical_date: str | None = None, **_) -> dict:
    logical_date = logical_date or os.environ.get("LOGICAL_DATE", "2025-08-07")
    mode = os.environ.get("EXECUTION_MODE", "local")
    OUT.mkdir(parents=True, exist_ok=True)

    files = sorted(LANDING.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No landing files under {LANDING}")

    frames = [pd.read_csv(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    df["_extracted_at"] = pd.Timestamp.utcnow().isoformat()
    df["_logical_date"] = logical_date
    df["_execution_mode"] = mode

    out_path = OUT / "raw_claims.parquet"
    try:
        df.to_parquet(out_path, index=False)
    except Exception:
        # parquet engine optional — fall back to csv
        out_path = OUT / "raw_claims.csv"
        df.to_csv(out_path, index=False)

    meta = {
        "task_id": "extract_raw_claims",
        "logical_date": logical_date,
        "execution_mode": mode,
        "row_count": int(len(df)),
        "output": str(out_path),
        "container_boundary": "KubernetesPodOperator in Composer/OpenShift; local callable here",
    }
    (OUT / "extract_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    print(extract_raw_claims())
