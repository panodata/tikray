import json
import logging
import sys
from pathlib import Path

import click
import yaml

from tikray.model.collection import CollectionTransformation
from tikray.util.data import jd
from tikray.util.logging import setup_logging

logger = logging.getLogger(__name__)


@click.command()
@click.option("--transformation", "-t", type=Path, required=True, help="Transformation YAML file")
@click.option("--input", "-i", "input_", type=Path, required=True, help="Input file")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, transformation: Path, input_: Path) -> None:
    setup_logging()
    logger.info(f"Using transformation {transformation}, input {input_}")
    tdata = yaml.safe_load(transformation.read_text())
    data = json.loads(input_.read_text())
    type_ = tdata["meta"]["type"]
    if type_ in ["tikray-project", "zyp-project"]:
        """
        from tikray.model.project import TransformationProject
        from tikray.model.collection import CollectionAddress

        project = TransformationProject.from_yaml(transformation.read_text())
        data = json.loads(Path("examples/eai-warehouse.json").read_text())
        address = CollectionAddress("foo", "bar")
        transformation = project.get(address)
        print(transformation.apply(data))
        """
        raise NotImplementedError("Processing projects not implemented yet")
    elif type_ in ["tikray-collection", "zyp-collection"]:  # noqa: RET506
        ct = CollectionTransformation.from_yaml(transformation.read_text())
        result = ct.apply(data)
        sys.stdout.write(jd(result))
    else:
        raise NotImplementedError(f"Unknown transformation type: {type_}")
