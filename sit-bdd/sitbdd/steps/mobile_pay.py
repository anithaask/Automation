import time

from behave import given, when, then

from behave.runner import Context
from sitbdd.sitcore.bdd_utils import utility
from cfrpos.core.pos.ui_metadata import POSFrame, POSButton


# region Given clauses
# deprecated, do not use in new features
@given("the Mobile Pay host does not prompt for access code")
def step_impl(context: Context):
    context.sit_product.eps.prompt_for_access_code(False)


# deprecated, do not use in new features
@given("Mobile Pay host prompts for access code")
def step_impl(context: Context):
    context.sit_product.eps.prompt_for_access_code(True)


@given('the pump "{pump_number:d}" was successfully reserved')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the Mobile Pay host tries to reserve the pump "{pump_number}"
        Then the fuel controller sends approval for reserve pump request to credit controller for pump "{pump_number}"
        '''
        )


@given('the pump "{pump_number:d}" was successfully reserved without access code')
def step_impl(context: Context, pump_number: int):
    context.sit_product.eps.prompt_for_access_code(False)
    context.execute_steps(
        f'''
        When the Mobile Pay host tries to reserve the pump "{pump_number}"
        Then the fuel controller sends approval for reserve pump request to credit controller for pump "{pump_number}"
        '''
    )


@given('the pump "{pump_number:d}" was successfully reserved with access code')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        Given Mobile Pay host prompts for access code
        When the Mobile Pay host tries to reserve the pump "{pump_number}"
        Then the fuel controller sends approval for reserve pump request to credit controller for pump "{pump_number}"
        '''
    )


# unused
@given('a request to reserve the pump "{pump_number:d}" was rejected')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the Mobile Pay host tries to reserve the pump "{pump_number}"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "{pump_number}"
        '''
    )


@given('the pump "{pump_number:d}" was authorized by the Mobile Pay host')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        Given the configured prompt "CREDITAUTH" was displayed on pump "{pump_number}"
        When the Mobile Pay host tries to authorize the pump "{pump_number}"
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Credit Auth",
        attempts=30,
    )


# unused
@given('the pump "{pump_number:d}" was authorized for Mobile Pay transaction with loyalty')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        Given the configured prompt "CREDITAUTH" was displayed on pump "{pump_number}"
        When the pump "{pump_number}" is authorized for Mobile Pay transaction with loyalty
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Credit Auth",
        attempts=30,
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Please Wait",
        attempts=30,
    )

    expected_display = ["Would you like   to accept a", "PLEASE ENTER    ACCESS CODE"]

    # Expecting two possible prompts so we need to check for both
    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    assert current_display in expected_display, f"Expected display {expected_display} does not contain {current_display}"


@given('the pump "{pump_number:d}" was authorized for Mobile Pay transaction with invalid loyalty')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        Given the configured prompt "CREDITAUTH" was displayed on pump "{pump_number}"
        When the pump "{pump_number}" is authorized for Mobile Pay transaction with invalid loyalty
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Credit Auth",
        attempts=30,
    )

    expected_display = ["Lift Handle", "PLEASE ENTER    ACCESS CODE"]

    # Expecting two possible prompts so we need to check for both
    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    assert current_display in expected_display, f"Expected display {expected_display} does not contain {current_display}"


# unused
@given('the Mobile Pay host successfully requested available products export for the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the Mobile Pay host requests available products export
        Then the pump "{pump_number}" is reported as available in credit controller product export
        '''
    )


# unused
@given('the Mobile Pay host unsuccessfully requested available products export for the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the Mobile Pay host requests available products export
        Then the pump "{pump_number}" is reported as unavailable in credit controller product export
        '''
    )


@given('the correct access code was entered on pump "{pump_number:d}" keypad')
def step_impl(context: Context, pump_number: int):
    context.execute_steps(
        f'''
        When the customer presses "123456E" key on pump "{pump_number}" keypad
        '''
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "PLEASE ENTER    ACCESS CODE*****",
        attempts=30,
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Credit Auth",
        attempts=30,
    )

    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        "Please Wait",
        attempts=30,
    )

    expected_display = ["Would you like   to accept a", "Lift Handle"]

    # Expecting two possible prompts so we need to check for both
    current_display = context.sit_product.simpumps.get_current_display(pump_number)
    assert current_display in expected_display, f"Expected display {expected_display} does not contain {current_display}"

# endregion


# region When clauses
@when('the Mobile Pay host tries to reserve the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    time.sleep(1)
    context.sit_product.eps.reserve_mobile_pay(pump_number)


@when('the Mobile Pay host tries to authorize the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    # context.sit_product.eps.authorize_mobile_pay(pump_number)
    # # Request a way to find the transaction id of a sale that occurs on the pump from the Fuel BDD team.
    # context.credit_transaction_id = context.sit_product.fuel.get_credit_transaction_id(pump_number)
    pass


@when('the pump "{pump_number:d}" is authorized for Mobile Pay transaction with loyalty')
def step_impl(context: Context, pump_number: int):
    # context.sit_product.eps.authorize_mobile_pay(pump_number, context.sit_product.card_deck.get_barcode("loyalty"), "barcode")
    # # Request a way to find the transaction id of a sale that occurs on the pump from the Fuel BDD team.
    # context.credit_transaction_id = context.sit_product.fuel.get_credit_transaction_id(pump_number)
    pass


@when('the pump "{pump_number:d}" is authorized for Mobile Pay transaction with invalid loyalty')
def step_impl(context: Context, pump_number: int):
    # context.sit_product.eps.authorize_mobile_pay(pump_number, context.sit_product.card_deck.get_barcode("loyalty_bad"), "barcode")
    # # Request a way to find the transaction id of a sale that occurs on the pump from the Fuel BDD team.
    # context.credit_transaction_id = context.sit_product.fuel.get_credit_transaction_id(pump_number)
    pass


@when('the Mobile Pay host releases the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    context.sit_product.eps.release_mobile_pay(pump_number)


# deprecated, do not use in new features
@when('the Mobile Pay host requests available products export')
def step_impl(context: Context):
    context.sit_product.eps_product_export = context.sit_product.eps.export_available_products()


@when('the cashier presses mobile pay tender button')
def step_impl(context: Context):
    context.sit_product.pos.press_button_on_frame(POSFrame.MAIN, POSButton.TENDER_MOBILE_PAY_NO_EXTERNAL_ID)


@when('the cashier scans a QR code "{qrcode}" on Please scan mobile wallet QR code frame')
def step_impl(context: Context, qrcode: str):
    context.execute_steps('''when the cashier presses mobile pay tender button''')
    context.sit_product.pos.wait_for_frame_open(POSFrame.ASK_MOBILE_QR_BARCODE_SCAN)
    context.sit_product.pos.scan_item_barcode(barcode=qrcode, barcode_type='QR_CODE')
# endregion


# region Then clauses
# deprecated, do not use in new features
@then('Mobile PAP receipt is sent to credit controller')
def step_impl(context: Context):
    credit_receipt = context.sit_product.eps.get_receipt(context.credit_transaction_id)
    assert credit_receipt is not None


# deprecated, do not use in new features
@then('Mobile PAP transaction is captured in credit controller')
def step_impl(context: Context):
    def verify_mobile_PAP_transaction(tran_status):
        if (
            tran_status is not None
            and tran_status.complete
            and tran_status.captured
            and tran_status.approved
        ):
            if tran_status.mobile_pay_pap:
                return True
            else:
                raise RuntimeError(
                    "Transaction was approved, captured, and complete "
                    "but was not a MobilePay PAP"
                )
        return False

    tran_status, success = utility.wait_until(
        lambda: context.sit_product.eps.get_transaction_status(context.credit_transaction_id),
        verify_mobile_PAP_transaction,
        240,
        0.5,
        timeout=120
    )

    if not success:
        raise TimeoutError("Timed out waiting for EPS transaction to be in the correct state")


@then('the pumps available to start transactions are reported as available in credit controller product export')
def step_impl(context: Context):
    context.sit_product.verify_available_pumps_reported_in_credit_controller_product_export()


@then('the fuel controller sends approval for reserve pump request to credit controller for pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    is_pump_tran_approved = context.sit_product.eps.get_mobile_pay_reserve_pump_transaction_status(pump_number)
    assert is_pump_tran_approved, "Pump reserve request was not approved"


# deprecated, do not use in new features
@then('fuel controller sends approval for reserve pump request to credit controller')
def step_impl(context: Context):
    is_pump_tran_approved = context.sit_product.eps.is_mobile_pay_reserve_pump_transaction_approved(
        context.pump_number
    )
    assert is_pump_tran_approved, "Pump reserve request was not approved"


@then('the fuel controller sends rejection for reserve pump request to credit controller for the pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    is_pump_tran_approved = context.sit_product.eps.get_mobile_pay_reserve_pump_transaction_status(pump_number)
    assert not is_pump_tran_approved, "Pump reserve request was not rejected"


# deprecated, do not use in new features
@then('fuel controller sends rejection for reserve pump request to credit controller')
def step_impl(context: Context):
    is_pump_tran_approved = context.sit_product.eps.is_mobile_pay_reserve_pump_transaction_approved(
        context.pump_number
    )
    assert not is_pump_tran_approved, "Pump reserve request was not rejected"


@then('the pump "{pump_number:d}" is reported as available in credit controller product export')
def step_impl(context: Context, pump_number: int):
    if not hasattr(context, "eps_product_export"):
        context.sit_product.eps_product_export = context.sit_product.eps.export_available_products()

    export = context.sit_product.eps_product_export
    assert export.verify_icr_availability(pump_number, True), f"Pump {pump_number} was not reported as available in credit controller product export"


@then('the pump "{pump_number:d}" is reported as unavailable in credit controller product export')
def step_impl(context: Context, pump_number: int):
    if not hasattr(context, "eps_product_export"):
        context.sit_product.eps_product_export = context.sit_product.eps.export_available_products()

    export = context.sit_product.eps_product_export
    assert export.verify_icr_availability(pump_number, False), f"Pump {pump_number} was not reported as unavailable in credit controller product export"


# deprecated, do not use in new features
@then('the captured credit transaction has {entry_method} entry method')
def step_impl(context: Context, entry_method):
    """
    :param entry_method: Expected credit entry method. Possible values include
     manual
     swipe
     mobile wallet  # This is used to check a Mobile Pay transaction
    """
    tran_status = context.sit_product.eps.get_transaction_status(context.credit_transaction_id)
    assert tran_status is not None

    if not tran_status.complete or not tran_status.captured or not tran_status.approved:
        context.execute_steps(
            '''
            Then Mobile PAP transaction is captured in credit controller
            '''
        )
        #  Get transaction again since it's been updated in EPS
        tran_status = context.sit_product.eps.get_transaction_status(context.credit_transaction_id)
        assert tran_status is not None

    assert tran_status.entry_method.lower() == entry_method.lower()


@then('the export with items available to sell by the fuel controller is sent to the credit controller')
def step_impl(context: Context):
    pass
    # # Just like with carwash items for sale should be set up in given and values from the given can be used here.
    # item_list = context.sit_product.fuel.get_items(None)

    # assert len(item_list) > 0

    # if not hasattr(context, "eps_product_export"):
    #     context.sit_product.eps_product_export = context.sit_product.eps.export_available_products()

    # # Will raise errors internally if something goes wrong
    # context.sit_product.eps_product_export.verify_items_in_export(item_list)

# endregion
