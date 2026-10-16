from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_compose_file_exists():
    assert (ROOT / "docker" / "compose.yml").is_file()


def test_data_folder_is_ignored():
    gitignore = (ROOT / ".gitignore").read_text()
    assert "data/" in gitignore
