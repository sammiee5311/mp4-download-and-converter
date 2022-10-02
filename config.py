from dotenv import load_dotenv

ENV_PATH = ".env"


def load_env() -> None:
    load_dotenv(dotenv_path=ENV_PATH)


class RetryError(BaseException):
    """Retry Error"""
