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
    def __init__(self, blob: bytes | AudioData) -> None:
        if isinstance(blob, AudioData):
            bio = BytesIO()
            soundfile.write(bio, AudioData.data, AudioData.sample_rate)
            blob = bio.getvalue()

        super().__init__(blob)

    def as_audio(self) -> AudioData:
        return AudioData(*soundfile.read(BytesIO(self._blob_bytes)))

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_audio().__repr__()})"
