"""
Allows other modules and steps to retrieve card data for use in tests.
Can retrieve payment or loyalty card data.
Currently parses cards.json which is static.
Future implementation could allow generation of card data on the fly.
"""
__all__ = ["CardDeck", "CardDict"]

import os
import json

from sitbdd.config import Config
from sitbdd.sitcore.bdd_utils.sit_logging import get_sit_logger, wrap_all_methods_with_log_trace

logger = get_sit_logger()


@wrap_all_methods_with_log_trace
class CardDict(dict):
    """
    Simple container for card data. Currently just reads from cards.json file.
    """

    CARDS_FILE_NAME = "cards.json"
    CARDS_FILE = os.path.join(Config.DATA_DIR, CARDS_FILE_NAME)

    def __init__(self, file=CARDS_FILE):
        super().__init__()
        self.file = file
        self.load()

    def load(self):
        """Load config from file.

        :return: None
        """

        self.clear()

        with open(self.file) as file:
            self.update(json.loads(file.read()))


@wrap_all_methods_with_log_trace
class CardDeck:
    """
    This class allows retrieval of card data to use in tests.
    Can get an entire card or a specific part of the card (such as the track data).
    Wrapper of actual cards list so that when we allow
    card data generation the callers don't have to change.
    """

    def __init__(self, card_file_path=CardDict.CARDS_FILE):
        self.cards_dict = CardDict(card_file_path)

    def get_card(self, card_name):
        """
        Retrieve full card information as a dict. Generally not necessary for
        steps to use but provided if desired.

        :param str card_name: Name of the card you intend to retrieve
        :return: Full card information or None
        :rtype: dict or None
        """

        result = None
        for card in self.cards_dict["cards"]:
            if card["name"] == card_name:
                result = card

        return result

    def get_track_data(self, card_name):
        """
        Attempts to retrieve the track data for the desired card.

        :param str card_name: Name of the card you intend to retrieve the track data for
        :return: Track data of card or None
        :rtype: str or None
        """

        card = self.get_card(card_name)

        result = None
        if card and "track_data" in card:
            result = card["track_data"]

        return result

    def get_barcode(self, card_name):
        """
        Attempts to retrieve the barcode for the desired card.

        :param str card_name: Name of the card you intend to retrieve the barcode for
        :return: Barcode of card or None
        :rtype: str or None
        """

        card = self.get_card(card_name)

        result = None
        if card and "barcode" in card:
            result = card["barcode"]

        return result

    def get_barcode_long(self, card_name):
        """
        Attempts to retrieve the long barcode for the desired card. The long barcode
        is used for one step SVC activation as it contains the card's barcode as well as
        a portion of its track data.

        :param str card_name: Name of the card you intend to retrieve
            the long barcode for
        :return: Long barcode of card or None
        :rtype: str or None
        """

        card = self.get_card(card_name)

        result = None
        if card and "barcode_long" in card:
            result = card["barcode_long"]

        return result

    def get_pin(self, card_name):
        """
        Attempts to retrieve the pin for the desired card.

        :param str card_name: Name of the card you intend to retrieve the pin for
        :return: Pin of card or None
        :rtype: str or None
        """

        card = self.get_card(card_name)

        result = None
        if card and "pin" in card:
            result = card["pin"]

        return result
