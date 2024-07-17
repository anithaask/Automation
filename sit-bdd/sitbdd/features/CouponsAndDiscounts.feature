@sitbdd @pos @fuel @sc @wip
Feature: This feature tests operations with coupons, discounts.

    Background:
        Given the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"


    @wip
    # RPOS-61900: RCMc ItemD Free coupon does not exist on our systems.
    Scenario Outline: Cashier adds postpay to transaction with free item coupon and tenders the transaction,
                      transaction is finalized and transaction data are correct.
        Given the cashier added item "Sale Item D" to the transaction
        And a coupon "RCMc ItemD free" is present in the transaction
        And the customer dispensed "Regular" for <price> price at pump "1"
        And the cashier added a postpay item to the transaction
        When the cashier tenders the transaction for exact dollar with tender type <tender_type>
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches <export> template

        Examples:
            | tender_type   | export                                                       | price   |
            | "cash"        | "postpay with free item coupon cash"                         | "3.00"  |
            | "check"       | "a postpay with a free item coupon sale tendered with check" | "20.85" |


    @wip
    # RPOS-52576: There are currently no pinpads on our systems.
    # RPOS-61900: RCMc ItemD Free coupon does not exist on our systems.
    Scenario: Cashier adds postpay to transaction with free item coupon and tenders the transaction with credit,
              transaction is finalized and transaction data are correct.
    Given the cashier added item "Sale Item D" to the transaction
    And a coupon "RCMc ItemD free" is present in the transaction
    And the customer dispensed "Regular" for "19.75" price at pump "1"
    And the cashier added a postpay item to the transaction
    And the customer swiped a credit card "credit_discover" on the pinpad
    When the cashier tenders the transaction for exact dollar with tender type "credit"
    Then all transactions are summarized
    And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
        | field       | value       |
        | Placeholder | Placeholder |
        | Placeholder | Placeholder |
        | Placeholder | Placeholder |


    @wip
    # RPOS-61900: BOGO coupon does not exist on our systems.
    Scenario: Cashier adds postpay to transaction with BOGO coupon and tenders the transaction with credit,
              transaction is finalized and transaction data are correct.
    Given the cashier added item "Sale Item D" to the transaction
    And a coupon "Buy one get one free" is present in the transaction
    And the customer dispensed "Regular" for "19.75" price at pump "1"
    And the cashier added a postpay item to the transaction
    When the cashier tenders the transaction for exact dollar with tender type "cash"
    Then all transactions are summarized
    And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
        | field       | value       |
        | Placeholder | Placeholder |
        | Placeholder | Placeholder |
        | Placeholder | Placeholder |
