from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import ffmpeg

from config import load_env
from helper import MAX_RETRY_TIMES
from helper import retry_func
from logs.logging import logger
from mp4_types import ConvertStatus

load_env()


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")


@dataclass(frozen=True)
class ConvertFile:
    input_path: Path
    output_path: Path
    name: str


def get_converted_videos() -> list[Path]:
    return [res for res in Path(CONVERTED_PATH).glob("**/*.mp3") if res.is_file()]


def convert_video(convert_file: ConvertFile, quiet: bool) -> None:
    video = ffmpeg.input(convert_file.input_path)
    audio = ffmpeg.output(video.audio, str(convert_file.output_path))
    ffmpeg.run(audio, overwrite_output=True, quiet=quiet)

    logger.debug(f"(CONVERT) %s has been converted successfully.", convert_file.name)


@retry_func(exceptions=ffmpeg.Error, times=MAX_RETRY_TIMES)  # type: ignore
def convert_mp4_to_mp3(file_name: str, overwrite: bool, quiet: bool) -> ConvertStatus:
    orginal_file_path = Path(file_name)
    output_file = orginal_file_path.with_suffix(".mp3")

    if not overwrite and CONVERTED_PATH / output_file in get_converted_videos():
        return ConvertStatus.EXIST

    input_file_path = DOWNLOAD_PATH / orginal_file_path
    output_file_path = CONVERTED_PATH / output_file
    convert_file = ConvertFile(input_file_path, output_file_path, file_name)

    convert_video(convert_file, quiet)
    status = ConvertStatus.OK

    return status
