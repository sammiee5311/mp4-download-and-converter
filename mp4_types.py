import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict  # >=3.8
else:
    from mypy_extensions import TypedDict  # <=3.7

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec, Concatenate  # <3.10
else:
    from typing import ParamSpec, Concatenate  # =3.10

from pathlib import Path
from enum import Enum
import httpx
import ffmpeg
from typing import Callable, Type, TypeVar, Union


class DownloadArgs(TypedDict):
    file_name: Path
    video_url: str
    is_concurrent: bool


class ConvertArgs(TypedDict):
    video_file: Path
    overwrite: bool
    quiet: bool


DownloadStatus = Enum("DownloadStatus", "OK NOT_FOUND ERROR")
ConvertStatus = Enum("ConvertStatus", "OK EXIST ERROR")

TPath = TypeVar("TPath", str, Path)
ParamType = ParamSpec("ParamType")
RetType = TypeVar("RetType", DownloadStatus, ConvertStatus)
OriginalFunc = Callable[ParamType, RetType]
DecoratedFunc = Callable[Concatenate[Union[DownloadArgs, ConvertArgs], ParamType], RetType]

DownloadVideoFunc = Callable[[DownloadArgs], DownloadStatus]
ConvertVideoFunc = Callable[[ConvertArgs], ConvertStatus]

InnerFunc = Union[DownloadStatus, ConvertStatus]
DecoratorFunc = Union[DownloadVideoFunc, ConvertVideoFunc]
RetryRetFunc = Callable[[DecoratorFunc], DecoratorFunc]

ExceptionArgs = Union[Type[httpx.HTTPStatusError], Type[ffmpeg.Error]]
