from __future__ import annotations

import os
import requests
import ffmpeg
import validators
from requests import Response
from pathlib import Path
from urllib import parse
from tqdm import tqdm
from typing import Union, no_type_check

from config import load_env
from mp4_type import ExceptionArgs, RetryRetFunc, DecoratorFunc, InnerFunc, RetryKwArgs
from logs.logging import logger

load_env()

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
VIDEOS_TEXT_FILE = os.environ.get("VIDEOS_TEXT_FILE", "example.txt")


def get_downloaded_videos() -> list[Path]:
    return [res for res in Path(DOWNLOAD_PATH).glob("**/*.mp4") if res.is_file()]


def get_converted_videos() -> list[Path]:
    return [res for res in Path(CONVERTED_PATH).glob("**/*.mp3") if res.is_file()]


def get_video_name_from_url(url: str) -> str:
    return os.path.basename(parse.urlsplit(url).path)


def delete_file(file_path: Path) -> None:
    current_state = "DOWNLOAD" if file_path.suffix == ".mp4" else "CONVERT"

    if file_path.exists():
        logger.warning(f"(%s) %s is failed to %s.", current_state, file_path.name, current_state.lower())
        print(f"Deleting {file_path.name!r}...")
        file_path.unlink()


def convert_to_url(line: str) -> str:
    if not line.startswith("http://") and not line.startswith("https://"):
        line = f"https://{line}"

    if not validators.url(line):
        raise Exception("URL is not correct.")

    return line


def get_all_video_urls_from_text_file() -> list[str]:
    with open(VIDEOS_TEXT_FILE, "r") as file:
        video_urls = [f"{convert_to_url(line.strip())}" for line in file.readlines()]

    return video_urls

@no_type_check
def remove_already_proceeded_videos(
    video_list: Union[list[str], list[Path]], directory_path: str
) -> Union[list[str], list[Path]]:
    fixed_videos_list: Union[list[str], list[Path]] = []
    proceeded_videos = set(res for res in Path(directory_path).glob("**/*.mp4") if res.is_file())

    for video in video_list:
        if isinstance(video, str):
            video_name = get_video_name_from_url(video)
            if directory_path / Path(video_name) not in proceeded_videos:
                fixed_videos_list.append(video)
        else:
            if directory_path / Path(video.name) not in proceeded_videos:
                fixed_videos_list.append(video)

    return fixed_videos_list


def get_response(video_url: str) -> Response:
    return requests.get(video_url, stream=True)


def save_video(file_name: Path, response: Response) -> None:
    output_file_path = DOWNLOAD_PATH / file_name
    size = int(response.headers.get("Content-Length", "0"))
    progress_bar = tqdm(total=size)
    chunk_size = 10_000

    with open(output_file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size):
            progress_bar.update(chunk_size)
            if chunk:
                file.write(chunk)

    logger.info(f"(DOWNLOAD) %s is saved successfully.", str(file_name))


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


def retry(exceptions: ExceptionArgs, times: int) -> RetryRetFunc:
    def decorator(func: DecoratorFunc) -> InnerFunc:
        def innerfunc(**kwargs: RetryKwArgs) -> None:
            attempt = 1
            while attempt < times:
                try:
                    return func(**kwargs)  # type: ignore
                except exceptions:  # type: ignore
                    print(f"Exception thrown when attemping to run {func}, attempt {attempt} of {times}")

                    attempt += 1
            return func(**kwargs)  # type: ignore

        return innerfunc  # type: ignore

    return decorator
