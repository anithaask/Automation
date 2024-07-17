from unittest import mock

import pytest

from sitbdd.sitcore.bdd_utils.card_deck import CardDeck

SAMPLE_CARD_DECK = {
    "cards": [
        {
            "name": "credit",
            "card_type": "Discover",
            "track_data": "%B6011009909111115^LUKE SKYWALKER"
            "^0706101000000000000000000000000000000000000?"
            ";6011000990911111=07061010000000000000?",
        },
        {
            "name": "svc_one_step",
            "card_type": "SVC",
            "track_data": "%B6276686730931235^07675004256$01500$        ^8012110  Y?"
            ";6276686730931235=801211016496782?",
            "barcode": "076750042560",
            "barcode_long": "076750042560006276686730931235",
        },
        {
            "name": "loyalty_cobranded_visa_old",
            "track_data": "%B4190013008100021^4190013008100021/NAME 2   "
            "^0907101154500000000200567000000?",
            "barcode": "40108512212",
        },
        {
            "name": "credit_wex",
            "card_type": "WEX",
            "track_data": ";6900460420001234566=00031017212100000?",
            "pin": "0841",
        },
    ]
}


@pytest.fixture
def card_deck():
    with mock.patch("sitbdd.sitcore.bdd_utils.card_deck.CardDict"):
        deck = CardDeck()
        deck.cards_dict = SAMPLE_CARD_DECK
        return deck


class TestCardDeck:
    def test__get_card__empty_string_card_name(self, card_deck: CardDeck):
        assert card_deck.get_card("") is None

    def test__get_card__simple(self, card_deck: CardDeck):
        result = card_deck.get_card("credit")
        assert result is not None
        assert result["name"] == "credit"
        assert result["card_type"] == "Discover"
        assert (
            result["track_data"] == "%B6011009909111115^LUKE SKYWALKER"
            "^0706101000000000000000000000000000000000000?;"
            "6011000990911111=07061010000000000000?"
        )

    def test__get_track_data__empty_string_card_name(self, card_deck: CardDeck):
        assert card_deck.get_track_data("") is None

    def test__get_track_data__simple(self, card_deck: CardDeck):
        assert (
            card_deck.get_track_data("credit") == "%B6011009909111115^LUKE SKYWALKER"
            "^0706101000000000000000000000000000000000000?;"
            "6011000990911111=07061010000000000000?"
        )

        assert (
            card_deck.get_track_data("svc_one_step")
            == "%B6276686730931235^07675004256$01500$        "
            "^8012110  Y?;6276686730931235=801211016496782?"
        )

        assert (
            card_deck.get_track_data("loyalty_cobranded_visa_old")
            == "%B4190013008100021^4190013008100021/NAME 2   "
            "^0907101154500000000200567000000?"
        )

        assert (
            card_deck.get_track_data("credit_wex")
            == ";6900460420001234566=00031017212100000?"
        )

    def test__get_barcode__empty_string_card_name(self, card_deck: CardDeck):
        assert card_deck.get_barcode("") is None

    def test__get_barcode__simple(self, card_deck: CardDeck):
        assert card_deck.get_barcode("credit") is None
        assert card_deck.get_barcode("svc_one_step") == "076750042560"
        assert card_deck.get_barcode("loyalty_cobranded_visa_old") == "40108512212"
        assert card_deck.get_barcode("credit_wex") is None

    def test__get_barcode_long__empty_string_card_name(self, card_deck: CardDeck):
        assert card_deck.get_barcode_long("") is None

    def test__get_barcode_long__simple(self, card_deck: CardDeck):
        assert card_deck.get_barcode_long("credit") is None
        assert (
            card_deck.get_barcode_long("svc_one_step")
            == "076750042560006276686730931235"
        )
        assert card_deck.get_barcode_long("loyalty_cobranded_visa_old") is None
        assert card_deck.get_barcode_long("credit_wex") is None

    def test__get_pin__empty_string_card_name(self, card_deck: CardDeck):
        assert card_deck.get_pin("") is None

    def test__get_pin__simple(self, card_deck: CardDeck):
        assert card_deck.get_pin("credit") is None
        assert card_deck.get_pin("svc_one_step") is None
        assert card_deck.get_pin("loyalty_cobranded_visa_old") is None
        assert card_deck.get_pin("credit_wex") == "0841"
