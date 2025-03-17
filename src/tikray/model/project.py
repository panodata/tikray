import typing as t

from attr import Factory
from attrs import define

from tikray.model.base import Dumpable, Metadata
from tikray.model.collection import CollectionAddress, CollectionTransformation


@define
class ProjectTransformation(Dumpable):
    meta: Metadata = Metadata(version=1, type="tikray-project")
    collections: t.List[CollectionTransformation] = Factory(list)
    _map: t.Dict[CollectionAddress, CollectionTransformation] = Factory(dict)

    def __attrs_post_init__(self):
        if self.collections and not self._map:
            for collection in self.collections:
                self._add(collection)

    def _add(self, collection: CollectionTransformation) -> "ProjectTransformation":
        if collection is None or collection.address is None:
            raise ValueError("CollectionTransformation or address missing")
        self._map[collection.address] = collection
        return self

    def add(self, collection: CollectionTransformation) -> "ProjectTransformation":
        self.collections.append(collection)
        return self._add(collection)

    def get(self, address: CollectionAddress) -> CollectionTransformation:
        return self._map[address]
