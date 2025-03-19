from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..blob import BytesBlob


class ImmutableBlobDictBase(ABC):
    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        ...

    @abstractmethod
    def get(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        ...

    @abstractmethod
    def __getitem__(self, key: str) -> BytesBlob:
        ...

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
