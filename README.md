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
- create python venv and install dependencies
    - use `make all` to create venv and install dependencies (if your os is mac os).
    - or create virtual python3.10 environment and download dependencies (`pip install -r requirements.txt`).
- use `convert`, `download`, `together` or `one` command with `python main.py`
    - example : `python main.py convert`

## command
- download
    - download all the urls in the text file.
- convert
    - convert all the downloaded videos from `mp4` to `mp3`.
- together
    - download all the urls and convert all the downloaded videos.
- one
    - argument:
        - `--url <video url>` 
            - ex) `python main.py one --url example.com/example.mp4`
    - download vid from url argument and convert the downloaded video.

## future plans
- [x] download and convert with url argument via terminal command.
- [ ] add more convert options.
