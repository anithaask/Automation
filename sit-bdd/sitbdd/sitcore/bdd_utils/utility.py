__all__ = [
    "read_sc_export",
    "get_pump_state_on_pos",
    "wait_until",
    "wait_for_frame_name",
    "wait_for_pump_state_on_pos",
    "wait_for_pump_state_on_fc",
    "wait_for_pump_dispense",
    "wait_for_icr_prompts",
    "suppress_until",
    "wait_for_pos_button_presence",
    "wait_until_sc_pubsub_stops_publishing",
    "wait_until_pos_offline",
    "wait_for_any_pos_menu_frame",
    "require_table_headings",
]

import os
import time
from datetime import datetime
from threading import Thread
from typing import Callable, Dict, Tuple, Type, TypeVar, Optional

from cfrpos.core.pos.user_interface import MenuFrame
from cfrpos.core.bdd_utils.errors import ProductError as POSProductError

from behave.model import Table
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger
from sitbdd.sitcore.bdd_utils.ignore_tags import *
from sitbdd.config import Config

from cfrfuelbdd.simpump_proxy import CSimPumpsProxy
from cfrpos.core.pos.pos_product import POSProduct
from cfrfuelbdd.fuel import FuelNode
from cfrsc.core.sc.sc_product import SCProduct

logger = get_sit_logger()

A = TypeVar("A")
B = TypeVar("B")


class PropagatingThread(Thread):
    def run(self):
        self.exception = None
        try:
            self.ret = self._target(*self._args, **self._kwargs)
        except Exception as ex:
            self.exception = ex
            
    def join(self, timeout: Optional[float] = None):
        super(PropagatingThread, self).join(timeout)
        if self.exception:
            raise RuntimeError('Exception in thread') from self.exception
        return self.ret


def read_device_totals_template(device_type: str):
    device_type = "device_totals_" + device_type.replace(" ", "_")
    target = os.path.join(Config.DATA_DIR, "sc", "device_totals", device_type + ".xml")
    with open(target) as file:
        return file.read()


def wait_until(
    poll: Callable[[], A],
    sentinel: Callable[[A], B],
    attempts: int,
    delay: float,
    timeout: float = 0,
) -> Tuple[B, bool]:
    """Wait until a function returns a given state.

    :param poll: Function to poll for a given state.
    :param sentinel: Function to check for desired state of return value.
    :param attempts: Number of attempts to try function.
    :param delay: Time (in seconds) between attempts.
    :param timeout: Optional. Time (in seconds) after which to stop trying.
    :return: Tuple of function return and last state check.
    """
    if timeout:
        timeout += time.time()
    state = poll()
    for _ in range(attempts):
        state = poll()
        if bool(sentinel(state)):
            return state, True
        if timeout and time.time() > timeout:
            return state, False
        if delay:
            time.sleep(delay)
    return state, False


def wait_for_frame_name(pos: POSProduct, name: str, timeout: int = 5) -> MenuFrame:
    """Waits for a POS frame with a given name (as opposed to use-description)

    Used when use-description is blank for a desired POS frame.

    :param pos: POS communicator.
    :param name: Desired frame name.
    :param timeout: Timeout (in seconds) to wait for frame.
    :return: Frame if found.
    :raise ProductError: Timeout is reached.
    """

    def menu_frame() -> MenuFrame:
        return pos.control.get_menu_frame()

    def frame_name_correct(frame: MenuFrame) -> MenuFrame:
        if frame.name == name:
            return frame

    end_frame, done = wait_until(menu_frame, frame_name_correct, timeout * 2, 0.5)
    if not done:
        raise ProductError(
            f'Timed out waiting for frame "{name}". Got "{end_frame}" instead.'
        )
    return end_frame


def get_pump_state_on_pos(pos: POSProduct, pump_number: int):
    """Checks POS for the current state of a pump.

    :param pos: POS communicator.
    :param pump_number: Desired pump.
    :raise ProductError: Provided pump was not found on the POS.
    """
    fuel_pumps_dict = pos._control._comm.get_frame("fuelpumps").get("Frame")
    for pump in fuel_pumps_dict.get("Pumps"):
        if pump.get("Name") == "pump-" + str(pump_number):
            return pump.get("State")
    raise ProductError(f"Pump {pump_number} was not found within fuelpumps frame.")


def wait_for_pump_state_on_pos(pos: POSProduct, pump_number: int, *state: str, timeout: int = 10) -> None:
    """Waits for POS to get to provided state.

    :param pos: POS communicator.
    :param pump_number: Desired pump.
    :param state: Desired state of pump.
    :param timeout: Amount of seconds to wait for desired state.
    :raise ProductError: Timed out waiting for provided state.
    """
    def pump_status():
        return get_pump_state_on_pos(pos, pump_number)

    def compare_state(current_state):
        return current_state in state

    end_state, done = wait_until(pump_status, compare_state, timeout * 10, 0.1)
    if not done:
        state = ', '.join(state)
        raise ProductError(
            f"Timed out waiting for pump state "
            f'"{state}". Got "{end_state}" instead.'
        )


def wait_for_pump_state_on_fc(
    fuel: FuelNode, pump_number: int, state: str, timeout: int = 10
) -> None:
    """Waits for desired state to appear on selected pump.

    :param fuel: Fuel controller communicator.
    :param state: Desired state of selected pump.
    :param pump_number: Pump number to wait on.
    :param timeout: Timeout (in seconds) to wait for pump.
    :raise: ProductError if pump does not enter state within timeout.
    """

    def pump_status():
        return fuel.get_pump_status(pump_number)

    def compare_state(current_state):
        return current_state == state

    end_state, done = wait_until(pump_status, compare_state, timeout * 10, 0.1)
    if not done:
        raise ProductError(
            f'Expected pump {pump_number}\'s state to be "{state}" within {timeout} '
            f'seconds, got "{end_state}" instead.'
        )


def wait_for_pump_dispense(
    simpumps: CSimPumpsProxy, pump_number: int, amount: float, attempts: int = 60
) -> None:
    """Waits for a pump to dispense given amount in dollars.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump to wait on.
    :param amount: Amount of fuel (in dollars) for pump to dispense.
    :param attempts: Number of times to check for the dispensed amount.
    :raise: ProductError
    """

    def amount_dispensed() -> float:
        money_display = simpumps.get_current_money_display(pump_number)
        if money_display is None:
            raise ProductError(simpumps.Message)
        return int(money_display) / 100

    def dispense_complete(current_amount: int) -> bool:
        return current_amount >= round(amount, 2)

    delay = 1
    end_amount, done = wait_until(amount_dispensed, dispense_complete, attempts, delay)
    if not done:
        raise ProductError(
            f"Expected pump {pump_number} to dispense ${amount} within "
            f"{attempts * delay} seconds, dispensed ${end_amount} instead."
        )


def wait_for_pump_dispense_gallons(
    simpumps: CSimPumpsProxy, pump_number: int, volume: float, attempts: int = 60
) -> None:
    """Waits for a pump to dispense given volume in gallons.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump to wait on.
    :param volume: Volume of fuel (in gallons) for pump to dispense.
    :param attempts: Number of times to check for the dispensed volume.
    :raise: ProductError
    """

    def volume_dispensed() -> float:
        gallons_display = simpumps.get_current_gallons_display(pump_number)
        if gallons_display is None:
            raise ProductError(simpumps.Message)
        return float(gallons_display) / 1000

    def dispense_complete(current_volume: float) -> bool:
        return current_volume >= round(volume, 2)

    delay = 1
    end_volume, done = wait_until(volume_dispensed, dispense_complete, attempts, delay)
    if not done:
        raise ProductError(
            f"Expected pump {pump_number} to dispense ${volume} within "
            f"{attempts * delay} seconds, dispensed ${end_volume} instead."
        )


def wait_for_icr_prompts(
    simpumps: CSimPumpsProxy,
    pump_number: int,
    *prompts: str,
    attempts: int = 60,
    delay: float = 1,
    timeout: float = None,
    exact_match: bool = True,
) -> bool:
    """Wait for a prompt from a list of prompts to match the ICR display.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump to wait on.
    :param prompts: Prompts to match.
    :param attempts: Number of tries to match the ICR display.
    :param delay: Seconds to wait between attempts.
    :return: Indicates if one of the given prompts matched the ICR display.
    :raise: ProductError
    """

    def get_current_display() -> str:
        current_display = simpumps.get_current_display(pump_number)
        if current_display is None:
            raise ProductError(simpumps.Message)
        return current_display

    def prompt_in_current_display(current_display: str) -> bool:
        if exact_match:
            return current_display in prompts
        else:
            for prompt in prompts:
                if prompt in current_display:
                    return True
            return False

    ending_display, done = wait_until(
        get_current_display, prompt_in_current_display, attempts, delay, timeout=timeout,
    )
    if done:
        return True

    raise ProductError(
        f"Expected pump {pump_number} to display one of {prompts} within "
        f'{attempts * delay} seconds, got "{ending_display}" instead.'
    )


def wait_for_not_icr_prompts(
    simpumps: CSimPumpsProxy,
    pump_number: int,
    *prompts: str,
    attempts: int = 60,
    delay: float = 1,
    timeout: float = None,
    exact_match: bool = True,
) -> bool:
    """Wait for all the given prompts to NOT be shown on the ICR display.

    :param simpumps: Simpumps communicator.
    :param pump_number: Pump to wait on.
    :param prompts: Prompts to match.
    :param attempts: Number of tries to match the ICR display.
    :param delay: Seconds to wait between attempts.
    :return: Indicates if one of the given prompts is not shown on the ICR display.
    :raise: ProductError
    """

    def get_current_display() -> str:
        current_display = simpumps.get_current_display(pump_number)
        if current_display is None:
            raise ProductError(simpumps.Message)
        return current_display

    def prompt_not_in_current_display(current_display: str) -> bool:
        if exact_match:
            return current_display not in prompts
        else:
            for prompt in prompts:
                if prompt in current_display:
                    return False
            return True

    ending_display, done = wait_until(
        get_current_display, prompt_not_in_current_display, attempts, delay, timeout=timeout,
    )
    if done:
        return True

    raise ProductError(
        f"Expected pump {pump_number} to change from one of {prompts} within "
        f'{attempts * delay} seconds, but still showing "{ending_display}".'
    )


def suppress_until(
    func: Callable[..., A],
    *exceptions: Type[Exception],
    attempts: int = 2,
    delay: float = 1,
) -> A:
    """Repeatedly call a function until it is called successfully without
    raising exceptions, or the number of attempts has been met.

    :param func: Function to call.
    :param exceptions: Exceptions to suppress.
    :param attempts: Number of times to call the given function.
    :param delay: Seconds to wait between calls.
    :return: Return value of the given function.
    :raise: Any previously suppressed exception once the limit is reached.
    """
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except exceptions:
            if attempt == attempts:
                raise
            if delay:
                time.sleep(delay)


def wait_for_pos_button_presence(
    pos: POSProduct, button_name: str, attempts=2, delay=1
) -> MenuFrame:
    """Parse the POS menu frame until the given button name is found.

    :param pos: POS communicator.
    :param button_name: Name of button to find.
    :param attempts: Number of times to parse the POS menu frame.
    :param delay: Time in seconds to wait between attempts.
    :return: POS menu frame containing the button.
    """

    def get_button_frame() -> Optional[MenuFrame]:
        # Suppress HTTP errors when getting the menu frame
        # to avoid intermittent failures.
        parent = suppress_until(
            pos.control.get_menu_frame, POSProductError, attempts=3, delay=3
        )
        for button in parent.buttons:
            if button.name == button_name:
                return parent
        for child in parent.frames:
            for button in child.buttons:
                if button.name == button_name:
                    return parent

    for _ in range(attempts):
        button_frame = get_button_frame()
        if button_frame is not None:
            return button_frame
        if delay:
            time.sleep(delay)
    raise ProductError(f'POS button "{button_name}" was not present.')


def wait_until_sc_pubsub_stops_publishing(
    sc: SCProduct, topic_id: str, stop_duration: int, attempts: int
) -> None:
    """Wait until a topic stops publishing messages.

    If a message is pulled during the stop duration, the stop duration restarts and
    another attempt is made. The wait ends when no messages are pulled within the stop
    duration. Waiting for the stop duration to pass may be necessary when trying to
    identify a cluster of published messages.

    As an example, a single POS transaction summary may be clustered with other summary
    messages originating from that same POS transaction. After waiting for the stop
    duration to pass, all transaction summary messages would have been published and
    generated exports will be more accurate.

    :param sc: SC communicator.
    :param topic_id: Topic ID to wait on.
    :param stop_duration: Time in seconds that must pass without a message being
        published for the pub-sub to be considered stopped.
    :param attempts: Number of times to wait for the stop duration to pass.
    :raise ProductError: Messages were published during the stop duration.
    """

    def poll_pubsub() -> Optional[Dict]:
        return sc.pubsub_subscriber.wait_for_pubsub_messages(
            topic_id, timeout=stop_duration
        )

    def is_empty(pubsub_message: Optional[Dict]) -> bool:
        if pubsub_message is None:
            return True
        message = pubsub_message.get("message")
        return message is None or len(message) == 0

    last_message, done = wait_until(poll_pubsub, is_empty, attempts, 0)
    if not done:
        raise ProductError(
            f"Expected to expire quiet period within "
            f"{stop_duration * attempts} seconds, got {last_message} instead."
        )


def wait_until_pos_offline(
    pos: POSProduct, attempts: int = 240, delay: float = 0.25
) -> None:
    """Wait for POS to go offline.

    :param pos: POS communicator.
    :param attempts: Number of times to poll POS state.
    :param delay: Time in seconds to wait between attempts.
    """
    online, _ = wait_until(
        pos.control.is_active, lambda active: not active, attempts, delay
    )
    if online:
        raise POSProductError(
            f"Failed to wait for POS to go offline within "
            f"{round(attempts * delay, 2)} seconds."
        )


def wait_for_any_pos_menu_frame(
    pos: POSProduct, attempts: int = 60, delay: float = 1.0
) -> None:
    """Wait for POS to return a menu frame when requested.

    When the POS is restarted, it may or may not return any frames just yet.
    This utility can be used to wait until the POS is fully active and returning frames.

    :param pos: POS Communicator.
    :param attempts: Number of times to poll for POS menu frame.
    :param delay: Time in seconds to wait between attempts.
    """

    def get_menu_frame() -> Optional[MenuFrame]:
        try:
            return pos.control.get_menu_frame()
        except POSProductError:
            pass

    _, menu_frame = wait_until(
        get_menu_frame, lambda frame: isinstance(frame, MenuFrame), attempts, delay
    )
    if not menu_frame:
        raise POSProductError(
            f"Failed to wait for POS to return a menu frame within "
            f"{round(attempts * delay, 2)} seconds."
        )


def require_table_headings(table: Table, *required_headings: str) -> None:
    """Require a given set of column headings from the context table.

    Behave has useful methods to require columns individually, but these methods
    merely does membership tests. This utility function will require an exact
    match in value and order.

    :param table: Behave table.
    :param required_headings: Expected column headings.
    :raise ValueError: Behave table is empty or column headings do
        not match the expected headings in both value and order.
    """
    if table is None:
        raise ValueError("This step requires a context table.")

    actual_headings = set(table.headings)
    if not set(required_headings).issubset(actual_headings):
        raise ValueError(
            f"This step requires context table headings {required_headings}, "
            f"got {actual_headings} instead."
        )

export_template_replacements = {
    "CURRENT_HOUR": lambda : datetime.now().hour
}

def read_sc_export(version: float, export_type: str, template_name: str):
    """Find the correct template for export comparison.

    :param version: NAXML export version.
    :param export_type: Type of export that is being compared.
    :param template_name: Name of the export template to compare to.
    :raise ValueError: The provided export type is not currently supported.
    """
    export_type_folder = {
        "PDICashierReport": "cashier_summary",
        "employee_time_clock_placeholder": "employee_time_clock",
        "fuel_grade_movement_placeholder": "fuel_grade_movement",
        "fuel_product_movement_placeholder": "fuel_product_movement",
        "NAXML-ItemSalesMovement": "item_sales_movement",
        "merchandise_code_movement_placeholder": "merchandise_code_movement",
        "PDIMiscSumMvmt": "miscellaneous_summary_movement",
        "NAXML-POSJournal": "pos_journal",
        "tank_product_movement_placeholder": "tank_product_movement",
    }.get(export_type)

    if export_type_folder is None:
        raise ValueError('Unknown export type: "{}"'.format(export_type))

    target = os.path.join(
        Config.DATA_DIR,
        "sc",
        "export",
        str(version).replace(".", "_"),
        export_type_folder,
        template_name.replace(" ", "_") + ".xml",
    )

    with open(target) as file:
        template = file.read()

    for (key,value) in export_template_replacements.items():
        template = template.replace(f"%%%{key}%%%", str(value()))
        
    return template


def get_ignore_tag(export_type: str) -> tuple:
    if export_type == "NAXML-POSJournal":
        return pos_journal_ignore_tag, pos_journal_ignore_tag_content
    elif export_type == "PDIMiscSumMvmt":
        return None, msm_ignore_tag_content
    elif export_type == "PDICashierReport":
        return None, cashier_summary_ignore_tag_content
    elif export_type == "NAXML-ItemSalesMovement":
        return None, ism_ignore_tag_content
    else:
        return None, None