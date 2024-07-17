@debit @emv @wip
Feature: ContactDebitEMV
    I want to test the contact debit EMV Functionality.

    Background: Contact debit EMV base configuration setup
        Given Pumps are configured for ICR
        And ICR timing event RECEIPT is configured AFTERFUELING
        And ICR timing event ADVERTISEMENT is configured DURINGFUELING
        And following ICR options are set in RCM
            | option        | value |
            | PROMPTTIMEOUT | 10    |
            | CREDITTIMEOUT | 15    |
            | NOFLOWTIMEOUT | 15    |
            | TRANTYPE      | NO    |
            | CANCELISNO    | NO    |
            | DEBITACCEPTED | YES   |
        And the system is in a ready to sell state


    @positive
    Scenario: Verify a contact debit EMV transaction where credit controller is offline #PEV-27
        Given I am using pump 1
        And ICR is ready for transactions
        When the credit controller goes offline
        And the card with attributes EMV Debit,Chip,SingleApplication,PIN is inserted
        Then the configured prompt "CREDITDOWN" is displayed on pump "1"
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        And I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive
    Scenario: Verify a contact debit EMV transaction with receipt before fueling #PEV-30
        Given ICR timing event RECEIPT is configured BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Discover,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 2 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        And the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt will contain verified by PIN
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive
    Scenario: Verify a contact debit EMV transaction with only one application for the card and carwash selection #PEV-404
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes EMV Debit,Chip,SingleApplication,PIN is inserted
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "ASKWASH PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then carwash items are displayed at ICR
        When I select first carwash item
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt will contain carwash item
        And I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive
    Scenario: Verify a contact debit EMV transaction with debit fee and receipt after fueling #PEV-33
        Given ICR timing event RECEIPT is configured AFTERFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        And credit controller is configured with a debit fee of $3
        And updated configuration is loaded by credit controller
        When the card with attributes Discover,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        When I perform fueling at pump
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt will contain debit fee
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive
    Scenario: Verify a contact debit EMV transaction with replace nozzle prompt and receipt after fueling #PEV-36
        Given ICR timing event RECEIPT,ADVERTISEMENT is configured AFTERFUELING,DURINGFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Discover,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 2 on chip card
        Then the Chip flow will prompt for PIN entry
        When the customer presses "1234E" key on pump "1" keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        When I lift the nozzle
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"
        When I select fuel grade 3
        And I fuel for 8 seconds
        Then ICR will display advertisement
        When I stop fueling
        And I wait for the configured timeout NOFLOWTIMEOUT seconds
        Then the configured prompt "REPLACENOZZLE" is displayed on pump "1"
        When I hang up the nozzle
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt will contain verified by PIN
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt
