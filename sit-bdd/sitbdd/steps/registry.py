from behave import given
from behave.runner import Context


# region Given clauses
# TODO: To be finished under RPOS-58630
@given('the "{registry_key}" key at path "{registry_path}" is set to "{registry_value}"')
def step_impl(context: Context, registry_key: str, registry_path: str, registry_value: str):
    # context.sit_product.change_epsilon_registry(registry_path, registry_key, registry_value)
    pass


# TODO: To be finished under RPOS-58630
@given('the "{registry_key}" key at path "{registry_path}" is "{registry_value}"')
def step_impl(context: Context, registry_key: str, registry_path: str, registry_value: str):
    # assert str(RegistryHandler.get_registry_value(registry_path, registry_key)) == registry_value
    pass


# TODO: To be finished under RPOS-58630
@given('the "{registry_key}" key at path "{registry_path}" is deleted')
def step_impl(context: Context, registry_key: str, registry_path: str):
    # RegistryHandler.delete_registry_value(registry_path, registry_key)
    # assert RegistryHandler.get_registry_value(registry_path, registry_key) is None
    pass
# endregion


# region When clauses
# endregion

# region Then clauses
# endregion
