from behave import given, when, then
from behave.runner import Context


# region When clauses
@when("the most recent transaction is bumped")
def step_impl(context: Context):
    transaction_number = context.sit_product.get_last_epsilon_transaction_number()
    context.sit_product.kps.bump_transaction(transaction_number)


# region Then clauses
@then("the KPS signals that the transaction was bumped")
def step_impl(context: Context):
    transaction_number = context.sit_product.get_last_epsilon_transaction_number()
    assert context.sit_product.kps.get_bump_status(transaction_number)
