from behave import given, when, then

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.utility import wait_for_icr_prompts, wait_for_pump_state_on_pos, wait_for_not_icr_prompts
from sitbdd.sitcore.bdd_utils.errors import ProductError


# region Given clauses
@given('the cashier added a postpay item to the transaction')
def step_impl(context: Context):

    start_item_count = context.sit_product.pos.get_transaction_item_count()
    context.execute_steps('When the cashier presses the "pay1" button')
    context.sit_product.pos.wait_for_transaction_item_count_increase(start_item_count)


@given('the customer started a postpay transaction at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "CASHINSIDE" key on pump "{pump_number}" keypad
        And the customer lifts the nozzle on pump "{pump_number}"
        '''
    )

    wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "GREETING",
        "ASKLOYALTYMOPPOSTPAY",
        attempts=30,
    )

    # Expecting multiple possible prompts so we need to check for all of them
    expected_display = ["CHOOSEGRADE", "REMOVE NOZZLE  AND SELECT GRADE"]
    wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        *expected_display,
        attempts=1,
    )


@given('the customer selected fuel grade "{grade}" for their postpay transaction at pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, pump_number: int):
    context.execute_steps(
        f'''
        When fuel grade "{grade}" is selected on pump "{pump_number}"
        '''
    )
    wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "INSIDEAUTH",
        attempts=60,
        delay=1,
        timeout=60,
        exact_match=False,
    )


@given('the cashier authorized the pump "{pump_number:d}" for postpay')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier authorizes postpay on the POS for pump "{pump_number}"
        '''
    )
    wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "REPLACENOZZLE",
        "LOWER NOZZLE",
        attempts=60,
        delay=1,
        timeout=60,
        exact_match=False,
    )


# unused
@given('the customer completed postpay fueling for "{seconds:d}" seconds on pump "{pump_number:d}"')
def step_impl(context: Context, seconds: int, pump_number: int):
    context.execute_steps(
        f'''
        When fuel is dispensed for "{seconds}" seconds on pump "{pump_number}"
        And the customer hangs up the nozzle on pump "{pump_number}"
        Then the pump "{pump_number}" displays welcome prompt
        '''
    )


# unused
@given('the customer completed postpay fueling for ${amount:f} on pump "{pump_number:d}"')
def step_impl(context: Context, amount: float, pump_number: int):
    context.execute_steps(
        f'''
        When the customer dispenses fuel up to ${amount} on pump "{pump_number}"
        And the customer hangs up the nozzle on pump "{pump_number}"
        Then the configured prompt "PAYCASHIER" is displayed on pump "{pump_number}"
        '''
    )
# endregion


# region When clauses
@when('the cashier authorizes postpay on the POS for pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier waits for the pump state to be "HandleLifted" on pump "{pump_number}"
        And the cashier selects the pump "{pump_number}"
        And the cashier selects the pump "{pump_number}"
        '''
    )


@when('the cashier authorizes postpay on the POS by double tapping the pump icon')
def step_impl(context: Context):
    """This step expects the following context values.

    * Pump Number
    """
    wait_for_pump_state_on_pos(context.sit_product.pos, context.pump_number, "HandleLifted")

    context.execute_steps(
        '''
        When the cashier selects the pump
        And the cashier selects the pump
        '''
    )


@when('the cashier tenders postpay fuel transaction on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier selects the pump "{pump_number}"
        When the cashier presses the "pay1" button
        And the cashier tenders the transaction for exact dollar with tender type "cash"
        '''
    )


@when('the cashier tenders postpay fuel transaction with tender type "{tender_type}" on pump "{pump_number:d}"')
def step_impl(context: Context, tender_type: str, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier selects the pump "{pump_number}"
        When the cashier presses the "pay1" button
        And the cashier tenders the transaction for exact dollar with tender type "{tender_type}"
        '''
    )


@when('the customer tries to cancel postpay transaction during fueling on pump "{pump_number}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When fuel is dispensed for "3" seconds on pump "{pump_number}"
        And the customer presses "CANCEL" key on pump "{pump_number}" keypad
        '''
    )
# endregion


# region Then clauses
# endregion
