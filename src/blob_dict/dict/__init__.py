from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..blob import BytesBlob


class ImmutableBlobDictBase(ABC):
    def __len__(self) -> int:
        return sum(1 for _ in self)

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        ...

    @abstractmethod
    def get(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        ...

    def __getitem__(self, key: str) -> BytesBlob:
        blob: BytesBlob | None = self.get(key)
        if blob is None:
            raise KeyError

        return blob

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        ...


class BlobDictBase(ImmutableBlobDictBase, ABC):
    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def pop(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        ...

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        ...

    @abstractmethod
    def __setitem__(self, key: str, blob: BytesBlob) -> None:
        ...
