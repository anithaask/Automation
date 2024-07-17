"""
This module contains SITCore's custom exceptions.
"""
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger
from sitbdd.sitcore.bdd_utils.sit_logging import wrap_all_methods_with_log_trace


__all_ = ["LoggedError", "NetworkError", "ProductError"]


logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class LoggedError(Exception):
    """An error that should be logged to the main log file."""

    def __init__(self, message, name=None, *args, **kwargs):
        if name:
            message = "{}: {}".format(name, message)

        logger.exception(message)
        super().__init__(message, *args, **kwargs)


@wrap_all_methods_with_log_trace
class NetworkError(LoggedError):
    """An error that occurs in network communication."""

    pass


@wrap_all_methods_with_log_trace
class ProductError(LoggedError):
    """An error that occurs within an RPOS product."""

    pass
