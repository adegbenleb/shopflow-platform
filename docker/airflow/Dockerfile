# Airflow with dbt installed in its own virtual environment,
# so dbt's packages never clash with Airflow's.
FROM apache/airflow:3.1.0-python3.12

RUN python -m venv /opt/airflow/dbt_venv \
 && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres
