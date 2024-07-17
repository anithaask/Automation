@fuel @pap @promptflow @wip
# RPOS-55586: RCM timing events (ICR Prompt Sequence Setup) must be available from the RCM API before this test can be implemented
# RPOS-55586: RCM auth modes must be available from the RCM API before this test can be implemented
Feature: PAPPromptFlow - Verify the ICR prompt flow of PAP transaction.
    Goal of this feature is to verify that PAP transaction is following correct flow for user prompts.

    Background: PAP configuration setup
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And following ICR options are set in RCM
            | option        | value   |
            | PROMPTTIMEOUT | 4       |
            | TRANTYPE      | DEFAULT |


    @smoke @positive @slow
    Scenario Outline: A customer swiped an MSR card and the correct prompt is displayed.
        Given the system is in a ready to sell state
        When an MSR card "<card_name>" is swiped at pump "1"
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"

        Examples:
            | card_name                  |
            | loyalty_cobranded_visa_old |
            | credit_visa                |
            | credit_mc                  |
            | credit_discover            |


    @smoke @positive @slow
    Scenario Outline: A customer selected fuel grade and the correct prompt is displayed.
        Given the system is in a ready to sell state
        And an MSR card "<card_name>" was swiped at pump "1"
        When fuel grade "Midgrade" is selected on pump "1"
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"

        Examples:
            | card_name                  |
            | loyalty_cobranded_visa_old |
            | credit_visa                |
            | credit_mc                  |
            | credit_discover            |


    @smoke @positive @slow
    Scenario Outline: A customer finishes fueling and the correct prompt is displayed.
        Given the system is in a ready to sell state
        And an MSR card "<card_name>" was swiped at pump "1"
        When the customer fuels "1" gallons of fuel grade "Midgrade" at pump "1"
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"

        Examples:
            | card_name                  |
            | loyalty_cobranded_visa_old |
            | credit_visa                |
            | credit_mc                  |
            | credit_discover            |


    @smoke @positive @slow
    Scenario Outline: A customer declines prompt after fueling and the correct follow-up prompt is displayed.
        Given the system is in a ready to sell state
        And an MSR card "<card_name>" was swiped at pump "1"
        And the customer fueled "1" gallons of fuel grade "Midgrade" at pump "1"
        When the customer presses "NO" key on pump "1" keypad
        Then the configured prompt "THANKS" is displayed on pump "1"
        And the pump "1" displays welcome prompt

        Examples:
            | card_name                  |
            | loyalty_cobranded_visa_old |
            | credit_visa                |
            | credit_mc                  |
            | credit_discover            |
