from behave import given, when

from cfrpos.core.pos.ui_metadata import POSButton
from cfrpos.core.pos.ui_metadata import POSFrame

from behave.runner import Context
from sitbdd.sitcore.bdd_utils import utility


# region Given clauses
@given('the "{card}" SVC card was activated for ${amount:g}')
def step_impl(context: Context, card: str, amount: float):
    """
    Cards are defined in sitbdd/data/cards.json.
    """
    context.execute_steps(
        f'''
        When the cashier adds a ${amount} SVC activation for "{card}" to the transaction
        And the cashier tenders the transaction for exact dollar with tender type "cash"
        '''
    )


@given('the cashier added a ${amount:f} SVC activation for "{card}" to the transaction')
def step_impl(context: Context, amount: float, card: str):
    context.execute_steps(
        f'''
        When the cashier adds a ${amount} SVC activation for "{card}" to the transaction
        '''
    )
    # Could not test if this works as we currently don't have a pinpad. Will have to be verified later.
    context.sit_product.pos.wait_for_item_added_to_VR("SVC Activation")
# endregion


# region When clauses
@when('the cashier adds a ${amount:f} SVC activation for "{card}" to the transaction')
def step_impl(context: Context, amount: float, card: str):
    """
    Cards are defined in sitbdd/data/cards.json.
    """
    context.sit_product.pos.press_button_on_frame(POSFrame.MAIN, "sell-bc-444666")
    context.sit_product.pos.wait_for_frame_open(POSFrame.ASK_CARD_SWIPE_FOR_ACTIVATION)
    card_data = context.sit_product.card_deck.get_track_data(card)
    context.pinpad.set_swiped_card_data(card_data)

    frame = utility.wait_for_frame_name(context.sit_product.pos, "credit-get-amount")
    context.pinpad.delete_swiped_card_data()
    for digit in f"{amount:.2f}".replace(".", ""):
        context.sit_product.pos.control.press_button(frame.instance_id, f"key-{digit}")
    context.sit_product.pos.control.press_button(frame.instance_id, POSButton.ENTER.value)

    context.sit_product.pos.control.wait_for_frame_open("show-message-8011")
    context.sit_product.pos.press_goback_on_current_frame()


# endregion


# region Then clauses
# endregion
