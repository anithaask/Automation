import random
import time

from behave import given, when

from behave.runner import Context


# region Given clauses
@given('the system is in a ready to sell state')
def step_impl(context: Context):
    context.sit_product.set_system_to_ready_to_sell_state()
# endregion

# region When clauses
# endregion
