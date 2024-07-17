@sitbdd @pos @sc @jag
Feature: POS and ICR utilities
    Test POS and ICR utilities.

    Background:
        Given event messages are cleared
        And the transaction history is clear
        And the pumps are configured for "Prepay,Postpay,ICR"
        And following POS options are set in RCM
            | option_name               | option | value_text      | value |
            | Prepay Grade Select Type  | 5124   | One Touch       | 1     |


    @fast
    Scenario: Ensure the pump buttons are functional when the POS terminal is locked - Cash Post-Pay
        Given the system is in a ready to sell state
        And the cashier locked the POS
        And the customer dispensed "Regular" for "5.00" price at pump "1"
        And the cashier unlocked the POS
        And the cashier added a postpay item to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then a fuel item "Regular" with price "5.00" and volume "1.250" is in the "previous" transaction


    @fast
    Scenario: Ensure the pump buttons are functional when the POS terminal is locked - PAP
        Given the system is in a ready to sell state
        And the cashier locked the POS
        And the customer completed a PAP of fuel grade "Regular" with "10.00" at pump "1"
        When the cashier unlocks the POS
        Then the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |


    @fast
    Scenario: Ensure the pump buttons are functional when the POS terminal is locked - Pre-Pay
        Given the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "10.00" at pump "1"
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the cashier locked the POS
        And the customer fully dispensed the prepay on pump "1" with grade "Regular"
        When the cashier unlocks the POS
        Then the first line in Scroll previous contains following elements
            | element           | value        |
            | node type         | Pump         |
            | node number       | 1            |
            | transaction type  | Prepay Final |


    @fast
    Scenario: Ensure that "STOP All Pumps" button should be functional when the POS terminal is locked - PAP
        Given the system is in a ready to sell state
        And the cashier locked the POS
        And the customer begins a PAP on pump "1" and selects a fuel grade "Regular"
        When the cashier stops all pumps
        Then the pump "1" stops


    @fast
    Scenario: PAP sale with receipt paper out on ICR
        Given the system is in a ready to sell state
        And the pump "1" is out of receipt paper
        And the customer begins a PAP on pump "1" with pump prompting out of receipt paper
        When the customer dispenses grade "Regular" fuel for $10.00 price on pump "1"
        Then the ICR displays the "THANKS" prompt within "5" seconds on pump "1"
        And the "Paper Out: ICR 1" alert is shown on the menu bar


    @fast
    Scenario: Pump is out of receipt paper. Cashier reffils paper in pump, Paper out alert is not shown on the menu bar
        Given the system is in a ready to sell state
        And the pump "1" is out of receipt paper
        And the customer completed a PAP of fuel grade "Regular" with "10.00" at pump "1"
        When the operator refills the receipt paper in pump "1"
        Then the "Paper Out: ICR 1" alert is not shown on the menu bar


    @fast
    Scenario: Customer presses Help button on the pump, the Help alert is shown on POS.
        Given the system is in a ready to sell state
        When the customer presses "HELP" key on pump "1" keypad
        Then the "Help: PUMP 01" alert is shown on the menu bar


    @fast
    Scenario: Cashier presses Help alert on POS, the Help alert is not shown on POS anymore.
        Given the system is in a ready to sell state
        And the customer pressed "HELP" button on pump "1"
        When the cashier presses the "Help: PUMP 01" alert on the menu bar
        Then the "Help: PUMP 01" alert is not shown on the menu bar


    @fast
    Scenario: Cashier presses print button on Tank Inventory Levels frame, report is printed and contains correct data
        Given the system is in a ready to sell state
        And the cashier navigates to Tank Inventory Levels frame
        When the cashier presses the "report-print" button
        Then the tank inventory levels printed report contains
            | line_number | line                                       |
            | 1           | *                                        * |
            | 2           | *         TANK INVENTORY LEVELS          * |
            | 3           | *----------------------------------------* |
            | 5           | *----------------------------------------* |
            | 6           | *Tank #:                                1* |
            | 7           | *Grade:                    Diesel Product* |
            | 8           | *Fuel Volume:                    4000.000* |
            | 9           | *TC Fuel Volume:                 4200.000* |
            | 10          | *Water Volume:                     50.000* |
            | 11          | *Ullage:                          950.000* |
            | 12          | *Temperature:                        75.4* |
            | 13          | *----------------------------------------* |
            | 14          | *Tank #:                                2* |
            | 15          | *Grade:                       Mid Product* |
            | 16          | *Fuel Volume:                    4000.000* |
            | 17          | *TC Fuel Volume:                 4200.000* |
            | 18          | *Water Volume:                     50.000* |
            | 19          | *Ullage:                          950.000* |
            | 20          | *Temperature:                        75.4* |
            | 21          | *----------------------------------------* |
            | 22          | *Tank #:                                3* |
            | 23          | *Grade:                   Premium Product* |
            | 24          | *Fuel Volume:                    4000.000* |
            | 25          | *TC Fuel Volume:                 4200.000* |
            | 26          | *Water Volume:                     50.000* |
            | 27          | *Ullage:                          950.000* |
            | 28          | *Temperature:                        75.4* |
            | 29          | *----------------------------------------* |
            | 30          | *Tank #:                                4* |
            | 31          | *Grade:                   Regular Product* |
            | 32          | *Fuel Volume:                    4000.000* |
            | 33          | *TC Fuel Volume:                 4200.000* |
            | 34          | *Water Volume:                     50.000* |
            | 35          | *Ullage:                          950.000* |
            | 36          | *Temperature:                        75.4* |
            | 37          | *----------------------------------------* |
            | 38          | *------------- end of report ------------* |
            | 39          | *                                        * |
            | 40          | *                                        * |
