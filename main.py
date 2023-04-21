""" mp4-download-and-converter """

__version__ = "0.0.8"

import os
from pathlib import Path

import click
from ffmpeg._run import Error
from httpx import RequestError

from config import RetryError
from helper import (
    convert_mp4_to_mp3,
    convert_to_url,
    delete_file,
    get_all_video_urls_from_text_file,
    get_downloaded_videos,
    get_video_name_from_url,
    remove_already_proceeded_videos,
    retry,
    save_video,
)

DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
MAX_RETRY_TIMES = int(os.environ.get("MAX_RETRY_TIMES", 3))

DOWNLOAD_RETRY_EXCEPTIONS = RequestError
CONVERT_RETRY_EXCEPTIONS = Error


@click.group()
def cli() -> None:
    """Download and Convert"""


@click.command("download")
@retry(exceptions=RetryError, times=MAX_RETRY_TIMES)
def download_videos() -> None:
    """download all the urls in the text file."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            video_file = Path(get_video_name_from_url(video_url))
            save_video(video_file, video_url)

        print("All done !")
    except DOWNLOAD_RETRY_EXCEPTIONS as exc:
        raise RetryError(f"An error is occurred to download {video_file!r} file. ({exc})")
    except Exception as exc:
        print(f"An error is occurred to download {video_file!r} file. ({exc})")
        delete_file(DOWNLOAD_PATH / video_file)
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(DOWNLOAD_PATH / video_file)


@click.command("convert")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=RetryError, times=MAX_RETRY_TIMES)
def convert_videos(overwrite: bool, quiet: bool) -> None:
    """convert all the downloaded videos from mp4 to mp3."""
    downloaded_videos = get_downloaded_videos()

    video_files = remove_already_proceeded_videos(downloaded_videos, CONVERTED_PATH)
    number_of_videos = len(video_files)

    try:
        for idx, video_file in enumerate(video_files):
            print(f"Proceeding {video_file!r} ({idx + 1}/{number_of_videos})...")
            convert_mp4_to_mp3(video_file.name, overwrite, quiet)

        print("All done !")
    except CONVERT_RETRY_EXCEPTIONS as exc:
        raise RetryError(f"An error is occurred to convert {video_file!r} file. ({exc})")
    except Exception as exc:
        print(f"An error is occurred to download {video_file!r} file. ({exc})")
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))


@click.command("together")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=RetryError, times=MAX_RETRY_TIMES)
def download_and_covert(overwrite: bool, quiet: bool) -> None:
    """download all the urls and convert all the downloaded videos."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            video_file = Path(get_video_name_from_url(video_url))
            save_video(video_file, video_url)
            convert_mp4_to_mp3(video_file.name, overwrite, quiet)

        print("All done !")
    except (DOWNLOAD_RETRY_EXCEPTIONS, CONVERT_RETRY_EXCEPTIONS) as exc:
        raise RetryError(f"An error is occurred with {video_file!r} file. ({exc})")
    except Exception as exc:
        print(f"An error is occurred to download {video_file!r} file. ({exc})")
        delete_file(DOWNLOAD_PATH / video_file)
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(DOWNLOAD_PATH / video_file)
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))


@click.command("one")
@click.option("--url", help="video url")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=RetryError, times=MAX_RETRY_TIMES)
def download_and_covert_from_url_argument(url: str, overwrite: bool, quiet: bool) -> None:
    """download vid from url argument and convert the downloaded video."""
    if not url:
        print("Please, provide a url that you want to download.")
        return

    video_url = convert_to_url(url)

    try:
        print(f"Proceeding {video_url!r}...")
        video_file = Path(get_video_name_from_url(video_url))
        save_video(video_file, video_url)
        convert_mp4_to_mp3(video_file.name, overwrite, quiet)

        print("All done !")
    except (DOWNLOAD_RETRY_EXCEPTIONS, CONVERT_RETRY_EXCEPTIONS) as exc:
        raise RetryError(f"An error is occurred with {video_file!r} file. ({exc})")
    except Exception as exc:
        print(f"An error is occurred to download {video_file!r} file. ({exc})")
        delete_file(DOWNLOAD_PATH / video_file)
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(DOWNLOAD_PATH / video_file)
        delete_file(CONVERTED_PATH / video_file.with_suffix(".mp3"))


if __name__ == "__main__":  # pragma: no cover
    cli.add_command(download_videos)
    cli.add_command(convert_videos)
    cli.add_command(download_and_covert)
    cli.add_command(download_and_covert_from_url_argument)
    cli()
