from __future__ import annotations

from io import BytesIO
from typing import NamedTuple, override

import numpy
import soundfile

from . import BytesBlob


class AudioData(NamedTuple):
    data: numpy.ndarray
    sample_rate: int


class AudioBlob(BytesBlob):
    __IN_MEMORY_FILE_NAME: str = "file.mp3"

    def __init__(self, blob: bytes | AudioData) -> None:
        if isinstance(blob, AudioData):
            bio = BytesIO()
            bio.name = AudioBlob.__IN_MEMORY_FILE_NAME
            soundfile.write(bio, AudioData.data, AudioData.sample_rate)
            blob = bio.getvalue()

        super().__init__(blob)

    def as_audio(self) -> AudioData:
        bio = BytesIO(self._blob_bytes)
        bio.name = AudioBlob.__IN_MEMORY_FILE_NAME
        return AudioData(*soundfile.read(bio))

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"
