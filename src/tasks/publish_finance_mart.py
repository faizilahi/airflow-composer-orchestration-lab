"""publish_finance_mart — pod-eligible publisher callable."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"


def publish_finance_mart(**_) -> dict:
    gate = json.loads((OUT / "gate_report.json").read_text(encoding="utf-8"))
    if not gate.get("passed"):
        raise RuntimeError("Refusing to publish — test_gate_attribution did not pass")

    df = pd.read_csv(OUT / "claim_lines_conformed.csv")
    df = df[df["attribution_status"] == "ATTRIBUTED"]
    mart = (
        df.groupby(["service_date", "payer_code"], as_index=False)
        .agg(
            claim_line_count=("claim_line_id", "count"),
            allowed_amount=("allowed_amount", "sum"),
            paid_amount=("paid_amount", "sum"),
        )
    )
    out_path = OUT / "finance_mart_daily.csv"
    mart.to_csv(out_path, index=False)
    meta = {
        "task_id": "publish_finance_mart",
        "execution_mode": os.environ.get("EXECUTION_MODE", "local"),
        "mart_rows": int(len(mart)),
        "paid_total": round(float(mart["paid_amount"].sum()), 2),
        "output": str(out_path),
        "container_boundary": "KubernetesPodOperator with finance-publisher SA",
    }
    (OUT / "publish_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    print(publish_finance_mart())
