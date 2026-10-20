"""Every container must get the shopflow DB credentials from the same variables."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")


def test_airflow_gets_same_credentials_as_postgres():
    services = yaml.safe_load((ROOT / "docker/compose.yml").read_text())["services"]
    postgres_env = services["postgres"]["environment"]
    airflow_env = services["airflow"]["environment"]
    for name in CREDENTIALS:
        assert airflow_env[name] == postgres_env[name]


def test_dbt_docker_target_has_no_fallbacks():
    docker = yaml.safe_load((ROOT / "transform/profiles.yml").read_text())["shopflow"][
        "outputs"
    ]["docker"]
    for key, name in [
        ("user", "POSTGRES_USER"),
        ("password", "POSTGRES_PASSWORD"),
        ("dbname", "POSTGRES_DB"),
    ]:
        assert docker[key] == f"{{{{ env_var('{name}') }}}}"
