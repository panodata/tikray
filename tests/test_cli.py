import json
from pathlib import Path

from tikray.cli import cli

eai_warehouse_reference = [
    {"id": 12, "meta": {"name": "foo", "location": "B"}, "data": {"value": 42.42}},
    {"id": 34, "meta": {"name": "bar", "location": "BY"}, "data": {"value": -84.01}},
]

acme_conversation_reference = json.loads((Path("tests") / "examples" / "conversation.json").read_text())


def test_cli_collection_stdout_success(cli_runner):
    """
    CLI test: Single resource to STDOUT.
    """

    result = cli_runner.invoke(
        cli,
        args="-t examples/transformation-collection.yaml -i examples/eai-warehouse.json",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == eai_warehouse_reference


def test_cli_collection_file_output_success(cli_runner, tmp_path):
    """
    CLI test: Single resource to file.
    """

    output_path = tmp_path / "output.json"
    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-collection.yaml -i examples/eai-warehouse.json -o {output_path}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert result.output == ""
    data = json.loads(output_path.read_text())
    assert data == eai_warehouse_reference


def test_cli_collection_directory_output_success(cli_runner, tmp_path):
    """
    CLI test: Single resource to directory.
    """

    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-collection.yaml -i examples/eai-warehouse.json -o {tmp_path}",
        catch_exceptions=False,
    )
    output_path = tmp_path / "eai-warehouse.json"
    assert result.exit_code == 0
    assert result.output == ""
    data = json.loads(output_path.read_text())
    assert data == eai_warehouse_reference


def test_cli_project_success(cli_runner, tmp_path):
    """
    CLI test: Multiple resources (project) to directory.
    """

    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-project.yaml -i examples/acme -o {tmp_path}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    output = json.loads(Path(tmp_path / "conversation.json").read_text())
    assert output == acme_conversation_reference


def test_cli_collection_from_project_file_success(cli_runner, tmp_path):
    """
    CLI test: Single resource from Tikray project file.
    """

    result = cli_runner.invoke(
        cli,
        args="-t examples/transformation-project.yaml -i examples/acme/conversation.json -a acme.conversation",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == acme_conversation_reference


def test_cli_project_warning_no_transformation(cli_runner, tmp_path, caplog):
    """
    CLI test: Verify processing multiple resources emits warnings on missing ones.
    """

    project = tmp_path / "project"
    project.mkdir()
    out = tmp_path / "output"
    out.mkdir()
    (project / "foo.json").touch()

    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-project.yaml -i {project} -o {out}",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert (
        "Could not find transformation definition for collection: CollectionAddress(container='project', name='foo')"
        in caplog.messages
    )


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


def test_cli_project_invocation_failure(cli_runner, tmp_path):
    """
    CLI test: Check that invoking `tikray` erroneously fails correctly.
    """

    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-project.yaml -i examples/acme/conversation.json -o {tmp_path}",
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert result.output == "Error: Input is not a directory: examples/acme/conversation.json\n"

    result = cli_runner.invoke(
        cli,
        args="-t examples/transformation-project.yaml -i examples/acme",
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert result.output == "Error: Processing multiple collections requires an output directory\n"

    result = cli_runner.invoke(
        cli,
        args=f"-t examples/transformation-project.yaml -i examples/acme -o {tmp_path / 'conversation.json'}",
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert result.output == f"Error: Output is not a directory: {tmp_path / 'conversation.json'}\n"
