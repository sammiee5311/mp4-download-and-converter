import click
import os

from helper import (
    get_all_video_urls_from_text_file,
    remove_already_proceeded_videos,
    save_video,
    get_downloaded_videos,
    get_file_name_and_response,
    delete_file,
    convert_mp4_to_mp3
)


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH")


@click.group()
def cli():
    """Download and Convert"""


@click.command("download")
def download_videos() -> None:
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(
        video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(
                f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            file_name, response = get_file_name_and_response(video_url)
            save_video(file_name, response)

        print("All done !")
    except Exception:
        print(f"An error is occurred to download {file_name!r} file.")
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))


@click.command("convert")
def convert_videos() -> None:
    downloaded_videos = get_downloaded_videos()
    video_files = remove_already_proceeded_videos(
        downloaded_videos, CONVERTED_PATH)
    number_of_videos = len(video_files)

    try:
        for idx, video_file in enumerate(video_files):
            print(
                f"Proceeding {video_file!r} ({idx + 1}/{number_of_videos})...")
            convert_mp4_to_mp3(video_file)

        print("All done !")
    except Exception:
        print(f"An error is occurred to convert {video_file!r} file.")
        delete_file(os.path.join(CONVERTED_PATH, video_file))


@click.command("together")
def download_and_covert():
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(
        video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(
                f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            file_name, response = get_file_name_and_response(video_url)
            save_video(file_name, response)
            convert_mp4_to_mp3(file_name)

        print("All done !")
    except Exception:
        print(f"An error is occurred with {file_name!r} file.")
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))
        delete_file(os.path.join(CONVERTED_PATH, file_name))


if __name__ == "__main__":
    cli.add_command(download_videos)
    cli.add_command(convert_videos)
    cli.add_command(download_and_covert)
    cli()
