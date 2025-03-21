import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any, override

from cloudpathlib import CloudPath
from simple_zstd import compress, decompress

from ..blob import BytesBlob, StrBlob
from ..blob.json import JsonDictBlob
from . import BlobDictBase


class LocalPath(Path):
    def rmtree(self) -> None:
        shutil.rmtree(self)


class PathBlobDict(BlobDictBase):
    def __init__(
        self,
        path: LocalPath | CloudPath,
        *,
        compression: bool = False,
        blob_class: type[BytesBlob] = BytesBlob,
        blob_class_args: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()

        self.__path: LocalPath | CloudPath = path

        self.__compression: bool = compression

        self.__blob_class: type[BytesBlob] = blob_class
        self.__blob_class_args: dict[str, Any] = blob_class_args or {}

    def create(self) -> None:
        self.__path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def delete(self) -> None:
        self.__path.rmtree()

    @override
    def __contains__(self, key: str) -> bool:
        return (self.__path / key).is_file()

    def __get_blob_class(self, key: str) -> type[BytesBlob]:
        match (self.__path / key).suffix.lower():
            case ".json":
                return JsonDictBlob
            case ".png":
                # Import here as it has optional dependency
                from ..blob.image import ImageBlob  # noqa: PLC0415

                return ImageBlob
            # Common text file extensions
            # https://en.wikipedia.org/wiki/List_of_file_formats
            case (
                ".asc"
                | ".bib"
                | ".cfg"
                | ".cnf"
                | ".conf"
                | ".csv"
                | ".diff"
                | ".htm"
                | ".html"
                | ".ini"
                | ".log"
                | ".markdown"
                | ".md"
                | ".tex"
                | ".text"
                | ".toml"
                | ".tsv"
                | ".txt"
                | ".xhtml"
                | ".xht"
                | ".xml"
                | ".yaml"
                | ".yml"
            ):
                return StrBlob
            case _:
                return self.__blob_class

    @override
    def get(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        if key not in self:
            return default

        blob_bytes: bytes = (self.__path / key).read_bytes()
        if self.__compression:
            blob_bytes = decompress(blob_bytes)
        return self.__get_blob_class(key)(blob_bytes, **self.__blob_class_args)

    @override
    def __iter__(self) -> Iterator[str]:
        # The concept of relative path does not exist for `CloudPath`,
        # and each walked path is always absolute for `CloudPath`.
        # Therefore, we extract each key by removing the path prefix.
        # In this way, the same logic works for both absolute and relative path.
        prefix_len: int = (
            len(str(self.__path))
            # Extra 1 is for separator `/` between prefix and filename
            + 1
        )

        for parent, _, files in self.__path.walk(top_down=False):
            for filename in files:
                yield str(parent / filename)[prefix_len:]

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

    __BAD_BLOB_CLASS_ERROR_MESSAGE: str = "Must specify blob that is instance of {blob_class}"

    @override
    def __setitem__(self, key: str, blob: BytesBlob) -> None:
        if not isinstance(blob, self.__blob_class):
            raise TypeError(PathBlobDict.__BAD_BLOB_CLASS_ERROR_MESSAGE.format(
                blob_class=self.__blob_class,
            ))

        (self.__path / key).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blob_bytes: bytes = blob.as_bytes()
        if self.__compression:
            blob_bytes = compress(blob_bytes)
        (self.__path / key).write_bytes(blob_bytes)
