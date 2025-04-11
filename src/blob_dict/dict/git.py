from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, override

from extratools_git.repo import Repo

from ..blob import BytesBlob
from .path import LocalPath, PathBlobDict


class GitBlobDict(PathBlobDict):
    def __init__(
        self,
        path: LocalPath,
        *,
        user_name: str,
        user_email: str,
        use_remote: bool = False,
        use_remote_frequence: timedelta = timedelta(minutes=1),
        **kwargs: Any,
    ) -> None:
        self.__repo_path: LocalPath = path.expanduser()

        self.__repo: Repo = Repo.init(
            path,
            user_name=user_name,
            user_email=user_email,
        )
        self.__user_name: str = user_name
        self.__user_email: str = user_email

        self.__use_remote: bool = use_remote
        self.__use_remote_frequence: timedelta = use_remote_frequence
        self.__last_use_remote_time: datetime = datetime.now(UTC) - use_remote_frequence

        super().__init__(self.__repo_path, **kwargs)

    @override
    def create(self) -> None:
        super().create()

        Repo.init(
            self.__repo_path,
            user_name=self.__user_name,
            user_email=self.__user_email,
        )

    @staticmethod
    def is_forbidden_key(key: str) -> bool:
        return key in {".git", ".gitignore"} or key.startswith(".git/")

    __FORBIDDEN_KEY_ERROR_MESSAGE: str = "Cannot use any Git reserved file name as key"

    @override
    def __contains__(self, key: str) -> bool:
        if self.is_forbidden_key(key):
            raise ValueError(self.__FORBIDDEN_KEY_ERROR_MESSAGE)

        return super().__contains__(key)

    def __can_use_remote(self) -> bool:
        return (
            self.__use_remote
            and datetime.now(UTC) - self.__last_use_remote_time >= self.__use_remote_frequence
        )

    @override
    def get(self, key: str | tuple[str, Any], default: BytesBlob | None = None) -> BytesBlob | None:
        if self.__can_use_remote():
            self.__repo.pull(background=True)

        if isinstance(key, str):
            return super().get(key, default)

        try:
            key, version = key

            return self._get(
                key,
                self.__repo.get_blob(key, version=version),
            )
        except FileNotFoundError:
            return default

    @override
    def __iter__(self) -> Iterator[str]:
        for child_path in self.__repo_path.iterdir():
            if self.is_forbidden_key(child_path.name):
                continue

            if child_path.is_dir():
                for parent, _, files in child_path.walk():
                    for filename in files:
                        yield str((parent / filename).relative_to(self.__repo_path))
            else:
                yield str(child_path.relative_to(self.__repo_path))

    @override
    def pop(self, key: str, default: BytesBlob | None = None) -> BytesBlob | None:
        if self.is_forbidden_key(key):
            raise ValueError(self.__FORBIDDEN_KEY_ERROR_MESSAGE)

        result: BytesBlob | None = super().pop(key, default)
        if result is None:
            return None

        self.__repo.stage(key)
        self.__repo.commit(f"Delete {key}")

        if self.__can_use_remote():
            self.__repo.push(background=True)

        return result

    @override
    def __delitem__(self, key: str) -> None:
        if self.is_forbidden_key(key):
            raise ValueError(self.__FORBIDDEN_KEY_ERROR_MESSAGE)

        super().__delitem__(key)

        self.__repo.stage(key)
        self.__repo.commit(f"Delete {key}")

        if self.__can_use_remote():
            self.__repo.push(background=True)

    @override
    def __setitem__(self, key: str, blob: BytesBlob) -> None:
        if self.is_forbidden_key(key):
            raise ValueError(self.__FORBIDDEN_KEY_ERROR_MESSAGE)

        exists: bool = key in self

        super().__setitem__(key, blob)

        self.__repo.stage(key)
        self.__repo.commit(f"{"Update" if exists else "Add"} {key}")

        if self.__can_use_remote():
            self.__repo.push(background=True)
