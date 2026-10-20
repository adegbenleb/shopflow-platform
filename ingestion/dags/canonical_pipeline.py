"""The canonical pipeline: raw files to tested gold tables in one run.

Step 1 triggers the load_raw DAG and waits for it to finish.
Step 2 runs dbt build: every staging and gold model, then every test, in dependency order.
"""

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import DAG

DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_DIR = "/opt/airflow/transform"

with DAG(
    dag_id="canonical_pipeline",
    schedule="@daily",
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    tags=["shopflow"],
) as dag:
    load_raw = TriggerDagRunOperator(
        task_id="load_raw",
        trigger_dag_id="load_raw",
        wait_for_completion=True,
        poke_interval=15,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"{DBT} build --project-dir {DBT_DIR} --profiles-dir {DBT_DIR} --target docker"
        ),
        env={"DBT_TARGET_PATH": "/tmp/dbt/target", "DBT_LOG_PATH": "/tmp/dbt/logs"},
        append_env=True,
    )

    load_raw >> dbt_build
