from pathlib import Path

import pytest
from tenant_config import (
    Tenant,
    TenantConfigError,
    load_tenants,
    parse_tenant,
    plan_loads,
    table_name_for,
)

ROOT = Path(__file__).resolve().parents[1]

VALID = {
    "tenant": "acme",
    "target_schema": "raw_acme",
    "sources": ["/data/a", "/data/b"],
}


def write(path: Path, text: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


# --- parse_tenant ---------------------------------------------------------


def test_parse_valid_tenant():
    tenant = parse_tenant(VALID)
    assert tenant == Tenant("acme", "raw_acme", (Path("/data/a"), Path("/data/b")))


@pytest.mark.parametrize("field", ["tenant", "target_schema", "sources"])
def test_missing_field_is_rejected(field):
    data = {k: v for k, v in VALID.items() if k != field}
    with pytest.raises(TenantConfigError, match=field):
        parse_tenant(data)


@pytest.mark.parametrize(
    "schema", ["Raw", "raw-acme", "1raw", "raw; drop table x", "", 5]
)
def test_unsafe_schema_name_is_rejected(schema):
    with pytest.raises(TenantConfigError, match="target_schema"):
        parse_tenant({**VALID, "target_schema": schema})


@pytest.mark.parametrize("sources", [[], "/data/a", [""], [None]])
def test_bad_sources_are_rejected(sources):
    with pytest.raises(TenantConfigError, match="sources"):
        parse_tenant({**VALID, "sources": sources})


def test_non_mapping_is_rejected():
    with pytest.raises(TenantConfigError, match="mapping"):
        parse_tenant(["not", "a", "mapping"])


# --- load_tenants -----------------------------------------------------------


def test_load_tenants_reads_yml_and_yaml_sorted(tmp_path):
    write(tmp_path / "b.yaml", "tenant: b\ntarget_schema: raw_b\nsources: [/x]\n")
    write(tmp_path / "a.yml", "tenant: a\ntarget_schema: raw_a\nsources: [/x]\n")
    write(tmp_path / "notes.txt", "ignored")
    assert [t.name for t in load_tenants(tmp_path)] == ["a", "b"]


def test_duplicate_schema_across_tenants_is_rejected(tmp_path):
    write(tmp_path / "a.yml", "tenant: a\ntarget_schema: raw_shared\nsources: [/x]\n")
    write(tmp_path / "b.yml", "tenant: b\ntarget_schema: raw_shared\nsources: [/x]\n")
    with pytest.raises(TenantConfigError, match="duplicate target_schema"):
        load_tenants(tmp_path)


def test_missing_tenants_folder_is_rejected(tmp_path):
    with pytest.raises(TenantConfigError, match="not found"):
        load_tenants(tmp_path / "nope")


def test_repo_olist_tenant_is_valid():
    (olist,) = [t for t in load_tenants(ROOT / "tenants") if t.name == "olist"]
    assert olist.target_schema == "raw_olist"
    assert olist.sources == (
        Path("/opt/airflow/data/raw/olist"),
        Path("/opt/airflow/data/raw/marketing_funnel"),
    )


# --- table_name_for / plan_loads -------------------------------------------


@pytest.mark.parametrize(
    ("file_name", "table"),
    [
        ("olist_orders_dataset.csv", "olist_orders"),
        ("product_category_name_translation.csv", "product_category_name_translation"),
        ("Olist_Sellers_Dataset.CSV", "olist_sellers"),
    ],
)
def test_table_name_for(file_name, table):
    assert table_name_for(Path(file_name)) == table


def test_table_name_for_rejects_unsafe_names():
    with pytest.raises(TenantConfigError):
        table_name_for(Path("my orders.csv"))


def test_plan_loads_finds_csvs_in_all_sources(tmp_path):
    write(tmp_path / "a" / "orders_dataset.csv")
    write(tmp_path / "a" / "readme.md")
    write(tmp_path / "b" / "leads_dataset.csv")
    tenant = Tenant("acme", "raw_acme", (tmp_path / "a", tmp_path / "b"))

    loads = plan_loads(tenant)

    assert [(x.schema, x.table, x.csv_path.name) for x in loads] == [
        ("raw_acme", "orders", "orders_dataset.csv"),
        ("raw_acme", "leads", "leads_dataset.csv"),
    ]


def test_plan_loads_rejects_two_files_for_one_table(tmp_path):
    write(tmp_path / "a" / "orders_dataset.csv")
    write(tmp_path / "b" / "orders.csv")
    tenant = Tenant("acme", "raw_acme", (tmp_path / "a", tmp_path / "b"))
    with pytest.raises(TenantConfigError, match="both map to table 'orders'"):
        plan_loads(tenant)


def test_plan_loads_rejects_missing_source_folder(tmp_path):
    tenant = Tenant("acme", "raw_acme", (tmp_path / "missing",))
    with pytest.raises(TenantConfigError, match="source folder not found"):
        plan_loads(tenant)
