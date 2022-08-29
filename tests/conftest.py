import pytest
import os

from helper import delete_file

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
VIDEOS_LIST = ["example.com/a.mp4", "http://example.com/b.mp4", "https://example.com/c.mp4"]


@pytest.fixture
def video_urls_from_text_file() -> list[str]:
    return VIDEOS_LIST


def get_download_files() -> list[str]:
    return [f"{DOWNLOAD_PATH}/{file}" for file in os.listdir(DOWNLOAD_PATH)]


def get_converted_files() -> list[str]:
    return [f"{CONVERTED_PATH}/{file}" for file in os.listdir(CONVERTED_PATH)]


def get_test_files() -> list[str]:
    return get_download_files() + get_converted_files()


def convert_mp4_to_mp3(file_name: str):
    output_file_path = os.path.join(CONVERTED_PATH, file_name.replace("mp4", "mp3"))

    with open(output_file_path, "w") as file:
        file.write(file_name)


@pytest.fixture(scope="session", autouse=True)
def clean_up():
    yield
    for file in get_test_files():
        delete_file(file)


def save_video(DOWNLOAD_PATH: str, file_name: str) -> None:
    with open(f"{DOWNLOAD_PATH}/{file_name}", "w") as file:
        file.write(file_name)
