import logging
import sys


def setup_logging(level=logging.INFO, verbose: bool = False):
    log_format = "%(asctime)-15s [%(name)-16s] %(levelname)-8s: %(message)s"
    logging.basicConfig(format=log_format, stream=sys.stderr, level=level)
