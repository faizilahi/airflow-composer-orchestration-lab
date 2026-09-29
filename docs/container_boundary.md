# Kubernetes / OpenShift boundary for claims_nightly

## Pod tasks

`extract_raw_claims` and `publish_finance_mart` are documented as KubernetesPodOperator tasks:

```python
KubernetesPodOperator(
    task_id="extract_raw_claims",
    image="claims-extract:stable",
    cmds=["python", "-m", "src.tasks.extract_raw_claims"],
    env_vars={"LOGICAL_DATE": "{{ ds }}", "EXECUTION_MODE": "pod"},
    namespace="airflow-jobs",
    service_account_name="claims-extract-sa",
    get_logs=True,
    is_delete_operator_pod=True,
)
```

On OpenShift the same shape applies with a BuildConfig-produced image and a restricted SCC-compatible SA.

## Local tasks

`conform_claim_lines` and `test_gate_attribution` stay on the Airflow worker (PythonOperator) because they are CPU-light and need no host network privileges.

## Teaching without a cluster

`src/local_dag_runner.py` sets `EXECUTION_MODE=local` and invokes the identical callables. Pod-only behavior (SA tokens, sidecars) is skipped; the data contract and gate logic remain the same.
