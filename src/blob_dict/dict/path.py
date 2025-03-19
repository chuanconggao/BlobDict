import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import override

from ..blob import BytesBlob
from . import BlobDictBase


class LocalPath(Path):
    def rmtree(self) -> None:
        shutil.rmtree(self)


class PathBlobDict(BlobDictBase):
    def __init__(self, path: LocalPath) -> None:
        super().__init__()

        self.__path: LocalPath = path

    def create(self) -> None:
        self.__path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def delete(self) -> None:
        self.__path.rmtree()

    @override
    def __len__(self) -> int:
        return sum(1 for _ in self)

    @override
    def __contains__(self, key: str) -> bool:
        return (self.__path / key).is_file()

    @override
    def get(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        if key not in self:
            return default

        return BytesBlob((self.__path / key).read_bytes())

    @override
    def __getitem__(self, key: str) -> BytesBlob:
        blob: BytesBlob | None = self.get(key)
        if blob is None:
            raise KeyError

        return blob

    @override
    def __iter__(self) -> Iterator[str]:
        for parent, _, files in self.__path.walk(top_down=False):
            parent = parent.relative_to(self.__path)
            for filename in files:
                yield str(parent / filename)

    @override
    def clear(self) -> None:
        for parent, dirs, files in self.__path.walk(top_down=False):
            for filename in files:
                (parent / filename).unlink()
            for dirname in dirs:
                (parent / dirname).rmdir()

    def __cleanup(self, key: str) -> None:
        (self.__path / key).unlink()

        for parent in (self.__path / key).parents:
            if parent == self.__path:
                return

            if parent.is_dir() and next(parent.iterdir(), None) is None:
                parent.rmdir()

    @override
    def pop(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        blob: BytesBlob | None = self.get(key)
        if blob:
            self.__cleanup(key)

        return blob or default

    @override
    def __delitem__(self, key: str) -> None:
        if key not in self:
            raise KeyError

        self.__cleanup(key)

    @override
    def __setitem__(self, key: str, blob: BytesBlob) -> None:
        (self.__path / key).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        (self.__path / key).write_bytes(blob.as_bytes())
