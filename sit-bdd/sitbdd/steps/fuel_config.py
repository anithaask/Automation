from behave import given, when, then

from behave.runner import Context
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils.errors import ProductError


# region Given clauses
# TODO: Implement via RCM API
@given('the fuel controller is configured to sell "{items}"')
def step_impl(context: Context, items):
    pass


# TODO: Implement via RCM API (auth_modes can be comma separated, eg.: Prepay,Postpay,ICR or single value, eg.: CLOSED)
@given('the pumps are configured for "{auth_modes}"')
def step_impl(context: Context, auth_modes):
    pass


# TODO: Implement via RCM API
@given('the pumps have the following timing events configured')
def step_impl(context: Context):
    """
    Given the pumps have the following timing events configured:
        | option  | value        |
        | RECEIPT | AFTERFUELING |
    """
    pass


@given('the configured prompt "{prompt_name}" was displayed on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_name: str, pump_number: int):
    context.execute_steps(
        f'''
        Then the configured prompt "{prompt_name}" is displayed on pump "{pump_number}"
        '''
    )


# unused
@given('the dynamic prompt "{prompt_text}" was displayed on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_text: str, pump_number: int):
    context.execute_steps(
        f'''
        Then the dynamic prompt {prompt_text} is displayed on pump {pump_number}
        '''
    )


# endregion


# region When clauses
# TODO: Implement via RCM API (auth_modes can be comma separated, eg.: Prepay,Postpay,ICR or single value, eg.: CLOSED)
@when('the fuel controller loads pump auth mode as "{mode}"')
def step_impl(context: Context, mode: str):
    pass


# endregion


# region Then clauses
@then('the pump "{pump_number:d}" displays welcome prompt')
def step_impl(context: Context, pump_number: int):
    context.sit_product.verify_pump_displayed_welcome_prompt(pump_number)


@then('the configured prompt "{prompt_name}" is not displayed on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_name: str, pump_number: int):
    """

    :param context:
    :param prompt_name: Acceptable values are AMOUNTTOOSMALL, ASKCHARGECOBRANDED,
    ASKDEBIT, ASKLOYALTY, ASKLOYALTYMOP, ASKWASH PROMPT, ATTENDANTBADPIN,
    ATTENDANTSIGNIN, ATTENDANTSIGNIN, BADCARDTYPE, BEGINFUELING, CANNOTCANCEL,
    CANNOTSWIPE, CANTINSERTLOYALTY, CARDDECLINED, CARDEXPIRED, CARDNOTREAD,
    CASHINSERTEDWAIT, CASHMAXMSG, CASHPAPGREETING, CASHWARNMSG, CHOOSEGRADE,
    CLOSED, CONGOFORCEFINALIZE, CONGOGREETING, CONGOREQUIRESPAP, CONGOWAITINGEND,
    CONGOWAITINGPROMPT, CREDITAUTH, CREDITDOWN, CURRENTCASHAMT, DEBITHOSTOFFLINE,
    DEBITNOTACCEPTED, FUELING, FULLAMTAPPROVED, FULLCASHPAID, FULLSERVEGREETING,
    GETCHANGE, GREETING, ICRGREETING, INSERTCARD, INSERTCASHPRESSENTER,
    INSERTLOYALTY, INSIDEAUTH, INVALIDCARD, INVALIDGRADE, LIMITEXCEEDED,
    LIMITREACHED, NO, NOCASHPAP, NOCHECKMOP, NOOPENSHIFT, NOPAP, NOPOSTPAY,
    NOPREPAY, PACDECLINED, PACGREETING, PACGREETINGCASH, PACGREETINGMOP,
    PACGREETINGPOSTPAY, PACREQUIRED, PAYCASHIER, PLEASEWAIT, PREPAYCOMPLETE,
    PREPAYGREETING, PREPAYICRGREETING, PRESSCANCEL, PUMP BUSY, PUMPOFFLINE,
    PUMPSTOPPED,  RCPT PRNTNG, RCPTPRINTED, RCPTPRINTEDCASH, RECEIPT PROMPT,
    RECEIPTFAIL, REINSERTCARD, REPLACENOZZLE, SALECANCELLED, SALETIMEDOUT,
    SEECASHIER, SELECTCARWASHNUMBER, SVCBALANCE, SVCHOSTOFFLINE, THANKS,
    WASH FAIL, Y/N, YES
    :return:
    """
    utility.wait_for_not_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        prompt_name,
        attempts=30,
        delay=1,
        timeout=30,
        exact_match=False,
    )


@then('the configured prompt "{prompt_name}" is displayed on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_name: str, pump_number: int):
    """

    :param context:
    :param prompt_name: Acceptable values are AMOUNTTOOSMALL, ASKCHARGECOBRANDED,
    ASKDEBIT, ASKLOYALTY, ASKLOYALTYMOP, ASKWASH PROMPT, ATTENDANTBADPIN,
    ATTENDANTSIGNIN, ATTENDANTSIGNIN, BADCARDTYPE, BEGINFUELING, CANNOTCANCEL,
    CANNOTSWIPE, CANTINSERTLOYALTY, CARDDECLINED, CARDEXPIRED, CARDNOTREAD,
    CASHINSERTEDWAIT, CASHMAXMSG, CASHPAPGREETING, CASHWARNMSG, CHOOSEGRADE,
    CLOSED, CONGOFORCEFINALIZE, CONGOGREETING, CONGOREQUIRESPAP, CONGOWAITINGEND,
    CONGOWAITINGPROMPT, CREDITAUTH, CREDITDOWN, CURRENTCASHAMT, DEBITHOSTOFFLINE,
    DEBITNOTACCEPTED, FUELING, FULLAMTAPPROVED, FULLCASHPAID, FULLSERVEGREETING,
    GETCHANGE, GREETING, ICRGREETING, INSERTCARD, INSERTCASHPRESSENTER,
    INSERTLOYALTY, INSIDEAUTH, INVALIDCARD, INVALIDGRADE, LIMITEXCEEDED,
    LIMITREACHED, NO, NOCASHPAP, NOCHECKMOP, NOOPENSHIFT, NOPAP, NOPOSTPAY,
    NOPREPAY, PACDECLINED, PACGREETING, PACGREETINGCASH, PACGREETINGMOP,
    PACGREETINGPOSTPAY, PACREQUIRED, PAYCASHIER, PLEASEWAIT, PREPAYCOMPLETE,
    PREPAYGREETING, PREPAYICRGREETING, PRESSCANCEL, PUMP BUSY, PUMPOFFLINE,
    PUMPSTOPPED,  RCPT PRNTNG, RCPTPRINTED, RCPTPRINTEDCASH, RECEIPT PROMPT,
    RECEIPTFAIL, REINSERTCARD, REPLACENOZZLE, SALECANCELLED, SALETIMEDOUT,
    SEECASHIER, SELECTCARWASHNUMBER, SVCBALANCE, SVCHOSTOFFLINE, THANKS,
    WASH FAIL, Y/N, YES
    :return:
    """
    # this step waits up to 1 minute until the display changes to the desired text
    # the timeout is quite long as it may be used for different prompts

    # alternative implementation:
    #assert context.sit_product.simpumps.match_prompt_on_display(context.pump_number, prompt_name, True, 180)
    utility.wait_for_icr_prompts(
        context.sit_product.simpumps,
        pump_number,
        prompt_name,
        attempts=60,
        delay=1,
        timeout=60,
        exact_match=False,
    )


@then('the dynamic prompt "{prompt_text}" is displayed on pump "{pump_number:d}"')
def step_impl(context: Context, prompt_text: str, pump_number: int):
    # prompt_text should be the full string. We will get the current display
    # and because it may be truncated based on the icr type we will expect
    # it to be a substring of the prompt_text. Allow 15 seconds for the
    # prompt to be available

    result, success = utility.wait_until(
        lambda: context.sit_product.simpumps.get_current_display(pump_number),
        lambda current_prompt: current_prompt in prompt_text,
        15,
        1,
        timeout=15
    )

    if not success:
        raise TimeoutError(f"Dynamic prompt {prompt_text} was no displayed on pump {pump_number} in time")


@then('carwash items are displayed at pump "{pump_number:d}"')
def step_impl(context: Context, pump_number: int):
    # context.sit_product.verify_carwash_items_displayed_at_pump(pump_number)
    pass
# endregion
