import logging
import typing as t
from pathlib import Path

from tikray.model.collection import CollectionAddress, CollectionTransformation
from tikray.model.project import TransformationProject
from tikray.util.data import load_json, save_json

logger = logging.getLogger(__name__)


def process_project(transformation: Path, input_: Path, output: Path, use_jsonl: bool = False):
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
        data = load_json(Path(item), use_jsonl=use_jsonl)
        output_path = output / item.name
        save_json(tikray_transformation.apply(data), output_path, use_jsonl=use_jsonl)
        logger.info(f"Processed output: {output_path}")


def process_collection(
    transformation: Path,
    input_: Path,
    output: t.Optional[Path] = None,
    address: t.Optional[str] = None,
    use_jsonl: bool = False,
):
    logger.info(f"Using transformation '{transformation}' on single-collection input '{input_}'")
    ct = CollectionTransformation.from_yaml(transformation.read_text())
    if address is not None:
        pt = TransformationProject.from_yaml(transformation.read_text())
        ct = pt.get(CollectionAddress(*address.split(".")))
    logger.info(f"Processing input: {input_}")
    data = load_json(input_, use_jsonl=use_jsonl)
    result = ct.apply(data)
    if output is not None:
        if output.is_dir():
            output = output / input_.name
    save_json(result, output, use_jsonl=use_jsonl)
    logger.info(f"Processed output: {output or 'stdout'}")
