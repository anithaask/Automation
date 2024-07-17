__all__ = ["ConexxusManager"]

import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace
from sitbdd.sitcore.eps_and_loyalty.service import Service

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class ConexxusManager(Service):
    """
    This class handles work with CONMOB network.
    """

    def __init__(self):
        super().__init__(
            pmi_hostname = "127.0.0.1",
            pmi_port = 7029,
            name = "Epsilon",
            registry_path = "Software\\RadiantSystems\\ElectronicPayments\\",
            service_name = "EPSStartup",
            networks = ["CONMOB"]
        )
        
        self.selected_network = "CONMOB"
        self.merchantId = "0305-0767"

        ET.register_namespace('xmlns', 'http://www.conexxus.org/schema/naxml/mobile/v02')
        ET.register_namespace('xmlns:cc=', 'http://www.naxml.org/POSBO/Vocabulary/2003-10-16')
        ET.register_namespace('xmlns:lc=', 'http://www.conexxus.org/schema/common')
        self.nsmap = {'xmlns':'http://www.conexxus.org/schema/naxml/mobile/v02','xmlns:cc': 'http://www.naxml.org/POSBO/Vocabulary/2003-10-16','xmlns:lc':'http://www.conexxus.org/schema/common'}
    
        self.journal_file_name = "JournalCONMOB.log"

    def get_journal_path(self):
        return self.get_registry_value("", "LogPath")

    def get_message(self, tran_number: int, message_type: str): 
        send_element = "<Send>"
        file_path = self.get_journal_path() + "\\" + self.journal_file_name

        with open(file_path) as f:
            for line in f:
                if str(tran_number) in line:
                    if message_type in line:
                        message = line.split(send_element, 1)[1]
                        return ET.fromstring(message)


    def get_original_amount(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:OriginalAmount/xmlns:Amount", self.nsmap):
            return item.text
    
    def get_original_unitprice(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:OriginalAmount/xmlns:UnitPrice", self.nsmap):
            return item.text

    def get_adjusted_amount(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:AdjustedAmount/xmlns:Amount", self.nsmap):
            return item.text
    
    def get_adjusted_unitprice(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:AdjustedAmount/xmlns:UnitPrice", self.nsmap):
            return item.text

    def get_quantity(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:Quantity", self.nsmap):
            return item.text

    def get_finalamount(self, message: ET.Element):
        return message.find(".//xmlns:PaymentInfo", self.nsmap).attrib["finalAmount"]

    def get_rebatelabel(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:PriceAdjustment/xmlns:RebateLabel", self.nsmap):
            return item.text

    def get_priceAdjustment_amount(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:PriceAdjustment/xmlns:Amount", self.nsmap):
            return item.text
    
    def get_priceAdjustment_unitprice(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:PriceAdjustment/xmlns:UnitPrice", self.nsmap):
            return item.text

    def get_priceAdjustment_quantity(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:PriceAdjustment/xmlns:Quantity", self.nsmap):
            return item.text

    def get_original_amount(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:OriginalAmount/xmlns:Amount", self.nsmap):
            return item.text
    
    def has_saleitem(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']", self.nsmap):
            return True
        return False
    
    def get_sale_item_id(self, message: ET.Element, saleitem_description: str):
        item = message.find(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']", self.nsmap)
        return item.attrib["itemID"]
            
    def get_postpay_discount_for_item(self, message: ET.Element, saleitem_description: str):
        fuel_item_id = self.get_sale_item_id(message, saleitem_description)
        assert fuel_item_id is not None, f"Cannot find sale item {saleitem_description}"
        
        for item in message.findall(".//xmlns:SaleItem/[xmlns:LinkedItemID='" + fuel_item_id + "']", self.nsmap):
            return item
        
    def get_discount_sale_item(self, message: ET.Element):
        for item in message.findall(".//xmlns:SaleItem[@reverseSale='NegativeAmount']/.", self.nsmap):
            if item.find(".//xmlns:LinkedItemID", self.nsmap) is None:
                return item
            
    def get_item_original_amount(self, item: ET.Element):
        for value in item.find(".//xmlns:OriginalAmount/[xmlns:Amount]", self.nsmap):
            return value.text
        
    def get_item_original_unit_price(self, item: ET.Element):
        for value in item.find(".//xmlns:OriginalAmount/[xmlns:UnitPrice]", self.nsmap):
            return value.text
    
    def get_item_adjusted_amount(self, item: ET.Element):
        for value in item.find(".//xmlns:AdjustedAmount/[xmlns:Amount]", self.nsmap):
            return value.text
        
    def get_item_adjusted_unit_price(self, item: ET.Element):
        for value in item.find(".//xmlns:AdjustedAmount/[xmlns:UnitPrice]", self.nsmap):
            return value.text
        
    def get_item_product_code(self, item: ET.Element):
        return item.find(".//xmlns:ProductCode", self.nsmap).text

    def get_item_item_id(self, item:ET.Element):
        print(item)
        return item.attrib["itemID"]

    def get_carWashcode(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:WashCodeDetails", self.nsmap):
            return item.attrib["carWashCode"]

    def get_carWashExpirationDate(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:WashCodeDetails", self.nsmap):
            return item.attrib["washExpirationDate"]
        
    def has_carwash_details(self, message: ET.Element, saleitem_description: str):
        for item in message.findall(".//xmlns:SaleItem/[xmlns:Description='" + saleitem_description + "']/xmlns:WashCodeDetails", self.nsmap):
            if item.attrib["carWashCode"] and item.attrib["washExpirationDate"]:
                return True
        return False

    def set_simulator_value(self, path: str, key: str, value: str) -> None:
        self.set_registry_value_host_simulator("\\" + path, key, value)

    def set_product_adjustment(self, product: str, key: str, value: str) -> None:
        self.set_registry_value_host_simulator("PriceAdjustments\\" + product + "\\Adjustment1", key, value)
    
    def create_product(self, product: str) -> None:
        self.create_registry_key_host_simulator("PriceAdjustments\\" + product, "Adjustment1")

    def enable_price_adjustments(self):
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "AddAuthPriceAdjustments", "YES")

    def enable_transaction_discount(self):
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "SendLoyaltyOnAuth", "YES")
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "AddTransactionDiscount", "YES")
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "AddAuthProducts", "YES")
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "LoyaltyAwardItemId", "")
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "LoyaltyAuthCardInfo", "")

    def reserve_pump(self, pump: int) -> None:
        """
        Handles the reserve pump request to start mobile pay transaction.
        Sets and deletes the relevant registry keys on Host Simulator.

        :param int pump: Number of the pump for which to reserve mobile pay
        :return: None
        """
        self.delete_registry_value_host_simulator("MerchantId\\" + self.merchantId, "ReservePumpTranNumber" + str(pump))
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "ReservePumpNumber", str(pump))
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "ReservePumpTrigger", "YES")

    def do_not_prompt_for_access_code(self) -> None:
        """
        """
        self.set_registry_value_host_simulator("MerchantId\\" + self.merchantId, "AccessCodeValidationType", "none")

    def clear_simulator_discounts_and_triggers(self) -> None:
        """
        Clears registries under ConMob host simulator that may interfere with running Epsilon related tests.
        Clears the pre-defined MPPA discounts and custom response codes. Any discount or timeout that is expected
        to be provided by host simulator needs to be specified in a Given step after calling this method.
        """
        self.delete_registry_key_host_simulator("", "PriceAdjustments")
        response_code_list = ['BatchClose', 'Capture', 'LoyaltyAuth', 'ProtStatus', 'ReceiptData', 'STACCapture']
        for key in response_code_list:
            self.delete_all_registry_values_host_simulator("ResponseCodes\\" + key)
