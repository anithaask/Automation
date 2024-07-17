import time
from behave import given, when

from behave.runner import Context


# region Given clauses
@given('the customer chose to use loyalty card "{card_name}"')
def step_impl(context: Context, card_name: str):
    card_data = context.sit_product.card_deck.get_track_data(card_name)
    context.pinpad.set_swiped_card_data(card_data)
    time.sleep(2)
    context.pinpad.trigger_card_swipe()
    context.sit_product.pos.wait_for_item_added_to_VR("Plus Card")


@given('the customer chose to use MSR card "{card_name}"')
def step_impl(context: Context, card_name: str):
    context.execute_steps(
        f'''
        When the customer chooses to use MSR card "{card_name}"
        '''
    )


@given('the customer swiped a cobranded card "{card_name}" on the pinpad')
def step_impl(context: Context, card_name: str):
    card_data = context.sit_product.card_deck.get_track_data(card_name)
    context.pinpad.set_swiped_card_data(card_data)
    time.sleep(2)
    context.pinpad.trigger_card_swipe()


@given('the customer swiped a credit card "{card_name}" on the pinpad')
def step_impl(context: Context, card_name: str):
    card_data = context.sit_product.card_deck.get_track_data(card_name)
    context.pinpad.set_swiped_card_data(card_data)
    time.sleep(2)
    context.pinpad.trigger_card_swipe()
# endregion


# region When classes
@when('the customer chooses to use MSR card "{card_name}"')
def step_impl(context: Context, card_name: str):
    """
    Cards are defined in sitbdd/data/cards.json.
    """
    card_data = context.sit_product.card_deck.get_track_data(card_name)
    context.pinpad.set_swiped_card_data(card_data)
# endregion


# region Then clauses
# endregion
