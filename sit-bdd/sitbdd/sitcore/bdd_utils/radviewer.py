__all__ = ["DEFAULT_RVRS_PATHS", "RVSResult", "RadViewerScript"]

import subprocess
from pathlib import Path
from typing import Sequence, Type, TypeVar

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger
from sitbdd.sitcore.bdd_utils.file_utility import temporary_file

DEFAULT_RVRS_PATHS = (
    Path("C:/Program Files/NCR/RadViewer/NTSeriallink/RadViewRunScript.exe"),
    Path("C:/Program Files (x86)/NCR/RadViewer/NTSeriallink/RadViewRunScript.exe"),
)
T = TypeVar("T", bound="RadViewerScript")


class RVSResult:
    """RadViewer script result."""

    def __init__(self, log: str) -> None:
        """
        :param log: Log file content.
        """

        self.log = log

    def find_lines(self, text: str) -> Sequence[str]:
        """
        Find any lines in the log with matching text.
        :param text: Text with which to identify matching line.
        :return: Line if found.
        """

        return [line for line in self.log.splitlines() if text in line]

    def find_errors(self) -> Sequence[str]:
        """
        Find any lines in the log with an error.
        :return: Line if found.
        """

        return self.find_lines("------ ERROR")

    def validate(self) -> None:
        """
        Check if the log contains an error and fail if so.
        :raise RuntimeError: if the log contains an error.
        """

        errors = self.find_errors()

        if errors:
            message = (
                "The RadViewer script completed, but the log contains errors:\n- {}"
            )
            raise RuntimeError(message.format("\n- ".join(errors)))


class RadViewerScript:
    r"""
    This class represent a RadViewer script. It uses a fluent builder style
    to allow adding multiple commands to the same script. Each step of the
    builder returns a new instance, so you can safely save any given version
    of the script without risk of mutation.
    >>> result = RadViewerScript() \
    ...     .stop_service("Example") \
    ...     .start_service("Example") \
    ...     .result("127.0.0.1")
    """

    def __init__(self):
        self._lines = tuple()

    @classmethod
    def from_lines(cls: Type[T], lines: Sequence[str]) -> T:
        """
        Create a new script from raw commands. Syntax will not be checked,
        so it is possible to create invalid scripts.
        :param lines: Lines to write into script.
        :return: New instance.
        """

        instance = cls()
        instance._lines = tuple(lines)
        return instance

    def result(
        self, target: str, timeout: int = 60, validate: bool = True, runner: Path = None
    ) -> RVSResult:
        """
        Run the RadViewer script and return its result.
        :param target: IP address to target for script execution.
        :param timeout: Maximum seconds to wait for script to finish.
        :param validate: Automatically validate the script's result.
        :param runner: Location of RadViewRunScript.exe. If not specified,
            will check known default paths.
        :return: RadViewer script result.
        """

        runner = self._get_rvrs(runner)
        with temporary_file(suffix=".rvs") as script_file:
            script_file.write_text(self.serialize())
            script_log_file = script_file.with_suffix(".rvs.log")
            self._run_script(runner, target, script_file, timeout)
        return self._get_result(script_log_file, validate)

    def serialize(self) -> str:
        """
        Return the script's content as text.
        :return: Script content.
        """

        return "\n".join(self._lines)

    @staticmethod
    def _get_rvrs(rvrs: Path = None) -> Path:
        """
        Find RadViewRunScript.exe at a specified path or a known default.
        :param rvrs: Location of RadViewRunScript.
        :return: Path to RadViewRunScript.
        :raise FileNotFoundError: if RadViewRunScript cannot be found.
        """

        if rvrs:
            candidates = [rvrs]
        else:
            candidates = DEFAULT_RVRS_PATHS

        for candidate in candidates:
            if candidate.is_file():
                return candidate

        raise FileNotFoundError("Could not find RadViewRunScript.exe.")

    @staticmethod
    def _run_script(rvrs: Path, target: str, script: Path, timeout: int) -> None:
        """
        Run a RadViewer script.
        :param rvrs: Location of RadViewRunScript.
        :param target: IP address to target for script execution.
        :param script: Location of script to run.
        :param timeout: Maximum seconds to wait for script to finish.
        :raise subprocess.CalledProcessError: if the exit code is not 0.
        """

        command = '"{}" /s{} /ip{}'.format(rvrs, script, target)
        get_sit_logger().debug("Running subprocess: '{}'".format(command))
        process = subprocess.run(command, timeout=timeout)
        process.check_returncode()

    @staticmethod
    def _get_result(script_log: Path, validate: bool) -> RVSResult:
        """
        Get the script's result.
        :param script_log: Location of script log file.
        :param validate: Validate the result.
        :return: RadViewer script result.
        :raise FileNotFoundError: if the log does not exist.
        :raise RuntimeError: if the log contains errors.
        """

        if not script_log.is_file():
            raise FileNotFoundError(
                "RadViewRunScript.exe completed, but did not write any log."
            )

        result = RVSResult(script_log.read_text())
        get_sit_logger().debug(
            "RadViewRunScript.exe log from {}:\n{}".format(
                script_log.absolute(), result.log
            )
        )
        script_log.unlink()

        if validate:
            result.validate()
        return result

    def _add_line(self: Type[T], line: str) -> T:
        """
        Return new script based on current state with a line added.
        :param line: Line to add.
        :return: New instance.
        """

        return self.from_lines([*self._lines, line])

    def start_service(self, name: str) -> "RadViewerScript":
        """
        Start a service.
        :param name: Name of service.
        :return: Updated RadViewer script.
        """
        return self._add_line("ServiceStart {}".format(name))

    def stop_service(self, name: str) -> "RadViewerScript":
        """
        Stop a service.
        :param name: Name of service.
        :return: Updated RadViewer script.
        """
        return self._add_line("ServiceStop {}".format(name))

    def get_service_info(self, name: str) -> "RadViewerScript":
        """
        Get information about a service.
        :param name: Name of service.
        :return: Updated RadViewer script.
        """
        return self._add_line("ServiceGetInfo {}".format(name))
