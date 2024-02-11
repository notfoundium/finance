import logging

logger = logging.getLogger("finance")
logger.setLevel("DEBUG")
fh = logging.FileHandler("latest.log")
ch = logging.StreamHandler()

formatter = logging.Formatter(
    "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s")

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)
