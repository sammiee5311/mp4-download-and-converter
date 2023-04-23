from __future__ import annotations

import os
from pathlib import Path

import ffmpeg

from config import load_env
from logs.logging import logger

load_env()


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")


def get_converted_videos() -> list[Path]:
    return [res for res in Path(CONVERTED_PATH).glob("**/*.mp3") if res.is_file()]


def convert_mp4_to_mp3(file_name: str, overwrite: bool, quiet: bool) -> None:  # pragma: no cover
    orginal_file_path = Path(file_name)
    output_file = orginal_file_path.with_suffix(".mp3")

    if not overwrite and CONVERTED_PATH / output_file in get_converted_videos():
        return

    input_file_path = DOWNLOAD_PATH / orginal_file_path
    output_file_path = CONVERTED_PATH / output_file
    video = ffmpeg.input(input_file_path)
    audio = ffmpeg.output(video.audio, str(output_file_path))
    ffmpeg.run(audio, overwrite_output=True, quiet=quiet)

    logger.info(f"(CONVERT) %s is converted successfully.", file_name)
