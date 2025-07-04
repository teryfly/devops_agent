# Simple logging utility

import logging
import os

def setup_logger(name="plan_manager", level="INFO", logfile=None):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    if not logger.handlers:
        if logfile:
            fh = logging.FileHandler(logfile, encoding='utf-8')
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)
    return logger

logger = setup_logger()