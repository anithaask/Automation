@sitbdd @pos @fuel @wip
Feature: This feature tests RLM.

    Background:
        Given the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state


    @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    # TODO: Fill in discount_description, discount_value and transaction values into the loyalty discount step once the previous steps are implemented and functioning
    Scenario: Postpay with RLM.
        Given the customer pressed "CASHINSIDE" key on pump "1" keypad
        And the customer dispensed "Regular" for "10.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the customer chose to use loyalty card "loyalty"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then a loyalty discount "{discount_description}" with value of "{discount_value:f}" is in the "{transaction}" transaction
        And the generated export "NAXML-POSJournal" matches "a postpay sale with RLM loyalty tendered with cash" template
        And some report for RLM should be verified
        And the pump "1" displays welcome prompt
