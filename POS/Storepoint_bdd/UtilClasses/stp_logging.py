__all__ = [
    "setup_logger",
    "STPCoreLogger",
    "LOG_LEVEL_TRACE",
    "get_stp_logger",
    "log_formatter",
    "log_trace",
    "wrap_all_methods_with_log_trace",
]
import os
import logging
import functools
import inspect

from logging.handlers import RotatingFileHandler

from features.Config import Config

CONFIG = Config()

LOG_FILE_NAME = 'log_file_name'
LOG_DIR = 'Log_folder'
LOG_FILE = os.path.join('staging', LOG_DIR, LOG_FILE_NAME)
LOG_FILE_MAX_BYTES = 10 * 1024 ** 2
LOG_FILE_BACKUP_COUNT = 5
LOG_LEVEL_TRACE = 5

logger  = logging.getLogger("")
file_handler = logging.FileHandler('logfile.log')
formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
# add file handler to logger
logger.addHandler(file_handler)

_recent_logs = []


def setup_logger():
    """
    Setup and retrieve the singleton logger.
    :return: Singleton of SIT logger
    :rtype: SITCoreLogger
    """
    _logger = get_stp_logger()

    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT
    )

    if "trace_logging" is True:
        _logger.setLevel(LOG_LEVEL_TRACE)
        file_handler.setLevel(LOG_LEVEL_TRACE)
    else:
        _logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)

    file_handler.setFormatter(log_formatter)
    _logger.handlers.clear()
    _logger.addHandler(file_handler)

    return _logger


class STPCoreLogger(logging.getLoggerClass()):
    """
    Wrapper to allow adding the "TRACE" level to the logger
    """

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        logging.addLevelName(LOG_LEVEL_TRACE, "TRACE")

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(LOG_LEVEL_TRACE):
            self._log(LOG_LEVEL_TRACE, msg, args, **kwargs)


class STPCoreLoggerFormatter(logging.Formatter):
    # Using a different format for TRACE logs to avoid having a ton of lines
    # mentioning the location of the log_trace function
    trace_fmt = "{asctime} | {levelname} | {message}"

    def __init__(
        self,
        fmt="{asctime} | {levelname} | [{filename}:{lineno} - {funcName}]{message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    ):
        logging.Formatter.__init__(self, fmt, datefmt, style)

    def format(self, record):

        if record.levelno == LOG_LEVEL_TRACE:
            orig_format = self._fmt
            orig_style_format = self._style._fmt
            self._fmt = STPCoreLoggerFormatter.trace_fmt
            self._style._fmt = STPCoreLoggerFormatter.trace_fmt
            result = logging.Formatter.format(self, record)
            self._fmt = orig_format
            self._style._fmt = orig_style_format
        else:
            result = logging.Formatter.format(self, record)

        return result


log_formatter = STPCoreLoggerFormatter()


def get_stp_logger():
    """
    Simple abstraction of logging.getLogger() so we can more easily
    make sweeping changes in the future if necessary.

    :return: Singleton logger
    :rtype: stpLogger
    """
    cls = logging.getLoggerClass()

    if cls is not STPCoreLogger:
        logging.setLoggerClass(STPCoreLogger)

    return logging.getLogger("STP Logger")


def log_trace(func):
    """Decorates a function to log trace information when the config file's
    "trace_logging" attribute is set to true

    :param func: Function to decorate
    :return: Decorated function
    :rtype: function
    """

    @functools.wraps(func)
    def _log_trace(*args, **kwargs):
        logger = get_stp_logger()

        file_name = os.path.basename(inspect.getsourcefile(func))
        function_name = func.__name__
        lines, line_no = inspect.getsourcelines(func)

        logger.trace(
            ">>>: [%s:%s - %s], [%s], [%s]"
            % (file_name, line_no, function_name, args, kwargs)
        )

        ret = func(*args, **kwargs)

        logger.trace(
            "<<<: [%s:%s - %s], [%s]" % (file_name, line_no, function_name, ret)
        )

        return ret

    return _log_trace


# TODO: Need to figure out how to have the wrapper work with
#  @staticmethod and @classmethod
def wrap_all_methods_with_log_trace(cls):
    """
    Allows decorating a class such that all methods in the class will be wrapped
    with the log_trace wrapper

    Note: This will not wrap static or class methods as log_trace needs to
    be applied prior to them. As such, you must explicitly wrap static and
    class methods with log_trace within the class.
    Be sure to place "@log_trace" just above the method def and
     underneath the "@staticmethod" or @classmethod" line like so:

        @staticmethod
        @log_trace
        def some_function_name():
            ...

    :param cls: Class to decorate the methods of
    :return: Decorated class
    :rtype: class
    """
    for key in cls.__dict__:
        value = getattr(cls, key)

        if callable(value):
            if inspect.isroutine(value):
                binded_value = cls.__dict__[key]
                if not isinstance(binded_value, staticmethod) and not isinstance(
                    binded_value, classmethod
                ):
                    setattr(cls, key, log_trace(value))

    return cls
