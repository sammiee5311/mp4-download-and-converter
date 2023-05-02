import os

import mock
from click.testing import CliRunner
from httpx import Response
from respx.router import MockRouter

from helper import get_all_video_urls_from_text_file
from helper import get_video_name_from_url
from main import convert_videos
from main import download_and_covert
from main import download_and_covert_from_url_argument
from main import download_videos
from modules.convert import get_converted_videos
from modules.download import get_downloaded_videos
from tests.conftest import convert_mp4_to_mp3
from tests.conftest import get_test_files

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "convert")


def test_download(respx_mock: MockRouter) -> None:
    video_urls_from_text_file = get_all_video_urls_from_text_file()
    downloaded_files = []

    for video_url in video_urls_from_text_file:
        respx_mock.get(video_url).mock(return_value=Response(200, text="data"))
        downloaded_files.append(get_video_name_from_url(video_url))

    runner = CliRunner()
    result = runner.invoke(download_videos)

    test_download_files = [file.name for file in get_test_files()]

    assert result.exit_code == 0
    assert sorted(test_download_files) == sorted(downloaded_files)


@mock.patch("modules.convert.convert_mp4_to_mp3", convert_mp4_to_mp3)
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


@mock.patch("modules.convert.convert_mp4_to_mp3", convert_mp4_to_mp3)
def test_download_and_covert(respx_mock: MockRouter) -> None:
    video_urls_from_text_file = get_all_video_urls_from_text_file()
    converted_files = []

    for video_url in video_urls_from_text_file:
        respx_mock.get(video_url).mock(return_value=Response(200, text="data"))
        converted_files.append(get_video_name_from_url(video_url).replace("mp4", "mp3"))

    runner = CliRunner()
    result = runner.invoke(download_and_covert)

    test_converted_files = [file.name for file in get_converted_videos()]

    assert result.exit_code == 0
    assert sorted(test_converted_files) == sorted(converted_files)


def test_one_without_url_argument() -> None:
    runner = CliRunner()
    result = runner.invoke(download_and_covert_from_url_argument)

    assert result.exit_code == 0
    assert result.output == "Please, provide a url that you want to download.\n"


@mock.patch("main.convert_mp4_to_mp3", convert_mp4_to_mp3)
def test_one_with_url_argument(respx_mock: MockRouter) -> None:
    video_url = "https://example-example.com/example-example.mp4"

    respx_mock.get(video_url).mock(return_value=Response(200, text="data"))

    runner = CliRunner()
    result = runner.invoke(download_and_covert_from_url_argument, args=["--url", video_url])

    file_name = get_video_name_from_url(video_url)
    test_download_files = [file.name for file in get_test_files()]

    assert file_name in test_download_files

    file_name = file_name.replace("mp4", "mp3")
    test_converted_files = [file.name for file in get_converted_videos()]

    assert result.exit_code == 0
    assert file_name in test_converted_files
