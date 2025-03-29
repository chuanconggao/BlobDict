from __future__ import annotations

from base64 import b64decode, b64encode
from typing import override


class BytesBlob:
    def __init__(self, blob: bytes) -> None:
        super().__init__()

        self._blob_bytes: bytes = blob

    def as_blob(self, blob_class: type[BytesBlob]) -> BytesBlob:
        return blob_class(self._blob_bytes)

    def as_bytes(self) -> bytes:
        return self._blob_bytes

    @staticmethod
    def from_b64_str(s: str) -> BytesBlob:
        return BytesBlob(b64decode(s))

    def as_b64_str(self) -> str:
        return b64encode(self._blob_bytes).decode("ascii")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_bytes().__repr__()})"


class StrBlob(BytesBlob):
    def __init__(self, blob: bytes | str) -> None:
        if isinstance(blob, str):
            blob = blob.encode()

        super().__init__(blob)

    def as_str(self) -> str:
        return self._blob_bytes.decode()

    def __str__(self) -> str:
        return self.as_str()

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_str().__repr__()})"
