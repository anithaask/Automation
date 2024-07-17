@fuel @two-tier @wip
Feature: Two-tier Pricing for Fuel Transactions
    Goal of this feature is set up a two-tier pricing system and perform different types of fuel transactions.
    Assumption is that credit tier price should be higher than cash tier pricing.

    Background:
        Given fuel items are configured for two-tier prices
        And the system is in a ready to sell state


    @positive
    Scenario: I should be able to prepay with cash and receive the cash tier fuel price at the pump
        And ICR is ready for transactions
        When fuel controller receives prepay authorization for $4.00 for cash tier
        And the customer lifts the nozzle on pump "1"
        And fuel grade "Midgrade" is selected on pump "1"
        Then pump will select cash tier fuel price


    @positive
    Scenario: I should be able to prepay with credit and receive the credit tier fuel price at the pump
        And ICR is ready for transactions
        When fuel controller receives prepay authorization for $4.00 for credit tier
        And the customer lifts the nozzle on pump "1"
        And fuel grade "Midgrade" is selected on pump "1"
        Then pump will select credit tier fuel price


    @positive
    Scenario: I should be able to postpay with cash and receive the cash tier fuel price at the pump
        And ICR is ready for transactions
        When the customer presses "CashInside" key on pump "1" keypad
        And the customer lifts the nozzle on pump "1"
        Then pump will select cash tier fuel price
        When fuel grade "Regular" is selected on pump "1"
        Then the configured prompt "INSIDEAUTH" is displayed on pump "1"
        When the cashier authorizes postpay on the POS for pump "1"
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"
        When fuel is dispensed for "2" seconds on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "PAYCASHIER" is displayed on pump "1"
        When the cashier tenders postpay fuel transaction with tender type "cash" on pump "1"
        Then the POS finalizes the postpay transaction using cash tier fuel price


    @positive
    Scenario: I should be able to postpay with cash and receive the cash tier fuel price at the pump even though I tender with credit at the POS
        And ICR is ready for transactions
        When the customer presses "CashInside" key on pump "1" keypad
        And the customer lifts the nozzle on pump "1"
        Then pump will select cash tier fuel price
        When fuel grade "Regular" is selected on pump "1"
        Then the configured prompt "INSIDEAUTH" is displayed on pump "1"
        When the cashier authorizes postpay on the POS for pump "1"
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"
        When fuel is dispensed for "2" seconds on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "PAYCASHIER" is displayed on pump "1"
        When the cashier tenders postpay fuel transaction with tender type "credit" on pump "1"
        Then the POS finalizes the postpay transaction using cash tier fuel price


    @positive
    Scenario: I should be able to postpay with credit, receive the credit tier fuel price at the pump, and receive a discount at the POS when tendering with cash
        And ICR is ready for transactions
        When the customer presses "CreditInside" key on pump "1" keypad
        And the customer lifts the nozzle on pump "1"
        Then pump will select credit tier fuel price
        When fuel grade "Regular" is selected on pump "1"
        Then the configured prompt "INSIDEAUTH" is displayed on pump "1"
        When the cashier authorizes postpay on the POS for pump "1"
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"
        When fuel is dispensed for "2" seconds on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "PAYCASHIER" is displayed on pump "1"
        When the cashier tenders postpay fuel transaction with tender type "cash" on pump "1"
        Then the POS finalizes the postpay transaction using cash tier fuel price


    @positive
    Scenario: I should be able to postpay with credit and receive the credit tier fuel price at the pump
        And ICR is ready for transactions
        When the customer presses "CreditInside" key on pump "1" keypad
        And the customer lifts the nozzle on pump "1"
        Then pump will select credit tier fuel price
        When fuel grade "Regular" is selected on pump "1"
        Then the configured prompt "INSIDEAUTH" is displayed on pump "1"
        When the cashier authorizes postpay on the POS for pump "1"
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"
        When fuel is dispensed for "2" seconds on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "PAYCASHIER" is displayed on pump "1"
        When the cashier tenders postpay fuel transaction with tender type "credit" on pump "1"
        Then the POS finalizes the postpay transaction using credit tier fuel price


    @positive
    Scenario: I should be able to pay at the pump with credit and receive the credit tier fuel price at the pump
        And ICR is ready for transactions
        When an MSR card "credit_visa" is swiped at pump "1"
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"
        When fuel grade "Regular" is selected on pump "1"
        And the customer lifts the nozzle on pump "1"
        Then pump will select credit tier fuel price
        Then the configured prompt "BEGINFUELING" is displayed on pump "1"
        When fuel is dispensed for "3" seconds on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "NO" key on pump "1" keypad
        Then the configured prompt "THANKS" is displayed on pump "1"
        And the pump "1" displays welcome prompt
