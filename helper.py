from __future__ import annotations

import os
import requests
import ffmpeg
import validators
from requests import Response
from tqdm import tqdm

from config import load_env
from mp4_type import ExceptionArgs, RetryRetFunc, DecoratorFunc, InnerFunc, RetryKwArgs

load_env()

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
VIDEOS_TEXT_FILE = os.environ.get("VIDEOS_TEXT_FILE", "example.txt")


def get_downloaded_videos() -> list[str]:
    return os.listdir(DOWNLOAD_PATH)


def get_converted_videos() -> list[str]:
    return os.listdir(CONVERTED_PATH)


def delete_file(file_name: str) -> None:
    if os.path.exists(file_name):
        print(f"Deleting {file_name!r}...")
        os.remove(file_name)


def is_valid_video_file(file: str) -> bool:
    return file.split(".")[-1] == "mp4"


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


def remove_already_proceeded_videos(video_list: list[str], directory_path: str) -> list[str]:
    fixed_videos_list = []
    proceeded_videos = set(os.listdir(directory_path))

    for video in video_list:
        video_name = video.split("/")[-1]
        if is_valid_video_file(video_name) and video_name not in proceeded_videos:
            fixed_videos_list.append(video)

    return fixed_videos_list


def get_response(video_url: str) -> Response:
    return requests.get(video_url, stream=True)


def save_video(file_name: str, response: Response) -> None:
    output_file_path = os.path.join(DOWNLOAD_PATH, file_name)
    size = int(response.headers.get("Content-Length", "0"))
    progress_bar = tqdm(total=size)
    chunk_size = 10_000

    with open(output_file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size):
            progress_bar.update(chunk_size)
            if chunk:
                file.write(chunk)


def convert_mp4_to_mp3(file_name: str, overwrite: bool, quiet: bool) -> None:  # pragma: no cover
    output_file = file_name.replace("mp4", "mp3")

    if not overwrite and output_file in get_converted_videos():
        return

    input_file_path = os.path.join(DOWNLOAD_PATH, file_name)
    output_file_path = os.path.join(CONVERTED_PATH, output_file)
    video = ffmpeg.input(input_file_path)
    audio = ffmpeg.output(video.audio, output_file_path)
    ffmpeg.run(audio, overwrite_output=True, quiet=quiet)


def retry(exceptions: ExceptionArgs, times: int) -> RetryRetFunc:
    def decorator(func: DecoratorFunc) -> InnerFunc:
        def innerfunc(**kwargs: RetryKwArgs) -> None:
            attempt = 1
            while attempt <= times:
                try:
                    return func(**kwargs)  # type: ignore
                except exceptions:  # type: ignore
                    print(f"Exception thrown when attemping to run {func}, attempt {attempt} of {times}")

                    attempt += 1
            return func(**kwargs)  # type: ignore

        return innerfunc  # type: ignore

    return decorator
