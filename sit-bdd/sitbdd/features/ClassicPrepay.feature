@sitbdd @rcm @pos @fuel @sc @prepay
Feature: Classic Prepay Transactions
    Goal of this feature is to perform several types of classic prepay transactions.

    Background: Classic Prepay configuration setup
        Given the pumps are configured for "Prepay"
        And following POS options are set in RCM
            | option_name               | option | value_text      | value |
            | Prepay Grade Select Type  | 5124   | One Touch       | 1     |
            | Fuel credit prepay method | 1851   | Sale and Refund | 2     |
        And the pumps have the following timing events configured
            | option        | value         |
            | ADVERTISEMENT | DURINGFUELING |
        And following ICR options are set in RCM
            | option         | value   |
            | PROMPTTIMEOUT  | 4       |
            | PPSTARTTIMEOUT | 15      |
            | TRANTYPE       | DEFAULT |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"


    @positive @glacial
    Scenario: Prepay Transaction, attempted cancel during fueling
        Given the cashier prepaid the fuel grade "Regular" for price "6.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the customer lifted the nozzle on pump "1"
        And the customer selected fuel grade "Regular" for their prepay transaction at pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "TRANSACTION CANCELLED" is not displayed on pump "1"


    @positive @slow
    Scenario: Cancelled Prepay Transaction
        Given the cashier prepaid the fuel grade "Regular" for price "4.00" at pump "2"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the configured prompt "BEGINFUELING" was displayed on pump "2"
        When the customer presses "CANCEL" key on pump "2" keypad
        Then the pump "2" displays welcome prompt


    @positive @slow @wip @product_specific
    # RPOS-55586: Need to implement auth modes before this scenario can be passing.
    Scenario: Pay Inside Transaction - No PAP allowed-PAP-Pre-Pay and Post-Pay only-sale cancelled
        Given the customer pressed "CREDITOUTSIDE" key on pump "1" keypad
        Then the configured prompt "NOPAP" is displayed on pump "1"


    @positive @slow @wip
    # Not able to turn on advertisements due to limitations of config team api.
    Scenario: Pay Inside Transaction - under-dispensed Pre-pay transaction, Advertisement
        Given the cashier prepaid the fuel grade "Midgrade" for price "5.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the customer lifted the nozzle on pump "1"
        And the customer selected fuel grade "Midgrade" for their prepay transaction at pump "1"
        When the customer starts fueling $2.00 in fuel on pump "1"
        Then the dynamic prompt "Advertisement" is displayed on pump "1"
        And fueling is completed on pump "1" for $2.00
        And the configured prompt "GETCHANGE" is displayed on pump "1"
        And the pump "1" displays welcome prompt
        And the completed sale amount is $2.00 on pump "1"


    @positive @slow @wip
    # Not able to turn on advertisements due to limitations of config team api.
    Scenario: Pay Inside Transaction - fully-dispensed Pre-pay transaction, Advertisement
        Given the cashier prepaid the fuel grade "Premium" for price "3.00" at pump "2"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the customer lifted the nozzle on pump "2"
        And the customer selected fuel grade "Premium" for their prepay transaction at pump "2"
        When the customer starts fueling $3.00 in fuel on pump "2"
        Then the dynamic prompt "Advertisement" is displayed on pump "2"
        And fueling is completed on pump "2" for $3.00
        And the pump "2" displays welcome prompt
        And the completed sale amount is $3.00 on pump "2"


    @glacial
    Scenario: Fuel grade is selected on the POS and fully dispensed on the pump
        Given the cashier prepaid the fuel grade "Regular" for price "20.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "a prepay sale" template


    @glacial
    Scenario: Fuel grade is selected on the POS and under dispensed on the pump
        Given the cashier prepaid the fuel grade "Regular" for price "20.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the customer dispensed "Regular" for "10.00" price at pump "1"
        When the cashier presses the "pay1" button
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field            | value       |
            | FuelGradeID      | fg_regular  |
            | Description      | Prepay Fuel |
            | SalesAmount      | -20         |
            | ActualSalesPrice | 4           |
            | SalesAmount      | 10          |


    @glacial
    Scenario: The correct fuel grade still can be dispensed after invalid fuel grades are selected on the pump.
        Given the cashier prepaid the fuel grade "Regular" for price "20.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the customer selected incorrect fuel grade "Midgrade" on pump "1"
        And the customer hung up the nozzle on pump "1" after selecting incorrect fuel grade
        And the customer selected incorrect fuel grade "Diesel" on pump "1"
        And the customer hung up the nozzle on pump "1" after selecting incorrect fuel grade
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field            | value       |
            | FuelGradeID      | fg_regular  |
            | Description      | Prepay Fuel |
            | SalesAmount      | -20         |
            | ActualSalesPrice | 4           |
            | SalesAmount      | 20          |
