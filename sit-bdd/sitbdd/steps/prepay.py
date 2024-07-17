from behave import given, when, then

from cfrpos.core.pos.ui_metadata import POSButton
from cfrpos.core.pos.ui_metadata import POSFrame

from behave.runner import Context

from sitbdd.sitcore.bdd_utils import utility


# region Given clauses
@given('the cashier prepaid the fuel grade "{grade_type}" for price "{price:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, grade_type: str, price: float, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier prepays the fuel grade "{grade_type}" for price "{price}" at pump "{pump_number}"
        Then a prepay item "Prepay:{grade_type}" with price "{price}" is in the "current" transaction
        '''
    )
    

@given('the cashier prepaid fuel for price "{price:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, price: float, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier prepays fuel for price "{price}" at pump "{pump_number}"
        Then a prepay item "Prepay Fuel" with price "{price}" is in the "current" transaction
        '''
    )


@given('the customer selected fuel grade "{grade}" for their prepay transaction at pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, pump_number: int):
    context.execute_steps(
        f'''
        When fuel grade "{grade}" is selected on pump "{pump_number}"
        '''
    )
    utility.wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "SELECT GRADE",
        "BEGINFUELING",
        attempts=60,
        delay=1,
        timeout=60,
        exact_match=False,
    )
# endregion


# region When clauses
@when('the cashier prepays fuel for price "{price:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, price: float, pump_number: int):
    """
    This step expects "None" set for the "Prepay Grade Select Type" RCM option.
    """
    context.sit_product.pos.select_pump(pump_number)
    context.sit_product.pos.press_button_on_frame(frame=POSFrame.MAIN, button=POSButton.PREPAY_CANCEL_PREPAY)
    context.sit_product.pos.press_digits(POSFrame.ASK_PREPAY_AMOUNT, price)
    context.sit_product.pos.press_button_on_frame(POSFrame.ASK_PREPAY_AMOUNT, POSButton.ENTER)

@when('the cashier prepays the fuel grade "{grade_type}" for price "{price:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, grade_type: str, price: float, pump_number: int):
    context.sit_product.pos.select_pump(pump_number)
    context.sit_product.pos.press_button_on_frame(frame=POSFrame.MAIN, button=POSButton.PREPAY_CANCEL_PREPAY)
    context.execute_steps(
        f'''
        When the cashier presses the "{grade_type}" button
        '''
    )
    context.sit_product.pos.press_digits(POSFrame.ASK_PREPAY_AMOUNT, price)
    context.sit_product.pos.press_button_on_frame(POSFrame.ASK_PREPAY_AMOUNT, POSButton.ENTER)
# endregion


# region Then clauses
@then('the Smart Prepay fuel grade "{grade_type}" for price "{price:f}" is in the POS virtual receipt')
def step_impl(context: Context, grade_type: str, price: float):
    assert context.sit_product.pos.verify_virtual_receipt_contains_item(grade_type, item_price=price),\
        f'The Smart Prepay fuel grade "{grade_type}" for price "{price}" is not in the POS virtual receipt'


@then('a prepay item "{description}" with price "{price:f}" is in the "{transaction}" transaction')
def step_impl(context: Context, description: str, price: float, transaction: str):
    assert context.sit_product.pos.wait_for_item_added(
        description=description, price=price, item_type=7, transaction=transaction
    ), f'A prepay item "{description}" with price "{price}" is not in the "{transaction}" transaction'
# endregion
