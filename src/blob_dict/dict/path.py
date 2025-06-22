import shutil
from abc import abstractmethod
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from mimetypes import guess_type
from pathlib import Path
from typing import Any, Literal, Protocol, cast, override

from extratools_core.path import rm_with_empty_parents
from extratools_core.typing import PathLike, SearchableMapping

from ..blob import BytesBlob, StrBlob
from ..blob.json import JsonDictBlob, YamlDictBlob
from . import MutableBlobDictBase


class LocalPath(Path):
    def rmtree(self) -> None:
        shutil.rmtree(self)


class ExtraPathLike(PathLike, Protocol):
    @abstractmethod
    def rmtree(self) -> None:
        ...


class PathBlobDict(MutableBlobDictBase, SearchableMapping[str, BytesBlob]):
    def __init__(
        self,
        path: ExtraPathLike | None = None,
        *,
        compression: bool = False,
        ttl: timedelta | None = None,
        blob_class: type[BytesBlob] = BytesBlob,
        blob_class_args: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()

        if path is None:
            path = LocalPath(".")

        if isinstance(path, Path):
            path = path.expanduser()

        self.__path: ExtraPathLike = path

        # The concept of relative path does not exist for `CloudPath`,
        # and each walked path is always absolute for `CloudPath`.
        # Therefore, we extract each key by removing the path prefix.
        # In this way, the same logic works for both absolute and relative path.
        self.__prefix_len: int = (
            len(str(self.__path.absolute()))
            # Extra 1 is for separator `/` between prefix and filename
            + 1
        )

        self.__compression: bool = compression

        # Note that we do not automatically cleanup by TTL for reasons below:
        # - It is tricky to do so for local path without CRON job or daemon process
        # - Multiple objects could actually use same directory with different TTLs
        # Thus, it is best to depend on native solution for cleanup by TTL,
        # like S3's object lifecycle management.
        self.__ttl: timedelta | None = ttl

        self.__blob_class: type[BytesBlob] = blob_class
        self.__blob_class_args: dict[str, Any] = blob_class_args or {}

    def create(self) -> None:
        self.__path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def delete(self) -> None:
        self.__path.rmtree()

    def __is_expired(self, key_path: PathLike) -> bool:
        return (
            datetime.now(UTC)
            - datetime.fromtimestamp(key_path.stat().st_mtime, UTC)
            > cast("timedelta", self.__ttl)
        )

    @override
    def __contains__(self, key: object) -> bool:
        key_path: PathLike = self.__path / str(key)

        return (
            key_path.is_file()
            and (
                not self.__ttl
                or not self.__is_expired(key_path)
            )
        )

    def __get_blob_class(self, key: str) -> type[BytesBlob]:  # noqa: PLR0911
        mime_type: str | None
        mime_type, _ = guess_type(self.__path / key)

        match mime_type:
            case "application/json":
                return JsonDictBlob
            case "application/octet-stream":
                return BytesBlob
            case "application/yaml":
                return YamlDictBlob
            case "audo/mpeg":
                # Import here as it has optional dependency
                from ..blob.audio import AudioBlob  # noqa: PLC0415

                return AudioBlob
            case "image/png":
                # Import here as it has optional dependency
                from ..blob.image import ImageBlob  # noqa: PLC0415

                return ImageBlob
            case (
                "text/css"
                 | "text/csv"
                 | "text/html"
                 | "text/javascript"
                 | "text/markdown"
                 | "text/plain"
                 | "text/xml"
            ):
                return StrBlob
            case "video/mp4":
                # Import here as it has optional dependency
                from ..blob.video import VideoBlob  # noqa: PLC0415

                return VideoBlob
            case _:
                return self.__blob_class

    def _get(self, key: str, blob_bytes: bytes) -> BytesBlob:
        blob: BytesBlob = BytesBlob.from_bytes(blob_bytes, compression=self.__compression)
        return blob.as_blob(
            self.__get_blob_class(key),
            self.__blob_class_args,
        )

    @override
    def __getitem__(self, key: str, /) -> BytesBlob:
        if key not in self:
            raise KeyError

        return self._get(key, (self.__path / key).read_bytes())

    def __path_to_str(self, path: ExtraPathLike) -> str:
        return str(path.absolute())[self.__prefix_len:]

    @override
    def __iter__(self) -> Iterator[str]:
        for parent, _, files in self.__path.walk():
            for filename in files:
                key_path: PathLike = parent / filename
                if self.__ttl and self.__is_expired(key_path):
                    continue

                yield self.__path_to_str(key_path)

    @override
    def search(self, filter_body: str | None = None) -> Iterator[str]:
        for key_path in self.__path.glob(filter_body or "**"):
            if key_path.is_file():
                yield self.__path_to_str(key_path)

    @override
    def clear(self) -> None:
        for parent, dirs, files in self.__path.walk(top_down=False):
            for filename in files:
                (parent / filename).unlink()
            for dirname in dirs:
                (parent / dirname).rmdir()

    def __cleanup(self, key: str) -> None:
        rm_with_empty_parents(self.__path / key, stop=self.__path)

    @override
    def pop[T: Any](
        self,
        key: str,
        /,
        default: BytesBlob | T | Literal["__DEFAULT"] = "__DEFAULT",
    ) -> BytesBlob | T:
        blob: BytesBlob | None = self.get(key)
        if blob:
            self.__cleanup(key)

        if blob is not None:
            return blob

        if default == "__DEFAULT":
            raise KeyError

        return default

    @override
    def __delitem__(self, key: str, /) -> None:
        if key not in self:
            raise KeyError

        self.__cleanup(key)

    __BAD_BLOB_CLASS_ERROR_MESSAGE: str = "Must specify blob that is instance of {blob_class}"

    @override
    def __setitem__(self, key: str, blob: BytesBlob, /) -> None:
        if not isinstance(blob, self.__blob_class):
            raise TypeError(PathBlobDict.__BAD_BLOB_CLASS_ERROR_MESSAGE.format(
                blob_class=self.__blob_class,
            ))

        (self.__path / key).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blob_bytes: bytes = blob.as_bytes(compression=self.__compression)
        (self.__path / key).write_bytes(blob_bytes)
