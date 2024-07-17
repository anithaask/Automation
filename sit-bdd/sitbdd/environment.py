from behave.model import Feature
from behave.model import Scenario
from behave.model import Step
from behave.model import Tag
from behave.runner import Context
from behave.contrib.scenario_autoretry import patch_scenario_with_autoretry

from sitbdd.sitcore.bdd_utils.sit_logging import setup_logger
from sitbdd.sitcore.sit.sit_product import SITProduct

logger = setup_logger()


def before_all(context: Context):
    context.sit_product = SITProduct()


def before_feature(context: Context, feature: Feature):
    for scenario in feature.scenarios:
        patch_scenario_with_autoretry(scenario, max_attempts=2)
    context.sit_product.rcm.update_pos_option_profile()


def before_scenario(context: Context, scenario: Scenario):
    logger.info('Starting scenario "%s"' % scenario)


def before_step(context: Context, step: Step):
    pass


def before_tag(context: Context, tag: Tag):
    pass


def after_tag(context: Context, tag: Tag):
    pass


def after_step(context: Context, step: Step):
    pass


def after_scenario(context: Context, scenario: Scenario):
    logger.info('Finished with scenario "%s"' % scenario)
    # classes containing instances of RegistryHandler
    # should call restore_original_values here
    context.sit_product.eps.registry_handler.restore_original_values()
    context.sit_product.sigma.registry_handler.restore_original_values()
    context.sit_product.eps.conexxus.registry_handler.restore_original_values()

    context.sit_product.eps.registry_handler_host_sim.restore_original_values()
    context.sit_product.sigma.registry_handler_host_sim.restore_original_values()
    context.sit_product.eps.conexxus.registry_handler_host_sim.restore_original_values()


def after_feature(context: Context, feature: Feature):
    pass


def after_all(context: Context):
    pass
