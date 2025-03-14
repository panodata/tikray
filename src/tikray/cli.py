import logging
from pathlib import Path

import click
import yaml

from tikray.core import process_collection, process_project
from tikray.util.logging import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option("--transformation", "-t", type=Path, required=True, help="Transformation YAML file")
@click.option("--input", "-i", "input_", type=Path, required=True, help="Input file or directory")
@click.option("--output", "-o", type=Path, required=False, help="Output file or directory")
@click.option("--address", "-a", type=str, required=False, help="Select specific collection address")
@click.option("--jsonl", type=bool, is_flag=True, required=False, help="Select JSONL/NDJSON processing")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, transformation: Path, input_: Path, output: Path, address: str, jsonl: bool) -> None:
    setup_logging()
    tdata = yaml.safe_load(transformation.read_text())
    type_ = tdata["meta"]["type"]

    if type_ in ["tikray-collection", "zyp-collection"] or address is not None:  # noqa: RET506
        process_collection(transformation, input_, output, address, jsonl)

    elif type_ in ["tikray-project", "zyp-project"]:
        if not input_.is_dir():
            raise click.ClickException(f"Input is not a directory: {input_}")
        if output is None:
            raise click.ClickException("Processing multiple collections requires an output directory")
        if not output.is_dir():
            raise click.ClickException(f"Output is not a directory: {output}")
        process_project(transformation, input_, output, jsonl)

    else:
        raise NotImplementedError(f"Unknown transformation type: {type_}")
