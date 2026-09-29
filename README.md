# Claims Nightly DAG: extract_raw_claims -> conform_claim_lines -> test_gate_attribution -> publish_finance_mart

Faiz Elahi — [LinkedIn](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [GitHub](https://github.com/faizilahi)

All claim extracts in this repo are generated.

## DAG topology (section names match task_id values)

```
extract_raw_claims
        │
        ▼
conform_claim_lines
        │
        ▼
test_gate_attribution ──(fail)──► skip publish, write gate_failures.json
        │
      (pass)
        ▼
publish_finance_mart
```

The DAG file `dags/claims_nightly_dag.py` wires these four tasks. Each task is a real Python callable under `src/tasks/` — not EmptyOperators. A local runner (`src/local_dag_runner.py`) executes the same callables in order without requiring an Airflow scheduler or a live Kubernetes/OpenShift cluster.

## Container boundary vs local task

| Task | Runs where in Composer / OpenShift | Why |
|------|------------------------------------|-----|
| `extract_raw_claims` | **KubernetesPodOperator** image `claims-extract:stable` | Needs JDBC drivers + VPN sidecar to the claims admin host; keep secrets in the pod SA |
| `conform_claim_lines` | Local `PythonOperator` on the worker | Pure pandas/SQL transform; no special system libs |
| `test_gate_attribution` | Local `PythonOperator` | Fast assertion suite; fail the DAG before publish |
| `publish_finance_mart` | **KubernetesPodOperator** image `finance-publisher:stable` | Writes to the warehouse with a locked-down SA and network policy |

Locally, pod tasks are emulated by the same callables with an environment flag `EXECUTION_MODE=local` so you can teach the boundary without a cluster.

## extract_raw_claims

Pulls the nightly CSV drop from `data/landing/`, validates file presence for `logical_date`, and stages to `output/raw_claims.parquet`.

## conform_claim_lines

Normalizes payer codes, casts amounts, derives `attribution_status`, writes `output/claim_lines_conformed.parquet`.

## test_gate_attribution

Fails if orphan encounter rate > 2% or paid-amount nulls exist. Writes `output/gate_report.json`.

## publish_finance_mart

Builds `output/finance_mart_daily.csv` rolled by service_date × payer only when the gate passes.

## Run without Airflow

```powershell
cd airflow-composer-orchestration-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas
python scripts/generate_landing_files.py
python -m src.local_dag_runner
```

To parse-check the DAG (optional, needs airflow installed):

```powershell
pip install "apache-airflow==2.8.4" --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.8.4/constraints-3.11.txt
$env:AIRFLOW_HOME = (Get-Location).Path
python -c "from dags.claims_nightly_dag import dag; print(dag.task_ids)"
```
