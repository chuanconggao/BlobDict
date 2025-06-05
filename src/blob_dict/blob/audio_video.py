from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir

from moviepy.audio.AudioClip import AudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def read_from_clip(
    clip: AudioClip | VideoClip,
    suffix: str,
    *,
    delete_temp_clip_file: bool = False,
) -> bytes:
    data: bytes

    clip_file: Path | None = None
    if (
        isinstance(clip, (AudioFileClip, VideoFileClip))
        # Need to check whether `filename` is `str` as it can also be sound array for Audio clip
        and isinstance(clip.filename, str)
    ):
        clip_file = Path(clip.filename)

    if (
        clip_file
        and clip_file.suffix.lower() == suffix
    ):
        data = clip_file.read_bytes()
    else:
        with NamedTemporaryFile(suffix=suffix, delete_on_close=False) as f:
            if isinstance(clip, AudioClip):
                clip.write_audiofile(f.name)
            elif isinstance(clip, VideoClip):
                clip.write_videofile(f.name)

            f.close()

            data = Path(f.name).read_bytes()

    if (
        delete_temp_clip_file
        and clip_file
        and clip_file.is_relative_to(gettempdir())
    ):
        clip_file.unlink()

    return data
