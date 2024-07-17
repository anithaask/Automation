from behave import given, when, then

from behave.runner import Context
from sitbdd.sitcore.bdd_utils import utility


# region Given clauses
@given('the customer dispensed "{grade}" for "{price:f}" price at pump "{pump_number:d}"')
@when('the customer dispenses "{grade}" for "{price:f}" price at pump "{pump_number:d}"')
def step_impl(context: Context, grade: str, price: float, pump_number: int):
    context.sit_product.dispense_fuel_for_price_at_pump(grade, price, pump_number)


@given('the Tank "{tank_number:d}" is offline')
def step_impl(context: Context, tank_number: int):
    context.execute_steps(
        f'''
        When the Tank Online button is pressed on fuel tank "{tank_number}"
        '''
    )
    assert not context.sit_product.tank_sim.get_tank_status(tank_number), f"Tank {tank_number} is not offline"


@given('the Tank "{tank_number:d}" is online')
def step_impl(context: Context, tank_number: int):
    context.execute_steps(
        f'''
        When the Tank Offline button is pressed on fuel tank "{tank_number}"
        '''
    )
    assert context.sit_product.tank_sim.get_tank_status(tank_number), f"Tank {tank_number} is not online"
# endregion


# region When clauses
@when('the Tank Online button is pressed on fuel tank "{tank_number:d}"')
def step_impl(context: Context, tank_number: int):
    context.sit_product.tank_sim.set_tank_offline(tank_number)


@when('the Tank Offline button is pressed on fuel tank "{tank_number:d}"')
def step_impl(context: Context, tank_number: int):
    context.sit_product.tank_sim.set_tank_online(tank_number)
# endregion


# region Then clauses
@then('the pump "{pump_number:d}" is authorized for ${amount:d}')
def step_impl(context: Context, pump_number: int, amount: int):
    context.sit_product.verify_pump_authorized_for_price(pump_number, amount)


@then('a pump "{pump_number:d}" is not authorized')
def step_impl(context: Context, pump_number: int):
    utility.wait_for_pump_state_on_fc(context.sit_product.fuel, pump_number, "IDLE")
# endregion
