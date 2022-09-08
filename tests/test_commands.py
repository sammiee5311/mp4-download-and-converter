import os
import requests_mock

from click.testing import CliRunner

from main import download_videos
from helper import get_all_video_urls_from_text_file, remove_already_proceeded_videos
from tests.conftest import save_video, get_test_files, get_download_files, get_converted_files, convert_mp4_to_mp3

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "convert")


def test_download() -> None:
    mock: requests_mock.Mocker
    with requests_mock.Mocker() as mock:
        video_urls_from_text_file = get_all_video_urls_from_text_file()
        downloaded_files = []

        for video_url in video_urls_from_text_file:
            mock.get(video_url, text="data")
            downloaded_files.append(video_url.split("/")[-1])

        runner = CliRunner()
        runner.invoke(download_videos)

        test_download_files = [file.split("/")[-1] for file in get_test_files() if file.split("/")[-1] != ".gitkeep"]

        assert sorted(test_download_files) == sorted(downloaded_files)


def test_convert() -> None:
    donwloaded_files = get_download_files()
    converted_files = []

    video_files = remove_already_proceeded_videos(donwloaded_files, CONVERTED_PATH)

    for video_file in video_files:
        file_name = video_file.split("/")[-1]
        convert_mp4_to_mp3(file_name)

        converted_files.append(file_name.replace("mp4", "mp3"))

    test_converted_files = [file.split("/")[-1] for file in get_converted_files() if file.split("/")[-1] != ".gitkeep"]

    assert sorted(test_converted_files) == sorted(converted_files)


def test_one() -> None:
    video_url = get_all_video_urls_from_text_file()[0]

    file_name = video_url.split("/")[-1]
    save_video(DOWNLOAD_PATH, file_name)

    test_download_files = [file.split("/")[-1] for file in get_test_files() if file.split("/")[-1] != ".gitkeep"]

    assert file_name in test_download_files

    convert_mp4_to_mp3(file_name)
    file_name = file_name.replace("mp4", "mp3")

    test_converted_files = [file.split("/")[-1] for file in get_converted_files() if file.split("/")[-1] != ".gitkeep"]

    assert file_name in test_converted_files
