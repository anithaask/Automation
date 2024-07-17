import time
import os
from behave.model import Table
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from sitbdd.config import Config
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils.utility import PropagatingThread
from sitbdd.sitcore.bdd_utils import icr_utilities
from sitbdd.sitcore.bdd_utils import pos_utilities
from sitbdd.sitcore.bdd_utils.mapping import SITMapping
from sitbdd.sitcore.rcm.update_types import UpdateTypes
from sitbdd.sitcore.bdd_utils.sit_logging import setup_logger
from sitbdd.sitcore.tank_simulator.tank_sim_product import TankSimProduct
from sitbdd.sitcore.rcm.rcm_product import RCMProduct
from sitbdd.sitcore.bdd_utils.card_deck import CardDeck
from sitbdd.sitcore.eps_and_loyalty.epsilon import Epsilon
from sitbdd.sitcore.eps_and_loyalty.sigma import Sigma
from sitbdd.sitcore.kps.kps_product import KPSProduct

# import packages from product teams
from cfrfuelbdd.fuel import FuelNode
from cfrfuelbdd.simpump_proxy import CSimPumpsProxy
from cfrpos.core.pos.pos_product import POSProduct
from cfrpos.core.pos.ui_metadata import POSButton
from cfrpos.core.pos.ui_metadata import POSFrame
from cfrpos.core.bdd_utils.receipt_comparer import compare_receipts
from sim4cfrpos.api.scan_sim.scan_sim_control import ScanSimControl
from sim4cfrpos.api.print_sim.print_sim_control import PrintSimControl
from cfrsmtaskman.core.smtaskman.smtaskman_product import SMTaskManProduct
from cfrsc.core.sc.sc_product import SCProduct
from cfrsc.core.bdd_utils.file_provider import FileProvider
from cfrsc.core.http_server_simulator.http_server_simulator_client import HttpServerSimulatorClient

logger = setup_logger()

class SITProduct:

    def __init__(self):
        self.mapping = SITMapping()
        self.config = Config()
        current_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.abspath(os.path.join(current_path, "data"))

        cards_file = os.path.join("data", "cards.json")
        if os.path.exists(cards_file):
            self.card_deck = CardDeck(card_file_path=cards_file)
        else:
            self.card_deck = CardDeck()

        if "pos" in self.config['nodes']:
            logger.info("+++++ Initializing POS +++++")
            # pos_config matches to the config consumed by POSProduct from cfrpos package
            pos_config = {
                'api': {
                    'pos': {
                        'address': ".".join([self.config['subnet'], self.config['nodes']['pos']['hostname_node']]),
                        'port': self.config['nodes']['pos']['port']
                    }
                },
                # This is used in POS and needed to point on the actual file, but has no impact on behavior for SIT BDD
                'bin_dir': self.config['nodes']['pos']['bin_dir']
            }
            # printer_config matches to the config consumed by PrintSimControl from sim4cfrpos package
            printer_config = {
                'address': ".".join([self.config['subnet'], self.config['nodes']['pos']['print_sim']['hostname_node']]),
                'port': self.config['nodes']['pos']['print_sim']['port'],
                'server_log_file': os.path.join(self.config['staging'], self.config['log_folder'], 'print_sim_server.log'),
                'log_file': os.path.join(self.config['staging'], self.config['log_folder'], 'print_sim.log')
            }
            # scan_config matches to the config consumed by ScanSimControl from sim4cfrpos package
            scanner_config = {
                'address': ".".join([self.config['subnet'], self.config['nodes']['pos']['scan_sim']['hostname_node']]),
                'port': self.config['nodes']['pos']['scan_sim']['port'],
                'server_log_file': os.path.join(self.config['staging'], self.config['log_folder'], 'scan_sim_server.log'),
                'log_file': os.path.join(self.config['staging'], self.config['log_folder'], 'scan_sim.log'),
                'api': {'scan_sim': {'barcodes': self.config['nodes']['pos']['scan_sim']['scan_sim_barcodes']}}
            }
            # smtaskman_config matches to the config consumed by SMTaskManProduct from cfrsmtaskman package
            smtaskman_config = {
                "api": {
                    "smtaskman": {
                        'address': ".".join([self.config['subnet'], self.config['nodes']['pos']['smtaskman']['hostname_node']]),
                        'port': self.config['nodes']['pos']['smtaskman']['port']
                    }
                }
            }
            self.pos = POSProduct(pos_config, printer=PrintSimControl(printer_config), scanner=ScanSimControl(scanner_config))
            self.smtaskman = SMTaskManProduct(smtaskman_config)
            self.pos._wait_for_availability(timeout=400)
            assert self.smtaskman.get_status() is not None, "SMTaskman status is None"
            logger.info("+++++ POS initialized +++++")

        if "jag" in self.config['nodes']:
            logger.info("+++++ Initializing Jag +++++")
            attempts = 200
            delay = 2
            self.fuel = None
            for attempt in range(attempts):
                logger.info(f"FuelNode initialization attempt: {attempt+1}.")
                try:
                    self.fuel = FuelNode(".".join([self.config['subnet'], self.config['nodes']['jag']['hostname_node']]))
                    break
                except Exception:
                    logger.info(f"FuelNode initialization not successful, waiting {delay} seconds...")
                    time.sleep(delay)
            if self.fuel is None:
                raise ProductError(f"FuelNode was not initialized successfully in {attempts*delay}.")
            self.simpumps = None
            for attempt in range(attempts):
                logger.info(f"SimPumps initialization attempt: {attempt+1}.")
                try:
                    self.simpumps = CSimPumpsProxy(
                        ".".join([self.config['subnet'], self.config['nodes']['jag']['simpumps']['hostname_node']]),
                        self.config['nodes']['jag']['simpumps']['port']
                    )
                    break
                except Exception:
                    logger.info(f"SimPumps initialization not successful, waiting {delay} seconds...")
                    time.sleep(delay)
            if self.simpumps is None:
                raise ProductError(f"SimPumps were not initialized successfully in {attempts*delay}.")
            logger.info("+++++ Jag Initialized +++++")

        if "sc" in self.config['nodes']:
            self.summarized_transactions = set()
            logger.info("+++++ Initializing SC +++++")
            # Both "FileProvider" and "HttpServerSimulatorClient" had to be configured
            # because of SC package limitations. System tests should not be using
            # "HttpServerSimulatorClient" or "FileProvider".
            self.sc = SCProduct(
                self.config['nodes']['sc'],
                FileProvider(data_path),
                HttpServerSimulatorClient(self.config['nodes']['sc']['hosts']['httpSimulator'])
            )
            # Subscribe to pub-sub topics.
            self.sc.pubsub_subscriber.subscribe(
                [
                    self.sc.pubsub_subscriber.EXPORT_SERVICE_TOPIC_ID,
                    self.sc.pubsub_subscriber.DOWNLOAD_SERVICE_TOPIC_ID,
                    self.sc.pubsub_subscriber.RELAYGEN_SERVICE_TOPIC_ID,
                    "transaction-summarization-event-v1",
                ]
            )
            self.sc.utilities.delete_shift_data()
            self.sc.business_days.open_new_business_day()
            tank_sim_config = {
                "hostname": ".".join([self.config['subnet'], self.config['simulators']['tank_sim']['hostname_node']]),
                "port": self.config['simulators']['tank_sim']['port']
            }
            self.tank_sim = TankSimProduct(
                tank_sim_config["hostname"],tank_sim_config["port"]
            )
            logger.info("+++++ SC Initialized +++++")

        if "eps_and_loyalty" in self.config['nodes']:
            logger.info("+++++ Initializing EPS and Loyalty +++++")
            # TODO: use epsilon package and define where it is installed from config
            # TODO: use pinpad simulator
            # TODO: fix ports in config.json once PMI has been reintroduced - RPOS-60082
            pmi_hostname = ".".join([self.config["subnet"], self.config["nodes"]["eps_and_loyalty"]["hostname_node"]])
            pmi_port = self.config["nodes"]["eps_and_loyalty"]["pmi_port"]
            self.eps = Epsilon(pmi_hostname, pmi_port)
            self.sigma = Sigma(pmi_hostname, pmi_port)
            logger.info("+++++ EPS and Loyalty Initialized +++++")

        if "rcm" in self.config['nodes']:
            logger.info("+++++ Initializing RCM +++++")
            self.rcm = RCMProduct(
                self.config['nodes']['rcm']['server']['hostname'],
                self.config['nodes']['rcm']['server']['port']
            )
            logger.info("+++++ RCM Initialized +++++")
        
        # if "kps" in self.config['nodes']:
        #     logger.info("+++++ Initializing KPS +++++")
        #     self.kps = KPSProduct(".".join([self.config["subnet"], self.config["nodes"]["kps"]["hostname_node"]]))
        #     logger.info("+++++ KPS Initialized +++++")


    def get_pump_numbers(self):
        self.pos._wait_for_availability(120)
        return [pump.pump_number for pump in self.pos.control.get_fuel_pumps_frame().pumps]


    def set_host_state(self, controller_type, state):
        """Set the host's state of the controller type.

        :param controller_type: Controller type. Only "loyalty" is supported.
        :param state: Host state. Can be "online" or "offline".
        :raise ValueError: If the controller doesn't have hosts associated with it or
            the given controller type or state are unknown.
        :raise NotImplementedError: If the given controller type is "credit".
        """
        if controller_type.lower() == "loyalty":
            loyalty_info = self.sigma.get_info()

            if loyalty_info.hosts_list:
                # Assume first host in list
                if loyalty_info.hosts_list[0].online and state.lower() == "offline":
                    self.sigma.stop_host()

                if not loyalty_info.hosts_list[0].online and state.lower() == "online":
                    self.sigma.start_host()

            else:
                raise ValueError("The {} controller does not have any hosts associated with it".format(controller_type))

        elif controller_type.lower() == "credit":
            # TODO: handle credit online/offline
            raise NotImplementedError("Unable to handle setting credit controller state")

        else:
            raise ValueError(
                "Unknown controller type or state: controller_type = {}, "
                "state = {}".format(controller_type, state)
            )


    def ensure_completed_transaction(self, controller_type):
        """Ensure a transaction has been completed on the given controller type.

        :param controller_type: Controller type. Only "loyalty" is supported.
        :raise NotImplementedError: If the given controller type is "credit".
        :raise ValueError: If the given controller type is unknown.
        """
        if controller_type.lower() == "loyalty":
            business_day = self.sc.business_days.get_current_business_day()
            # business_day is coming in form of "2019-06-25"
            self.sigma.post_transaction(business_day.replace('-', ''))

        elif controller_type.lower() == "credit":
            # TODO: handle credit transaction
            raise NotImplementedError("Unable to handle credit transaction")

        else:
            raise ValueError("Unknown controller type: controller_type = {}".format(controller_type))


    def prepare_pump_for_transactions(self, pump_number):
        """
        Sets the ICR to be prepared for transactions. This includes
        hanging up the nozzle, clearing any pending sales, and waiting
        for the welcome prompt

        :param pump_number: Pump number.
        """
        # turn on pump if it's currently offline
        self.simpumps.activate_pump(pump_number)
        # turn on icr if it's currently offline
        self.simpumps.activate_icr(pump_number)
        # hang up nozzle if it isn't already
        self.simpumps.return_nozzle(pump_number)
        # Press the cancel button, which will help the pump get out stale prompts
        self.simpumps.press_button(pump_number, self.mapping.get_icr_keys_remap("CANCEL"))
        # clear transactions
        self.fuel.clear_all_sales(pump_number)
        # Reset SimPumps parameters to clear out any previous transaction data
        # (like printed receipts)
        self.simpumps.reset_parameters(pump_number)
        # wait for welcome prompt
        self.verify_pump_displayed_welcome_prompt(pump_number, timeout_seconds=240)


    def reconnect_simpumps(self):
        """ Reconnect and ensure we are connected to simpumps.
        """
        fuel_config = self.config.get("nodes").get("jag")
        self.simpumps._connect_to_host(
            ".".join([self.config.get("subnet"), fuel_config.get("simpumps").get("hostname_node")]),
            fuel_config.get("simpumps").get("port")
        ), self.simpumps.Message


    def ready_available_pumps(self):
        """Retrieves pump statuses and clears any pending sales on the ICR.

        :raise ProductError: If getting the ICR display fails.
        :raise AssertionError: If any call to the "simpumps" interface fails.
        """
        # Calling "FCProduct.update_configuration" will require reconnection to "simpumps".
        self.reconnect_simpumps()

        pump_numbers = self.get_pump_numbers()
        for pump_number in pump_numbers:
            assert self.simpumps.reset_parameters(pump_number), self.simpumps.Message

            prompt = self.simpumps.get_current_display(pump_number)
            if prompt is None:
                raise ProductError(self.simpumps.Message)

            idle_prompts = self.get_welcome_prompts()

            if prompt not in idle_prompts:
                assert self.simpumps.return_nozzle(pump_number), self.simpumps.Message
                assert self.simpumps.press_button(pump_number, "C"), self.simpumps.Message
                utility.wait_for_icr_prompts(
                    self.simpumps, pump_number, *idle_prompts, attempts=10
                )
            pump = self.fuel.pump(pump_number)
            if pump.status() != "Idle":
                pump.clear_all_sales()

            assert self.simpumps.set_flow_rate(pump_number, 25), self.simpumps.Message

            icr_utilities.reset_paper(self.simpumps, pump_number)


    def dispense_fuel_for_price_at_pump(self, grade: str, price: float, pump_id: int):
        """Dispenses fuel at the given grade, price, and pump.

        :param grade: Grade of fuel to be dispensed.
        :param price: Dollar amount of fuel to be dispensed.
        :param pump_id: ID of pump to dispense fuel from.
        :raise ProductError: Unable to set fuel amount for given pump.
        """
        self.simpumps.press_button(pump_id, self.mapping.get_icr_keys_remap('CASHINSIDE'))

        if self.simpumps.match_prompt_on_display(pump_id, "Loyalty card?", True, 5):
            self.simpumps.press_button(pump_id, self.mapping.get_icr_keys_remap('NO'))

        self.simpumps.lift_nozzle(pump_id)
        self.simpumps.select_grade(pump_id, self.mapping.get_grades_remap(grade))
        utility.wait_for_pump_state_on_pos(self.pos, pump_id, "HandleLifted", "FuelingPrepay")

        self.pos.select_pump(pump_id)
        self.pos.select_pump(pump_id)
        utility.wait_for_pump_state_on_fc(self.fuel, pump_id, "FUELING")
        if not self.simpumps.set_fuel_money(pump_id, round(price * 100, 2)):
            raise ProductError(f"Could not set fueling amount to ${price}")
        self.simpumps.start_fueling(pump_id)
        utility.wait_for_pump_dispense(self.simpumps, pump_id, price)

        self.simpumps.return_nozzle(pump_id)
        utility.wait_for_icr_prompts(
            self.simpumps,
            pump_id,
            "GREETING",
            "ASKLOYALTYMOPPOSTPAY",
            "PUMP BUSY",
            attempts=20,
        )


    def verify_pump_authorized_for_price(self, pump_number: int, amount: float):
        """Verify by pump number that a pump is authorized for a given amount.

        :param pump_number: Number of the pump to check
        :param amount: Amount in dollars rounded to the nearest hundredths.
        :raise TimeoutError: If the pump is not authorized for the given amount in ~1.5
            seconds.
        """
        # A timeout is used here because there is a delay
        # between prepay tendering and pump authorization.

        result, success = utility.wait_until(
            lambda: self.fuel.pump(pump_number).get_authorized_amount(pump_number),
            lambda actual_amount_cents: actual_amount_cents == amount * 100,
            6,
            0.25
        )


    def verify_pump_authorized_for_price(self, pump_number: int, amount: float):
        """Verify by pump number that a pump is authorized for a given amount.

        This function expects the following context values.

        * Pump Number

        :param amount: Amount in dollars rounded to the nearest hundredths.
        :raise TimeoutError: If the pump is not authorized for the given amount in ~1.5
            seconds.
        """
        # A timeout is used here because there is a delay
        # between prepay tendering and pump authorization.

        result, success = utility.wait_until(
            lambda: self.fuel.pump(pump_number).get_authorized_amount(pump_number),
            lambda actual_amount_cents: actual_amount_cents == amount * 100,
            20,
            0.25
        )

        if not success:
            raise (
                TimeoutError(
                    f"Timed out waiting for pump to be authorized for "
                    f"{amount * 100} cents. "
                    f"Pump is instead authorized for {result} cents."
                )
            )


    def verify_pump_displayed_welcome_prompt(self, pump_number: int, timeout_seconds: int = 45):
        prompt_list = self.get_welcome_prompts()

        def poll_for_current_prompt():
            # Updating the configuration on JAG node will require reconnection to "simpumps".
            self.reconnect_simpumps()
            return self.simpumps.get_current_display(pump_number)

        def verify_prompt(actual_prompt):
            for prompt_name in prompt_list:
                if self.simpumps.match_prompt_on_display(pump_number, prompt_name, True, 1):
                    return True
            return False

        actual_prompt, success = utility.wait_until(
            poll_for_current_prompt,
            verify_prompt,
            timeout_seconds,
            1,
            timeout=timeout_seconds
        )

        if not success:
            error = ('Welcome prompt not displayed within {} seconds. Last displayed prompt: "{}"')
            raise TimeoutError(error.format(timeout_seconds, actual_prompt))


    # Setup carwash items in given and use the values from the given here instead.
    def verify_carwash_items_displayed_at_pump(self, pump_number: int):
        # Check the prompt on ICR display to see if it contains any carwash items.
        # if the carwash items are not displayed in 15 seconds then
        # # function will consider that as failure.
        # timeout = time.time() + 15
        # carwash_item_type = ItemTypes.ITEM_TYPE_CARWASH.value

        # carwash_items = self.fuel.get_items(carwash_item_type)
        # if len(carwash_items) > 0:
        #     while time.time() < timeout:
        #         current_prompt = self.simpumps.get_current_display(pump_number)

        #         for item in carwash_items:
        #             # fuel controller truncates the name in carwash screen
        #             # so we will try to match first 5 characters only.
        #             carwash_name = item["Name"][:5]
        #             if carwash_name in current_prompt:
        #                 return

        #         time.sleep(1)

        #     raise TimeoutError("Timed out waiting for ICR to display carwash items")
        # else:
        #     raise RuntimeError("No carwash items found in fuel controller configuration")
        pass


    def verify_available_pumps_reported_in_credit_controller_product_export(self):
        pump_numbers = self.get_pump_numbers()
        product_export = self.eps.export_available_products()
        error_list = []

        for index in pump_numbers:
            pump_online = self.fuel.get_pump_status(index) != "DEAD"

            pump_and_export_match = product_export.verify_icr_availability(index, pump_online)
            # In this step pump available = online and pump unavailable = offline
            if not pump_and_export_match:
                if pump_online:
                    error_list.append(f"Pump {index} was available but was exported as unavailable.")
                else:
                    error_list.append(f"Pump {index} was unavailable but was exported as available.")

            if error_list:
                raise ProductError(". ".join(error_list))


    def finalize_completed_fuel_sales(self):
        """Tender any pending fuel transaction on the POS with cash.

        Some scenarios may leave the POS in an unready state because of pending
        fuel transactions stacked on pumps. This step tenders prepay refunds and
        drive-off post-pays.
        """
        pump_numbers = self.get_pump_numbers()
        for pump_number in pump_numbers:
            sales = self.pos.get_count_of_stacked_sales_on_pump(pump_number)
            if sales:
                # Select pump with one or more stacked sales.
                self.pos.select_pump(pump_number)
            for _ in range(sales):
                # Observe item count when adding the fuel transaction.
                original = self.pos.get_transaction_item_count()
                self.pos.press_button_on_frame(POSFrame.MAIN, POSButton.PAY_FIRST)
                self.pos.wait_for_transaction_item_count_increase(original)

                # If pressing the "Pay 1" button did not end a transaction, then it
                # must be a drive-off post-pay because prepay refunds are automatically
                # tendered in cash.
                if self.pos.get_current_transaction() is not None:
                    # Tender the drive-off post-pay transaction.
                    try:
                        self.pos.tender_transaction("cash", "cash-tender")
                    except AssertionError:
                        # If the tender attempt fails, attempt to process loyalty
                        # and continue with tender step.
                        utility.wait_for_frame_name(self.pos, "tender-dynamic-get-a", 30)
                        menu_frame = utility.wait_for_pos_button_presence(self.pos, "exact-dollar")
                        self.pos.control.press_button(menu_frame.instance_id, "exact-dollar")
                        self.pos.wait_for_frame_open(POSFrame.WAIT_CREDIT_PROCESSING)

                # Minimize race conditions for subsequent steps by waiting for
                # the transaction to end here.
                self.pos.control.wait_for_transaction_end()


    def verify_scroll_previous_printed_receipt_contains(self, table: Table):
        """Verify that the previous printed receipt contains a given Gherkin table.

        This step should be preceeded by a waiting step when used in a PAP
        scenario in order to ensure the transaction is finalized on POS.
        The wait time should be 10 seconds.

        This step must be accompanied by a table, as below. Note the actual
        receipt lines must be delimited by asterisks (*), as whitespace is
        sensitive.

        .. code-block:: text
            Then the previous printed receipt contains:
            | line | content                                 |
            | 11   | *Prepay Fuel Sale                     * |
            | 12   | *Pump # 1 Regular                     * |
            | 13   | *10.588 Gallons @ $1.889/Gal    $20.00* |

        :param table: Behave table.
        :raise ValueError: If the Gherkin table is not formatted correctly.
        """
        utility.require_table_headings(table, "line_number", "line")

        # TODO: Do further investigation of best way to wait for transaction to be
        #  fully completed and replace below line with wait_until_transaction_completed
        #  Wait until transaction reaches POS (for PAP transactions)
        time.sleep(3)  # waiting for transaction/prepay finalization
        self.pos.press_button_on_frame(POSFrame.RECEIPT, POSButton.OTHER_FUNCTIONS)
        self.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.SCROLL_PREVIOUS)
        utility.wait_for_frame_name(self.pos, "other-pap-history")

        frame = self.pos.control.get_menu_frame()
        initial_count = self.pos.get_receipt_count()
        self.pos.control.press_button(frame.instance_id, POSButton.PRINT_RECEIPT.value)
        self.pos.control.press_button(frame.instance_id, POSButton.DONE.value)
        assert self.pos.wait_for_receipt_count_increase(initial_count), 'Receipt was not returned.'

        receipt = self.pos.get_latest_printed_receipt()
        receipt = receipt.split('<br/>')
        actual = []

        for row in table:
            actual.append(receipt[int(row["line_number"]) - 1])

        assert compare_receipts(table, actual, html=False), 'Receipts do not match'


    def verify_printed_EOS_report_contains(self, table: Table):
        """Verify that the previous printed end of shift report contains
        lines from a given Gherkin table.

        This step must be accompanied by a table, as below. Note the actual
        report lines must be delimited by asterisks (*), as whitespace is
        sensitive.

        .. code-block:: text
            Then the previous printed receipt contains:
            | line | content                                 |
            | 11   | *Prepay Fuel Sale                     * |
            | 12   | *Pump # 1 Regular                     * |
            | 13   | *10.588 Gallons @ $1.889/Gal    $20.00* |

        :param table: Behave table.
        :raise ValueError: If the Gherkin table is not formatted correctly.
        """
        utility.require_table_headings(table, "line_number", "line")

        report = self.pos.get_latest_printed_receipt()
        report = report.split('<br/>')
        actual = []

        for row in table:
            actual.append(report[int(row["line_number"]) - 1])

        assert compare_receipts(table, actual, html=False), 'EOS reports do not match'


    def get_welcome_prompts(self):
        """Get all possible welcome prompt names for idle pump.

        :return: list of welcome prompt names
        :rtype: list of strings
        """

        """
        provisional Currently,
        there is no product level API to retrieve this information.
        """
        prompt_list = [
            "ASKLOYALTY",
            "ASKLOYALTYMOP",
            "ASKLOYALTYMOPPOSTPAY",
            "ASKLOYALTYPOSTPAYONLY",
            "CASHPAPGREETING",
            "CLOSED",
            "FULLSERVEGREETING",
            "GREETING",
            "ICRGREETING",
            "POSTPAYGREETING",
            "POSTPAYICRGREETING",
            "PREPAYGREETING",
            "PREPAYICRGREETING",
            "STATIONCLOSED",
            "Choose MOP Payaso",
            "SWIPE AIR MILES  NO TO CONTINUE",
        ]
        return prompt_list


    def apply_config_update_on_POS(self):
        """Apply RCM configuration update to the POS node.

        This function has an internal timeout of about 45 seconds
        to wait for the POS to restart.
        """
        duration = time.time()
        def get_buttons():
            return self.smtaskman.get_frame_content().get('Buttons')

        def button_found(buttons):
            for button in buttons:
                if button.get('Name') == 'alert-configuration-update-required':
                    return True
            return False

        buttons, done = utility.wait_until(get_buttons, button_found, attempts=5, delay=1.0)
        logger.info(f"Upgrade button was found: {done}")

        if done:
            self.smtaskman.press_button('alert-configuration-update-required')
            utility.wait_until_pos_offline(self.pos)
            is_available = self.pos._wait_for_availability(360)
            logger.info(f"POS API is available for use: {is_available}.")
            utility.wait_for_any_pos_menu_frame(self.pos, 60)
        logger.info(f"POS node was updated in: {time.time()-duration} seconds.")


    def apply_config_update_on_FC(self):
        """Apply RCM configuration update to the fuel node.

        This function has an internal timeout of 4 minutes
        to wait for the fuel node to restart.
        """
        duration = time.time()
        self.fuel.radstart_restart()
        self.reconnect_simpumps()
        # Wait for welcome prompt
        pump_numbers = self.get_pump_numbers()
        for pump in pump_numbers:
            # Wait up to 6 minutes since there is a chance that the fuel node restarts.
            self.verify_pump_displayed_welcome_prompt(pump, timeout_seconds=360)
        logger.info(f"JAG node was updated in: {time.time()-duration} seconds.")


    def set_POS_to_ready_to_sell_state(self):
        """Prepare POS node for sale and verify readiness
        """
        # Operator id 70000000003 is Cashier
        if self.pos.is_someone_signed_in() and not self.pos.is_signed_in(operator_id=70000000003):
            self.pos.ensure_ready_to_start_shift(operator_pin=self.config["nodes"]["rcm"]["rcm_users"]["cashier"])
        self.pos.ensure_ready_to_sell(operator_pin=self.config["nodes"]["rcm"]["rcm_users"]["cashier"])


    def set_SC_to_ready_to_sell_state(self):
        """Prepare SC node for sale and verify readiness
        """
        self.sc.utilities.delete_summary_totals()
        self.sc.utilities.delete_transaction_history()


    # Currently KPS is never restarted but config updates should be possible and later implemented.
    def set_KPS_to_ready_to_sell_state(self):
        """Prepare KPS node for sale and verify readiness
        """
        if not self.kps.get_kps_status():
            raise ProductError(f"KPS is not currently online.")


    def accept_new_fuel_price(self):
        """ Accept new fuel prices if there is button present for it
        """
        buttons = self.smtaskman.get_frame_content()['Buttons']
        for button in buttons:
            if button['Name'] == 'alert-136':
                self.smtaskman.press_button('alert-136')
                self.pos.wait_for_frame_open(POSFrame.ASK_APPROVE_PRICE_CHANGE)
                self.pos.press_button_on_frame(POSFrame.ASK_APPROVE_PRICE_CHANGE, POSButton.YES)


    def set_system_to_ready_to_sell_state(self):
        """Prepare nodes for sale and verify readiness

        This function executes an RCM download and propagates node updates.
        """
        logger.info("Start setting system to ready to sell state.")
        duration = time.time()

        pump_numbers = self.get_pump_numbers()
        self.reconnect_simpumps()

        for pump_number in pump_numbers:
            self.prepare_pump_for_transactions(pump_number)
            
        # TODO: Optimize with multithreading
        if self.eps.registry_handler.is_reboot_needed():
            logger.info("Restarting Epsilon.")
            self.eps.restart()

        if self.sigma.registry_handler.is_reboot_needed():
            logger.info("Restarting Sigma.")
            self.sigma.restart()

        if self.rcm.get_update_needed_value():
            self.download_rcm()

            POS_thread = PropagatingThread(target=self.apply_config_update_on_POS)
            FC_thread = PropagatingThread(target=self.apply_config_update_on_FC)
            logger.info("Start applying config update on POS.")
            POS_thread.start()
            logger.info("Start applying config update on Fuel Controller.")
            FC_thread.start()
            POS_thread.join()
            logger.info("Updating on POS has finished.")
            FC_thread.join()
            logger.info("Updating on Fuel Controller has finished.")

        logger.info(f"POS and Fuel controller updates finished in: {time.time()-duration} seconds.")

        self.accept_new_fuel_price()
        self.set_POS_to_ready_to_sell_state()
        self.finalize_completed_fuel_sales()
        self.ready_available_pumps()
        self.set_SC_to_ready_to_sell_state()
        # self.set_KPS_to_ready_to_sell_state()

        for pump_number in pump_numbers:
            utility.wait_for_pump_state_on_pos(self.pos, pump_number, "Idle", 30)

        logger.info(f"The set_system_to_ready_to_sell_state function has finished in: {time.time()-duration} seconds.")


    def download_rcm(self, update_type: UpdateTypes = UpdateTypes.CONFIG):
        """ Initiates download from RCM and waits for successful end.

        :param update_type: Update type of the RCM download.
        """
        self.rcm.create_download(update_type)
        self.sc.config.initiate_download_from_host()
        if not self.rcm.wait_for_update_finish(update_type):
            raise ProductError("RCM was not correctly downloaded, please see the logs.")


    def link_site_server_to_RCM(self, site_id: str):
        """ Links site server to RCM and updates files on SC.

        :param site_id: ID of the site, we want to link
        """
        self.rcm.link_RCM(site_id)
        messageUrl, fileUrl = self.rcm.get_service_endpoints()
        self.sc.config.patch_host_parameters('RCM', site_id=site_id, get_message_url=messageUrl, get_file_url=fileUrl)


    def get_last_epsilon_transaction_number(self) -> int:
        previous_transaction = self.pos.get_previous_transaction()
        assert previous_transaction is not None, "Previous transaction is None"
        assert len(previous_transaction.epsilon_tran_numbers) == 1, 'There isn\'t exactly one epsilon tender in last transaction'
        
        return previous_transaction.epsilon_tran_numbers[0]
