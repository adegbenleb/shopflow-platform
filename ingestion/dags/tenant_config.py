"""Read tenant YAML files and work out which CSV goes into which raw table.

Plain Python on purpose: no Airflow and no database imports, so it can be unit
tested on a laptop. The load_raw DAG imports it (Airflow puts the dags folder on
sys.path).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

# Postgres identifiers: lowercase, start with a letter or underscore, max 63 bytes.
# Names end up in SQL, so anything else is rejected rather than quoted and hoped for.
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")

CSV_SUFFIX = "_dataset.csv"


class TenantConfigError(ValueError):
    """A tenant file is missing a field, has a bad value, or clashes with another."""


@dataclass(frozen=True)
class Tenant:
    name: str
    target_schema: str
    sources: tuple[Path, ...]


@dataclass(frozen=True)
class TableLoad:
    """One CSV file to load into one raw table."""

    tenant: str
    schema: str
    table: str
    csv_path: Path


def parse_tenant(data: object, origin: str = "<config>") -> Tenant:
    """Validate the contents of one tenant file and turn it into a Tenant."""
    if not isinstance(data, dict):
        raise TenantConfigError(f"{origin}: expected a mapping at the top level")

    missing = {"tenant", "target_schema", "sources"} - data.keys()
    if missing:
        raise TenantConfigError(f"{origin}: missing field(s) {sorted(missing)}")

    name = data["tenant"]
    schema = data["target_schema"]
    sources = data["sources"]

    for field, value in (("tenant", name), ("target_schema", schema)):
        if not isinstance(value, str) or not IDENTIFIER.match(value):
            raise TenantConfigError(
                f"{origin}: {field}={value!r} must be lowercase letters, digits "
                "or underscores, starting with a letter or underscore"
            )

    if (
        not isinstance(sources, list)
        or not sources
        or not all(isinstance(s, str) and s for s in sources)
    ):
        raise TenantConfigError(f"{origin}: sources must be a non-empty list of paths")

    return Tenant(
        name=name, target_schema=schema, sources=tuple(Path(s) for s in sources)
    )


def load_tenants(tenants_dir: Path) -> list[Tenant]:
    """Read every *.yml / *.yaml file in tenants_dir, sorted by file name."""
    if not tenants_dir.is_dir():
        raise TenantConfigError(f"tenants folder not found: {tenants_dir}")

    files = sorted([*tenants_dir.glob("*.yml"), *tenants_dir.glob("*.yaml")])
    tenants = [
        parse_tenant(yaml.safe_load(f.read_text()), origin=f.name) for f in files
    ]

    # Two tenants writing to the same schema would truncate each other's tables.
    for field in ("name", "target_schema"):
        values = [getattr(t, field) for t in tenants]
        dupes = sorted({v for v in values if values.count(v) > 1})
        if dupes:
            raise TenantConfigError(f"duplicate {field} across tenant files: {dupes}")

    return tenants


def table_name_for(csv_path: Path) -> str:
    """olist_orders_dataset.csv -> olist_orders; other.csv -> other."""
    name = csv_path.name.lower()
    if name.endswith(CSV_SUFFIX):
        table = name[: -len(CSV_SUFFIX)]
    elif name.endswith(".csv"):
        table = name[: -len(".csv")]
    else:
        raise TenantConfigError(f"not a CSV file: {csv_path}")

    if not IDENTIFIER.match(table):
        raise TenantConfigError(f"{csv_path.name}: {table!r} is not a valid table name")
    return table


def plan_loads(tenant: Tenant) -> list[TableLoad]:
    """List every CSV in the tenant's source folders, with its target table."""
    loads: dict[str, TableLoad] = {}
    for folder in tenant.sources:
        if not folder.is_dir():
            raise TenantConfigError(
                f"tenant {tenant.name}: source folder not found: {folder}"
            )
        for csv_path in sorted(folder.glob("*.csv")):
            table = table_name_for(csv_path)
            if table in loads:
                raise TenantConfigError(
                    f"tenant {tenant.name}: {csv_path} and {loads[table].csv_path} "
                    f"both map to table {table!r}"
                )
            loads[table] = TableLoad(tenant.name, tenant.target_schema, table, csv_path)
    return list(loads.values())
