@sitbdd @rcm @pos @fuel @sc
Feature: Pay Out
    Goal of this feature is to perform several tests of Pay Out functionality on POS.

    Background: Default
        Given the system is in a ready to sell state


    @glacial
    Scenario: Pay Out with fuel.
        Given the customer dispensed "Regular" for "3.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        When the cashier presses Pay Out button on other functions frame
        Then the POS displays the "TRANSACTION ALREADY IN PROG" frame


    @glacial
    Scenario: Unable to Delete Pay Out. Verify that Pay Outs do not go into scroll previous receipt therefore can't be deleted.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the cashier navigated to the other functions frame
        When the cashier performs a "cash" Pay Out with amount of "8.00"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 10          | *I1    Sale Item A                  $0.99* |
            | 11          | *----------------------------------------* |


    @glacial @wip
    Scenario: Cash Pay Out
    # RPOS-63446: Reports are not possible yet through automation.
        Given the cashier performed a "cash" Pay Out with amount of "12.00"
        And the Pay Out of "12.00" appeared in the Shift Financial Report
        And the cashier performed a "cash" Pay Out with amount of "13.17"
        And the Pay Out of "25.17" appeared in the Shift Financial Report
        When the cashier performs a "cash" Pay Out with amount of "14.00"
        Then the Pay Out of "39.17" appears in the Shift Financial Report


    @glacial @wip
    Scenario: Pay Out with merchandise.
    # RPOS-63446: Reports are not possible yet through automation.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier performed a Pay Out in the middle of a transaction
        And the cashier navigated to the main frame
        And the cashier voided item "Sale Item A"
        When the cashier performs a "cash" Pay Out with amount of "6.00"
        Then the Pay Out of "6.00" appears in the Shift Financial Report


    @glacial @wip
    Scenario: Pay Out refund.
    # RPOS-63446: Reports are not possible yet through automation.
        Given the cashier started a refund transaction
        And the cashier performed a Pay Out in the middle of a transaction
        And the cashier cancelled the refund transaction
        When the cashier performs a "cash" Pay Out with amount of "10.00"
        Then the Pay Out of "6.00" appears in the Shift Financial Report
