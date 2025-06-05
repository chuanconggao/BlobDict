from __future__ import annotations

from pathlib import Path
from typing import Self, override

from moviepy.video.VideoClip import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from . import BytesBlob
from .audio_video import read_from_clip


class VideoBlob(BytesBlob):
    def __init__(
        self,
        blob: bytes | VideoClip,
        *,
        delete_temp_clip_file: bool = False,
    ) -> None:
        if isinstance(blob, VideoClip):
            blob = read_from_clip(
                blob,
                ".mp4",
                delete_temp_clip_file=delete_temp_clip_file,
            )

        super().__init__(blob)

    def as_video(self, filename: str) -> VideoFileClip:
        Path(filename).write_bytes(self._blob_bytes)

        return VideoFileClip(filename)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"

    @classmethod
    @override
    def load(cls: type[Self], f: Path | str) -> Self:
        f = Path(f).expanduser()

        if f.suffix.lower() == ".mp4":
            return cls(f.read_bytes())

        clip = VideoFileClip(str(f))
        blob = cls(clip)
        clip.close()

        return blob

    @override
    def dump(self, f: Path | str) -> None:
        f = Path(f).expanduser()
        if f.suffix.lower() != ".mp4":
            msg = "Only MP4 file is supported."
            raise ValueError(msg)

        f.write_bytes(self.as_bytes())
