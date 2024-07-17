@sitbdd @rcm @pos @fuel
Feature: Smart Prepay feature
    This feature file tests scenarios with Smart prepay.

    Background:
        Given following POS options are set in RCM
            | option_name               | option | value_text       | value |
            | Fuel credit prepay method | 1851   | Auth and Capture | 1     |
            | Prepay Grade Select Type  | 5124   | One Touch        | 1     |


    @slow
    Scenario: Perform a Smart Prepay transaction, check VR and pump authorization.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then the Smart Prepay fuel grade "Prepay:Regular" for price "20.0" is in the POS virtual receipt
        And the pump "1" is authorized for $20


    @slow
    Scenario: Perform a Smart Prepay transaction, check export is correct.
        Given the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "a smart prepay with cash" template


    @slow
    Scenario: Tender the prepay with cash. Cancel the prepay by pressing Cancel button at pump,
              validate the sale on ICR is cancelled.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the pump "1" displays welcome prompt


    @slow @credit @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Dispense all the prepaid fuel. Attempt to refund the fuel from the previous transaction,
              the POS displays Refund not allowed frame.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_discover" on the pinpad
        And the customer fully dispensed the prepay on pump "1" with grade "Regular"
        And the cashier navigated to the POS scroll previous frame
        When the cashier tries to refund the most recent fuel transaction
        Then the POS displays the "REFUND NOT ALLOWED" frame


    @slow @credit @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with credit. Cancel the prepay by pressing the cancel button at the pump,
              the ICR displays Sale cancelled frame.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_discover" on the pinpad
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @slow @credit @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with credit. Cancel the prepay by lifting and
              hanging up the nozzle after the grade is selected, the sale on pump is cancelled.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_discover" on the pinpad
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @credit @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with credit. Cancel the prepay by pressing the cancel button at the pump,
              the ICR displays Sale cancelled frame
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_discover" on the pinpad
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @slow @credit @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with credit. Cancel the prepay by lifting and
              hanging up the nozzle after the grade is selected, the sale on ICR is cancelled.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_discover" on the pinpad
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @negative_items_disabled @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Fuel Prepay before the SVC is activated
        Given following POS options are set in RCM
            | option_name                                       | option | value_text       | value |
            | Fuel credit prepay method                         | 1851   | Auth and Capture | 1     |
            | Allow Negative Items in Smart Prepay Transactions | 5145   | No               | 0     |
            | Container deposits active                         | 1440   | Yes              | 1     |
        And the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "10.0" at pump "1"
        And the cashier added a $100.00 SVC activation for "credit_svc" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit" on the pinpad
        When the customer dispenses fuel up to $5.00 on pump "1"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @negative_items_disabled @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Fuel Prepay after the SVC is activated
        Given following POS options are set in RCM
            | option_name                                       | option | value_text       | value |
            | Fuel credit prepay method                         | 1851   | Auth and Capture | 1     |
            | Allow Negative Items in Smart Prepay Transactions | 5145   | No               | 0     |
            | Container deposits active                         | 1440   | Yes              | 1     |
        And the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state
        And the cashier added a $100.00 SVC activation for "credit_svc" to the transaction
        And the cashier prepaid the fuel grade "Regular" for price "10.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit" on the pinpad
        When the customer dispenses fuel up to $5.00 on pump "1"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @negative_items_enabled @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Fuel Prepay before the gift card is activated
        Given following POS options are set in RCM
            | option_name                                       | option | value_text       | value |
            | Fuel credit prepay method                         | 1851   | Auth and Capture | 1     |
            | Prepay Grade Select Type                          | 5124   | One Touch        | 1     |
            | Allow Negative Items in Smart Prepay Transactions | 5145   | Yes              | 1     |
            | Container deposits active                         | 1440   | Yes              | 1     |
        And the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "10.0" at pump "1"
        And the cashier added a $100.00 SVC activation for "credit_svc" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit" on the pinpad
        When the customer dispenses fuel up to $5.00 on pump "1"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @negative_items_enabled @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Fuel Prepay after the gift card is activated
        Given following POS options are set in RCM
            | option_name                                       | option | value_text       | value |
            | Fuel credit prepay method                         | 1851   | Auth and Capture | 1     |
            | Prepay Grade Select Type                          | 5124   | One Touch        | 1     |
            | Allow Negative Items in Smart Prepay Transactions | 5145   | Yes              | 1     |
            | Container deposits active                         | 1440   | Yes              | 1     |
        And the system is configured for NAXML exports with schema version "3.4"
        And the system is in a ready to sell state
        And the cashier added a $100.00 SVC activation for "credit_svc" to the transaction
        And the cashier prepaid the fuel grade "Regular" for price "10.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit" on the pinpad
        When the customer dispenses fuel up to $5.00 on pump "1"
        Then all transactions are summarized
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with SVC card. Dispense all the prepaid fuel, validate the fuel item
              is printed in the receipt with correct grade name and dispensed value.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *5.000 Gallons @ $4.000/Gal        $20.00* |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with SVC card. Under-dispense the prepaid fuel, validate the fuel item
              is printed in the receipt with correct grade name and dispensed value.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer dispenses fuel up to $10.00 on pump "1"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *2.500 Gallons @ $4.000/Gal        $10.00* |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with SVC card. Dispense all the prepaid fuel, validate the fuel item
              is printed in the receipt with correct dispensed volume and price, together with the dry stock.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *5.000 Gallons @ $4.000/Gal        $20.00* |
            | 13          | *I1    Sale Item A                  $0.99* |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with SVC card. Under-dispense the prepaid fuel, validate the fuel item
              is printed in the receipt with correct dispensed volume and price, together with the dry stock.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item B" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer dispenses fuel up to $10.00 on pump "1"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *2.500 Gallons @ $4.000/Gal        $10.00* |
            | 13          | *I1    Sale Item B                  $1.99* |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with SVC card. Transfer the prepay to another pump, dispense all the prepaid fuel,
              validate the fuel item is printed in the receipt with correct pump number.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        And the cashier transferred a prepay from pump "1" to "2"
        When the customer fully dispenses the prepay on pump "2" with grade "Regular"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 2  Regular             *           |
            | 12          | *5.000 Gallons @ $4.000/Gal        $20.00* |


    @fast @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with SVC card. Cancel the prepay by lifting and
              hanging up the nozzle after the grade is selected, the sale on ICR is cancelled,
              the receipt printed from the last transction is containing fuel item with zero value.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt
        And the scroll previous printed receipt contains
            | line_number | line                                      |
            | 11          | *Pump # 1  Regular             *          |
            | 12          | *0.000 Gallons @ $4.000/Gal        $0.00* |


    @fast @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay with SVC card. Cancel the prepay by pressing Cancel button at the pump,
              the sale on ICR is cancelled, and the receipt printed from the last transaction
              is containing fuel item with zero value.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the pump "1" displays welcome prompt
        And the scroll previous printed receipt contains
            | line_number | line                                      |
            | 11          | *Pump # 1  Regular             *          |
            | 12          | *0.000 Gallons @ $4.000/Gal        $0.00* |


    @fast @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with SVC card. Cancel the prepay by lifting and hanging up the nozzle
              after the grade is selected, the sale on ICR is cancelled, and the receipt printed from the last transction
              is containing fuel item with zero value and dry stock items.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *0.000 Gallons @ $4.000/Gal        $0.00*  |
            | 13          | *I1    Sale Item A                  $0.99* |
            | 14          | *I1    Sale Item B                  $1.99* |


    @fast @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay and dry stock with SVC card. Cancel the prepay by pressing Cancel button at the pump,
              the sale on ICR is cancelled, and the receipt printed from the last transaction
              is containing fuel item with zero value and dry stock items.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the pump "1" displays welcome prompt
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *0.000 Gallons @ $4.000/Gal        $0.00*  |
            | 13          | *I1    Sale Item A                  $0.99* |
            | 14          | *I1    Sale Item B                  $1.99* |
        And the section "Placeholder" in generated export "NAXML-POSJournal" matches the following values
            | field       | value       |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |
            | Placeholder | Placeholder |


    @slow @svc @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Tender the prepay, containing the loyalty card in the transaction, with SVC card.
              Dispense all the prepaid fuel, validate the fuel item is printed in the receipt
              together with the loyalty discount.
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "20.0" at pump "1"
        And the customer chose to use loyalty card "loyalty"
        And the cashier tendered the transaction for exact dollar with tender type "credit"
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the customer fully dispenses the prepay on pump "1" with grade "Regular"
        Then the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *5.000 Gallons @ $4.000/Gal        $20.00* |
            | 13          | * Loyalty Reward             *             |
            | 14          | * 0.100 /gal Discount        *             |
