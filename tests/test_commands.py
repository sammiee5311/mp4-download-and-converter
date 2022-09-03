import os

from helper import get_all_video_urls_from_text_file, remove_already_proceeded_videos

from tests.conftest import save_video, get_test_files, get_download_files, get_converted_files, convert_mp4_to_mp3

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "convert")


def test_download() -> None:
    video_urls_from_text_file = get_all_video_urls_from_text_file()
    downloaded_files = []

    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)

    for video_url in video_urls:
        file_name = video_url.split("/")[-1]
        save_video(DOWNLOAD_PATH, file_name)

        downloaded_files.append(file_name)

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
