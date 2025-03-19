from __future__ import annotations

import json
from typing import Any


class BytesBlob:
    def __init__(self, blob: bytes) -> None:
        super().__init__()

        self._blob_bytes: bytes = blob

    def as_bytes(self) -> bytes:
        return self._blob_bytes


class StrBlob(BytesBlob):
    def __init__(self, blob: bytes | str) -> None:
        if isinstance(blob, str):
            blob = blob.encode()

        super().__init__(blob)

    def as_str(self) -> str:
        return self._blob_bytes.decode()


class JsonDictBlob(StrBlob):
    def __init__(self, blob: bytes | str | dict[str, Any]) -> None:
        if isinstance(blob, dict):
            blob = json.dumps(blob)

        super().__init__(blob)

    def as_dict(self) -> dict[str, Any]:
        return json.loads(self._blob_bytes)
