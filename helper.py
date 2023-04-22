from __future__ import annotations

import os
import typing
from collections import Counter
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from urllib import parse

import ffmpeg
import httpx
import validators
from tqdm import tqdm

from config import load_env
from logs.logging import logger
from mp4_type import DecoratorFunc
from mp4_type import DownloadStatus
from mp4_type import ExceptionArgs
from mp4_type import InnerFunc
from mp4_type import RetryKwArgs
from mp4_type import RetryRetFunc
from mp4_type import TPath

load_env()


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
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
def retry_download(exceptions: ExceptionArgs, times: int):
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


def save_video(output_file_path: Path, response: httpx.Response, is_concurrent: bool) -> None:
    size = int(response.headers.get("Content-Length", "0"))
    if not is_concurrent:
        progress_bar = tqdm(total=size)
    chunk_size = 10_000

    with open(output_file_path, "wb") as file:
        for chunk in response.iter_bytes(chunk_size):
            if not is_concurrent:
                progress_bar.update(chunk_size)
            if chunk:
                file.write(chunk)


def report_download_status(download_status: Counter[DownloadStatus]) -> None:
    print(
        "All Done!\n"
        f"{download_status[DownloadStatus.OK]} success to download\n"
        f"{download_status[DownloadStatus.ERROR]} failed to download\n"
        "Check the 'output.log' file to see more details."
    )


@retry_download(exceptions=httpx.HTTPStatusError, times=MAX_RETRY_TIMES)  # type: ignore
def download_video(file_name: Path, video_url: str, is_concurrent: bool = False) -> DownloadStatus:
    output_file_path = DOWNLOAD_PATH / file_name

    with httpx.stream("GET", video_url, follow_redirects=True) as response:
        response.raise_for_status()
        save_video(output_file_path, response, is_concurrent)
        status = DownloadStatus.OK

    return status


def download_videos_con(video_urls: list[str]) -> None:
    download_status: Counter[DownloadStatus] = Counter()

    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUEST) as executor:
        to_do_map = {}

        for video_url in video_urls:
            video_file = Path(get_video_name_from_url(video_url))
            future = executor.submit(partial(download_video, video_file, video_url, True))
            to_do_map[future] = video_file

        done_iter = as_completed(to_do_map)
        done_iter = tqdm(done_iter, total=len(video_urls))

        for future in done_iter:
            file_name = to_do_map[future]

            try:
                status = future.result()
            except httpx.HTTPStatusError as exc:
                error_msg = "HTTP error {resp.status_code} - {resp.reason_phrase}"
                error_msg = error_msg.format(resp=exc.response)
            except httpx.RequestError as exc:
                error_msg = f"{exc} {type(exc)}".strip()
            except KeyboardInterrupt:
                logger.debug("Ctrl-C interrupted !")
                delete_file(DOWNLOAD_PATH / file_name)
                break
            else:
                error_msg = ""

            if error_msg:
                status = DownloadStatus.ERROR
                delete_file(DOWNLOAD_PATH / file_name)
                logger.error(f"An error is occurred to download {str(file_name)!r} file. ({error_msg})")

            else:
                logger.debug(f"(DOWNLOAD) %s is saved successfully.", str(file_name))

            download_status[status] += 1

    report_download_status(download_status)


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
