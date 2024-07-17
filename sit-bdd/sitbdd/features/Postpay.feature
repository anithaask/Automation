@sitbdd @pos @fuel @sc
Feature: Postpay Transactions
    Goal of this feature is to perform several types of postpay transactions

    Background: Postpay configuration setup
        Given following POS options are set in RCM
            | option_name                | option | value_text | value |
            | Partial tender not allowed | 1205   | No         | 0     |
        And the Epsilon has following global options configured
            | option                     | value |
            | SendAvailableProductExport | YES   |
        And updated configuration is loaded by credit controller
        And the pumps are configured for "Prepay,Postpay,ICR"
        And the pumps have the following timing events configured
            | option        | value         |
            | ADVERTISEMENT | DURINGFUELING |
        And following ICR options are set in RCM
            | option           | value   |
            | PROMPTTIMEOUT    | 4       |
            | FUELSTARTTIMEOUT | 10      |
            | TRANTYPE         | DEFAULT |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"


    @positive @glacial
    Scenario: Postpay transaction, successful fueling
        Given the customer dispensed "Regular" for "10.00" price at pump "1"
        When the cashier tenders postpay fuel transaction on pump "1"
        Then all transactions are summarized


    @positive @slow
    Scenario: Postpay transaction, attempted cancel during fueling
        Given the customer started a postpay transaction at pump "2"
        And the customer selected fuel grade "Midgrade" for their postpay transaction at pump "2"
        And the cashier authorized the pump "2" for postpay
        When the customer tries to cancel postpay transaction during fueling on pump "2"
        Then the configured prompt "REPLACENOZZLE" is displayed on pump "2"


    @positive @slow
    Scenario: Postpay Transaction - Sale Timed Out
        Given the customer started a postpay transaction at pump "2"
        And the customer selected fuel grade "Regular" for their postpay transaction at pump "2"
        And the cashier authorized the pump "2" for postpay
        When the customer hangs up the nozzle on pump "2"
        Then the pump "2" displays welcome prompt


    @positive @slow @wip
    # RPOS-55586: Not displaying Advertisement because timing event step isn't implemented for RCM yet.
    Scenario: PostPay with Advertisement
        Given the customer started a postpay transaction at pump "2"
        And the customer selected fuel grade "Premium" for their postpay transaction at pump "2"
        And the cashier authorized the pump "2" for postpay
        When the customer starts fueling on pump "2"
        Then the dynamic prompt "Advertisement" is displayed on pump "2"


    @positive @slow @product_specific
    Scenario: Cancel postpay at pump by pressing cancel button on pump, the sale on pump is cancelled.
        Given the customer started a postpay transaction at pump "1"
        And the customer selected fuel grade "Regular" for their postpay transaction at pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the pump "1" displays welcome prompt


    @positive @slow @product_specific
    Scenario: Cancel postpay at pump by lifting and hanging up the nozzle at the pump, the sale on the pump is cancelled.
        Given the customer started a postpay transaction at pump "1"
        And the customer selected fuel grade "Regular" for their postpay transaction at pump "1"
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt


    @glacial @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Postpay is tendered using credit SVC
        Given the "credit_svc" SVC card was activated for $40
        And the customer dispensed "Regular" for "17.38" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the generated export "POS journal" matches "an SVC activation first and postpay sale second" template


    @glacial
    Scenario: Pump is stacked and fully tendered
        Given the customer dispensed "Midgrade" for "19.23" price at pump "2"
        And the customer dispensed "Midgrade" for "19.23" price at pump "2"
        And the cashier added a postpay item to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the cashier added a postpay item to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "a two postpay sale" template


    @glacial
    Scenario: Postpay refund is not allowed
        Given the customer dispensed "Midgrade" for "19.23" price at pump "2"
        When the cashier tries to refund postpay from pump "2" on position "1"
        Then the POS displays the "Item not allowed." frame


    @glacial @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Customer dispensed fuel at pump. Cashier adds postpay to the transaction and customer tenders transaction using SVC card, 
              transaction is finalized and transaction data are correct.
        Given the "credit_svc" SVC card was activated for $100
        And the customer dispensed "Regular" for "5.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @glacial @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Cashier partially tenders postpay transaction with cash. Customer tenders the transaction with SVC card,  
              transaction is finalized and transaction data are correct.
        Given the "credit_svc" SVC card was activated for $100
        And the customer dispensed "Regular" for "15.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the cashier tendered the transaction with $5 in cash
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @positive @fast @wip
    Scenario: Available Product Export - initiated by fuel controller - after price change
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 4     |
            | CREDITTIMEOUT      | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | NO    |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISNO         | NO    |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        When the fuel controller receives new fuel prices
        Then the export with items available to sell by the fuel controller is sent to credit controller
        And the pumps available to start transactions are reported as available in credit controller product export


    @positive @slow @carwash @wip
    Scenario: Transaction Flow - No loyalty, Normal PAP, carwash configured during fueling and should not be suppressed due to normal pay at pump transaction.
        Given the pumps have the following timing events configured
            | option  | value         |
            | CARWASH | DURINGFUELING |
            | RECEIPT | AFTERFUELING  |
        And the fuel controller is configured to sell "fuel,carwash"
        And the system is in a ready to sell state
        And an MSR card "credit_visa" was swiped at pump "1"
        And the customer dispensed grade "Regular" for 3 seconds at pump 1
        And the configured prompt "ASKWASH PROMPT" was displayed on pump "1"
        And carwash is accepted on pump "1" keypad
        And the customer selected the first carwash option at the pump "1"
        When the customer hangs up the nozzle on pump "1"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"


    @positive @glacial
    Scenario: Cashier adds postpay to the transaction and attempts to perform pay in, the POS displays Transaction already in progress error.
        Given the system is in a ready to sell state
        And the customer dispensed "Regular" for "10.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        When the cashier presses Pay In button on other functions frame
        Then the POS displays Transaction already in progress error
