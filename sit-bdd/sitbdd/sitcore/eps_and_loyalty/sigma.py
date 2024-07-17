import bs4
import time

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.eps_and_loyalty.service import Service

logger = get_sit_logger()

# methods are tagged and sorted by where in the code they remain used
# tags: "used", "deprecated", "commented" with this respective priority
@wrap_all_methods_with_log_trace
class Sigma(Service):
    """
    This class handles functions for the loyalty controller, 
    interacts directly with Sigma by using PMI,
    and is meant as container for helper, Sigma related functions
    and simplify initialisation of the Sigma service.
    """

    def __init__(
        self, 
        pmi_hostname: str,
        pmi_port: int,
    ):
        super().__init__(
            pmi_hostname = pmi_hostname,
            pmi_port = pmi_port,
            name = "Sigma",
            registry_path = "Software\\RadiantSystems\\Sigma\\",
            service_name = "SigmaStartup",
            networks = ["RLM"],
        )

    # usage in code: used
    def get_info(self) -> None:
        """
        Retrieve info about the service/controller including its name and online/offline status
        and names and online/offline statuses of the underlying Host Simulator services.

        :return: A dict conataining the following key - value pairs:
            "ControllerName" - Name of the controller as str
            "ControllerOnline" - Whether controller is online as bool
            "Hosts" - list of dicts containing the following key - value pairs:
                "Name" - Name of the underlying service as str
                "Online" - Whether the underlying service is online as bool
        :rtype: dict
        """
        data = {
            "ControllerOnline": False,
            "ControllerName": "",
            "Hosts": None,
        }

        if self.get_registry_value("", "Version"):
            """
            Basically, if the version reg is set,
            then Sigma is installed since it's looking into the Sigma reg path
            """
            data["ControllerName"] = self.name
            data["ControllerOnline"] = self.is_online()

        if (
            self.get_registry_value_host_simulator("", "DLLName")
            == "SigmaHostSimulatorRLM.dll"
        ):
            # Similar to Sigma, already looking into Host Sim RLM path
            final_hosts_list = []
            for network in self.networks:
                final_hosts_list.append({"Name": network, "Online": self.is_host_online()})
            data["Hosts"] = final_hosts_list

        return {"Info": data}

    # usage in code: used
    def post_transaction(self, business_date: str) -> None:
        """
        Sends a mock loyalty transaction into Sigma.

        :param str business_date: Current business date,
            formatted as "%Y%m%d" e.g. "20180205".
        :return: None
        """
        transaction_id = self.post_loyalty_decode()
        self.post_loyalty_capture(transaction_id, business_date)

    # usage in code: used
    def post_loyalty_decode(self) -> None:
        """
        Sends a loyalty decode to Sigma

        :return: Transaction Id of the loyalty decode transaction.
            Will raise RuntimeError if something goes wrong.
        :rtype: str
        """
        requested_operation = "LoyaltyDecode"
        pmi_header = self._pmi.build_pmi_request_message_header(
            operation=requested_operation
        )
        message_soup = bs4.BeautifulSoup(pmi_header, "xml")

        card_info_tag = message_soup.new_tag(
            "CardInfo",
            EntryMethod="ST",
            RawCardData="%605079441600000408?;605079441600000408?;",
        )
        message_soup.Message.append(card_info_tag)

        # display_items_tag = message_soup.new_tag("DisplayItems")
        # message_soup.Message.append(display_items_tag)
        #
        # item_tag = message_soup.new_tag("Item",
        #                                 Description="BiLo",
        #                                 ExternalId="1")
        # message_soup.DisplayItems.append(item_tag)
        #
        # tran_amount_tag = message_soup.new_tag("TranAmount",
        #                                        AmountDue="0.00",
        #                                        TotalTax="0.00")
        # message_soup.Message.append(tran_amount_tag)

        result = self._pmi._communicate(str(message_soup.Message))
        parsed_response = self._pmi.parse_response(result, requested_operation, True)
        if parsed_response:
            response_soup = bs4.BeautifulSoup(parsed_response, "xml")
            if (
                response_soup.Message.TranStatus[
                    self._pmi.TRAN_STATUS_ATT_IS_APPROVED
                ].lower()
                == "yes"
            ):
                return str(
                    response_soup.Message[self._pmi.MESSAGE_ATT_TRANSACTION_NUMBER]
                )

        raise RuntimeError("LoyaltyManager - loyalty decode failed")

    # usage in code: used
    def post_loyalty_capture(self, transaction_id: str, business_date: str) -> None:
        """
        Sends a loyalty capture to sigma.
        Must have the same transaction_id as a previously sent loyalty decode.
        Includes 1 "Coffee" item in the capture.

        :param str transaction_id: Transaction Id to capture
        :param str business_date: Current business date,
            formatted as "%Y%m%d" e.g. "20180205".
        :return: None
            Will raise RuntimeError if something goes wrong.
        """
        requested_operation = "LoyaltyCapture"
        pmi_header = self._pmi.build_pmi_request_message_header(
            operation=requested_operation
        )
        message_soup = bs4.BeautifulSoup(pmi_header, "xml")
        message_soup.Message[self._pmi.MESSAGE_ATT_TRANSACTION_NUMBER] = transaction_id

        line_items_tag = message_soup.new_tag("LineItems")
        message_soup.Message.append(line_items_tag)

        item_tag = message_soup.new_tag(
            "Item",
            Description="Coffee",
            DiscCnt="0",
            ExAmt="1.2900",
            GenProd="2015",
            ItemId="2",
            LineNumber="2",
            UAmt="1.2900",
            Qty="1.0000",
        )

        message_soup.LineItems.append(item_tag)

        pos_data_tag = message_soup.new_tag(
            "POSData",
            BusinessDay=business_date,
            DateTime=time.strftime("%Y/%m/%d %H:%M:%S"),
            OperatorName="EVAgent",
        )

        message_soup.Message.append(pos_data_tag)

        result = self._pmi._communicate(str(message_soup.Message))
        parsed_response = self._pmi.parse_response(result, requested_operation, True)
        if parsed_response:
            response_soup = bs4.BeautifulSoup(parsed_response, "xml")
            if (
                response_soup.Message.TranStatus[
                    self._pmi.TRAN_STATUS_ATT_IS_APPROVED
                ].lower()
                == "yes"
            ):
                return

        raise RuntimeError("LoyaltyManager - loyalty capture failed")
 