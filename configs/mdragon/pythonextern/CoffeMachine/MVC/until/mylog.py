import logging
import logging.handlers

def getlogger(name=None):
    LOG_FILENAME = 'mylog.log'
    #logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    if name:
        my_logger = logging.getLogger(name)
    else:
        my_logger = logging.getLogger(default)
    my_logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    return my_logger


"""

def get_logger(name=None):
    default = "__app__"
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(funcName)s(%(lineno)d) -- %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
    log_map = {"__app__": "app.log", "__basic_log__": "file1.log", "__advance_log__": "file2.log"}
    if name:
        logger = logging.getLogger(name)
    else:
        logger = logging.getLogger(default)
    fh = logging.FileHandler(log_map[name])
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)
    return logger
"""