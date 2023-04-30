from __future__ import annotations

from collections import Counter
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import ffmpeg
from tqdm import tqdm

from helper import CONCURRENT_REQUEST
from helper import CONVERTED_PATH
from helper import delete_file
from helper import MAX_RETRY_TIMES
from helper import retry_func
from logs.logging import logger
from mp4_types import ConvertStatus


@dataclass(frozen=True)
class ConvertFile:
    input_path: Path
    output_path: Path
    name: str


def get_converted_videos() -> list[Path]:
    return [res for res in Path(CONVERTED_PATH).glob("**/*.mp3") if res.is_file()]


def report_convert_status(convert_status: Counter[ConvertStatus]) -> None:
    print(
        "All Done!\n"
        f"{convert_status[ConvertStatus.OK]} success to convert\n"
        f"{convert_status[ConvertStatus.ERROR]} failed to convert\n"
        "Check the 'output.log' file to see more details."
    )


def convert_video(convert_file: ConvertFile, quiet: bool) -> None:
    video = ffmpeg.input(convert_file.input_path)
    audio = ffmpeg.output(video.audio, str(convert_file.output_path))
    ffmpeg.run(audio, overwrite_output=True, quiet=quiet)

    logger.debug(f"(CONVERT) %s has been converted successfully.", convert_file.name)


@retry_func(exceptions=ffmpeg.Error, times=MAX_RETRY_TIMES)  # type: ignore
def convert_mp4_to_mp3(video_file: Path, overwrite: bool, quiet: bool) -> ConvertStatus:
    orginal_file_path = video_file
    output_file_path = CONVERTED_PATH / Path(orginal_file_path.with_suffix(".mp3").name)

    if not overwrite and output_file_path in get_converted_videos():
        return ConvertStatus.EXIST

    convert_file = ConvertFile(orginal_file_path, output_file_path, video_file.name)

    convert_video(convert_file, quiet)
    status = ConvertStatus.OK

    return status


def convert_mp4_to_mp3_con(video_files: list[Path], overwrite: bool, quite: bool) -> None:
    download_status: Counter[ConvertStatus] = Counter()

    with ThreadPoolExecutor(max_workers=CONCURRENT_REQUEST) as executor:
        to_do_map = {}

        for video_file in video_files:
            future = executor.submit(partial(convert_mp4_to_mp3, video_file, overwrite, quite))
            to_do_map[future] = video_file

        done_iter = as_completed(to_do_map)
        done_iter = tqdm(done_iter, total=len(video_files))

        for future in done_iter:
            video_file_to_do: Path = to_do_map[future]

            try:
                status = future.result()
            except ffmpeg.Error as exc:
                error_msg = f"{exc} {type(exc)}".strip()
            except KeyboardInterrupt:
                logger.debug("Ctrl-C interrupted !")
                delete_file(CONVERTED_PATH / Path(video_file_to_do.with_suffix(".mp3").name))
                break
            else:
                error_msg = ""

            if error_msg:
                status = ConvertStatus.ERROR
                delete_file(CONVERTED_PATH / Path(video_file_to_do.with_suffix(".mp3").name))
                logger.error(f"An error is occurred to convert {str(video_file_to_do)!r} file. ({error_msg})")

            download_status[status] += 1

    report_convert_status(download_status)
