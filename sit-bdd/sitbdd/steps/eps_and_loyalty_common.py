from behave import given, then

from behave.runner import Context


# region Given clauses
@given('the "{controller_type}" host is "{state}"')
def step_impl(context: Context, controller_type, state):
    context.sit_product.set_host_state(controller_type, state)


@given('the "{controller_type}" controller has a completed transaction')
def step_impl(context: Context, controller_type):
    context.sit_product.ensure_completed_transaction(controller_type)


# To be done either by the Epsilon package or the RCM package.
@given('updated configuration is loaded by loyalty controller')
def step_impl(context: Context):
    pass


# To be done either by the Epsilon package or the RCM package.
@given('the Epsilon has following global options configured')
def step_impl(context: Context):
    """
    Given these ICR options are set:
        | option                 | value         |
        | Loyalty Prompt Control | Do Not Prompt |
    """
    pass


# To be done either by the Epsilon package or the RCM package.
@given('updated configuration is loaded by credit controller')
def step_impl(context: Context):
    pass
# endregion


# region When clauses
# endregion


# region Then clauses
# endregion
