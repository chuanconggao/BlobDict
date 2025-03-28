from __future__ import annotations

from typing import override

from extratools_image import bytes_to_image, image_to_bytes
from PIL.Image import Image

from . import BytesBlob


class ImageBlob(BytesBlob):
    def __init__(self, blob: bytes | Image) -> None:
        if isinstance(blob, Image):
            blob = image_to_bytes(blob)

        super().__init__(blob)

    def as_image(self) -> Image:
        return bytes_to_image(self._blob_bytes)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"
