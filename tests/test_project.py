import sys

import pytest

from tikray.model.collection import CollectionAddress, CollectionTransformation
from tikray.model.project import ProjectTransformation


@pytest.mark.skipif(sys.version_info < (3, 9), reason="Does not work on Python 3.8 and earlier")
def test_project_success():
    address = CollectionAddress(container="foo", name="bar")
    ct = CollectionTransformation(address=address)
    pt = ProjectTransformation().add(ct)
    pt.to_yaml()

    pt = ProjectTransformation(collections=[ct])
    pt.to_yaml()

    assert pt.get(address) is ct


def test_project_failure():
    with pytest.raises(ValueError) as ex:
        ProjectTransformation().add(CollectionTransformation())
    assert ex.match("CollectionTransformation or address missing")
