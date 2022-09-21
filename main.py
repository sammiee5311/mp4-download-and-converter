""" mp4-download-and-converter """

__version__ = "0.0.8"

import click
import os

from config import ReteyError

from helper import (
    get_all_video_urls_from_text_file,
    remove_already_proceeded_videos,
    save_video,
    get_downloaded_videos,
    get_response,
    delete_file,
    convert_mp4_to_mp3,
    convert_to_url,
    retry,
)


DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH", "download")
CONVERTED_PATH = os.environ.get("CONVERTED_PATH", "converted")
MAX_RETRY_TIMES = int(os.environ.get("MAX_RETRY_TIMES", 3))


@click.group()
def cli() -> None:
    """Download and Convert"""


@click.command("download")
@retry(exceptions=ReteyError, times=MAX_RETRY_TIMES)
def download_videos() -> None:
    """download all the urls in the text file."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            file_name = video_url.split("/")[-1]
            response = get_response(video_url)
            save_video(file_name, response)

        print("All done !")
    except Exception as e:
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))

        raise ReteyError(f"An error is occurred to download {file_name!r} file. ({e})")
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))


@click.command("convert")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=ReteyError, times=MAX_RETRY_TIMES)
def convert_videos(overwrite: bool, quiet: bool) -> None:
    """convert all the downloaded videos from mp4 to mp3."""
    downloaded_videos = get_downloaded_videos()

    video_files = remove_already_proceeded_videos(downloaded_videos, CONVERTED_PATH)
    number_of_videos = len(video_files)

    try:
        for idx, video_file in enumerate(video_files):
            print(f"Proceeding {video_file!r} ({idx + 1}/{number_of_videos})...")
            convert_mp4_to_mp3(video_file, overwrite, quiet)

        print("All done !")
    except Exception as e:
        delete_file(os.path.join(CONVERTED_PATH, video_file.replace("mp4", "mp3")))

        raise ReteyError(f"An error is occurred to convert {video_file!r} file. ({e})")
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(os.path.join(CONVERTED_PATH, video_file.replace("mp4", "mp3")))


@click.command("together")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=ReteyError, times=MAX_RETRY_TIMES)
def download_and_covert(overwrite: bool, quiet: bool) -> None:
    """download all the urls and convert all the downloaded videos."""
    video_urls_from_text_file = get_all_video_urls_from_text_file()

    video_urls = remove_already_proceeded_videos(video_urls_from_text_file, DOWNLOAD_PATH)
    number_of_videos = len(video_urls)

    try:
        for idx, video_url in enumerate(video_urls):
            print(f"Proceeding {video_url!r} ({idx + 1}/{number_of_videos})...")
            file_name = video_url.split("/")[-1]
            response = get_response(video_url)
            save_video(file_name, response)
            convert_mp4_to_mp3(file_name, overwrite, quiet)

        print("All done !")
    except Exception as e:
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))
        delete_file(os.path.join(CONVERTED_PATH, file_name.replace("mp4", "mp3")))

        raise ReteyError(f"An error is occurred with {file_name!r} file. ({e})")
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))
        delete_file(os.path.join(CONVERTED_PATH, file_name.replace("mp4", "mp3")))


@click.command("one")
@click.option("--url", help="video url")
@click.option("--overwrite/--no-overwrite", default=True, show_default=True, help="overwrite converted videos")
@click.option("--quiet/--no-quiet", default=True, show_default=True, help="show ffmpg output log")
@retry(exceptions=ReteyError, times=MAX_RETRY_TIMES)
def download_and_covert_from_url_argument(url: str, overwrite: bool, quiet: bool) -> None:
    """download vid from url argument and convert the downloaded video."""
    if not url:
        print("Please, provide a url that you want to download.")
        return

    video_url = convert_to_url(url)

    try:
        print(f"Proceeding {video_url!r}...")
        file_name = video_url.split("/")[-1]
        response = get_response(video_url)
        save_video(file_name, response)
        convert_mp4_to_mp3(file_name, overwrite, quiet)

        print("All done !")
    except Exception as e:
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))
        delete_file(os.path.join(CONVERTED_PATH, file_name.replace("mp4", "mp3")))

        raise ReteyError(f"An error is occurred with {file_name!r} file. ({e})")
    except KeyboardInterrupt:
        print(f"Ctrl-C interrupted !")
        delete_file(os.path.join(DOWNLOAD_PATH, file_name))
        delete_file(os.path.join(CONVERTED_PATH, file_name.replace("mp4", "mp3")))


if __name__ == "__main__":  # pragma: no cover
    cli.add_command(download_videos)
    cli.add_command(convert_videos)
    cli.add_command(download_and_covert)
    cli.add_command(download_and_covert_from_url_argument)
    cli()
