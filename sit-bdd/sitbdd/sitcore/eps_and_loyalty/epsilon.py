import bs4
import time
from typing import Union, Any

from sitbdd.sitcore.eps_and_loyalty.eps_product_export import EPSProductExport
from sitbdd.sitcore.bdd_utils import utility

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.eps_and_loyalty.service import Service
from sitbdd.sitcore.eps_and_loyalty.conexxus_manager import ConexxusManager

logger = get_sit_logger()

# methods are tagged and sorted by where in the code they remain used
# tags: "used", "deprecated", "commented" with this respective priority
@wrap_all_methods_with_log_trace
class Epsilon(Service):
    """
    This class handles HTTP requests to the EPS manager,
    interacts directly with Epsilon by using PMI,
    and is meant as container for helper, Epsilon related functions
    and simplify initialization of the Epsilon service.
    """

    def __init__(
        self, 
        pmi_hostname: str,
        pmi_port: int,
    ):
        super().__init__(
            pmi_hostname = pmi_hostname,
            pmi_port = pmi_port,
            name = "Epsilon",
            registry_path = "Software\\RadiantSystems\\ElectronicPayments\\",
            service_name = "EPSStartup",
            networks = ["ConcordATL", "CONMOB"]
        )
        self.conexxus = ConexxusManager()

    # usage in code: used
    def prompt_for_access_code(self, should_prompt: bool) -> None:
        """
        Sets up the configuration to prompt for
        access code during Mobile Pay transaction

        :param bool should_prompt: bool of whether it should prompt for access code
        :return: None
        """
        self.set_registry_value_host_simulator(
            "MerchantId\\100_MobilePay",
            "PromptAccessCode",
            "YES" if should_prompt else "NO"
        )

    # usage in code: used
    def reserve_mobile_pay(self, pump: int) -> None:
        """
        Handles the reserve pump request to start mobile pay transaction.
        Sets and deletes the relevant registry keys on Host Simulator.

        :param int pump: Number of the pump for which to reserve mobile pay
        :return: None
        """
        self.delete_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReservePumpTranNumber" + str(pump))
        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReservePumpNumber", str(pump))
        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReservePumpTrigger", "YES")

    # usage in code: used
    def release_mobile_pay(self, pump: int) -> None:
        """
        Handle the release pump request to release mobile pay transaction.
        Sets the relevant registry keys on Host Simulator.

        :param int pump: Number of the pump for which to release mobile pay
        :return: None
        """
        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReservePumpNumber", str(pump))
        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReleasePumpTrigger", "YES")

    # usage in code: used
    def export_available_products(self, timeout: int = 60) -> EPSProductExport:
        """
        Request the available product export to be generated.

        :param int timeout: Seconds to wait for request to be finished
        :return: EPSProductExport object generated based on the 
            transaction number of new product export transaction
        :rtype: EPSProductExport
        """

        def get_export_tran_maybe():
            try:
                return self.get_product_export_t_number()
            except FileNotFoundError:
                return None

        old_export_tran = get_export_tran_maybe()
        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "GetProductInfoSeconds", "-1")

        tran_number, success = utility.wait_until(
            get_export_tran_maybe,
            lambda new: new is not None and old_export_tran != new,
            timeout,
            1
        )

        if success:
            return EPSProductExport(tran_number, self)
        else:
            message = "Available products were not exported within {} seconds"
            raise TimeoutError(message.format(timeout))

    # usage in code: used
    def get_product_export_t_number(self) -> int:
        """
        Retrieve the transaction number for the available product export.

        :return: Last Epsilon transaction number
        :rtype: int
        """
        return int(
            self.get_registry_value_host_simulator("MerchantId\\100_MobilePay", "AvailableProductsTranNumber")
        )

    # usage in code: used
    def get_mobile_pay_reserve_pump_transaction_status(self, pump: int, retry_sleep: float = 1) -> dict:
        """
        Find the mobile pay reserve pump transaction for the given pump_number
        and see if it was approved by the fuel controller.
        If it wasn't approved then also retrieve the reason for decline.
        
        :param int pump_number: Pump number to check mobile pay transaction
        :param float retry_sleep: Amount of time in seconds to sleep between retries
        :return: dict containing the following key - value pairs:
            "MobilePayReservePumpStatus" - dict containing the following key - value pairs:
                "Approved" - Whether the transaction has been approved as bool
            Can raise RuntimeError or FileNotFoundError if something goes wrong
        :rtype: dict
        """
        retry_count = 5
        while retry_count:
            try:
                reserve_pump_tran_number = self.get_registry_value_host_simulator(
                    "MerchantId\\100_MobilePay",
                    "ReservePumpTranNumber" + str(pump)
                )
                break
            except FileNotFoundError as e:
                """
                The HostSimulator deletes the registry setting after each transaction
                and does not populate it if it was declined by Fuel Controller.
                It is also possible that registry is not
                yet created so we will retry 3 times.
                """
                if e.errno == 2:  # Registry key not found error
                    retry_count -= 1
                    time.sleep(retry_sleep)
                else:
                    raise e

        if retry_count == 0:
            return False

        if reserve_pump_tran_number is not None:
            reserve_pump_tran_number = int(reserve_pump_tran_number)
        else:
            raise RuntimeError(
                "EPSManager - could not retrieve ReservePumpTranNumber"
                + str(pump)
                + " for MobilePay"
            )

        result = self.get_nvps(reserve_pump_tran_number, ["bmISAPPROVED"])
        
        data = {
            "Approved": False
        }
        if result is not None:
            is_approved = result.get("bmISAPPROVED")
            if is_approved == "Y":
                data["Approved"] = True

        return {
            "MobilePayReservePumpStatus": data
        }
    
    # usage in code: used
    def get_product_export(self, export_tran_num: int) -> dict:
        """
        Attempt to retrieve the available products and the line items from the product export.

        :param int export_tran_num: EPS transaction number of the Product Export
        :return: dict containing the following key - value pairs:
            "ProductExport" - a dict containing the following key - value pairs:
                "AvailableProducts" - String of the line items xml or None
                "LineItems" - String of the available products or None
        :rtype: dict
        """
        if export_tran_num is None:
            export_tran_num = self.get_product_export_t_number()

        results = self.get_nvps(export_tran_num, ["soAVAILPRODUCTS1", "noPOTLINEITEMTAGLIST"])

        available_products = None
        line_items = None
        if results is not None:
            if "soAVAILPRODUCTS1" in results:
                available_products = results["soAVAILPRODUCTS1"]
            if "noPOTLINEITEMTAGLIST" in results and results["noPOTLINEITEMTAGLIST"] is not None:
                export_line_items_xml = "<LineItems>"
                """
                noPOTLINEITEMTAGLIST should equal a comma separated list of
                numbers ending in a comma, like '1,2,3,'
                """
                line_item_tags = results["noPOTLINEITEMTAGLIST"].split(",")
                pot_line_item_nvps = []
                for line_item_tag in line_item_tags:
                    if line_item_tag != "":
                        pot_line_item_nvp = "toPOTLINEITEM" + line_item_tag
                        pot_line_item_nvps.append(pot_line_item_nvp)

                pot_line_items_result = self.get_nvps(
                    export_tran_num, pot_line_item_nvps, remove_special_characters=True
                )

                if pot_line_items_result is not None:
                    for pot_line_item_nvp in pot_line_item_nvps:
                        if pot_line_items_result.get(pot_line_item_nvp) is not None:
                            # Each line item NVP is composed of the following data:
                            # GenProd=####UAmt=#.####Description=CCCCCCCCCC
                            if len(pot_line_items_result[pot_line_item_nvp]) < 36:
                                raise ValueError(
                                    "The line item's value "
                                    "was too small to be parsed properly. "
                                    "pot_line_items_result[%s] = %s"
                                    % (
                                        pot_line_item_nvp,
                                        pot_line_items_result[pot_line_item_nvp],
                                    )
                                )
                            gen_prod = pot_line_items_result[pot_line_item_nvp][8:12]
                            unit_amount = pot_line_items_result[pot_line_item_nvp][17:23]
                            description = pot_line_items_result[pot_line_item_nvp][35:]
                            export_line_items_xml += (
                                '<Item Name="%s" CreditCode="%s" Price="%s"/>'
                                % (description, gen_prod, unit_amount)
                            )

                export_line_items_xml += "</LineItems>"
                line_items = export_line_items_xml

        return {
            "ProductExport": {
                "AvailableProducts": available_products,
                "LineItems": line_items,
            }
        }

    # usage in code: deprecated
    def get_transaction_status(self, transaction_number: int) -> dict:
        """
        Retreieve the transaction status of a given transaction.

        :param int transaction_number: Transaction number of the transaction to retrieve the status of
        :return: a dict containing the following key - value pairs:
            "TransactionStatus" - a dict containing the following key - value pairs:
                "Approved" - whether the transaction has been approved as bool
                "Captured" - whether the transaction is captured as bool
                "Complete" - whether the transaction is complete as bool
                "MobilePay_PAP": whether the transaction is a Mobile Pay PAP transaction as bool
                "Entry_Method": entry method of the transaction as str or None
                    translated from EPS' abbreviation to colloquial term.
                    Can be "manual", "swipe", "mobile wallet", or "chip".
        :rtype: dict
        """
        # Retrieve relevant NVPs
        nvp_list = [
            "soAPPROVALMETHOD", "bmISAPPROVED", # Approved
            "smTRANTYPE",                       # Captured
            "amPOSSTATE",                       # Complete
            "IcarusMobileTran", "soPOSTYPE",    # MobilePay_PAP
            "smENTRYMETHOD",                    # Entry_Method
        ]
        result_list = self.get_nvps(transaction_number, nvp_list)

        # Set default values
        data = {
            "Approved": False,
            "Captured": False,
            "Complete": False,
            "MobilePay_PAP": False,
            "Entry_Method": None,
        }

        # Parse results
        if "soAPPROVALMETHOD" in result_list and "bmISAPPROVED" in result_list:
            data["Approved"] = result_list["soAPPROVALMETHOD"] and result_list["bmISAPPROVED"] == "Y"
        if "smTRANTYPE" in result_list:
            data["Captured"] = result_list["smTRANTYPE"] == "CAPTURE"
        if "amPOSSTATE" in result_list:
            data["Complete"] = result_list["amPOSSTATE"] == "COMPLETE"
        if "IcarusMobileTran" in result_list and "soPOSTYPE" in result_list:
            data["MobilePay_PAP"] = result_list["IcarusMobileTran"] == "Y" and result_list["soPOSTYPE"] == "MOBILE"
        if "smENTRYMETHOD" in result_list:
            method = result_list["smENTRYMETHOD"]
            methods = {"MB": "manual", "ST": "swipe", "SW": "mobile wallet", "CC": "chip"}
            if method not in methods:
                message = "Unrecognized credit entry method '{}'"
                raise ValueError(message.format(method))
            data["Entry_Method"] = methods[method]

        return {"TransactionStatus": data}

    # usage in code: deprecated
    def get_receipt(self, transaction_number: int) -> dict:
        """
        Attempt to retrieve the given transaction's receipt from Epsilon.
        first, see if this is a Mobile Pay transaction and,
        if so, get the actual receipt transaction number.
        Poll given transaction for receipt line count nvp for up to 120 seconds.
        This is to work around the fact that a Mobile Pay transactions'
        receipt is held in a different transaction which takes extra time to be filled.

        :param int transaction_number: ID of transaction you want to retrieve NVPs for.
        :return: dict containing the following key - value pairs:
            "ReceiptText" - str of receipt text or None
        :rtype: dict
        """
        data = {"ReceiptText": None}
        result = self.get_nvps(transaction_number, ["EVTPOSCompleteTran"])

        if result is not None and result.get("EVTPOSCompleteTran") is not None:
            receipt_transaction_number = int(result.get("EVTPOSCompleteTran"))
            result, success = utility.wait_until(
                lambda: self.get_nvps(transaction_number, ["noPOSRECEIPTCOUNT"]),
                lambda nvps: nvps is not None and not nvps == {},
                240,
                0.5,
                timeout=120
            )
            if success:
                receipt_line_count_nvp = result
            else:
                raise TimeoutError(
                    "Timed out waiting for EPS Mobile Pay transaction to have "
                    "receipt information"
                )
        else:
            receipt_transaction_number = transaction_number
            receipt_line_count_nvp = self.get_nvps(
                receipt_transaction_number, ["noPOSRECEIPTCOUNT"]
            )

        if (
            receipt_line_count_nvp is not None
            and receipt_line_count_nvp.get("noPOSRECEIPTCOUNT") is not None
        ):
            receipt_line_count = int(receipt_line_count_nvp.get("noPOSRECEIPTCOUNT"))
        else:
            logger.error(
                "Could not retrieve receipt line count nvp for transaction %d. "
                "Does the transaction exist?" % transaction_number
            )
            return data

        receipt_text = ""

        receipt_line_nvp_list = []

        for receipt_line in range(1, receipt_line_count + 1):
            receipt_line_nvp_list.append("soPOSRECEIPT" + str(receipt_line))

        receipt_lines = self.get_nvps(receipt_transaction_number, receipt_line_nvp_list)

        if receipt_lines is not None and len(receipt_lines) > 0:
            receipt_line_nvp_index = 1

            for receipt_line_nvp in receipt_line_nvp_list:
                receipt_text += receipt_lines.get(receipt_line_nvp)

                if receipt_line_nvp_index < len(receipt_line_nvp_list):
                    receipt_text += "\n"

                receipt_line_nvp_index += 1

            data["ReceiptText"] = receipt_text
            return data
        else:
            logger.error(
                "Receipt lines for transaction %d is either None or less than 1."
                % transaction_number
            )
            return data

    # usage in code: commented
    def authorize_mobile_pay(
        self,
        pump: int,
        loyalty_data: Any = None,
        loyalty_entry_method: Union[str, None] = None
    ) -> None:
        """
        Handle the authorize pump request to authorize mobile pay transaction
        
        :param int pump: Number of the pump to authorize mobile pay for
        :param Any loyalty_data: relevant loyalty data
        :param str/None loyalty_entry_method: entry method of loyalty in colloquial terms
        :return: None
        """
        methods = {"barcode": "BB", "manual": "MB", "swipe": "ST"}
        if loyalty_entry_method not in methods:
            message = "Unrecognized loyalty entry method '{}'"
            raise ValueError(message.format(loyalty_entry_method))

        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "ReservePumpNumber", str(pump))

        if loyalty_data and loyalty_entry_method:
            self.set_registry_value_host_simulator(
                "MerchantId\\100_MobilePay",
                "LoyaltyAuthCardInfo",
                'LoyaltyEntryMethod="{}" LoyaltyCardNumber="{}"'.format(
                    methods[loyalty_entry_method],
                    loyalty_data,
                ),
            )
            self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "SendLoyaltyOnAuth", "YES")
        elif loyalty_data or loyalty_entry_method:
            raise ValueError("Must specify both loyalty data and method")
        else:
            self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "SendLoyaltyOnAuth", "NO")

        self.set_registry_value_host_simulator("MerchantId\\100_MobilePay", "AuthTrigger", "YES")
