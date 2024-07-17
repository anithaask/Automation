__all__ = [
    "set_roof_bar_frame",
    "roof_bar_pages",
    "wait_for_roof_bar_button_presence",
    "wait_for_roof_bar_button_absence",
]

import time
from typing import Optional

from cfrsmtaskman.core.bdd_utils.errors import NetworkError
from cfrsmtaskman.core.smtaskman.smtaskman_product import SMTaskManProduct

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger

logger = get_sit_logger()


def set_roof_bar_frame(smtaskman: SMTaskManProduct, frame_name: str) -> None:
    """Set the active roof-bar frame by name.

    This may iterate through other frames to ensure that it starts from the
    first page of given a frame.

    :param smtaskman: SMTaskMan communicator.
    :param frame_name: Roof-bar frame name which can be one of "alerts",
        "hotkeys", or "apps".
    :raise ValueError: Unknown frame name.
    """
    known_frame_names = "alerts", "hotkeys", "apps"
    if frame_name not in known_frame_names:
        raise ValueError(
            f'Unknown frame name "{frame_name}". Must be one of {known_frame_names}.'
        )
    for _ in range(len(known_frame_names) + 1):
        frame = smtaskman.get_frame_content()
        assert frame, "Failed to get frame."
        if frame["FrameName"] == frame_name and frame["Page"]["Number"] == 1:
            return
        assert smtaskman.switch_content(), "Failed to switch frames."
    raise ValueError(f'Failed to set roof-bar frame to "{frame_name}".')


def roof_bar_pages(smtaskman: SMTaskManProduct) -> dict:
    """Generate pages of the current roof-bar frame until the last page.

    :param smtaskman: SMTaskMan communicator.
    :return: Roof-bar page.
    """

    def get_frame() -> dict:
        _frame = smtaskman.get_frame_content()
        assert _frame, "Failed to get frame."
        return _frame

    started = False
    frame = get_frame()
    while not started or frame["Page"]["Number"] != 1:
        try:
            started = True
            yield frame

            # Frames with multiple pages can be switched infinitely.
            # Frames with multiple pages can become a single page frame anytime.
            # Switching pages in a single page frame will raise a NetworkError.
            switch = smtaskman.switch_content_page()
            assert switch, "Failed to switch frames."

            # All pages must have been visited if a subsequent page is the first page.
            frame = get_frame()
        except NetworkError:
            return
    return


def wait_for_roof_bar_button_presence(
    smtaskman: SMTaskManProduct, button: dict, attempts: int = 5, delay: int = 1
) -> Optional[dict]:
    """Wait until a given button is present on the roof-bar's current frame.

    This utility allows full or partial matching of buttons. Buttons are considered
    equal if all keys and values in the expected button exists in the actual button.
    Each attempt searches all the pages of a given frame until the button is found.

    :param smtaskman: SMTaskMan communicator.
    :param button: Roof-bar button.
    :param attempts: Number of times to search the frame for the button.
    :param delay: Seconds to wait between searches.
    :return: Matching roof-bar button if present. Otherwise, None.
    """
    for attempt in range(max(1, attempts)):
        for page in roof_bar_pages(smtaskman):
            for actual_button in page.get("Buttons", []):
                if button.items() <= actual_button.items():
                    return actual_button
        if attempt < attempts - 1 and delay:
            time.sleep(delay)


def wait_for_roof_bar_button_absence(
    smtaskman: SMTaskManProduct, button: dict, attempts: int = 5, delay: int = 1
) -> Optional[dict]:
    """Wait until a given button is not on the roof-bar's current frame.

    This utility allows full or partial matching of buttons. Buttons are considered
    equal if all keys and values in the expected button exists in the actual button.
    Each attempt searches all the pages of a given frame until the button is not found.

    :param smtaskman: SMTaskMan communicator.
    :param button: Roof-bar button.
    :param attempts: Number of times to search the frame for the button.
    :param delay: Seconds to wait between searches.
    :return: Matching roof-bar button if present. Otherwise, None.
    """
    matching_button = None
    for attempt in range(max(1, attempts)):
        matching_button = wait_for_roof_bar_button_presence(smtaskman, button, attempts=1)
        if matching_button is None:
            return
        if attempt < attempts - 1 and delay:
            time.sleep(delay)
    return matching_button


def press_alert_on_menu_bar(smtaskman: SMTaskManProduct, alert_message: str) -> None:
    """Press alert on the SMTaskMan bar.

    :param smtaskman: SMTaskMan communicator.
    :param alert_message: Message that appears on the alert.
    :raise SMTaskManProductError: Alert was not present on the SMTaskMan bar.
    """
    set_roof_bar_frame(smtaskman, "alerts")
    expected_button = {"Message": alert_message}
    attempts = 5
    delay = 1
    actual_button = wait_for_roof_bar_button_presence(
        smtaskman, expected_button, attempts=attempts, delay=delay
    )
    if actual_button is None:
        raise SMTaskManProductError(
            f"{expected_button} was not present within "
            f"{round(attempts * delay, 2)} seconds."
        )
    smtaskman.press_button(actual_button["Name"])