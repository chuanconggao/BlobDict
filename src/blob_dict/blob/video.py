from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import override

from moviepy.editor import VideoClip, VideoFileClip

from . import BytesBlob


class VideoBlob(BytesBlob):
    def __init__(self, blob: bytes | VideoClip) -> None:
        if isinstance(blob, VideoClip):
            with NamedTemporaryFile(suffix=".mp4", delete_on_close=False) as f:
                blob.write_videofile(f.name)
                blob.close()

                f.close()

                blob = Path(f.name).read_bytes()

        super().__init__(blob)

    def as_video(self, filename: str) -> VideoFileClip:
        Path(filename).write_bytes(self._blob_bytes)

        return VideoFileClip(filename)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"
