from __future__ import annotations

import os
import typing
from pathlib import Path
from urllib import parse

import validators

from config import load_env
from logs.logging import logger
from mp4_types import DecoratorFunc
from mp4_types import ExceptionArgs
from mp4_types import InnerFunc
from mp4_types import RetryKwArgs
from mp4_types import RetryRetFunc
from mp4_types import TPath

load_env()


CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
VIDEOS_TEXT_FILE = os.environ.get("VIDEOS_TEXT_FILE", "example.txt")
MAX_RETRY_TIMES = int(os.environ.get("MAX_RETRY_TIMES", 3))
CONCURRENT_REQUEST = 3


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


@typing.no_type_check
def retry_func(exceptions: ExceptionArgs, times: int):
    def decorator(func: DecoratorFunc):
        def innerfunc(*args, **kwargs):
            attempt = 1
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    print(f"Exception thrown when attemping to run {func}, attempt {attempt} of {times}")

                    attempt += 1
            return func(**kwargs)

        return innerfunc

    return decorator


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


def remove_already_proceeded_videos(video_list: list[TPath], directory_path: str) -> list[TPath]:
    fixed_videos_list: list[TPath] = []
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
