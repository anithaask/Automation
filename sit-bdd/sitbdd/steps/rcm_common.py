from behave import given

from behave.runner import Context


# region Given clauses
@given('following POS options are set in RCM')
def step_impl(context: Context):
    """
    Given following POS options are set in RCM
        | option_name            | option | value_text    | value |
        | Loyalty Prompt Control | 4214   | Do Not Prompt | 0     |
    """
    original_options = {}
    for row in context.table:
        option = int(row["option"])
        new_value = float(row["value"]) if '.' in row["value"] else int(row["value"])
        current_value = context.sit_product.rcm.get_pos_option_value(option)
        if current_value != new_value:
            original_options[option] = current_value
            context.sit_product.rcm.set_pos_option(option, new_value)


@given('following ICR options are set in RCM')
def step_impl(context: Context):
    """
    Given following ICR options are set in RCM
      | option                   | value |
      | PROMPTTIMEOUT            | 4     |

    Find translations of ICR option values from code to values viewable in RCM app here:
    https://github.com/ncr-swt-cfr/rcm/blob/main/Install/DDL/6.7C2/InitialValues/Update_Fuel_ICR_Option_TRANTYPE.sql
    """
    for row in context.table:
        option = row["option"]
        new_value = row["value"]
        current_value = context.sit_product.rcm.get_icr_option_value(option)
        if new_value != current_value:
            context.sit_product.rcm.set_icr_option(option, new_value)


# TODO: Implement via RCM API
@given('the site server is linked to the RCM')
def step_impl(context: Context):
    pass


# TODO: Implement via RCM API
# This step will need to set context.sit_product.rcm_download_needed accordingly
# similar to how "following POS options are set in RCM" does it
@given('following tenders are set in RCM')
def step_impl(context: Context):
    pass


@given('POS profile with name "{profile_name}" is created with the following options')
def step_impl(context: Context, profile_name: str):
    pos_options_list = []
    for row in context.table:
        option = int(row['option'])
        new_value = float(row['value']) if '.' in row['value'] else int(row['value'])
        pos_options_list.append({'posId': option, 'value': new_value})

    create_profile = True

    for profile in context.sit_product.rcm.get_pos_option_profiles():
        if profile['name'] == profile_name:
            create_profile = False

    if create_profile:
        context.sit_product.rcm.create_pos_option_profile(profile_name=profile_name, pos_options_list=pos_options_list)


@given('ICR profile with name "{profile_name}" is created with the following options')
def step_impl(context: Context, profile_name: str):
    print(context.sit_product.rcm.get_icr_option_profiles())
    icr_options_list = []
    for row in context.table:
        option = row['option']
        new_value = row['value']
        icr_options_list.append({'code': option, 'value': new_value})

    create_profile = True

    for profile in context.sit_product.rcm.get_icr_option_profiles():
        if profile['name'] == profile_name:
            create_profile = False

    if create_profile:
        context.sit_product.rcm.create_icr_option_profile(profile_name=profile_name, icr_options_list=icr_options_list)

@given('following discounts are set in RCM')
def step_impl(context: Context):
    """
    """

    for row in context.table:
        context.sit_product.rcm.set_discount(discount_name=row["name"], discount_external_id=row["external_id"], discount_type=row["type"], discount_value=row["value"])

# endregion


# region When clauses
# endregion

# region Then clauses
# endregion
