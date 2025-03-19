from __future__ import annotations

from io import BytesIO

from PIL.Image import Image
from PIL.Image import open as open_image

from . import BytesBlob


class ImageBlob(BytesBlob):
    def __init__(self, blob: bytes | Image) -> None:
        if isinstance(blob, Image):
            bio = BytesIO()
            blob.save(bio, format="PNG")

            blob = bio.getvalue()

        super().__init__(blob)

    def as_image(self) -> Image:
        return open_image(self._blob_bytes)
