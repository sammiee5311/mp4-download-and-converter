# mp4 download and converter
[![CI](https://github.com/sammiee5311/mp4-download-and-converter/actions/workflows/CI.yaml/badge.svg)](https://github.com/sammiee5311/mp4-download-and-converter/actions/workflows/CI.yaml) [![python](./python-version.svg)]() [![](./coverage.svg)]()

download all the `mp4` videos from urls and convert from `mp4` to `mp3`.

## prerequisites
- <= python 3.7
- ffmpeg

## how to use
1. download [`ffmpeg`](https://ffmpeg.org/).
    - (if you are using homebrew, use following command in terminal `brew install ffmpeg`.)
2. type environment variables in `.env` file.
    - `DOWNLOAD_PATH` is a directory where you want to download to.
    - `CONVERTED_PATH` is a directory where you want to save converted videos to.
    - `VIDEOS_TEXT_FILE` is a text file with urls that you want to download.
    - `MAX_RETRY_TIMES` is how many times you want to retry when it occurs an error.
3. create virtual python environment
    - `python -m venv venv`
    - or `virtualenv venv -ppy< python version(ex, 310) >` (if you have installed virtualenv)
4. activate python venv
    - mac
        - `source venv/bin/activate`
    - window
        - `./venv/Scripts/activate`
    - linux
        - `. venv/bin/activate`
5. install dependencies
    - `pip install -r requirements.txt`
6. use `convert`, `download`, `together` or `one` command with `python main.py`
    - example : `python main.py convert`

## command
- download
    - download all the urls in the text file.
- convert
    - argument:
        - `--overwrite/--no-overwrite`
            - ex) `python main.py convert --no-overwrite`
            - overwrite already converted videos (default: True)
        - `--quiet/--no-quiet`
            - ex) `python main.py convert --no-quiet`
            - show ffmpg output log (default: True)
    - convert all the downloaded videos from `mp4` to `mp3`.
- together
    - argument:
        - `--overwrite/--no-overwrite`
            - ex) `python main.py together --no-overwrite`
            - overwrite already converted videos (default: True)
        - `--quiet/--no-quiet`
            - ex) `python main.py convert --no-quiet`
            - show ffmpg output log (default: True)
    - download all the urls and convert all the downloaded videos.
- one
    - argument:
        - `--url <video url>`
            - ex) `python main.py one --url example.com/example.mp4`
        - `--overwrite/--no-overwrite`
            - ex) `python main.py one --no-overwrite`
            - overwrite already converted videos (default: True)
        - `--quiet/--no-quiet`
            - ex) `python main.py convert --no-quiet`
            - show ffmpg output log (default: True)
    - download vid from url argument and convert the downloaded video.

## future plans
- [x] download and convert with url argument via terminal command.
- [x] add a progress bar to show status of downloading videos.
- [ ] add more convert options.
