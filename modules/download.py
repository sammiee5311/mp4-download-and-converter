from __future__ import annotations

import os
from collections import Counter
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import httpx
from tqdm import tqdm

from config import load_env
from helper import delete_file
from helper import get_video_name_from_url
from helper import MAX_RETRY_TIMES
from helper import retry_func
from logs.logging import logger
from mp4_types import DownloadStatus

load_env()


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONCURRENT_REQUEST = 3


def get_downloaded_videos() -> list[Path]:
    return [res for res in Path(DOWNLOAD_PATH).glob("**/*.mp4") if res.is_file()]


def report_download_status(download_status: Counter[DownloadStatus]) -> None:
    print(
        "All Done!\n"
        f"{download_status[DownloadStatus.OK]} success to download\n"
        f"{download_status[DownloadStatus.ERROR]} failed to download\n"
        "Check the 'output.log' file to see more details."
    )


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


@retry_func(exceptions=httpx.HTTPStatusError, times=MAX_RETRY_TIMES)  # type: ignore
def download_video(file_name: Path, video_url: str, is_concurrent: bool = False) -> DownloadStatus:
    output_file_path = DOWNLOAD_PATH / file_name

    with httpx.stream("GET", video_url, follow_redirects=True) as response:
        response.raise_for_status()
        save_video(output_file_path, response, is_concurrent)
        status = DownloadStatus.OK

    logger.debug(f"(DOWNLOAD) %s has been downloaded successfully.", str(file_name))

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

            download_status[status] += 1

    report_download_status(download_status)
