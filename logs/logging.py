import logging
import os

from config import load_env

load_env()

LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "./logs/output.log")

formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger("mp4")
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_FILE_PATH)

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
