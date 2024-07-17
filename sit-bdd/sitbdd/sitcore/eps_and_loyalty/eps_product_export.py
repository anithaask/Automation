import bs4

from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger
from sitbdd.sitcore.bdd_utils.sit_logging import wrap_all_methods_with_log_trace

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class EPSProductExport:
    """This class holds information for an EPS available product export."""

    def __init__(self, transaction_number, manager):
        self._tran_number = transaction_number
        self._manager = manager

        self.line_items_soup = None
        self.available_products_soup = None

    def verify_icr_availability(self, icr, available):
        """Verify the availability of an ICR.

        :param int icr: The ICR number
        :param bool available: Whether ICR is expected to be available
        :return: Whether ICR matches the expected availability
        :rtype: bool
        """
        self._get_product_export()
        exported_icr = self._get_exported_icr(icr)
        expected_availability = "YES" if available else "NO"
        return exported_icr["Available"] == expected_availability

    def verify_items_in_export(self, fc_config_item_list):
        """
        Verifies that the given list of items appear in the product export
            for the desired pump.

        These are the main points of validation:
            1) All item GenProd codes must appear in the FC's configuration item list
            2) All product Ids in the ProductList must be in the acceptable range
                (1 - 1099)
            3) All unique product Ids must appear in the LineItems of the product export
            4) All item GenProd codes must appear in the ProductList
                of the product export

        The acceptable Credit Code range is: 1 to 1099
            Fuel items are from 1 to 999
            Car wash items are from 1000 to 1099

        :param list(evcore.pos.item.Item) fc_config_item_list: List of items
            from IcarusItems.xml to check the export for
        :return: None
        """
        self._get_product_export()

        products_list = self.available_products_soup.find_all("Product")
        product_codes_list = []
        item_gen_prod_list = []
        products_out_of_range = []
        items_not_in_fc_config = []

        items_list = self.line_items_soup.find_all("Item")
        items_dict = {}

        for item in items_list:
            item_gen_prod = int(item["CreditCode"])
            item_description = item["Name"]
            item_amount = float(item["Price"])
            items_dict[item_gen_prod] = {"Name": item_description, "Price": item_amount}
            item_gen_prod_list.append(item_gen_prod)

            found = False
            for config_item in fc_config_item_list:
                if 1 <= config_item.credit_code <= 1099:
                    if item_description in config_item.name:
                        if item_gen_prod != config_item.credit_code:
                            items_not_in_fc_config.append(item_gen_prod)
                        else:
                            found = True
                            break
            if found is False:
                items_not_in_fc_config.append(item_gen_prod)

        # Validation point 1
        if len(items_not_in_fc_config):
            raise ValueError(
                "Items in the item list of the the product export do not exist "
                "in the FC item config. Item list codes: %s, items not in FC config: %s"
                % (str(item_gen_prod_list), str(items_not_in_fc_config))
            )

        for product in products_list:
            product_id = int(product["Id"])
            if product_id not in product_codes_list:
                product_codes_list.append(product_id)
            if (
                product_id < 1 or product_id > 1099
            ) and product_id not in products_out_of_range:
                products_out_of_range.append(product_id)

        # Validation point 2
        if len(products_out_of_range):
            raise ValueError(
                "Item codes outside of the acceptable range were found "
                "in the product export. Product codes: %s, incorrect codes: %s"
                % (str(product_codes_list), str(products_out_of_range))
            )

        # Validation points 3 and 4
        if set(product_codes_list) != set(item_gen_prod_list):
            raise ValueError(
                "The list of unique products does not match the items in the items "
                "list of the product export. "
                "Product codes: %s, item list: %s"
                % (str(product_codes_list), str(item_gen_prod_list))
            )

    def _get_product_export(self):
        """
        Retrieve the product export and stores the results into member variables.

        :return: None
        """
        available_products, line_items = self._manager.get_product_export(
            int(self._tran_number)
        )
        self.available_products_soup = bs4.BeautifulSoup(available_products, "xml")
        self.line_items_soup = bs4.BeautifulSoup(line_items, "xml")

    def _get_exported_icr(self, icr):
        """
        Retrieve the product export
        and find and return a particular ICR of the Products section.

        :param int icr: ICR number to retrieve products list for
        :return: Soup of ICR's product export
        :rtype: bs4.BeautifulSoup
        """
        if self.available_products_soup is None:
            self._get_product_export()

        attributes = {"LocationId": "ICR{}".format(icr), "Type": "ICR"}
        exported_icr = self.available_products_soup.find("Products", attrs=attributes)

        if exported_icr is None:
            raise ValueError("ICR {} not found in export".format(icr))

        return exported_icr
