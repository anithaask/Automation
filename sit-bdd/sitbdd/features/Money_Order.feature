@sitbdd @pos @rcm @sc
Feature: Money order feature
# system this was tested on didn't have functional exports so these are left for later
# export verify prices for money order item and fees and total balance

    Background:
        Given following POS options are set in RCM
            | option_name                   | option | value_text         | value |
            | Money order fee amount        | 111    | $0.69              | 0.69  |
            | Money order refund fee amount | 112    | $0.79              | 0.79  |


    @glacial
    Scenario: 5 - Refund transaction - Money order transaction is not allowed - Refund Not Allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text         | value |
            | Money order refund            | 1305   | Refund not allowed | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier started a refund transaction
        And the cashier failed to add a money order to the transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the previous transaction's total is $0.00
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 9 - Money order transaction is not refunded - Refund Not Allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text         | value |
            | Money order refund            | 1305   | Refund not allowed | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And a refund transaction was denied
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | 0.69        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 20.69       |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 6 - Refund transaction - Money order transaction is refunded correctly - Refund Amount Only
        Given following POS options are set in RCM
            | option_name                   | option | value_text         | value |
            | Money order refund            | 1305   | Refund amount only | 1     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier started a refund transaction
        And the cashier added a $20.00 money order to the transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then  all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.79       |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.21       |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 10 - Money order transaction is refunded correctly - Refund Amount Only
        Given following POS options are set in RCM
            | option_name                   | option | value_text         | value |
            | Money order refund            | 1305   | Refund amount only | 1     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier started a refund transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.79       |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.21       |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 13 - Money order refund purchase fee only - Refund Amt. or Fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text           | value |
            | Money order refund            | 1305   | Refund amount or fee | 2     |
            | Money order voids not allowed | 1828   | No                   | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier started a refund transaction
        And the cashier added a $20.00 money order to the transaction
        And the cashier voided item "Money Order/EACH"
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
            | field                  | value       |
            | MoneyOrderFeeCollected | 0.69        |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 0.69        |
        # And the RSM report for "Money order sales" is correct


    # POS VR item selection is bad, doesn't generate missing MO fee dialog
    # RPOS-63827 ticket created under the POS_Cobalt team
    @glacial @wip
    Scenario: 23 - Return MO purchase fee - Refund transaction
        Given following POS options are set in RCM
            | option_name                   | option | value_text           | value |
            | Money order voids not allowed | 1828   | No                   | 0     |
            | Money order refund            | 1305   | Refund amount or fee | 2     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier voided item "M.O. Fee"
        And the cashier restored the money order fee
        And the cashier started a refund transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        # Then the previous transaction's total is $20.69
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "a money order sale" template
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 11 - Money order transaction is refunded correctly - Refund Amt. or Fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text           | value |
            | Money order refund            | 1305   | Refund amount or fee | 2     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier started a refund transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.1        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.9        |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 7 - Refund transaction - Money order transaction is refunded correctly - Refund Amt. or Fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text           | value |
            | Money order refund            | 1305   | Refund amount or fee | 2     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier started a refund transaction
        And the cashier added a $20.00 money order to the transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.1        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.9        |
        # And the RSM report for "Money order sales" is correct


    # Doesn't work even manually since voids are set to not allowed but the scenario expects them to work
    # RPOS-63826 ticket created under the POS_Cobalt team
    @glacial @wip
    Scenario: 16 - Money order void refund transaction - Void not allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text            | value |
            | Money order refund            | 1305   | Refund amount and fee | 3     |
            | Money order voids not allowed | 1828   | Yes                   | 1     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier started a refund transaction
        And the cashier voided item "Money Order/EACH"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then the previous transaction's total is $0.00
        And all transactions are summarized
        # And the generated export "NAXML-POSJournal" matches "a money order sale" template
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 17 - Money order void refund transaction - Void is allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text            | value |
            | Money order refund            | 1305   | Refund amount and fee | 3     |
            | Money order voids not allowed | 1828   | No                    | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier started a refund transaction
        And the cashier navigated to the main frame
        And the cashier voided item "Money Order/EACH"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then the previous transaction's total is $0.00
        And all transactions are summarized
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 8 - Refund transaction - Money order transaction is refunded correctly - Refund Amt. and Fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text            | value |
            | Money order refund            | 1305   | Refund amount and fee | 3     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier started a refund transaction
        And the cashier added a $20.00 money order to the transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.1        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.9        |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 12 - Money order transaction is refunded correctly - Refund Amt. and Fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text            | value |
            | Money order refund            | 1305   | Refund amount and fee | 3     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier started a refund transaction
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | -0.1        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 19.9        |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 19 - Void money order purchase fee - Void is allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text | value |
            | Money order voids not allowed | 1828   | No         | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier voided item "M.O. Fee"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 20          |
        # And the RSM report for "Money order sales" is correct


    # POS VR item selection is bad, doesn't generate missing MO fee dialog
    # RPOS-63827 ticket created under the POS_Cobalt team
    @glacial @wip
    Scenario: 22 - Return MO purchase fee
        Given following POS options are set in RCM
            | option_name                   | option | value_text | value |
            | Money order voids not allowed | 1828   | No         | 0     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier voided item "M.O. Fee"
        And the cashier restored the money order fee
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        # Then the previous transaction's total is $20.69
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "a money order sale" template
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 18 - Void money order purchase fee - Void not allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text | value |
            | Money order voids not allowed | 1828   | Yes        | 1     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And the cashier voided item "M.O. Fee"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 20          |
        # And the RSM report for "Money order sales" is correct


    @glacial
    Scenario: 14 - Money order void - Void not allowed
        Given following POS options are set in RCM
            | option_name                   | option | value_text | value |
            | Money order voids not allowed | 1828   | Yes        | 1     |
        And the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"
        And the cashier added a $20.00 money order to the transaction
        And an attempt to void item "Money Order/EACH" was denied
        And the cashier navigated to the main frame
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "TransactionDetailGroup" in generated export "NAXML-POSJournal" matches the following values
            | field                  | value       |
            | MoneyOrderFeeCollected | 0.69        |
            | MoneyOrderFaceAmount   | 20          |
            | TenderSubCode          | cash_tender |
            | TenderAmount           | 20.69       |
        # And the RSM report for "Money order sales" is correct
