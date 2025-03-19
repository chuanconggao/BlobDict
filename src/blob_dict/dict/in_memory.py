from collections.abc import Iterator
from typing import override

from ..blob import BytesBlob
from . import BlobDictBase


class InMemoryBlobDict(BlobDictBase):
    def __init__(self) -> None:
        super().__init__()

        self.__dict: dict[str, BytesBlob] = {}

    @override
    def __len__(self) -> int:
        return len(self.__dict)

    @override
    def __contains__(self, key: str) -> bool:
        return key in self.__dict

    @override
    def get(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        return self.__dict.get(key, default)

    @override
    def __getitem__(self, key: str) -> BytesBlob:
        blob: BytesBlob | None = self.get(key)
        if blob is None:
            raise KeyError

        return blob

    @override
    def __iter__(self) -> Iterator[str]:
        yield from (
            key for key in self.__dict
        )

    @override
    def clear(self) -> None:
        self.__dict.clear()

    @override
    def pop(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        return self.__dict.pop(key, default)

    @override
    def __delitem__(self, key: str) -> None:
        del self.__dict[key]

    @override
    def __setitem__(self, key: str, blob: BytesBlob) -> None:
        self.__dict[key] = blob
