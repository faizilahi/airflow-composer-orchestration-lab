"""Optional notify hook after publish — documents Composer branching."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "output"


def notify_ops(**_) -> dict:
    publish = json.loads((OUT / "publish_meta.json").read_text(encoding="utf-8"))
    payload = {
        "channel": "#finance-data-ops",
        "text": (
            f"finance_mart_daily published rows={publish['mart_rows']} "
            f"paid_total={publish['paid_total']}"
        ),
        "task_id": "notify_ops",
    }
    (OUT / "notify_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(notify_ops())
