@sitbdd @rcm @pos @sc @wip
Feature: Cobranded tests that validate an export

    Background:
        Given following POS options are set in RCM
            | option_name                          | option | value_text    | value |
            | Automatically charge cobranded cards | 1903   | No            | 0     |
            | Loyalty Prompt Control               | 4214   | Do Not Prompt | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"


    @slow @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Cashier adds dry stock and tenders the transaction in credit with cobranded card, transaction is finalized and 
              loyalty card and tender credit are in the POS journal export.
        Given the cashier added item "Sale Item A" to the transaction
        And the customer swiped a cobranded card "loyalty_cobranded_mc_new" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "cobranded dry stock credit" template


    @slow @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Cashier adds dry stock. Customer swipes a cobranded card on the pinpad and cashier tenders the transaction with cash, 
              transaction is finalized and loyalty card and tender cash are in the POS journal export.
        Given the cashier added item "Sale Item A" to the transaction
        And the customer swiped a cobranded card "loyalty_cobranded_mc_new" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Cashier tenders postpay transaction in credit with cobranded card, transaction is finalized and  
              transaction is finalized and transaction data are correct.
        Given the cashier added item "Sale Item A" to the transaction
        And the customer dispensed "Regular" for "3.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the customer swiped a cobranded card "loyalty_cobranded_mc_new" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Cashier adds dry stock and Customer swipes a cobranded card. Cashier partially tenders transaction with cash and rest in credit with cobranded card,  
              transaction is finalized and transaction data are correct.
        Given an item "Sale Item A" is present in the transaction "5" times
        And the customer swiped a cobranded card "loyalty_cobranded_mc_new" on the pinpad
        And the cashier tendered the transaction with $3 in cash
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
