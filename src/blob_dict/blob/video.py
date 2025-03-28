from __future__ import annotations

from pathlib import Path
from typing import override
from uuid import uuid4

from moviepy.editor import VideoClip, VideoFileClip

from . import BytesBlob


class VideoBlob(BytesBlob):
    def __init__(self, blob: bytes | VideoClip) -> None:
        if isinstance(blob, VideoClip):
            temp_file: Path = Path(f"{uuid4()}.mp4")
            blob.write_videofile(temp_file)
            blob.close()

            blob = temp_file.read_bytes()
            temp_file.unlink()

        super().__init__(blob)

    def as_video(self, filename: str) -> VideoFileClip:
        Path(filename).write_bytes(self._blob_bytes)

        return VideoFileClip(filename)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"
