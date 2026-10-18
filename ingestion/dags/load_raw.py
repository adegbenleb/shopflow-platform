"""Load every tenant's raw CSV files into Postgres, one text-only table per file.

Flow:  plan  ->  create_schemas  ->  load_table (one mapped task per CSV)

Each load runs in a single transaction: TRUNCATE, then COPY. If the COPY fails,
the transaction rolls back and the table keeps its previous contents, so the
DAG can be rerun at any time.
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path

import psycopg2
from airflow.sdk import dag, get_current_context, task
from psycopg2 import sql
from tenant_config import load_tenants, plan_loads

TENANTS_DIR = Path(os.environ.get("SHOPFLOW_TENANTS_DIR", "/opt/airflow/tenants"))

METADATA_COLUMNS = ("_loaded_at", "_source_file")


def connect():
    return psycopg2.connect(
        host=os.environ.get("SHOPFLOW_PG_HOST", "postgres"),
        port=int(os.environ.get("SHOPFLOW_PG_PORT", "5432")),
        user=os.environ.get("SHOPFLOW_PG_USER", "shopflow"),
        password=os.environ.get("SHOPFLOW_PG_PASSWORD", "shopflow"),
        dbname=os.environ.get("SHOPFLOW_PG_DB", "shopflow"),
    )


def existing_columns(cur, schema: str, table: str) -> list[str]:
    cur.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema, table),
    )
    return [row[0] for row in cur.fetchall() if row[0] not in METADATA_COLUMNS]


def load_csv(conn, schema: str, table: str, csv_path: Path) -> int:
    """Truncate schema.table and COPY csv_path into it. Returns the row count."""
    target = sql.Identifier(schema, table)

    # utf-8-sig drops the byte-order mark some files start with, so it does not
    # end up glued to the first column name.
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader([f.readline()]))
        if not header or len(set(header)) != len(header) or "" in header:
            raise ValueError(
                f"{csv_path}: header is empty or has duplicate names: {header}"
            )

        with conn, conn.cursor() as cur:  # one transaction, committed on success
            column_defs = [sql.SQL("{} text").format(sql.Identifier(c)) for c in header]
            cur.execute(
                sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} ({}, "
                    "_loaded_at timestamptz NOT NULL DEFAULT now(), "
                    "_source_file text NOT NULL)"
                ).format(target, sql.SQL(", ").join(column_defs))
            )

            # TRUNCATE keeps the table (and anything built on it), so a changed
            # CSV layout must be handled on purpose rather than silently.
            current = existing_columns(cur, schema, table)
            if current != header:
                raise ValueError(
                    f"{schema}.{table} has columns {current} but {csv_path.name} has "
                    f"{header}. Drop the table to reload it with the new layout."
                )

            # The metadata columns are filled in by column defaults during COPY.
            # now() is the transaction start time, so every row in one load
            # gets the same _loaded_at.
            cur.execute(
                sql.SQL(
                    "ALTER TABLE {} ALTER COLUMN _source_file SET DEFAULT {}"
                ).format(target, sql.Literal(str(csv_path)))
            )
            cur.execute(sql.SQL("TRUNCATE {}").format(target))
            # The header line was already read above, so COPY sees data rows only.
            cur.copy_expert(
                sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv)").format(
                    target, sql.SQL(", ").join(map(sql.Identifier, header))
                ),
                f,
            )
            cur.execute(sql.SQL("SELECT count(*) FROM {}").format(target))
            return cur.fetchone()[0]


@dag(
    dag_id="load_raw",
    schedule=None,  # triggered by hand for now
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ingestion", "raw"],
    doc_md=__doc__,
)
def load_raw():
    @task
    def plan() -> list[dict]:
        """Read tenants/*.yml and list every CSV to load (XCom needs plain types)."""
        return [
            {
                "tenant": load.tenant,
                "schema": load.schema,
                "table": load.table,
                "csv_path": str(load.csv_path),
            }
            for tenant in load_tenants(TENANTS_DIR)
            for load in plan_loads(tenant)
        ]

    @task
    def create_schemas(loads: list[dict]) -> list[dict]:
        """Create schemas once, up front, so parallel loads do not race on it."""
        conn = connect()
        try:
            with conn, conn.cursor() as cur:
                for schema in sorted({load["schema"] for load in loads}):
                    cur.execute(
                        sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                            sql.Identifier(schema)
                        )
                    )
        finally:
            conn.close()
        return loads

    # map_index_template shows "raw_olist.olist_orders" in the UI instead of 0, 1, 2...
    @task(map_index_template="{{ table_label }}", max_active_tis_per_dagrun=4)
    def load_table(tenant: str, schema: str, table: str, csv_path: str) -> int:
        get_current_context()["table_label"] = f"{schema}.{table}"
        conn = connect()
        try:
            rows = load_csv(conn, schema, table, Path(csv_path))
        finally:
            conn.close()
        print(f"[{tenant}] loaded {rows} rows into {schema}.{table} from {csv_path}")
        return rows

    load_table.expand_kwargs(create_schemas(plan()))


load_raw()
