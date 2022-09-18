import sys


if sys.version_info >= (3, 8):
    from typing import TypedDict  # >=3.8
else:
    from mypy_extensions import TypedDict  # <=3.7

from typing import Callable, Union, Sequence, Type


class RetryKwArgs(TypedDict):
    overwrite: bool
    url: str


DownloadFunc = Callable[[], None]
ConvertFunc = Callable[[bool], None]
DownloadConvertFunc = Callable[[str, bool], None]

InnerFunc = Callable[[RetryKwArgs], None]
DecoratorFunc = Union[DownloadFunc, ConvertFunc, DownloadConvertFunc]
RetryRetFunc = Callable[[DecoratorFunc], InnerFunc]

ExceptionArgs = Union[Type[Exception], Sequence[Exception]]
