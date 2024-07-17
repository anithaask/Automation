import io
import logging
import re

import pytest

from sitbdd.sitcore.bdd_utils.sit_logging import SITCoreLogger
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger
from sitbdd.sitcore.bdd_utils.sit_logging import log_formatter
from sitbdd.sitcore.bdd_utils.sit_logging import LOG_LEVEL_TRACE
from sitbdd.sitcore.bdd_utils.sit_logging import log_trace
from sitbdd.sitcore.bdd_utils.sit_logging import wrap_all_methods_with_log_trace


def generalize_log(log: str):
    """
    Replace unpredictable elements of log messages.

    - Memory addresses become 0x00000000.
    - Python module line numbers become 0.

    :param log: Log message to generalize.
    :return: Generalized message.
    """
    return re.sub(r"0x[0-9A-Fa-f]{8,}", "0x00000000", re.sub(r"\.py:\d+", ".py:0", log))


@log_trace
def traced_function():
    logger = get_sit_logger()
    logger.info("info logged")
    logger.debug("debug logged")
    logger.warning("warning logged")
    logger.error("error logged")


@wrap_all_methods_with_log_trace
class LogTraceWrappedClass:
    """
    Used to test wrap_all_methods_with_log_trace
    """

    def __init__(self):
        self.logger = get_sit_logger()

    def traced_method(self):
        self.logger.info("info logged")
        self.logger.debug("debug logged")
        self.logger.warning("warning logged")
        self.logger.error("error logged")

    @classmethod
    def untraced_class_method(self):
        logger = get_sit_logger()
        logger.info("info logged")
        logger.debug("debug logged")
        logger.warning("warning logged")
        logger.error("error logged")

    @staticmethod
    def untraced_static_method():
        logger = get_sit_logger()
        logger.info("info logged")
        logger.debug("debug logged")
        logger.warning("warning logged")
        logger.error("error logged")

    @classmethod
    @log_trace
    def traced_class_method(self):
        logger = get_sit_logger()
        logger.info("info logged")
        logger.debug("debug logged")
        logger.warning("warning logged")
        logger.error("error logged")

    @staticmethod
    @log_trace
    def traced_static_method():
        logger = get_sit_logger()
        logger.info("info logged")
        logger.debug("debug logged")
        logger.warning("warning logged")
        logger.error("error logged")


@pytest.fixture
def log_trace_wrapped_class():
    return LogTraceWrappedClass()


class TestLoggingUtils:
    def setup(self):
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(
            self.stream
        )  # Would use pytest's capsys instead but it's not working
        # to get logging output
        self.logger = get_sit_logger()
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(self.handler)

    def teardown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()

    def test__get_sit_logger(self):
        logging.setLoggerClass(
            logging.Logger
        )  # Necessary since __init__.py imports stuff which calls get_sit_logger()
        logger_class = logging.getLoggerClass()
        assert logger_class is logging.Logger

        logger = get_sit_logger()

        logger_class = logging.getLoggerClass()
        assert logger_class is SITCoreLogger
        assert isinstance(logger, SITCoreLogger)

    def test__log_level(self):
        log_level = self.logger.getEffectiveLevel()
        assert log_level == logging.WARNING

        self.logger.trace("This should not appear")
        self.handler.flush()
        assert "" == self.stream.getvalue()

        self.logger.setLevel(LOG_LEVEL_TRACE)

        log_level = self.logger.getEffectiveLevel()
        assert log_level == LOG_LEVEL_TRACE
        self.logger.trace("This should appear")
        self.handler.flush()
        assert "This should appear\n" == self.stream.getvalue()

    def test__log_trace(self):
        self.logger.setLevel(LOG_LEVEL_TRACE)

        traced_function()

        self.handler.flush()
        expected = (
            ">>>: [test_logging_utils.py:0 - traced_function], [()], [{}]"
            "\ninfo logged\ndebug logged\nwarning logged\nerror logged\n"
            "<<<: [test_logging_utils.py:0 - traced_function], [None]\n"
        )
        assert expected == generalize_log(self.stream.getvalue())

    def test__wrap_all_methods_with_log_trace__traced_method(
        self, log_trace_wrapped_class: LogTraceWrappedClass
    ):
        self.logger.setLevel(LOG_LEVEL_TRACE)

        log_trace_wrapped_class.traced_method()
        self.handler.flush()

        expected = (
            ">>>: [test_logging_utils.py:0 - traced_method], "
            "[(<test_logging_utils.LogTraceWrappedClass object at 0x00000000>,)], "
            "[{}]\ninfo logged\ndebug logged\nwarning logged\nerror logged\n"
            "<<<: [test_logging_utils.py:0 - traced_method], [None]\n"
        )
        assert expected == generalize_log(self.stream.getvalue())

    def test__wrap_all_methods_with_log_trace__untraced_class_method(
        self, log_trace_wrapped_class: LogTraceWrappedClass
    ):
        log_trace_wrapped_class.untraced_class_method()
        self.handler.flush()
        assert (
            "info logged\ndebug logged\nwarning logged\nerror logged\n"
            == generalize_log(self.stream.getvalue())
        )

    def test__wrap_all_methods_with_log_trace__traced_class_method(
        self, log_trace_wrapped_class: LogTraceWrappedClass
    ):
        log_trace_wrapped_class.traced_class_method()
        self.handler.flush()

        expected = (
            ">>>: [test_logging_utils.py:0 - traced_class_method], "
            "[(<class 'test_logging_utils.LogTraceWrappedClass'>,)], "
            "[{}]\ninfo logged\ndebug logged\nwarning logged\nerror logged\n"
            "<<<: [test_logging_utils.py:0 - traced_class_method], [None]\n"
        )
        assert expected == generalize_log(self.stream.getvalue())

    def test__wrap_all_methods_with_log_trace__untraced_static_method(
        self, log_trace_wrapped_class: LogTraceWrappedClass
    ):
        log_trace_wrapped_class.untraced_static_method()
        self.handler.flush()
        assert (
            "info logged\ndebug logged\nwarning logged\nerror logged\n"
            == generalize_log(self.stream.getvalue())
        )

    def test__wrap_all_methods_with_log_trace__traced_static_method(
        self, log_trace_wrapped_class: LogTraceWrappedClass
    ):
        log_trace_wrapped_class.traced_static_method()
        self.handler.flush()

        expected = (
            ">>>: [test_logging_utils.py:0 - traced_static_method], [()], "
            "[{}]\ninfo logged\ndebug logged\nwarning logged\nerror logged\n"
            "<<<: [test_logging_utils.py:0 - traced_static_method], [None]\n"
        )
        assert expected == generalize_log(self.stream.getvalue())

    def test__format__untraced(self, log_trace_wrapped_class: LogTraceWrappedClass):
        self.handler.setFormatter(log_formatter)
        self.logger.setLevel(logging.DEBUG)
        log_trace_wrapped_class.untraced_class_method()
        self.handler.flush()

        log = [generalize_log(line) for line in self.stream.getvalue().split("\n")]

        assert (
            "| INFO | [test_logging_utils.py:0 - untraced_class_method]info logged"
            == log[0][20:]
        )
        assert (
            "| DEBUG | [test_logging_utils.py:0 - untraced_class_method]debug logged"
            == log[1][20:]
        )
        assert (
            "| WARNING | [test_logging_utils.py:0 - "
            "untraced_class_method]warning logged" == log[2][20:]
        )
        assert (
            "| ERROR | [test_logging_utils.py:0 - untraced_class_method]error logged"
            == log[3][20:]
        )
        assert "" == log[4]

    def test__format__traced(self, log_trace_wrapped_class: LogTraceWrappedClass):
        self.handler.setFormatter(log_formatter)
        self.logger.setLevel(LOG_LEVEL_TRACE)
        log_trace_wrapped_class.traced_method()
        self.handler.flush()

        log = [generalize_log(line) for line in self.stream.getvalue().split("\n")]

        assert (
            "| TRACE | >>>: [test_logging_utils.py:0 - traced_method], "
            "[(<test_logging_utils.LogTraceWrappedClass object at 0x00000000>,)], "
            "[{}]" == log[0][20:]
        )
        assert (
            "| INFO | [test_logging_utils.py:0 - traced_method]info logged"
            == log[1][20:]
        )
        assert (
            "| DEBUG | [test_logging_utils.py:0 - traced_method]debug logged"
            == log[2][20:]
        )
        assert (
            "| WARNING | [test_logging_utils.py:0 - traced_method]warning logged"
            == log[3][20:]
        )
        assert (
            "| ERROR | [test_logging_utils.py:0 - traced_method]error logged"
            == log[4][20:]
        )
        assert (
            "| TRACE | <<<: [test_logging_utils.py:0 - traced_method], [None]"
            == log[5][20:]
        )
        assert "" == log[6]
