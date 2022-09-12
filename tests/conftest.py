from __future__ import annotations

import pytest
import os

from helper import delete_file

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")


def get_download_files() -> list[str]:
    return [f"{DOWNLOAD_PATH}/{file}" for file in os.listdir(DOWNLOAD_PATH) if file.split("/")[-1] != ".gitkeep"]


def get_converted_files() -> list[str]:
    return [f"{CONVERTED_PATH}/{file}" for file in os.listdir(CONVERTED_PATH) if file.split("/")[-1] != ".gitkeep"]


def get_test_files() -> list[str]:
    return get_download_files() + get_converted_files()


def convert_mp4_to_mp3(file_name: str, overwrite: bool) -> None:
    output_file = file_name.replace("mp4", "mp3")
    if not overwrite and output_file in get_converted_files():
        return

    output_file_path = os.path.join(CONVERTED_PATH, output_file)

    with open(output_file_path, "w") as file:
        file.write(file_name)


@pytest.fixture(scope="session", autouse=True)
def clean_up():
    yield
    for file in get_test_files():
        delete_file(file)
