# mp4 download and converter

download all the `mp4` videos from urls and convert from `mp4` to `mp3`.

## prerequisites
- <= python 3.10
- ffmpeg

## how to use
- download [`ffmpeg`](https://ffmpeg.org/).
    - (if you are using homebrew, use following command in terminal `brew install ffmpeg`.)
- type environment variables in `.env` file.
    - `DOWNLOAD_PATH` is a directory where you want to download to.
    - `CONVERTED_PATH` is a directory where you want to save converted videos to.
    - `VIDEOS_TEXT_FILE` is a text file with urls that you want to download.
- use `make all` to create venv and install dependencies (if your os is mac os).
- use `convert`, `download` or `together` command with `python main.py`
    - example : `python main.py convert`

## command
- download
    - download all the urls in the text file.
- convert
    - convert all the downloaded videos from `mp4` to `mp3`.
- together
    - download all the urls and convert all the downloaded videos.
