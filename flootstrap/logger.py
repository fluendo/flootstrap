import logging

import colorlog

logger = logging.getLogger(__name__)
stream_handle = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "[%(asctime)s] %(log_color)s%(levelname)s%(reset)s %(filename)s:%(lineno)s %(message)s"
)

stream_handle.setFormatter(formatter)
logger.addHandler(stream_handle)
