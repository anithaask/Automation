import time

from behave import given, when, then

from cfrpos.core.pos.ui_metadata import POSFrame

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils import icr_utilities
from decimal import Decimal


# region Given clauses
@given('the cashier transferred a prepay from pump "{first_pump:d}" to "{second_pump:d}"')
def step_impl(context: Context, first_pump: int, second_pump: int):
    context.execute_steps(
        f'''
        When the cashier transfers a prepay from pump "{first_pump}" to "{second_pump}"
        '''
    )
    context.sit_product.pos.wait_for_item_added_to_VR("Prepay Fuel")


@given('the customer pressed "HELP" button on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "HELP" key on pump "{pump_number}" keypad
        Then the "Help: PUMP 01" alert is shown on the menu bar
        '''
    )


@given('the customer completed a PAP of fuel grade "{grade}" with "{amount:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, amount: float, pump_number: int):
    context.execute_steps(
        f'''
        When the customer completes a PAP of fuel grade "{grade}" with "{amount}" at pump "{pump_number}"
        '''
    )


@given('the customer begins a PAP on pump "{pump_number:d}" and selects a fuel grade "{grade}"')
def step_impl(context: Context, pump_number: int, grade: str):

    context.execute_steps(f'When the customer swipes the "credit_visa2" card at pump "{pump_number}"')

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "Carwash?", "ASKWASH PROMPT", attempts=30
    )

    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap('NO'))

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "RECEIPT PROMPT", attempts=30
    )

    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap('NO'))
    context.sit_product.simpumps.lift_nozzle(pump_number)
    context.sit_product.simpumps.select_grade(pump_number, grade)

    context.sit_product.simpumps.start_fueling(pump_number)
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "FUELING")


@given('the customer begins a PAP on pump "{pump_number:d}" with pump prompting out of receipt paper')
def step_impl(context: Context, pump_number: int):

    context.execute_steps(f'When the customer swipes the "credit_visa2" card at pump "{pump_number}"')

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "Carwash?", "ASKWASH PROMPT", attempts=30
    )

    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap('NO'))

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "RECEIPTFAIL", attempts=30
    )

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "CHOOSEGRADE", attempts=30
    )


@given('the customer fully dispensed the prepay on pump "{pump_number:d}" with grade "{grade}"')
def step_impl(context: Context, pump_number: int, grade: str):
    context.execute_steps(
        f'''
        When the customer fully dispenses the prepay on pump "{pump_number}" with grade "{grade}"
        Then a pump "{pump_number}" is not authorized
        '''
    )


@given('the pump "{pump_number:d}" went offline')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the pump "{pump_number}" goes offline
        '''
    )

    # Check whether pump is actually offline
    time.sleep(2)
    pump_online = context.sit_product.fuel.get_pump_status(pump_number)
    assert pump_online == "DEAD", f"Pump {pump_number} did not go offline"


@given('the pump "{pump_number:d}" is out of receipt paper')
def step_impl(context: Context, pump_number: int):
    icr_utilities.set_paper_out(context.sit_product.simpumps, pump_number)


@given('an MSR card "{card_name}" was swiped at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int, card_name: str):
    context.execute_steps(
        f'''
        When an MSR card "{card_name}" is swiped at pump "{pump_number}"
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "REMOVE CARD",
        attempts=30,
    )

    # Check whether card swipe was successful
    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    if current_display in ["REINSERTCARD", "CARDNOTREAD"]:
        raise ProductError(
            f"Card read error on pump {pump_number}: '{current_display}'"
        )


@given('a loyalty swipe was performed with "{card_name}" at pump "{pump_number:d}"')
def step_impl(context: Context, card_name: str, pump_number: int):
    context.execute_steps(
        f'''
        When a loyalty swipe is performed with "{card_name}" at pump "{pump_number}"
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "REMOVE CARD",
        attempts=30,
    )

    # Check whether card swipe was successful
    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    if current_display in ["REINSERTCARD", "CARDNOTREAD"]:
        raise ProductError(
            f"Card read error on pump {pump_number}: '{current_display}'"
        )


@given('a postpay transaction was started on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "CASHINSIDE" key on pump "{pump_number}" keypad
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer fueled "{volume:g}" gallons of fuel grade "{grade}" at pump "{pump_number:d}"')
def step_impl(context: Context, volume: float, grade: str, pump_number: int):
    context.execute_steps(f'When the customer fuels "{volume}" gallons of fuel grade "{grade}" at pump "{pump_number}"')


@given('the customer lifted the nozzle on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        '''
    )
    utility.wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "REMOVE NOZZLE",
        "BEGINFUELING",
        attempts=60,
        delay=1,
        timeout=60,
        exact_match=False,
    )


@given('the nozzle is hung up on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer hangs up the nozzle on pump "{pump_number}"
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "{pump_number}"
        '''
    )


@given('the ICR on pump "{pump_number:d}" went offline')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the ICR on pump "{pump_number}" goes offline
        Then the dynamic prompt "Please PayInside" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer declines loyalty at pump "{pump_number:d}" keypad')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        Given the configured prompt "ASKLOYALTY" was displayed on pump "{pump_number}"
        When the customer presses "NO" key on pump "{pump_number}" keypad
        Then the pump {pump_number} displays the "Lift Handle" prompt within 5 seconds
        '''
    )


@given('carwash is accepted on pump "{pump_number:d}" keypad')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "YES" key on pump "{pump_number}" keypad
        Then carwash items are displayed at pump "{pump_number}"
        '''
    )


@given('the customer selected the first carwash option at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "1" key on pump "{pump_number}" keypad
        Then the configured prompt "FUELING" is displayed on pump "{pump_number}"
        '''
    )


# unused
@given('the customer started fueling ${amount:f} with advertising displayed on pump "{pump_number:d}"')
def step_impl(context: Context, amount: float, pump_number: int):
    context.execute_steps(
        f'''
        When the customer starts fueling ${amount} in fuel on pump "{pump_number}"
        Then the dynamic prompt "Advertisement" is displayed on pump "{pump_number}"
        '''
    )


# unused
@given('fueling was completed on pump "{pump_number:d}" for ${amount:f}')
def step_impl(context: Context, pump_number: int, amount: float):
    context.execute_steps(
        f'''
        Then fueling is completed on pump "{pump_number}" for ${amount}
        '''
    )


@given('the customer selected incorrect fuel grade "{grade}" on pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, pump_number: int):
    context.execute_steps(
        f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        And fuel grade "{grade}" is selected on pump "{pump_number}"
        Then the configured prompt "INVALIDGRADE" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer hung up the nozzle on pump "{pump_number:d}" after selecting incorrect fuel grade')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer hangs up the nozzle on pump "{pump_number}"
        Then the configured prompt "BEGINFUELING" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer inserted card with attributes "{card_attributes}" at pump "{pump_number:d}"')
def step_impl(context: Context, card_attributes: str, pump_number: int):
    context.execute_steps(
        f'''
        When the customer inserts card with attributes "{card_attributes}" at pump "{pump_number}"
        Then the chip flow prompted for "Application" entry on pump "{pump_number}"
        '''
    )


@given('the customer selected application "{app_number:d}" on chip card on pump "{pump_number:d}"')
def step_impl(context: Context, app_number: int, pump_number: int):
    context.sit_product.simpumps.press_softkey(pump_number, app_number, 1)
    context.execute_steps(
        f'''
        Then the chip flow prompted for "PIN" entry on pump "{pump_number}"
        '''
    )


@given('the customer entered the correct PIN "{pin}" on pump "{pump_number:d}" keypad')
def step_impl(context: Context, pin: str, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "{pin}" key on pump "{pump_number}" keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer removed their card from the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer removes their card from the pump "{pump_number}"
        Then the dynamic prompt "CHOOSEGRADE" is displayed on pump "{pump_number}"
        '''
    )


@given('the customer pressed "{key}" key on pump "{pump_number:d}" keypad')
def step_impl(context: Context, key: str, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "{key}" key on pump "{pump_number}" keypad
        '''
    )
# endregion


# region When clauses
@when('the cashier stops all pumps')
def step_impl(context: Context):
    """Stop all pumps on the POS.

    :param context: Behave context.
    """
    pump_frame = context.sit_product.pos.control.get_fuel_pumps_frame()
    context.sit_product.pos.control.press_button(pump_frame.instance_id, "stop-all")
    stop_all_pumps_frame = context.sit_product.pos.control.get_menu_frame()
    context.sit_product.pos.control.press_button(stop_all_pumps_frame.instance_id, "yes")


@when('the cashier transfers a prepay from pump "{first_pump:d}" to "{second_pump:d}"')
def step_impl(context: Context, first_pump: int, second_pump: int):
    context.execute_steps(f'When the cashier selects the pump "{first_pump}"')
    context.sit_product.pos.press_button_on_frame(POSFrame.MAIN, "start-stop")
    context.execute_steps(f'When the cashier selects the pump "{second_pump}"')


@when('the cashier selects the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.pos.select_pump(pump_number)


@when('the cashier waits for the pump state to be "{pump_state}" on pump "{pump_number:d}"')
def step_impl(context: Context, pump_state: str, pump_number: int):
    utility.wait_for_pump_state_on_pos(context.sit_product.pos, pump_number, pump_state)


@when('the pump "{pump_number:d}" goes offline')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.deactivate_pump(pump_number)


@when('fuel grade "{grade}" is selected on pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, pump_number: int):
    context.sit_product.simpumps.select_grade(pump_number, context.sit_product.mapping.get_grades_remap(grade))


@when('the customer hangs up the nozzle on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.return_nozzle(pump_number)


@when('the customer starts fueling on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.start_fueling(pump_number)


@when('fuel is dispensed for "{seconds:d}" seconds on pump "{pump_number:d}"')
def step_impl(context: Context, seconds: int, pump_number: int):
    context.sit_product.simpumps.start_fueling(pump_number)
    time.sleep(seconds)
    context.sit_product.simpumps.stop_fueling(pump_number)


@when('the customer lifts the nozzle on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.lift_nozzle(pump_number)


@when('the customer starts fueling ${amount:f} in fuel on pump "{pump_number:d}"')
def step_impl(context: Context, amount: float, pump_number: int):
    # Set the final money at which fueling should automatically complete
    # and start fueling.
    money_cents = int(amount * 100)
    if not context.sit_product.simpumps.set_fuel_money(pump_number, money_cents):
        raise ProductError("Could not set fuel money")

    context.sit_product.simpumps.start_fueling(pump_number)


@when('the customer fuels "{volume:g}" gallons of fuel grade "{grade}" at pump "{pump_number:d}"')
def step_impl(context: Context, volume: float, grade: str, pump_number: int):
    context.execute_steps(f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        And fuel grade "{grade}" is selected on pump "{pump_number}"
        And the customer dispenses "{volume}" gallons on pump "{pump_number}"
        And the customer hangs up the nozzle on pump "{pump_number}"
    ''')


@when('the customer dispenses fuel up to ${amount:f} on pump "{pump_number:d}"')
def step_impl(context: Context, amount: float, pump_number: int):
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "FUELING")
    if not context.sit_product.simpumps.set_fuel_money(
        pump_number, round(amount * 100, 2)
    ):
        raise ProductError(f"Could not set fueling amount to ${amount}")
    context.execute_steps(f'When the customer starts fueling on pump "{pump_number}"')
    utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, amount)


@when('the customer dispenses "{volume:g}" gallons on pump "{pump_number:d}"')
def step_impl(context: Context, volume: float, pump_number: int):
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "FUELING")
    if not context.sit_product.simpumps.set_fuel_quantity_gallons(
        pump_number, round(volume*1000, 2)
    ):
        raise ProductError(f"Could not set fueling volume to ${volume}")
    context.execute_steps(f'When the customer starts fueling on pump "{pump_number}"')
    utility.wait_for_pump_dispense_gallons(context.sit_product.simpumps, pump_number, volume)


@when('the customer fully dispenses the prepay on pump "{pump_number:d}" with grade "{grade}"')
def step_impl(context: Context, pump_number: int, grade: str):

    context.sit_product.simpumps.lift_nozzle(pump_number)
    context.sit_product.simpumps.select_grade(pump_number, context.sit_product.mapping.get_grades_remap(grade))

    context.sit_product.simpumps.start_fueling(pump_number)
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "FUELING")
    authorized_amount = (context.sit_product.fuel.pump(pump_number).get_authorized_amount(pump_number)/100)
    utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, authorized_amount)

    context.sit_product.simpumps.return_nozzle(pump_number)
    
@when('the customer dispenses fuel up to ${amount:f} on the pump "{pump_number:d}" with grade "{grade}"')
def step_impl(context: Context, amount: float, pump_number: int, grade: str):

    context.execute_steps(f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        And fuel grade "{grade}" is selected on pump "{pump_number}"
        And the customer dispenses fuel up to ${amount} on pump "{pump_number}"
        And the customer hangs up the nozzle on pump "{pump_number}"
    ''')


@when('the customer lifts and hangs up the nozzle at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        And the customer hangs up the nozzle on pump "{pump_number}"
        '''
    )


@when('the customer completes a PAP of fuel grade "{grade}" with "{amount:f}" at pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, amount: float, pump_number: int):

    context.execute_steps(f'When the customer swipes the "credit_visa2" card at pump "{pump_number}"')

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "Carwash?", "ASKWASH PROMPT", attempts=30
    )

    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap('NO'))

    utility.wait_for_icr_prompts(
        context.sit_product.simpumps, pump_number, "RECEIPT PROMPT", "CHOOSEGRADE", attempts=30
    )

    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap('NO'))
    context.sit_product.simpumps.lift_nozzle(pump_number)
    context.sit_product.simpumps.select_grade(pump_number, grade)

    context.sit_product.simpumps.start_fueling(pump_number)
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "FUELING")

    if not context.sit_product.simpumps.set_fuel_money(pump_number, round(amount * 100, 2)):
        raise ProductError(f"Could not set fueling amount to ${amount}")
    utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, amount)

    context.sit_product.simpumps.return_nozzle(pump_number)
    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap("NO"))


@when('the customer starts fueling')
def step_impl(context: Context):
    """
    This step expects the following context values.

    * Pump Number
    """
    context.sit_product.simpumps.start_fueling(context.pump_number)


@when('the customer stops fueling')
def step_impl(context: Context):
    """
    This step expects the following context values.

    * Pump Number
    """
    context.sit_product.simpumps.stop_fueling(context.pump_number)


@when('the ICR on pump "{pump_number:d}" goes offline')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.deactivate_icr(pump_number)


@when('an MSR card "{card_name}" is swiped at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int, card_name: str):
    MSR_status, MSR_ready = utility.wait_until(
        lambda: int(context.sit_product.simpumps.get_MSR_status(pump_number)),
        lambda x: x == 1,  # 0 = DISABLED, 1 = ENABLED
        30,
        1,
    )
    if not MSR_ready:
        raise ProductError("MSR on SimPumps was not enabled in time")
    track = context.sit_product.card_deck.get_track_data(card_name)
    context.sit_product.simpumps.swipe_card(pump_number, track)


@when('the customer inserts card with attributes "{card_attributes}" at pump "{pump_number:d}"')
def step_impl(context: Context, card_attributes: str, pump_number: int):
    # Verify what chip card wait time is and whether we need this implemented by fuel team or not.
    wait_time = context.sit_product.fuel.get_chip_card_insert_wait_time()
    time.sleep(wait_time)

    context.sit_product.simpumps.insert_card(pump_number, card_attributes)


@when('the customer removes their card from the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.simpumps.remove_card(pump_number)


@when('the customer presses "{key}" key on pump "{pump_number:d}" keypad')
def step_impl(context: Context, key: str, pump_number: int):
    """
    :param key: Acceptable values are CASHINSIDE, YES, NO, HELP, ENTER, CLEAR,
        CREDITOUTSIDE, CREDITINSIDE, DEBIT, CASHOUTSIDE, CANCEL, and numbers 0-9.
        Pump button aliases are defined in sitbdd/sitcore/bdd_utils/mapping.py.
    """
    context.sit_product.simpumps.press_button(pump_number, context.sit_product.mapping.get_icr_keys_remap(key))


@when('a loyalty swipe is performed with "{card_name}" at pump "{pump_number:d}"')
def step_impl(context: Context, card_name: str, pump_number: int):
    context.execute_steps(
        f'''
        When an MSR card "{card_name}" is swiped at pump "{pump_number}"
        '''
    )


@when('the customer swipes the "{card_name}" card at pump "{pump_number:d}"')
def step_impl(context: Context, card_name: str, pump_number: int):
    track_data = context.sit_product.card_deck.get_track_data(card_name)
    context.sit_product.simpumps.swipe_card(pump_number, track_data)
    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "REMOVE CARD",
        attempts=30,
    )

    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    if current_display in ["REINSERTCARD", "CARDNOTREAD"]:
        raise ProductError(f"Card read error on pump {pump_number}: '{current_display}'")


@when('the operator refills the receipt paper in pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    icr_utilities.reset_paper(context.sit_product.simpumps, pump_number)


@when('the customer dispenses grade "{grade}" fuel for ${amount:f} price on pump "{pump_number:d}"')
def step_impl(context: Context, amount: float, grade: str, pump_number: int):
    context.execute_steps(
        f'''
        When the customer lifts the nozzle on pump "{pump_number}"
        And fuel grade "{grade}" is selected on pump "{pump_number}"
        And the customer starts fueling ${amount} in fuel on pump "{pump_number}"
        '''
    )


@when('the customer declines the receipt on pump "{pump_number:d}" keypad')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "NO" key on pump "{pump_number}" keypad
        '''
    )
# endregion


# region Then clauses
# unused
@then('there are stacked sales on pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    ending_count, done = utility.wait_until(
        lambda: context.sit_product.pos.get_count_of_stacked_sales_on_pump(pump_number),
        lambda count: count > 0,
        10,
        0.5,
    )
    if not done:
        raise ProductError(
            f"Expected at least 1 stacked sale on pump {pump_number}"
            f", got {ending_count} instead."
        )


@then('the completed sale amount is ${money:f} on pump "{pump_number:d}"')
def step_impl(context: Context, money: float, pump_number: int):
    expected_money = int(money * 100)
    # Find another means to find the end total for a completed transaction
    sale_info = context.sit_product.fuel.get_completed_sale_info(pump_number, 1)
    actual_money = sale_info["Money"]
    assert actual_money == expected_money, f'THe completed sale amount was not {expected_money} on pump {pump_number}, was {actual_money} instead'


@then('the pump "{pump_number:d}" stops')
def step_impl(context: Context, pump_number: int):
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "STOP")


@then('the chip flow prompted for "{prompt_name}" entry on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_name: str, pump_number: int):
    expected_prompt = context.sit_product.simpumps.get_chip_prompt_text(pump_number, prompt_name, False)
    exact_match = True
    if prompt_name == "Application":
        exact_match = False
    timeout = 120
    if not context.sit_product.simpumps.match_prompt_on_display(
        pump_number, expected_prompt, exact_match, timeout
    ):
        raise TimeoutError("Not prompted within {} seconds".format(timeout))


@then('the ICR displays the "{prompt_name}" prompt within "{timeout_seconds:d}" seconds on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_name: str, timeout_seconds: int, pump_number: int):
    result, success = utility.wait_until(
        lambda: context.sit_product.simpumps.get_current_display(pump_number),
        lambda current_display: current_display == prompt_name,
        timeout_seconds,
        1
    )

    if not success:
        raise ProductError(f"Timed out waiting for {prompt_name} prompt to display")


@then('fueling is completed on pump "{pump_number:d}" for ${amount:f}')
def step_impl(context: Context, pump_number: int, amount: float):
    utility.wait_for_pump_dispense(context.sit_product.simpumps, pump_number, amount)


@then('price for grade "{grade}" on pump "{pump_number:d}" is "{ppu:F}" for tier "{tier}"')
def step_impl(context: Context, grade:str, pump_number: int, ppu: Decimal, tier: str):
    actual_ppu = context.sit_product.simpumps.get_current_ppu_display(pump_number, context.sit_product.mapping.get_grades_remap(grade), context.sit_product.mapping.get_tiers_remap(tier))
    assert Decimal(actual_ppu) == ppu * 1000

# endregion
