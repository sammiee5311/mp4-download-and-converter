""" mp4-download-and-converter """

__version__ = "0.1.0"

import os
from pathlib import Path

import click
from ffmpeg._run import Error
from httpx import HTTPError

from modules.download import download_videos_con, get_downloaded_videos
from modules.convert import convert_mp4_to_mp3_con
from helper import (
    convert_to_url,
    get_all_video_urls_from_text_file,
    get_video_name_from_url,
    remove_already_proceeded_videos,
)

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
MAX_RETRY_TIMES = int(os.environ.get("MAX_RETRY_TIMES", 3))

DOWNLOAD_RETRY_EXCEPTIONS = HTTPError
CONVERT_RETRY_EXCEPTIONS = Error


@click.group()
def cli() -> None:
    """Download and Convert"""


@click.command("download")
def download_videos() -> None:
    """download all the urls in the text file."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()
    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)

    download_videos_con(video_urls)


@click.command("convert")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
def convert_videos(overwrite: bool, quiet: bool) -> None:
    """convert all the downloaded videos from mp4 to mp3."""
    downloaded_videos = get_downloaded_videos()
    video_files = remove_already_proceeded_videos(downloaded_videos, CONVERTED_PATH)

    convert_mp4_to_mp3_con(video_files, overwrite, quiet)


@click.command("together")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
def download_and_covert(overwrite: bool, quiet: bool) -> None:
    """download all the urls and convert all the downloaded videos."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()
    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)

    download_videos_con(video_urls)

    downloaded_videos = get_downloaded_videos()
    video_files = remove_already_proceeded_videos(downloaded_videos, CONVERTED_PATH)

    convert_mp4_to_mp3_con(video_files, overwrite, quiet)


@click.command("one")
@click.option("--url", help="video url")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
def download_and_covert_from_url_argument(url: str, overwrite: bool, quiet: bool) -> None:
    """download vid from url argument and convert the downloaded video."""
    if not url:
        print("Please, provide a url that you want to download.")
        return

    video_url = convert_to_url(url)
    video_file = DOWNLOAD_PATH / Path(get_video_name_from_url(video_url))

    download_videos_con([video_url])
    convert_mp4_to_mp3_con([video_file], overwrite, quiet)


if __name__ == "__main__":  # pragma: no cover
    cli.add_command(download_videos)
    cli.add_command(convert_videos)
    cli.add_command(download_and_covert)
    cli.add_command(download_and_covert_from_url_argument)
    cli()
