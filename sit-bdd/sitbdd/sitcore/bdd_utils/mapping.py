class SITMapping():
    """
    For internal purposes only. Helps with readability of tests in feature files.
    """
    def __init__(self):
        self._grades_mapping = self._set_grades_mapping()
        self._pos_frames_mapping = self._set_pos_frames_mapping()
        self._icr_keys_mapping = self._set_icr_keys_mapping()
        self._sale_items_mapping = self._set_sale_items_mapping()
        self._tiers_mapping = self._set_tiers_mapping()

    def get_grades_remap(self, value: str):
        return self._check_for_value("grades", value)

    def get_pos_frames_remap(self, value: str):
        return self._check_for_value("pos_frames", value)

    def get_icr_keys_remap(self, value: str):
        return self._check_for_value("icr_keys", value)

    def get_sale_items_remap(self, value: str):
        return self._check_for_value("sale_items", value)
    
    def get_tiers_remap(self, value: str):
        return self._check_for_value("tiers", value)

    def _check_for_value(self, mapping_type: str, value: str):
        mapping = None
        if mapping_type == "grades":
            mapping = self._grades_mapping
        elif mapping_type == "pos_frames":
            mapping = self._pos_frames_mapping
        elif mapping_type == "icr_keys":
            mapping = self._icr_keys_mapping
        elif mapping_type == "sale_items":
            mapping = self._sale_items_mapping
        elif mapping_type == "tiers":
            mapping = self._tiers_mapping
        else:
            raise NotImplementedError(f"Mapping for {mapping_type} does not exist.")
        ret_val = mapping.get(value)
        if ret_val is None:
            raise NotImplementedError(f"Value {value} is not in mapping for {mapping_type}.")
        return ret_val

    def _set_grades_mapping(self):
        return {"Regular": 1, "Midgrade": 2, "Premium": 3, "Diesel": 0}

    def _set_pos_frames_mapping(self):
        return {
            "main": "main-frame",
            "prepay amount": "ask-for-prepay-amount",
            "REFUND NOT ALLOWED": "show-message-505",
            "partial tender not allowed": "show-message-3009",
            "grade selection": "ask-fuel-grade-select",
            "Item not allowed.": "show-message-1553",
            "CANCEL NOT ALLOWED FOR ITEM": "show-message-501",
            "TRANSACTION ALREADY IN PROG": "show-message-3501",
            "ITEM NOT FOUND": "show-message-1502",
            "Transaction Failure": "credit-abort",
            "Reason code required" : "show-message-3551",
            "No amount entered" : "show-message-3011",
        }

    def _set_icr_keys_mapping(self):
        return {
            "CASHINSIDE": "I",
            "YES": "Y",
            "NO": "N",
            "HELP": "H",
            "ENTER": "E",
            "CLEAR": "L",
            "CREDITOUTSIDE": "P",
            "CREDITINSIDE": "R",
            "DEBIT": "D",
            "CASHOUTSIDE": "Q",
            "CANCEL": "C",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9",
            "0": "0",
        }

    def _set_sale_items_mapping(self):
        return {
            "Sale Item A": "099999999990",
            "Sale Item B": "088888888880",
            "Sale Item C": "077777777770",
            "Sale Item D": "066666666660",
            "Negative Sale Item": "1122",
        }

    def _set_tiers_mapping(self):
        return {"Cash": 0, "Credit": 1}
