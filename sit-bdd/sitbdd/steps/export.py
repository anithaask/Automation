import json

from behave import given, then
from cfrsc.core.bdd_utils.errors import SCBddException

from behave.runner import Context
from sitbdd.sitcore.bdd_utils.errors import ProductError
from sitbdd.sitcore.bdd_utils import utility
from sitbdd.sitcore.bdd_utils.ignore_tags import *


# region Given clauses
@given('the NAXML Export schema is "{version:f}"')
def step_impl(context: Context, version: float):
    """Provide the NAXML export schema version for subsequent export validation steps
    to determine which export template to use during validation.

    Below is an example on how to use this step in a Gherkin file.

    * Given the NAXML Export schema is "3.4"

    :param context: Behave context.
    :param version: NAXML export schema version. Only version 3.4 is supported.
    """
    context.naxml_version = version


@given('the transaction history is clear')
def step_impl(context: Context):
    """Clear the transaction history.

    This step is required when working with export validation and must be used before
    any exports are generated. This clears previous transactions that may not be
    relevant and prevents those transactions from showing up in any subsequent export
    generation.

    :param context: Behave context.
    """
    utility.suppress_until(
        context.sit_product.sc.utilities.delete_transaction_history,
        SCBddException,
        attempts=3,
        delay=3,
    )

@given('the system is in a clear state')
def step_impl(context: Context):
    """Clear the transaction history.

    This step is required when working with export validation and must be used before
    any exports are generated. This clears previous transactions and summaries that may not be
    relevant and prevents items from those transactions from showing up in any subsequent export
    generation.

    :param context: Behave context.
    """
    context.execute_steps("Given The cashier ended the shift")
    utility.suppress_until(
        context.sit_product.sc.utilities.delete_transaction_history,
        SCBddException,
        attempts=3,
        delay=3,
    )
    utility.suppress_until(
        context.sit_product.sc.utilities.delete_summary_totals,
        SCBddException,
        attempts=3,
        delay=3,
    )
    utility.suppress_until(
        context.sit_product.sc.utilities.delete_shift_data,
        SCBddException,
        attempts=3,
        delay=3,
    )
    context.execute_steps("Given The cashier started the shift")


@given('the previous transaction is summarized')
def step_impl(context: Context):
    """Ensure the previous transaction is summarized.

    This step ensures that any export generated in a scenario is not affected by
    transactions from previous scenarios. Unless a previous transaction exists and has
    not yet summarized, this step does not do anything.

    :param context: Behave context.
    """
    # Wait for the previous transaction to summarize.
    summary = context.sit_product.pos._control.wait_for_transaction_end(60)


@given('event messages are cleared')
def step_impl(context: Context):
    """Clear all event messages.

    This step saves summarized transaction sequence numbers before clearing them
    to allow subsequent steps to check whether a transaction has summarized.

    :param context: Behave context.
    """
    topic_id = "transaction-summarization-event-v1"

    # Pull new summary messages once.
    context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_messages(topic_id, timeout=0)

    # Save all summary messages before clearing.
    for message in context.sit_product.sc.pubsub_subscriber.received_messages:
        if message.get("topicId") != topic_id:
            continue

        # Save transaction ID to summarized transactions.
        message = message.get("message")
        if type(message) is str:
            message = message.replace("\\", "\\\\")
            message = json.loads(message)

            # Transaction ID from the message is a string.
            tran_id = message.get("transactionId")
            if type(tran_id) is str and tran_id.isdigit():
                context.sit_product.summarized_transactions.add(int(tran_id))

    # Clear past messages to ensure that only subsequent messages are kept.
    context.sit_product.sc.pubsub_subscriber.clear_all_messages()


@given('the system is configured for NAXML exports with schema version "{version:f}"')
def step_impl(context: Context, version: float):
    """Configure the system for export validation.

    This step executes the following step definitions in order.

    * Given the NAXML Export schema is "{version}"
    * Given the previous transaction is summarized
    * Given event messages are cleared
    * Given the transaction history is clear

    Below is an example on how to use this step in a Gherkin file.

    * Given the system is configured for NAXML exports with schema version "3.4"

    :param context: Behave context.
    :param version: NAXML export schema version. Only version 3.4 is supported.
    """
    context.execute_steps(
        f'''
        Given the NAXML Export schema is "{version}"
        And the previous transaction is summarized
        And event messages are cleared
        And the transaction history is clear
        '''
    )


@given('the SC is in a ready to sell state')
def step_impl(context: Context):
    context.sit_product.sc.utilities.delete_shift_data()
    context.sit_product.sc.utilities.delete_summary_totals()
    context.sit_product.sc.utilities.delete_transaction_history()
# endregion


# region When clauses
# endregion


# region Then clauses
@then('all transactions are summarized')
def step_impl(context: Context):
    """Wait for the most recent POS transaction and its internal transactions to
    summarize.

    This step ensures subsequent export generation in a scenario to include
    the summarized transactions and must be used when working with exports.
    A recent transaction without a transaction summary is required when using
    this step definition.

    :param context: Behave context.
    :raise ProductError: No prior transaction existed, the POS transaction did not
        summarize, or an internal transaction did not summarize.
    """
    # Capture the last POS transaction.
    transaction = context.sit_product.pos.control.wait_for_transaction_end()
    if transaction is None:
        # Step was called without prior transactions.
        raise ProductError("No transaction to summarize.")

    topic_id = "transaction-summarization-event-v1"

    # Wait for the POS transaction summary.
    timeout = 80
    summary = context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_json_message(
        topic_id,
        message_keys=dict(transactionId=str(transaction.sequence_number)),
        timeout=timeout,
    )
    if summary is None:
        raise ProductError(
            f"Transaction #{transaction.sequence_number} did not summarize within "
            f"{timeout} seconds."
        )
    elif summary.get("status") != "COMPLETED":
        raise ProductError(
            f"Transaction #{transaction.sequence_number} "
            f"did not summarize successfully."
        )

    # Wait for internal transaction summaries to finish.
    quiet_period = 60
    attempts = 4
    utility.wait_until_sc_pubsub_stops_publishing(
        context.sit_product.sc, topic_id, quiet_period, attempts
    )

    # Look for an internal transaction that did not summarize successfully.
    failed_status = "SKIPPED", "FAILED", "ALL_DENIED"
    failed_summary = context.sit_product.sc.pubsub_subscriber.wait_for_pubsub_json_message(
        topic_id,
        message_keys=[dict(status=status) for status in failed_status],
        # Avoid waiting for and pulling new messages by using a timeout value of 0.
        timeout=0,
    )
    if failed_summary is not None:
        raise ProductError(
            f"A transaction originating from #{transaction.sequence_number} "
            f"failed to summarize."
        )

    context.execute_steps("Given event messages are cleared")


@then('the section "{tag}" with namespace "{namespace}" in generated export "{export}" matches the following values')
def step_impl(context: Context, tag: str, namespace: str, export: str):
    fields = {}
    for row in context.table:
        field = row["field"]
        value = row["value"]
        fields[field] = value

    context.execute_steps("Given event messages are cleared")
    context.sit_product.sc.exports_manager.compare_export_tags(tag, fields, system_export_type=export, namespace=namespace)


@then('the section "{tag}" in generated export "{export}" matches the following values')
def step_impl(context: Context, tag: str, export: str):
    fields = {}
    for row in context.table:
        field = row["field"]
        value = row["value"]
        fields[field] = value

    context.execute_steps("Given event messages are cleared")
    context.sit_product.sc.exports_manager.compare_export_tags(tag, fields, system_export_type=export)


@then('the section "{tag}" with namespace "{namespace}" in generated export "{export}" matches exactly the following values')
def step_impl(context: Context, tag: str, namespace: str, export: str):
    fields = {}
    for row in context.table:
        field = row["field"]
        value = row["value"]
        fields[field] = value

    context.execute_steps("Given event messages are cleared")
    context.sit_product.sc.exports_manager.compare_export_tags(tag, fields, system_export_type=export, namespace=namespace, exclusive=True)


@then('the section "{tag}" in generated export "{export}" matches exactly the following values')
def step_impl(context: Context, tag: str, export: str):
    fields = {}
    for row in context.table:
        field = row["field"]
        value = row["value"]
        fields[field] = value

    context.execute_steps("Given event messages are cleared")
    context.sit_product.sc.exports_manager.compare_export_tags(tag, fields, system_export_type=export, exclusive=True)


@then('the generated "{export}" matches XSD schema')
def step_impl(context: Context, export: str):
    context.execute_steps("Given event messages are cleared")
    context.sit_product.sc.exports_manager.verify_xsd_schema(context.sit_product.config["nodes"]["sc"]["NAXML_schema_path"], export)


@then('the generated export "{export_type}" matches "{template_name}" template')
def step_impl(context: Context, export_type: str, template_name: str):
    """Compare a generated export against a template.
    The last transaction should have already summarized before using this step.
    When generating exports, the ending pub-sub message is matched to its
    corresponding starting message by ID that's randomly generated by the Site Server.
    Dynamic elements and differences in whitespaces are ignored during comparison.
    Below is an example on how to use this step in a Gherkin file.
    * Then the generated export "POS journal" matches "a prepay sale" template
    :param context: Behave context.
    :param export: Export type that can be one of
        "PDICashierReport",
        "employee time summary",
        "fuel grade movement",
        "fuel product movement",
        "NAXML-ItemSalesMovement",
        "merchandise code movement",
        "PDIMiscSumMvmt",
        "NAXML-POSJournal",
        or "tank product movement".
    :param template_name: Template name.
    :raise ProductError: Export generation did not start or finish, or the generated
        export is empty.
    """
    ignore_tag, ignore_tag_content = utility.get_ignore_tag(export_type)

    context.execute_steps("Given event messages are cleared")

    context.sit_product.sc.exports_manager._exports_controller.request_export_generation(export_type)
    export_content = context.sit_product.sc.exports_manager.verify_export_can_be_retrieved(export_type)

    if export_content is None:
        raise ProductError(f'Requested "{export_type}" was empty.')

    template_content = utility.read_sc_export(context.naxml_version, export_type, template_name)
    context.sit_product.sc.exports_manager.compare(template_content, export_content, export_type, ignore_tag, ignore_tag_content)
# endregion
