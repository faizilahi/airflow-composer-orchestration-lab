"""Execute claims nightly callables in DAG order without a scheduler."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("EXECUTION_MODE", "local")
os.environ.setdefault("LOGICAL_DATE", "2025-08-07")

from src.tasks.conform_claim_lines import conform_claim_lines
from src.tasks.extract_raw_claims import extract_raw_claims
from src.tasks.publish_finance_mart import publish_finance_mart
from src.tasks.test_gate_attribution import GateFailed, test_gate_attribution


def main() -> None:
    print(">>> extract_raw_claims")
    print(extract_raw_claims())
    print(">>> conform_claim_lines")
    print(conform_claim_lines())
    print(">>> test_gate_attribution")
    try:
        print(test_gate_attribution())
    except GateFailed as exc:
        print("GATE FAILED — publish skipped:", exc)
        sys.exit(2)
    print(">>> publish_finance_mart")
    print(publish_finance_mart())
    print("DAG local run complete")


if __name__ == "__main__":
    main()
