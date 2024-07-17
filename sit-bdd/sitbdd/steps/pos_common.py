import re
import time
import math

from behave import given, when, then

from cfrpos.core.bdd_utils.errors import ProductError as POSProductError
from cfrpos.core.pos.ui_metadata import POSButton
from cfrpos.core.pos.ui_metadata import POSFrame
from cfrpos.core.bdd_utils.receipt_comparer import compare_receipts
from cfrsmtaskman.core.bdd_utils.errors import ProductError as SMTaskManProductError

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils import pos_utilities


# region Given clauses
@given('the cashier locked the POS')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier locks the POS
        '''
    )
    context.sit_product.pos.wait_for_frame_open(POSFrame.TERMINAL_LOCK)


@given('the cashier unlocked the POS')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier unlocks the POS
        '''
    )
    context.sit_product.pos.wait_for_frame_open(POSFrame.MAIN)


@given('the "{user}" entered pin on Ask security override frame')
def step_impl(context: Context, user: str):
    context.sit_product.pos.wait_for_frame_open(POSFrame.ASK_SECURITY_OVERRIDE)
    context.sit_product.pos.press_digits(POSFrame.ASK_SECURITY_OVERRIDE, context.sit_product.config["nodes"]["rcm"]["rcm_users"][user.lower()])
    context.sit_product.pos.press_button_on_frame(POSFrame.ASK_SECURITY_OVERRIDE, POSButton.ENTER)


@given('the cashier navigates to Tank Inventory Levels frame')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier navigates to the other functions frame
        And the cashier presses the "tank-inv-level" button
        '''
    )
    context.sit_product.pos.wait_for_frame_open(POSFrame.TANK_INVENTORY_LEVELS)


@given('the cashier added a ${money_order_amount:f} money order to the transaction')
def step_impl(context: Context, money_order_amount: float):
    context.execute_steps(
        f'''
        When the cashier adds a ${money_order_amount} money order to the transaction
        '''
    )

    # Verify Money Order is in transaction
    context.sit_product.pos.verify_virtual_receipt_contains_item("Money Order", money_order_amount)


@given('the cashier failed to add a money order to the transaction')
def step_impl(context: Context):
    context.execute_steps(
        f'''
        When the cashier presses the "sell-money-order" button
        Then the POS displays the "Item not allowed." frame
        '''
    )


@given('a refund transaction was denied')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier starts a refund transaction
        Then the POS displays the "REFUND NOT ALLOWED" frame
        '''
    )


@given('the cashier started a refund transaction')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier starts a refund transaction
        Then the POS displays the "main" frame
        '''
    )


@given('the cashier voided item "{item_name}"')
def step_impl(context: Context, item_name: str):
    context.sit_product.pos.void_item(item_name=item_name)
    assert not context.sit_product.pos.verify_virtual_receipt_contains_item(item_name), f'Item "{item_name}" still in transaction after voiding'


@given('an attempt to void item "{item_name}" was denied')
def step_impl(context: Context, item_name: str):
    context.sit_product.pos.void_item(item_name=item_name)
    context.execute_steps(
        f'''
        Then the POS displays the "CANCEL NOT ALLOWED FOR ITEM" frame
        '''
    )
    # Navigate back from error frame
    context.sit_product.pos.press_goback_on_current_frame()


@given('the cashier navigated to the main frame')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier navigates to the main frame
        Then the POS displays the "main" frame
        '''
    )


@given('the cashier navigated to the other functions frame')
def step_impl(context: Context):
    context.execute_steps('When the cashier navigates to the other functions frame')
    context.sit_product.pos.wait_for_frame_open(POSFrame.OTHER_FUNCTIONS)


@given('the cashier added item "{item_name}" to the transaction')
def step_impl(context: Context, item_name: str):
    context.execute_steps(
        f'''
        When the cashier adds item "{item_name}"
        '''
    )


@given('an item "{item_name}" is present in the transaction "{item_count:d}" times')
def step_impl(context: Context, item_name: str, item_count: int):
    count = int(item_count)
    while count > 0:
        context.sit_product.pos.press_item_button(context.sit_product.mapping.get_sale_items_remap(item_name))
        context.sit_product.pos.wait_for_item_added(context.sit_product.mapping.get_sale_items_remap(item_name))
        count = count - 1


@given('the cashier added Rest in gas on the POS for the pump "{pump_number:d}" to the transaction')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the cashier selects the pump "{pump_number}"
        And the cashier presses the "prepay-cancel-prepay" button
        And the cashier presses the "rest-in-gas" button
        '''
    )


@given('the cashier tendered the transaction with ${amount:g} in cash')
def step_impl(context: Context, amount: float):
    context.execute_steps(
        f'''
        When the cashier tenders the transaction with ${amount} in cash
        Then the POS displays the "main" frame
        '''
    )


@given('the manager tendered the transaction with ${amount:g} in cash')
def step_impl(context: Context, amount: float):
    context.execute_steps(
        f'''
        When the cashier tenders the transaction with ${amount} in cash
        Given the "manager" entered pin on Ask security override frame
        Then the POS displays the "main" frame
        '''
    )


@given('the cashier navigated to the POS scroll previous frame')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier navigates to the POS scroll previous frame
        '''
    )


@given('the POS displays Other functions frame')
def step_impl(context: Context):
    context.sit_product.pos.press_button_on_frame(POSFrame.RECEIPT, POSButton.OTHER_FUNCTIONS)


@given('a coupon "{coupon}" is present in the transaction')
def step_impl(context: Context, coupon: str):
    context.execute_steps(
        f'''
        When the cashier navigates to the coupon lookup frame
        And the cashier selects "{coupon}" from the list
        And the cashier presses the "enter" button
        '''
    )


@given('the cashier tendered the transaction for exact dollar with tender type "{tender_type}"')
def step_impl(context: Context, tender_type: str):
    try:
        context.sit_product.pos.tender_transaction(tender_type.lower(), f"{tender_type}-tender")
    except AssertionError:
        # If the tender attempt fails, attempt to process loyalty
        # and continue with tender step.
        utility.wait_for_frame_name(context.sit_product.pos, "tender-dynamic-get-a", 30)
        time.sleep(2)
        # should be replaced with timeout
        # timeout for items in vr to change names
        context.execute_steps('When the cashier presses the "exact-dollar" button')
        context.sit_product.pos.wait_for_frame_open(POSFrame.WAIT_CREDIT_PROCESSING)

    context.sit_product.pos.control.wait_for_transaction_end()


@given('the cashier added a container deposit to the transaction')
def step_impl(context: Context):
    context.execute_steps("When the cashier adds a container deposit to the transaction")
    context.sit_product.pos.wait_for_item_added_to_VR("Deposit (for Co")


@given('the cashier added a lottery redemption item to the transaction for ${amount:f}')
def step_impl(context: Context, amount: float):
    context.execute_steps(
        f'''
        When the cashier adds a lottery redemption item to the transaction for ${amount}"
        '''
    )
    context.sit_product.pos.wait_for_item_added_to_VR("PDI Instant Lot")


@given('the cashier added carwash "{item_name}" to the transaction')
def step_impl(context: Context, item_name: str):
    context.execute_steps(
        f'''
        When the cashier adds carwash "{item_name}"
        '''
    )
    context.sit_product.pos.wait_for_item_added_to_VR(item_name)


@given('cashier performed a "{tender_type}" Pay In with amount of "{amount:f}"')
def step_impl(context: Context, tender_type: str, amount: float):
    context.sit_product.pos.pay_in_transaction(amount, tender_type, f'{tender_type}-tender')
    context.execute_steps(f'''Then an item "{tender_type}" with price of "{amount}" is in the "previous" transaction''')


@given('cashier performed a "{tender_type}" Pay Out with amount of "{amount:f}"')
def step_impl(context: Context, tender_type: str, amount: float):
    context.sit_product.pos.pay_out_transaction(amount, tender_type, f'{tender_type}-tender')
    context.execute_steps(f'''Then an item "{tender_type}" with price of "{amount}" is in the "previous" transaction''')


@given('the cashier navigated to the Pay Out reason frame')
def step_impl(context: Context):
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.PAY_OUT)
    context.sit_product.pos.wait_for_frame_open(POSFrame.ASK_REASON_AND_TENDER)


@given('the cashier performed a Pay Out in the middle of a transaction')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.PAY_OUT)
    context.execute_steps('Then the POS displays the "TRANSACTION ALREADY IN PROG" frame')


@given('the cashier ended the shift')
def step_impl(context: Context):
    context.execute_steps('When the cashier ends the shift')
    context.sit_product.pos.wait_for_frame_open(POSFrame.START_SHIFT)


@given('the cashier started the shift')
def step_impl(context: Context):
    context.execute_steps('When the cashier starts the shift')
    context.sit_product.pos.ensure_ready_to_sell(operator_pin=context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"])
    context.sit_product.pos.wait_for_frame_open(POSFrame.MAIN)


@given('the cashier added the discount "{discount}"')
def step_impl(context: Context, discount: str):
    context.execute_steps(
        f'''
        When the cashier navigates to the discount lookup frame
        And the cashier selects discount "{discount}" from the list 
        And the cashier presses the "enter" button
        And the cashier presses the "go-back" button
        And the cashier presses the "go-back" button
        '''
    )
# endregion


# region When clauses
@when('the cashier tenders the transaction with ${amount:g} in cash')
def step_impl(context: Context, amount: float):
    context.sit_product.pos.tender_transaction("cash", "cash-tender", amount)


@when('the cashier tenders the transaction for ${amount:g} with tender type "{tender_type}"')
def step_impl(context: Context, amount: float, tender_type: str):
    context.sit_product.pos.tender_transaction(tender_type.lower(), f"{tender_type}-tender", amount)


@when('the cashier adds item "{item_name}"')
def step_impl(context: Context, item_name: str):
    context.sit_product.pos.press_item_button(context.sit_product.mapping.get_sale_items_remap(item_name))


@when('the cashier adds carwash "{item_name}"')
def step_impl(context: Context, item_name: str):
    context.sit_product.pos.press_button_on_frame(POSFrame.MAIN, POSButton.SELL_CARWASH)
    button = item_name.replace(' ', '-').lower()
    context.sit_product.pos.press_button_on_frame(POSFrame.ASK_CARWASH_SALE_SELECT, button)
    
    frame = context.sit_product.pos.control.get_menu_frame()
    #not using POSFrame.ASK_SELL_CARWASH_WITHOUT_CODE because current SIT config displays 'Invalid Wash Number.' title
    if frame.name == 'common-yes/no':
        context.sit_product.pos.control.press_button(frame.instance_id, POSButton.YES.value)


@when('the cashier navigates to the POS scroll previous frame')
def step_impl(context: Context):
    time.sleep(3)  # Wait for transaction/prepay finalization
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, "scroll-prev-transaction")
    utility.wait_for_frame_name(context.sit_product.pos, "other-pap-history")


@when('the cashier presses Pay In button on other functions frame')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.PAY_IN)


@when('the cashier presses Pay Out button on other functions frame')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.PAY_OUT)


@when('the cashier performs a "{tender_type}" Pay In with amount of "{amount:f}"')
def step_impl(context: Context, tender_type: str, amount: float):
    context.sit_product.pos.pay_in_transaction(amount, tender_type, f'{tender_type}-tender')


@when('the cashier performs a "{tender_type}" Pay Out with amount of "{amount:f}"')
def step_impl(context: Context, tender_type: str, amount: float):
    context.sit_product.pos.pay_out_transaction(amount, tender_type, f'{tender_type}-tender')


@when('the cashier navigates to the other functions frame')
def step_impl(context: Context):
    context.sit_product.pos.press_button_on_frame(POSFrame.RECEIPT, POSButton.OTHER_FUNCTIONS)


@when('the cashier navigates to the main frame')
def step_impl(context: Context):
    """
    Prompts presented while navigating back will be answered with negative values
    such as "No", default value for numeric input, etc.
    """
    context.sit_product.pos.return_to_mainframe()


@when('the cashier tries to refund the most recent fuel transaction')
def step_impl(context: Context):
    """
    When prompted for a reason, the first reason in the list will be selected.
    """
    # Press "Refund Fuel" button.
    context.sit_product.pos.press_button_on_frame(POSFrame.SCROLL_PREVIOUS_FRAME, POSButton.REFUND_FUEL)

    # Select first reason from the list.
    context.sit_product.pos.select_item_in_list(POSFrame.ASK_FOR_A_REASON, item_position=0)

    frame = utility.wait_for_frame_name(context.sit_product.pos, "common-yes/no")
    # Press "Yes" button to continue.
    context.sit_product.pos.control.press_button(frame.instance_id, POSButton.YES.value)


@when('the cashier presses the "{button_name}" button')
def step_impl(context: Context, button_name: str):
    # POS buttons "Pay 1" and "Pay 2" may be greyed out if the pumps aren't connected.
    # POS will allow pressing them, but will have no effect.
    menu_frame = utility.wait_for_pos_button_presence(context.sit_product.pos, button_name)
    context.sit_product.pos.control.press_button(menu_frame.instance_id, button_name)


@when('the cashier selects "{item_name}" from the list')
def step_impl(context: Context, item_name: str):
    context.sit_product.pos.select_item_in_list(item_name=item_name)


@when('the cashier adds a ${money_order_amount:f} money order to the transaction')
def step_impl(context: Context, money_order_amount: float):
    context.execute_steps(
        f'''
        When the cashier presses the "sell-money-order" button
        And the cashier inputs ${money_order_amount}
        '''
    )
    # respond to "is the following amount correct?" prompt
    frame = utility.wait_for_frame_name(context.sit_product.pos, "common-yes/no")
    context.sit_product.pos.control.press_button(frame.instance_id, POSButton.YES.value)

    # respond to "money order fee will not be refunded, continue?" prompt
    # only applicable when the following POS option is set
    # | option_name        | option | value_text         | value |
    # | Money order refund | 1305   | Refund amount only | 1     |
    frame = context.sit_product.pos.control.get_menu_frame()
    if frame.name == "common-yes/no":
        context.sit_product.pos.control.press_button(frame.instance_id, POSButton.YES.value)


@when('the cashier tenders the transaction for exact dollar with tender type "{tender_type}"')
def step_impl(context: Context, tender_type: str):
    try:
        context.sit_product.pos.tender_transaction(tender_type.lower(), f"{tender_type}-tender")
    except AssertionError:
        # If the tender attempt fails, attempt to process loyalty
        # and continue with tender step.
        utility.wait_for_frame_name(context.sit_product.pos, "tender-dynamic-get-a", 30)
        time.sleep(2)
        # should be replaced with timeout
        # timeout for items in vr to change names
        context.execute_steps('When the cashier presses the "exact-dollar" button')
        context.sit_product.pos.wait_for_frame_open(POSFrame.WAIT_CREDIT_PROCESSING)


@when('the cashier locks the POS')
def step_impl(context: Context):
    context.sit_product.pos.lock_pos()


@when('the cashier unlocks the POS')
def step_impl(context: Context):
    """
    This step uses the cashier PIN as defined in config.json when unlocking the POS.
    """
    context.sit_product.pos.unlock_pos(context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"])


@when('the cashier inputs ${pay_amount:g}')
def step_impl(context: Context, pay_amount: float):
    menu_frame = context.sit_product.pos.control.get_menu_frame()
    use_description = menu_frame.use_description
    # Appease the POSFrame type expectation.
    if any(x.value == use_description for x in POSFrame):
        digits_frame = POSFrame(use_description)
    else:
        digits_frame = use_description
    context.sit_product.pos.press_digits(digits_frame, pay_amount)
    context.sit_product.pos.press_enter_on_current_frame()


@when('the cashier inputs ${money_order_amount:f} as the money order amount')
def step_impl(context: Context, money_order_amount: float):
    context.execute_steps(
        f'''
        When the cashier inputs ${money_order_amount}
        And the cashier presses the "yes" button
        '''
    )


@when('the cashier manually enters "{barcode}"')
def step_impl(context: Context, barcode: str):
    """
    Requires the current POS menu frame to have digit keys.
    Contiguous numeric digits as barcode are considered valid and no actual standards
    such as EAN and UPC are followed.
    """
    if not re.match(r"^\d+$", barcode):
        raise ProductError(f'"{barcode}" is not a valid barcode.')

    menu_frame = context.sit_product.pos.control.get_menu_frame()
    for digit in barcode:
        context.sit_product.pos.control.press_button(menu_frame.instance_id, f"key-{digit}")
    context.sit_product.pos.press_enter_on_current_frame()


@when('the POS waits for an increase in the transaction item count')
def step_impl(context: Context):
    result, success = utility.wait_until(
        context.sit_product.pos.get_transaction_item_count,
        lambda x: x > 0,
        20,
        0.5
    )

    if not success:
        raise ProductError("POS timed out while waiting for increase in transaction item count")


@when('the cashier starts a refund transaction')
def step_impl(context: Context):
    """
    This step uses the first configured reason code when prompted
    for one on the POS and primes the POS to the point where it's
    ready to select the item to refund.
    """
    context.sit_product.pos.press_button_on_frame(POSFrame.RECEIPT, POSButton.OTHER_FUNCTIONS)
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.REFUND)
    context.sit_product.pos.press_button_on_frame(POSFrame.ASK_CONFIRM_REFUND, POSButton.YES)
    context.sit_product.pos.select_item_in_list(POSFrame.ASK_FOR_A_REASON, item_position=0)

    # respond to "money order fee will not be refunded, continue?" prompt
    # only applicable when the following POS option is set
    # | option_name        | option | value_text         | value |
    # | Money order refund | 1305   | Refund amount only | 1     |
    frame = context.sit_product.pos.control.get_menu_frame()
    if frame.name == "common-yes/no":
        context.sit_product.pos.control.press_button(frame.instance_id, POSButton.YES.value)

    # wait for a frame that needs to be handled for 5s (a simple if doesn't work here)
    try:
        utility.wait_for_frame_name(context.sit_product.pos, "tender-refund-verify")
        context.sit_product.pos.press_goback_on_current_frame()  # get out of "select refund tender" frame
        context.sit_product.pos.press_goback_on_current_frame()  # get out of "other functions" frame
    except ProductError:
        pass


@when('the cashier starts the shift')
def step_impl(context: Context):
    context.sit_product.pos.start_shift(operator_pin=context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"])


@when('the cashier ends the shift')
def step_impl(context: Context):
    context.sit_product.pos.end_shift(operator_pin=context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"], tender_for_safedrop="tender-cash-cash-tender")


@given('a new business day is started')
def step_impl(context: Context):
    context.execute_steps('When the cashier ends the current business day')
    context.sit_product.pos.ensure_ready_to_sell(operator_pin=context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"])


@when('the cashier ends the current business day')
def step_impl(context: Context):
    context.sit_product.pos.end_business_day(operator_pin=context.sit_product.config["nodes"]["rcm"]["rcm_users"]["cashier"], tender_for_safedrop="tender-cash-cash-tender")


@when('the cashier presses the "{alert_message}" alert on the menu bar')
def step_impl(context: Context, alert_message: str):
    pos_utilities.press_alert_on_menu_bar(context.sit_product.smtaskman, alert_message)


@when('the cashier adds a lottery redemption item to the transaction for ${amount:f}')
def step_impl(context: Context, amount: float):
    context.execute_steps(
        f'''
        When the cashier presses the "redeem-lotery" button
        And the cashier presses the "pdi-instant-lottery-tx" button
        And the cashier presses the "cash" button
        And the cashier inputs ${amount}
        And the cashier presses the "instant-approval" button
        '''
    )


@when('the cashier navigates to the coupon lookup frame')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, "coupon-lookup")
    utility.wait_for_frame_name(context.sit_product.pos, "tender-coupon")


@when('the cashier adds the coupon "{coupon}"')
def step_impl(context: Context, coupon: str):
    context.execute_steps(
        f'''
        When the cashier navigates to the coupon lookup frame
        And the cashier selects "{coupon}" from the list
        And the cashier presses the "enter" button
        '''
    )


@when('the cashier tries to refund postpay from pump "{pump_number:d}" on position "{position:d}"')
def step_impl(context: Context, pump_number: int, position: int):
    context.sit_product.pos.select_pump(pump_number)
    context.execute_steps(
        f'''
        When the cashier starts a refund transaction
        And the cashier presses the "pay{position}" button
        '''
    )


@when('the cashier adds a container deposit to the transaction')
def step_impl(context: Context):
    context.execute_steps(
        '''
        When the cashier navigates to the other functions frame
        And the cashier presses the "redeem-container-deposit" button
        And the cashier manually enters "2345"
        And the cashier presses the "manual-enter-bar-cod" button
        And the cashier manually enters "055555555550"
        '''
    )


@when('the cashier presses the "{button}" button on the other functions frame')
def step_impl(context: Context, button: str):
    context.execute_steps(
        f'''
        When the cashier navigates to the other functions frame
        And the cashier presses the "{button}" button
        '''
    )


@when('the cashier completes a money order vendor payout of ${amount:f}')
def step_impl(context: Context, amount: float):
    context.execute_steps(
        f'''
        When the cashier navigates to the other functions frame
        And the cashier presses the "money-order-vendor-pay-out" button
        And the cashier selects "RCM - Pay Out Money Order" from the list
        And the cashier inputs ${amount} as the money order amount
        '''
    )


@when('the cashier selects discount "{discount_name}" from the list')
def step_impl(context: Context, discount_name: str):
    context.sit_product.pos.select_item_in_list("select-discount", item_name=discount_name)


@when('the cashier navigates to the discount lookup frame')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the other functions frame")
    context.sit_product.pos.press_button_on_frame(POSFrame.OTHER_FUNCTIONS, POSButton.DISCOUNT_LOOKUP)
    utility.wait_for_frame_name(context.sit_product.pos, 'other-discounts')
# endregion


# region Then clauses
@then("the previous transaction's total is ${total:f}")
def step_impl(context: Context, total: float):
    transaction = context.sit_product.pos.get_previous_transaction()
    assert math.isclose(transaction.total, total, rel_tol=1e-5), f"The total of previous transaction is {transaction.total:.2f} instead of {total:.2f}"


@then('a loyalty discount "{discount_description}" with value of "{discount_value:f}" is in the "{transaction}" transaction')
def step_impl(context: Context, discount_description: str, discount_value: float, transaction: str):
    assert context.sit_product.pos.wait_for_item_added(description=discount_description, price=-discount_value, item_type=29, transaction=transaction),\
        f'A loyalty discount "{discount_description}" with value of "{discount_value}" was not added to "{transaction}" transaction'


@then('the POS displays the "{frame_name}" frame')
def step_impl(context: Context, frame_name: str):
    try:
        context.sit_product.pos.wait_for_frame_open(context.sit_product.mapping.get_pos_frames_remap(frame_name))
    except POSProductError:
        raise ProductError(f'POS did not display frame "{frame_name}"')


@then('a fuel item "{description}" with price "{price:f}" and volume "{volume:f}" is in the "{transaction}" transaction')
def step_impl(context: Context, description: str, price: float, volume: float, transaction: str):
    assert context.sit_product.pos.wait_for_item_added(
        description=description, price=price, quantity=volume, item_type=7, transaction=transaction
    ), f'A fuel item "{description}" with price "{price}" and volume "{volume}" was not added to "{transaction}" transaction'


@then('the first line in Scroll previous contains following elements')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the POS scroll previous frame")
    context.sit_product.pos.select_item_in_scroll_previous_list(position=0)
    selected_line = context.sit_product.pos.get_tran_param_from_scroll_previous_line()
    assert selected_line is not None, f"get_tran_param_from_scroll_previous_line was None"

    for row in context.table.rows:
        actual_row = str(getattr(selected_line, row.cells[0].replace(' ', '_')))
        assert actual_row == row.cells[1], f"The first line in Scroll previous doesn't contain {row.cells[1]}, contains {actual_row} instead"


@then('the scroll previous printed receipt contains')
def step_impl(context: Context):
    context.execute_steps("When the cashier navigates to the main frame")
    context.sit_product.verify_scroll_previous_printed_receipt_contains(context.table)


@then('the previous printed EOS report contains')
def step_impl(context: Context):
    context.sit_product.verify_printed_EOS_report_contains(context.table)


@then('the "{button_name}" button is not present on the current frame')
def step_impl(context: Context, button_name):
    if context.sit_product.pos.current_frame_has_button(POSButton(button_name)):
        raise ProductError(
            f"Current frame was not supposed to have button {button_name},"
            f" but button is present."
        )


@then('the tank inventory levels printed report contains')
def step_impl(context: Context):
    """
    This step must be accompanied by a table, as below. Note the actual
    receipt lines must be delimited by asterisks (*), as whitespace is
    sensitive.

    Then the tank inventory levels printed report contains
    | content                                    |
    | *         TANK INVENTORY LEVELS          * |
    | *----------------------------------------* |
    | *----------------------------------------* |
    | *Tank #:                                1* |
    | *Grade:                      UNL 91-ExtId* |
    """

    utility.require_table_headings(context.table, "line_number", "line")
    if not context.sit_product.pos.wait_for_receipt_count_increase(0):
        raise POSProductError("Receipt did not print.")

    receipt = context.sit_product.pos.get_latest_printed_receipt()
    if not receipt:
        raise ProductError("Printed receipt was empty.")
    receipt = receipt.split('<br/>')
    actual = []

    for row in context.table:
        actual.append(receipt[int(row["line_number"]) - 1])

    assert compare_receipts(context.table, actual, html=False), 'Receipts do not match'


@then('the "{alert_message}" alert is not shown on the menu bar')
def step_impl(context: Context, alert_message: str):
    pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "alerts")
    expected_button = {"Message": alert_message}
    attempts = 5
    delay = 1
    matching_button = pos_utilities.wait_for_roof_bar_button_absence(
        context.sit_product.smtaskman, expected_button, attempts=attempts, delay=delay
    )
    if matching_button is not None:
        raise SMTaskManProductError(
            f"{matching_button} was not absent within "
            f"{round(attempts * delay, 2)} seconds."
        )


@then('the "{alert_message}" alert is shown on the menu bar')
def step_impl(context: Context, alert_message: str):
    pos_utilities.set_roof_bar_frame(context.sit_product.smtaskman, "alerts")
    expected_button = {"Message": alert_message}
    attempts = 5
    delay = 1
    matching_button = pos_utilities.wait_for_roof_bar_button_presence(
        context.sit_product.smtaskman, expected_button, attempts=attempts, delay=delay
    )
    if matching_button is None:
        raise SMTaskManProductError(
            f"{expected_button} was not present within "
            f"{round(attempts * delay, 2)} seconds."
        )


@then('the transaction on POS is finalized')
def step_impl(context: Context):
    assert context.sit_product.pos.control.wait_for_transaction_end() is not None, f"Transaction on POS was not finalized"


@then('the transaction on POS is not finalized')
def step_impl(context: Context):
    assert context.sit_product.pos.control.wait_for_transaction_end(timeout=3) is None, f"Transaction on POS was finalized"


@then('sale item "{item}" is in the POS virtual receipt')
def step_impl(context: Context, item: str):
    assert context.sit_product.pos.verify_virtual_receipt_contains_item(item), f"POS virtual receipt does not contain {item}"


@then('tender "{tender_type}" is not added to POS virtual receipt')
def step_impl(context: Context, tender_type: str):
    assert not context.sit_product.pos.control.wait_for_tender_added(tender_type=tender_type, timeout=5), f'Tender "{tender_type}" was added to POS virtual receipt'


@then('the POS displays Transaction already in progress error')
def step_impl(context: Context):
    context.sit_product.pos.wait_for_frame_open(POSFrame.MSG_TRANSACTION_ALREADY_IN_PROG)


@then('an item "{description}" with price of "{price:f}" is in the "{transaction}" transaction')
def step_impl(context: Context, description: str, price: float, transaction: str):
    assert context.sit_product.pos.is_item_in_transaction(description=description, price=price, transaction=transaction),\
        f'Item "{description}" with price of "{price}" is not in the "{transaction}" transaction'
# endregion
