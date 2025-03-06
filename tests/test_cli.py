import json

from tikray.cli import cli


def test_cli_without_options_fail(cli_runner):
    """
    CLI test: Invoke `tikray` without any options passed.
    """
    result = cli_runner.invoke(
        cli,
        catch_exceptions=False,
    )
    assert result.exit_code == 2
    assert "Error: Missing option '--transformation' / '-t'." in result.output


def test_cli_success(cli_runner):
    """
    CLI test: Invoke `tikray` with example data.
    """

    data_out = [
        {"id": 12, "meta": {"name": "foo", "location": "B"}, "data": {"value": 42.42}},
        {"id": 34, "meta": {"name": "bar", "location": "BY"}, "data": {"value": -84.01}},
    ]

    result = cli_runner.invoke(
        cli,
        args="-t tests/transformation-collection.yaml -i examples/eai-warehouse.json",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    result = json.loads(result.output)
    assert result == data_out
