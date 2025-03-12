import json
import logging
import sys
import typing as t
from pathlib import Path

from tikray.model.collection import CollectionAddress, CollectionTransformation
from tikray.model.project import TransformationProject
from tikray.util.data import jd

logger = logging.getLogger(__name__)


def process_project(transformation: Path, input_: Path, output: Path):
    logger.info(f"Using transformation '{transformation}' on multi-collection input '{input_}'")

    project = TransformationProject.from_yaml(transformation.read_text())
    for item in input_.iterdir():
        logger.info(f"Processing input: {item}")
        address = CollectionAddress(container=item.parent.name, name=item.stem)
        try:
            tikray_transformation = project.get(address)
        except KeyError as ex:
            logger.warning(f"Could not find transformation definition for collection: {ex}")
            continue
        data = json.loads(Path(item).read_text())
        output_path = output / item.name
        with open(output_path, "w") as output_stream:
            print(jd(tikray_transformation.apply(data)), file=output_stream)
            logger.info(f"Processed output: {output_path}")


def process_collection(transformation: Path, input_: Path, output: t.Optional[Path] = None):
    logger.info(f"Using transformation '{transformation}' on single-collection input '{input_}'")
    data = json.loads(input_.read_text())
    ct = CollectionTransformation.from_yaml(transformation.read_text())
    result = ct.apply(data)
    output_stream = sys.stdout
    if output is not None:
        if output.is_dir():
            output = output / input_.name
        output_stream = open(output, "w")
    output_stream.write(jd(result))
    output_stream.flush()
