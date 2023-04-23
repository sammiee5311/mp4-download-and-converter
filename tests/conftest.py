from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

import pytest

from helper import delete_file
from modules.convert import get_converted_videos
from modules.download import get_downloaded_videos

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "logs/log_test.log")


def get_test_files() -> list[Path]:
    return get_downloaded_videos() + get_converted_videos()


def convert_mp4_to_mp3(file_name: str, overwrite: bool, quite: bool) -> None:
    orginal_file_path = Path(file_name)
    output_file = orginal_file_path.with_suffix(".mp3")

    if not overwrite and CONVERTED_PATH / output_file in get_converted_videos():
        return

    output_file_path = CONVERTED_PATH / output_file

    output_file_path.write_text(file_name)


@pytest.fixture(scope="session", autouse=True)
def clean_up() -> Generator[None, None, None]:
    yield
    for file in get_test_files() + [Path(LOG_FILE_PATH)]:
        delete_file(file)
