import os
import requests
import ffmpeg
from requests import Response

from config import load_env

load_env()

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH")
VIDEOS_TEXT_FILE = os.environ.get("VIDEOS_TEXT_FILE")


def get_downloaded_videos() -> list[str]:
    return os.listdir(DOWNLOAD_PATH)


def delete_file(file_name: str) -> None:
    if os.path.exists(file_name):
        print(f"Deleting {file_name!r}...")
        os.remove(file_name)


def convert_to_url(line: str) -> str:
    if not line.startswith("http://") or not line.startswith("https://"):
        line = f"https://{line}"

    return line


def get_all_video_urls_from_text_file() -> list[str]:
    with open(VIDEOS_TEXT_FILE, "r") as file:
        video_urls = [
            f"{convert_to_url(line.strip())}" for line in file.readlines()]

    return video_urls


def remove_already_proceeded_videos(video_list: list[str], directory_path: str) -> list[str]:
    fixed_videos_list = []
    proceeded_videos = set(os.listdir(directory_path))

    for video in video_list:
        video_name = video.split("/")[-1]
        if video_name not in proceeded_videos:
            fixed_videos_list.append(video)

    return fixed_videos_list


def get_file_name_and_response(video_url: str) -> tuple[str, bytes]:
    file_name = video_url.split("/")[-1]
    response = requests.get(video_url, stream=True)

    return file_name, response


def save_video(file_name: str, response: Response) -> None:
    output_file_path = os.path.join(DOWNLOAD_PATH, file_name)
    with open(output_file_path, "wb") as file:
        for chunk in response.iter_content(10000):
            if chunk:
                file.write(chunk)


def convert_mp4_to_mp3(file_name: str):
    input_file_path = os.path.join(DOWNLOAD_PATH, file_name)
    output_file_path = os.path.join(
        CONVERTED_PATH, file_name.replace("mp4", "mp3"))

    video = ffmpeg.input(input_file_path)
    audio = ffmpeg.output(video.audio, output_file_path)
    ffmpeg.run(audio, overwrite_output=True)
