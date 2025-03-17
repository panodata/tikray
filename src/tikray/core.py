import logging
import typing as t
from pathlib import Path

from toolz import partition_all
from tqdm import tqdm

from tikray.model.collection import CollectionAddress, CollectionTransformation
from tikray.model.project import ProjectTransformation
from tikray.util.data import lines_in_file, load_json, save_json

logger = logging.getLogger(__name__)


def process_project(transformation: Path, input_: Path, output: Path, use_jsonl: bool = False) -> None:
    logger.info(f"Using transformation '{transformation}' on multi-collection input '{input_}'")

    project = ProjectTransformation.from_yaml(transformation.read_text())
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
) -> None:
    logger.info(f"Using transformation '{transformation}' on single-collection input '{input_}'")
    ct = CollectionTransformation.from_yaml(transformation.read_text())
    if address is not None:
        pt = ProjectTransformation.from_yaml(transformation.read_text())
        ct = pt.get(CollectionAddress(*address.split(".")))
    logger.info(f"Processing input: {input_}")
    lines = lines_in_file(input_)
    logger.info(f"Input lines: {lines}")
    data = load_json(input_, use_jsonl=use_jsonl)
    if output is not None:
        if output.is_dir():
            output = output / input_.name
    if output:
        output.write_bytes(b"")
    if isinstance(data, t.Generator):
        progress = tqdm(total=lines)
        for chunk in partition_all(5_000, data):
            result = ct.apply(chunk)
            save_json(result, output, use_jsonl=use_jsonl, append=True)
            progress.update(len(chunk))
    else:
        result = ct.apply(data)
        save_json(result, output, use_jsonl=use_jsonl)

    logger.info(f"Processed output: {output or 'stdout'}")
