from collections.abc import Iterator
from typing import override

from ..blob import BytesBlob
from . import BlobDictBase


class MultiReplicaBlobDict(BlobDictBase):
    def __init__(
        self,
        replica_dicts: dict[str, BlobDictBase],
    ) -> None:
        super().__init__()

        self.__replica_dicts: dict[str, BlobDictBase] = replica_dicts
        self.__primary_dict: BlobDictBase = next(iter(replica_dicts.values()))

    @override
    def __len__(self) -> int:
        return len(self.__primary_dict)

    def len(
        self,
        *,
        replica_name: str | None = None,
    ) -> int:
        return len(
            self.__replica_dicts[replica_name] if replica_name
            else self.__primary_dict,
        )

    @override
    def __contains__(self, key: str) -> bool:
        return self.contains(key)

    def contains(
        self,
        key: str,
        *,
        replica_names: set[str] | None = None,
    ) -> bool:
        return any(
            key in self.__replica_dicts[replica_name]
            for replica_name in (
                self.__replica_dicts.keys() if replica_names is None
                else replica_names
            )
        )

    @override
    def get(
        self,
        key: str,
        default: BytesBlob | None = None,
        *,
        replica_names: set[str] | None = None,
    ) -> BytesBlob | None:
        for replica_name in (
            self.__replica_dicts.keys() if replica_names is None
            else replica_names
        ):
            replica_dict: BlobDictBase = self.__replica_dicts[replica_name]
            blob: BytesBlob | None
            if blob := replica_dict.get(key, default):
                return blob

        return default

    @override
    def __getitem__(self, key: str) -> BytesBlob:
        blob: BytesBlob | None = self.get(key)
        if blob is None:
            raise KeyError

        return blob

    @override
    def __iter__(self) -> Iterator[str]:
        yield from (
            key for key in self.__primary_dict
        )

    def iter(
        self,
        *,
        replica_name: str | None = None,
    ) -> Iterator[str]:
        yield from (
            key for key in (
                self.__replica_dicts[replica_name] if replica_name
                else self.__primary_dict
            )
        )

    @override
    def clear(
        self,
        *,
        replica_names: set[str] | None = None,
    ) -> None:
        for replica_name in (
            self.__replica_dicts.keys() if replica_names is None
            else replica_names
        ):
            replica_dict: BlobDictBase = self.__replica_dicts[replica_name]
            replica_dict.clear()

    @override
    def pop(
        self,
        key: str,
        default: BytesBlob | None = None,
        *,
        replica_names: set[str] | None = None,
    ) -> BytesBlob | None:
        final_blob: BytesBlob | None = default
        for replica_name in (
            self.__replica_dicts.keys() if replica_names is None
            else replica_names
        ):
            replica_dict: BlobDictBase = self.__replica_dicts[replica_name]
            if (blob := replica_dict.pop(key)) and not final_blob:
                final_blob = blob

        return final_blob

    @override
    def __delitem__(self, key: str) -> None:
        if key not in self:
            raise KeyError

        self.pop(key)

    @override
    def __setitem__(
        self,
        key: str,
        blob: BytesBlob,
        *,
        replica_names: set[str] | None = None,
    ) -> None:
        for replica_name in (
            self.__replica_dicts.keys() if replica_names is None
            else replica_names
        ):
            replica_dict: BlobDictBase = self.__replica_dicts[replica_name]
            replica_dict[key] = blob
