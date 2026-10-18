# Design decisions

## 2026-10-16: Raw loading for multiple tenants

**What:** `tenants/*.yml` describes each tenant (source folders and target schema).
The `load_raw` Airflow DAG reads those files and loads every CSV into
`<target_schema>.<file name without _dataset.csv>`, with every column as `text`,
plus `_loaded_at` and `_source_file`.

**Choices and trade-offs**

- **Config as data, one file per tenant.** Adding a tenant means adding a YAML
  file, not changing code. The parsing lives in `ingestion/dags/tenant_config.py`,
  which has no Airflow imports, so it is unit tested without Airflow.
- **All columns as text.** The raw layer keeps the data exactly as delivered,
  so a load never fails because of a bad date or number. Types are applied in the
  next layer (staging), where problems can be found and reported.
- **TRUNCATE + COPY in one transaction.** Reruns are safe: a failed load rolls
  back and the old rows stay. TRUNCATE (not DROP) keeps the table, so views built
  on it later keep working. The cost: if a CSV gains or loses a column, the load
  stops with a clear error, and the table has to be dropped by hand. That is on
  purpose, because a layout change should be noticed.
- **COPY instead of INSERT.** COPY streams the file to Postgres in one command.
  The 1M-row geolocation file loads in seconds.
- **One mapped task per CSV.** Each file is its own task in the Airflow UI, with
  its own logs and retries. At most 4 run at once, to keep a laptop responsive.
  Schemas are created in a step before that, so parallel tasks do not race to
  create the same schema.
- **Safe names only.** Tenant, schema and table names must match
  `^[a-z_][a-z0-9_]*$`, and all SQL names go through `psycopg2.sql.Identifier`.
  Two tenants with the same schema, or two files mapping to one table, are errors,
  because one load would otherwise silently truncate the other.
- **Config is read at run time, not when Airflow parses the DAG.** Airflow parses
  DAG files often. Listing folders there would slow that down, and a broken
  YAML file would make the whole DAG disappear from the UI, where a failed task is
  easier to see and debug.
