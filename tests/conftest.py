# ruff: noqa: E402
import pytest
from click.testing import CliRunner

jmespath = pytest.importorskip("jmespath")
jsonpointer = pytest.importorskip("jsonpointer")
transon = pytest.importorskip("transon")


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()
