from behave import then, given, when
from behave.runner import Context
from decimal import Decimal
from sitbdd.sitcore.bdd_utils import utility


# region Given clauses
@given('the host simulator has set following registries')
def step_impl(context: Context):
    """Sets value for key in host simulator registry.

    Given the host simulator has set following registries
            | path                       | key      | value         |
            | ResponseCodes\\STACCapture | 1.06     | 00001,Decline |

    This step expects the following context values.

    * path - host simulator registry path
    * Key, like Amount for example
    * Value of the key, like 1.00 for Amount for example

    :param context: Behave context.
    """
    original_options = {}
    utility.require_table_headings(context.table, "path", "key", "value")
    for row in context.table:
        path = str(row["path"])
        key = str(row["key"])
        value = str(row["value"])
        context.sit_product.eps.conexxus.set_simulator_value(path, key, value)


@given("ConMob settings are cleared in the host simulator")
def step_impl(context: Context):
    """
    Clears all MPPA discounts and custom response codes. Ensure any steps setting the discounts
    are executed after this step.
    """
    context.sit_product.eps.conexxus.clear_simulator_discounts_and_triggers()


@given('transaction discount is enabled in host simulator')
def step_impl(context: Context):
    """
    Set the transaction discount here, do not rely on hte initial simulator configuration
    """
    context.sit_product.eps.conexxus.enable_transaction_discount()


@given('following values are set under "Software\...\Adjustment1" registry path for "{product}"')
def step_impl(context: Context, product: str):
    """
    Given following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                 | value  |
            | Amount              | 0.00   |
            | doNotRelieveTaxFlag | true   |
            | MaximumQuantity"    | 10     |
            | priceAdjustmentID   | 112233 |
    """
    context.sit_product.eps.conexxus.enable_price_adjustments()
    context.sit_product.eps.conexxus.create_product(product)

    utility.require_table_headings(context.table, "key", "value")
    for row in context.table:
        key = str(row["key"])
        value = str(row["value"])
        context.sit_product.eps.conexxus.set_product_adjustment(product, key, value)


@given('customer reserved pump "{pump_number:d}" via mobile application')
def step_impl(context: Context, pump_number: int):
    context.sit_product.eps.conexxus.reserve_pump(pump_number)
# endregion

# region When clauses
@when(u'Conexxus host sends authorization request without CustomerPromptData')
def step_impl(context):
    context.sit_product.eps.conexxus.do_not_prompt_for_access_code()
# endregion

# region Then clauses
@then('"{request_name}" message contains sale item "{sale_item}" with OriginalAmount/Amount "{original_amount}"')
def step_impl(context: Context, request_name: str, sale_item: str, original_amount: str):
    """Verify that the Mobile request contains correct original amount for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * Original Amount Value

    :param context: Behave context.
    """
    dec_orig_amount = Decimal(original_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    amount =  context.sit_product.eps.conexxus.get_original_amount(message, sale_item)
    assert Decimal(amount).quantize(dec_orig_amount) == dec_orig_amount, f"{request_name} message amount {amount} doesn't match given amount {original_amount}"


@then('"{request_name}" message contains discount sale item with AdjustedAmount/Amount "{adjusted_amount}"')
def step_impl(context: Context, request_name: str, adjusted_amount: str):

    dec_adj_amount = Decimal(adjusted_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_discount_sale_item(message)
    assert discount is not None, f"Cannot find discount sale item in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_adjusted_amount(discount)

    assert Decimal(amount).quantize(dec_adj_amount) == dec_adj_amount, f"{request_name} message amount {amount} doesn't match given amount {adjusted_amount}"


@then('"{request_name}" message contains discount sale item with OriginalAmount/Amount "{original_amount}"')
def step_impl(context: Context, request_name: str, original_amount: str):

    dec_adj_amount = Decimal(original_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_discount_sale_item(message)
    assert discount is not None, f"Cannot find discount sale item in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_original_amount(discount)

    assert Decimal(amount).quantize(dec_adj_amount) == dec_adj_amount, f"{request_name} message amount {amount} doesn't match given amount {original_amount}"


@then('"{request_name}" message contains discount sale item with ProductCode "{product_code}"')
def step_impl(context: Context, request_name: str, product_code: str):

    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_discount_sale_item(message)
    assert discount is not None, f"Cannot find discount sale item in {request_name}"
    actual_product_Code = context.sit_product.eps.conexxus.get_item_product_code(discount)

    assert product_code == actual_product_Code, f"{request_name} message product code {actual_product_Code} doesn't match given product code {product_code}"


@then('"{request_name}" message contains discount sale item with ItemID "{item_id}"')
def step_impl(context: Context, request_name: str, item_id: str):

    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_discount_sale_item(message)
    assert discount is not None, f"Cannot find discount sale item in {request_name}"
    actual_item_id = context.sit_product.eps.conexxus.get_item_item_id(discount)

    assert item_id == actual_item_id, f"{request_name} message product code {actual_item_id} doesn't match given product code {item_id}"


@then('"{request_name}" message contains PriceAdjustment under discount sale item with Amount "{amount}"')
def step_impl(context: Context, request_name: str, amount: str):
    context.execute_steps(
        f'''
        Then "{request_name}" message contains PriceAdjustment under sale item "Ticket Rebate 1" with Amount "{amount}"
        '''
    )


@then('"{request_name}" message contains PriceAdjustment under discount sale item with UnitPrice "{unitprice}"')
def step_impl(context: Context, request_name: str, unitprice: str):
    context.execute_steps(
        f'''
        Then "{request_name}" message contains PriceAdjustment under sale item "Ticket Rebate 1" with UnitPrice "{unitprice}"
        '''
    )


@then('"{request_name}" message contains PriceAdjustment under discount sale item with Quantity "{quantity}"')
def step_impl(context: Context, request_name: str, quantity: str):
    context.execute_steps(
        f'''
        Then "{request_name}" message contains PriceAdjustment under sale item "Ticket Rebate 1" with Quantity "{quantity}"
        '''
    )


@then('"{request_name}" message contains linked discount for "{sale_item}" with OriginalAmount/Amount "{original_amount}"')
def step_impl(context: Context, request_name: str, sale_item: str, original_amount: str):

    dec_orig_amount = Decimal(original_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_postpay_discount_for_item(message, sale_item)
    assert discount is not None, f"Cannot find postpay discount for (sale_item) in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_original_amount(discount)

    assert Decimal(amount).quantize(dec_orig_amount) == dec_orig_amount, f"{request_name} message amount {amount} doesn't match given amount {original_amount}"


@then('"{request_name}" message contains linked discount for "{sale_item}" with OriginalAmount/UnitPrice "{original_unit_price}"')
def step_impl(context: Context, request_name: str, sale_item: str, original_unit_price: str):

    dec_orig_unit_price = Decimal(original_unit_price)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_postpay_discount_for_item(message, sale_item)
    assert discount is not None, f"Cannot find postpay discount for (sale_item) in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_original_unit_price(discount)

    assert Decimal(amount).quantize(dec_orig_unit_price) == dec_orig_unit_price, f"{request_name} message amount {amount} doesn't match given amount {original_unit_price}"


@then('"{request_name}" message contains linked discount for "{sale_item}" with AdjustedAmount/Amount "{adjusted_amount}"')
def step_impl(context: Context, request_name: str, sale_item: str, adjusted_amount: str):

    dec_adjusted_amount = Decimal(adjusted_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_postpay_discount_for_item(message, sale_item)
    assert discount is not None, f"Cannot find postpay discount for (sale_item) in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_adjusted_amount(discount)

    assert Decimal(amount).quantize(dec_adjusted_amount) == dec_adjusted_amount, f"{request_name} message amount {amount} doesn't match given amount {adjusted_amount}"


@then('"{request_name}" message contains linked discount for "{sale_item}" with AdjustedAmount/UnitPrice "{adjusted_unit_price}"')
def step_impl(context: Context, request_name: str, sale_item: str, adjusted_unit_price: str):

    dec_adjusted_unit_price = Decimal(adjusted_unit_price)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    discount = context.sit_product.eps.conexxus.get_postpay_discount_for_item(message, sale_item)
    assert discount is not None, f"Cannot find postpay discount for (sale_item) in {request_name}"
    amount = context.sit_product.eps.conexxus.get_item_adjusted_unit_price(discount)

    assert Decimal(amount).quantize(dec_adjusted_unit_price) == dec_adjusted_unit_price, f"{request_name} message amount {amount} doesn't match given amount {adjusted_unit_price}"


@then('"{request_name}" message contains sale item "{sale_item}" with OriginalAmount/UnitPrice "{original_unitprice}"')
def step_impl(context: Context, request_name: str, sale_item: str, original_unitprice: str):
    """Verify that the MobileFinalizeRequest contains correct original unit price for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * Original UnitPrice Value

    :param context: Behave context.
    """
    dec_orig_unitprice = Decimal(original_unitprice)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    unit_price =  context.sit_product.eps.conexxus.get_original_unitprice(message, sale_item)
    assert Decimal(unit_price).quantize(dec_orig_unitprice) == dec_orig_unitprice,\
        f"{request_name} message unit price {unit_price} doesn't match given unit price {original_unitprice}"


@then('"{request_name}" message contains sale item "{sale_item}" with AdjustedAmount/Amount "{adjusted_amount}"')
def step_impl(context: Context, request_name: str, sale_item: str, adjusted_amount: str):
    """Verify that the MobileFinalizeRequest contains correct original amount for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * Adjusted Amount Value

    :param context: Behave context.
    """
    dec_adjusted_amount = Decimal(adjusted_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    amount =  context.sit_product.eps.conexxus.get_adjusted_amount(message, sale_item)
    assert Decimal(amount).quantize(dec_adjusted_amount) == dec_adjusted_amount,\
        f"{request_name} message adjusted amount {amount} doesn't match given adjusted amount {adjusted_amount}"


@then('"{request_name}" message contains sale item "{sale_item}" with AdjustedAmount/UnitPrice "{adjusted_unitprice}"')
def step_impl(context: Context, request_name: str, sale_item: str, adjusted_unitprice: str):
    """Verify that the MobileFinalizeRequest contains correct adjusted unit price for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * Adjusted UnitPrice Value

    :param context: Behave context.
    """
    dec_adjusted_unitprice = Decimal(adjusted_unitprice)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    unit_price =  context.sit_product.eps.conexxus.get_adjusted_unitprice(message, sale_item)
    assert Decimal(unit_price).quantize(dec_adjusted_unitprice) == dec_adjusted_unitprice,\
        f"{request_name} message adjusted unit price {unit_price} doesn't match given adjusted unit price {adjusted_unitprice}"


@then('"{request_name}" message contains sale item "{sale_item}" with Quantity "{quantity}"')
def step_impl(context: Context, request_name: str, sale_item: str, quantity: str):
    """Verify that the MobileFinalizeRequest contains correct quantity for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * Quantity Value

    :param context: Behave context.
    """
    dec_quantity = Decimal(quantity)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_quantity =  context.sit_product.eps.conexxus.get_quantity(message, sale_item)
    assert Decimal(message_quantity).quantize(dec_quantity) == dec_quantity,\
        f"{request_name} message quantity {message_quantity} doesn't match given quantity {quantity}"


@then('"{request_name}" message has finalAmount "{final_amount}"')
def step_impl(context: Context, request_name: str, final_amount: str):
    """Verify that the MobileFinalizeRequest contains correct finalAmount.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * finalAmount Value

    :param context: Behave context.
    """
    
    dec_final_amount = Decimal(final_amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_finalAmount =  context.sit_product.eps.conexxus.get_finalamount(message)
    assert Decimal(message_finalAmount).quantize(dec_final_amount) == dec_final_amount,\
        f"{request_name} message final amount {message_finalAmount} doesn't match given final amount {final_amount}"


@then('"{request_name}" message contains PriceAdjustment under sale item "{sale_item}" with Amount "{amount}"')
def step_impl(context: Context, request_name: str, sale_item: str, amount: str):
    """Verify that the MobileFinalizeRequest contains correct PriceAdjustment amount for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * PriceAdjustment Amount Value

    :param context: Behave context.
    """
    dec_amount = Decimal(amount)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_amount =  context.sit_product.eps.conexxus.get_priceAdjustment_amount(message, sale_item)
    assert Decimal(message_amount).quantize(dec_amount) == dec_amount,\
        f"{request_name} message price adjustment amount {message_amount} doesn't match given price adjustment amount {amount}"


@then('"{request_name}" message contains PriceAdjustment under sale item "{sale_item}" with UnitPrice "{unitprice}"')
def step_impl(context: Context, request_name: str, sale_item: str, unitprice: str):
    """Verify that the MobileFinalizeRequest contains correct PriceAdjustment unitprice for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * PriceAdjustment Unit Price Value

    :param context: Behave context.
    """
    dec_unitprice = Decimal(unitprice)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_unitprice =  context.sit_product.eps.conexxus.get_priceAdjustment_unitprice(message, sale_item)
    assert Decimal(message_unitprice).quantize(dec_unitprice) == dec_unitprice,\
        f"{request_name} message price adjustment unit price {message_unitprice} doesn't match given price adjustment unit price {unitprice}"


@then('"{request_name}" message contains PriceAdjustment under sale item "{sale_item}" with Quantity "{quantity}"')
def step_impl(context: Context, request_name: str, sale_item: str, quantity: str):
    """Verify that the MobileFinalizeRequest contains correct PriceAdjustment unitprice for specific sale item.
    The value found in the message is first rounded to the same number of decimal places as 
    the value provided in the invocation, and then compared

    This step expects the following context values.

    * Sale Item Description
    * PriceAdjustment Quantity Value

    :param context: Behave context.
    """
    dec_quantity = Decimal(quantity)
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_quantity =  context.sit_product.eps.conexxus.get_priceAdjustment_quantity(message, sale_item)
    assert Decimal(message_quantity).quantize(dec_quantity) == dec_quantity,\
        f"{request_name} message price adjustment unit price {message_quantity} doesn't match given price adjustment unit price {quantity}"


@then('"{request_name}" message contains PriceAdjustment under sale item "{sale_item}" with RebateLabel "{rebatelabel}"')
def step_impl(context: Context, request_name: str, sale_item: str, rebatelabel: str):
    """Verify that the MobileFinalizeRequest contains correct PriceAdjustment Rebate Label for specific sale item.

    This step expects the following context values.

    * Sale Item Description
    * PriceAdjustment Rebate Label Value

    :param context: Behave context.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_rebatelabel =  context.sit_product.eps.conexxus.get_rebatelabel(message, sale_item)
    assert message_rebatelabel == rebatelabel,\
        f"{request_name} message price adjustment rebate label {message_rebatelabel} doesn't match given price adjustment rebate label {rebatelabel}"


@then('"{request_name}" message contains sale item "{sale_item}"')
def step_impl(context: Context, request_name: str, sale_item: str):
    """Verify that the MobileFinalizeRequest contains the specific sale item.

    This step expects the following context values.

    * Sale Item Description

    :param context: Behave context.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    assert context.sit_product.eps.conexxus.has_saleitem(message, sale_item), "{request_name} message doesn't contain {sale_item}"


@then('"{request_name}" message contains carwash item "{sale_item}" with carwash code and expiration elements')
def step_impl(context: Context, request_name: str, sale_item: str):
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    assert context.sit_product.eps.conexxus.has_carwash_details(message, sale_item), "{sale_item} item in {request_name} message doesn't contain carwash details"


@then('"{request_name}" message contains car wash code "{carwash_code}" for sale item "{sale_item}"')
def step_impl(context: Context, request_name: str, sale_item: str, carwash_code: str):
    """Verify that the MobileFinalizeRequest contains correct quantity for specific sale item.

    This step expects the following context values.

    * Sale Item Description
    * Quantity Value

    :param context: Behave context.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_carwash_code =  context.sit_product.eps.conexxus.get_carWashcode(message, sale_item)
    assert message_carwash_code == carwash_code,\
        f"{request_name} message car wash code {message_carwash_code} doesn't match given car wash code {carwash_code}"


@then('"{request_name}" message contains car wash code expiration date "{carwash_code_expiration_date}" for sale item "{sale_item}"')
def step_impl(context: Context, request_name: str, sale_item: str, carwash_code_expiration_date: str):
    """Verify that the MobileFinalizeRequest contains correct quantity for specific sale item.

    This step expects the following context values.

    * Sale Item Description
    * Quantity Value

    :param context: Behave context.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message = context.sit_product.eps.conexxus.get_message(eps_tran_number, request_name)
    assert message is not None, f"{request_name} message is None"

    message_carwash_code_expiration_date =  context.sit_product.eps.conexxus.get_carWashExpirationDate(message, sale_item)
    assert message_carwash_code_expiration_date == carwash_code_expiration_date,\
        f"{request_name} message car wash code expiration date {message_carwash_code_expiration_date} doesn't match given car wash code expiration date {carwash_code_expiration_date}"


@then('the Epsilon sends finalize request to Conexxus host')
def step_impl(context):
    """Verify that the MobileFinalizeRequest exists in journal.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message, success = utility.wait_until(
        poll =lambda: context.sit_product.eps.conexxus.get_message(eps_tran_number, "MobileFinalizeRequest"),
        sentinel = lambda msg: msg is not None,
        attempts = 240,
        delay = 0.5,
        timeout = 120
    )

    if not success:
        raise TimeoutError(f"Timed out waiting for MobileFinalizeRequest to apper in JournalCONMOB for Epsilon transaction {eps_tran_number}")
    
@then('the Epsilon sends loyalty award request to Conexxus host')
def step_impl(context):
    """Verify that the MobileLoyaltyAwardRequest exists in journal.
    """
    eps_tran_number = context.sit_product.get_last_epsilon_transaction_number()

    message, success = utility.wait_until(
        poll =lambda: context.sit_product.eps.conexxus.get_message(eps_tran_number, "MobileLoyaltyAwardRequest"),
        sentinel = lambda msg: msg is not None,
        attempts = 240,
        delay = 0.5,
        timeout = 120
    )

    if not success:
        raise TimeoutError(f"Timed out waiting for MobileLoyaltyAwardRequest to apper in JournalCONMOB for Epsilon transaction {eps_tran_number}")

# endregion