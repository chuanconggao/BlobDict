from __future__ import annotations


class BytesBlob:
    def __init__(self, blob: bytes) -> None:
        super().__init__()

        self._blob_bytes: bytes = blob

    def as_blob(self, blob_class: type[BytesBlob]) -> BytesBlob:
        return blob_class(self._blob_bytes)

    def as_bytes(self) -> bytes:
        return self._blob_bytes


class StrBlob(BytesBlob):
    def __init__(self, blob: bytes | str) -> None:
        if isinstance(blob, str):
            blob = blob.encode()

        super().__init__(blob)

    def as_str(self) -> str:
        return self._blob_bytes.decode()
