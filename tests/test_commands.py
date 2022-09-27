import os
import requests_mock
import mock

from click.testing import CliRunner

from main import download_videos, convert_videos, download_and_covert_from_url_argument
from helper import (
    get_all_video_urls_from_text_file,
    get_video_name_from_url,
    get_converted_videos,
    get_downloaded_videos,
)
from tests.conftest import get_test_files, convert_mp4_to_mp3

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "convert")


def test_download() -> None:
    mock: requests_mock.Mocker
    with requests_mock.Mocker() as mock:
        video_urls_from_text_file = get_all_video_urls_from_text_file()
        downloaded_files = []

        for video_url in video_urls_from_text_file:
            mock.get(video_url, text="data")
            downloaded_files.append(get_video_name_from_url(video_url))

        runner = CliRunner()
        result = runner.invoke(download_videos)

        test_download_files = [file.name for file in get_test_files()]

        assert result.exit_code == 0
        assert sorted(test_download_files) == sorted(downloaded_files)


@mock.patch("main.convert_mp4_to_mp3", convert_mp4_to_mp3)
def test_convert() -> None:
    downloaded_files = get_downloaded_videos()
    converted_files = []

    for video_file in downloaded_files:
        converted_files.append(video_file.with_suffix(".mp3").name)

    runner = CliRunner()
    result = runner.invoke(convert_videos)

    test_converted_files = [file.name for file in get_converted_videos()]

    assert result.exit_code == 0
    assert sorted(test_converted_files) == sorted(converted_files)


def test_one_without_url_argument() -> None:
    runner = CliRunner()
    result = runner.invoke(download_and_covert_from_url_argument)

    assert result.exit_code == 0
    assert result.output == "Please, provide a url that you want to download.\n"


@mock.patch("main.convert_mp4_to_mp3", convert_mp4_to_mp3)
def test_one_with_url_argument() -> None:
    mock: requests_mock.Mocker
    with requests_mock.Mocker() as mock:
        video_url = "https://example-example.com/example-example.mp4"

        mock.get(video_url, text="data")

        runner = CliRunner()
        result = runner.invoke(download_and_covert_from_url_argument, args=["--url", video_url])

        file_name = get_video_name_from_url(video_url)

        test_download_files = [file.name for file in get_test_files()]

        assert file_name in test_download_files

        file_name = file_name.replace("mp4", "mp3")

        test_converted_files = [file.name for file in get_converted_videos()]

        assert result.exit_code == 0
        assert file_name in test_converted_files
