"""test_gate_attribution — fail the DAG before publish when quality breaks."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"

MAX_ORPHAN_RATE = 0.02


class GateFailed(Exception):
    pass


def test_gate_attribution(**_) -> dict:
    path = OUT / "claim_lines_conformed.csv"
    df = pd.read_csv(path)
    total = len(df)
    orphans = int((df["attribution_status"] == "UNATTRIBUTED").sum())
    null_paid = int(df["paid_amount"].isna().sum())
    orphan_rate = orphans / total if total else 1.0

    report = {
        "task_id": "test_gate_attribution",
        "total_rows": total,
        "orphan_rows": orphans,
        "orphan_rate": round(orphan_rate, 4),
        "null_paid_rows": null_paid,
        "max_orphan_rate": MAX_ORPHAN_RATE,
        "passed": orphan_rate <= MAX_ORPHAN_RATE and null_paid == 0,
    }
    (OUT / "gate_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not report["passed"]:
        (OUT / "gate_failures.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        raise GateFailed(f"Attribution gate failed: {report}")
    return report


if __name__ == "__main__":
    print(test_gate_attribution())
