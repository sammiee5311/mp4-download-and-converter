import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict  # >=3.8
else:
    from mypy_extensions import TypedDict  # <=3.7

from pathlib import Path
from enum import Enum
from typing import Callable, Sequence, Type, TypeVar, Union


class RetryKwArgs(TypedDict):
    overwrite: bool
    url: str


class RetryArgs(TypedDict):
    file_name: Path
    video_url: str
    is_concurrent: bool


TPath = TypeVar("TPath", str, Path)

DownloadStatus = Enum("DownloadStatus", "OK NOT_FOUND ERROR")
DownloadFunc = Callable[[], None]
ConvertFunc = Callable[[bool, bool], None]
DownloadConvertFunc = Callable[[str, bool, bool], None]
DownloadVideoFunc = Callable[[Path, str, bool], DownloadStatus]

InnerFunc = Callable[[RetryKwArgs], None]
DecoratorFunc = Union[DownloadFunc, ConvertFunc, DownloadConvertFunc]
RetryRetFunc = Callable[[DecoratorFunc], InnerFunc]

ExceptionArgs = Union[Type[BaseException], Sequence[BaseException]]
