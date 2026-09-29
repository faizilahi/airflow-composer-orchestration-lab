"""
Airflow DAG: claims_nightly
Task ids are the section anchors documented in the README.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Allow `from src...` when AIRFLOW_HOME is this repo
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:  # pragma: no cover - local parse without airflow
    DAG = None
    PythonOperator = None

from src.tasks.conform_claim_lines import conform_claim_lines
from src.tasks.extract_raw_claims import extract_raw_claims
from src.tasks.publish_finance_mart import publish_finance_mart
from src.tasks.test_gate_attribution import test_gate_attribution

DEFAULT_ARGS = {
    "owner": "faiz-elahi",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _pod_note(task_id: str) -> str:
    return (
        f"{task_id} is a KubernetesPodOperator in Composer/OpenShift; "
        "this DAG file uses PythonOperator so the callable can be unit-run locally."
    )


if DAG is not None:
    with DAG(
        dag_id="claims_nightly",
        description="Nightly claims extract → conform → attribution gate → finance mart publish",
        default_args=DEFAULT_ARGS,
        start_date=datetime(2025, 8, 1),
        schedule="@daily",
        catchup=False,
        tags=["claims", "finance", "gate"],
    ) as dag:
        t_extract = PythonOperator(
            task_id="extract_raw_claims",
            python_callable=extract_raw_claims,
            op_kwargs={"logical_date": "{{ ds }}"},
            doc_md=_pod_note("extract_raw_claims"),
        )
        t_conform = PythonOperator(
            task_id="conform_claim_lines",
            python_callable=conform_claim_lines,
            doc_md="Local PythonOperator on the worker — no pod required.",
        )
        t_gate = PythonOperator(
            task_id="test_gate_attribution",
            python_callable=test_gate_attribution,
            doc_md="Quality gate; failures skip publish via upstream trigger rule defaults.",
        )
        t_publish = PythonOperator(
            task_id="publish_finance_mart",
            python_callable=publish_finance_mart,
            doc_md=_pod_note("publish_finance_mart"),
        )

        t_extract >> t_conform >> t_gate >> t_publish
else:
    dag = None
