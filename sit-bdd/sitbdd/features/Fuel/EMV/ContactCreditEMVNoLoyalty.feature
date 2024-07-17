@credit @emv @wip
Feature: ContactCreditEMVNoLoyalty
    Goal of this feature is to test the contact credit EMV with no loyalty functionality.

    Background: Contact credit EMV with no loyalty base configuration setup
        Given the pumps are configured for "Prepay,Postpay,ICR"
        And following ICR options are set in RCM
        | option        | value   |
        | PROMPTTIMEOUT | 10      |
        | CREDITTIMEOUT | 15      |
        | TRANTYPE      | DEFAULT |
        | CANCELISNO    | NO      |
        And the pumps have the following timing events configured
        | option  | value        |
        | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state


    @positive @glacial @wip
    # The verification for dispense fuel step is inconsistent and needs to be researched.
    Scenario: Perform a simple EMV transaction.
        Given the customer inserted card with attributes "Visa,Chip,MultiApplication,PIN" at pump "1"
        And the customer selected application "1" on chip card on pump "1"
        And the customer entered the correct PIN "1234E" on pump "1" keypad
        And the customer removed their card from the pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        When the customer declines the receipt on pump "1" keypad
        Then the configured prompt "THANKS" is displayed on pump "1"


    @positive @glacial
    Scenario: Verify a contact credit EMV transaction where loyalty is not accepted.
        When a loyalty swipe is performed with "loyalty" at pump "1"
        Then the configured prompt "INVALIDCARD" is displayed on pump "1"


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with invalid card #PEV-38
        Given I am using pump 1
        And following ICR options are set in RCM
            | option           | value |
            | MAXCHIPFAILRETRY | 1     |
        And ICR is ready for transactions
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "REINSERTCARD" is displayed on pump "1"
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the dynamic prompt Please Swipe Card is displayed on pump 1
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        And EMV card is logged with Chip Failure in credit controller transaction
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction where card brand is not accepted #PEV-40
        Given I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Unsupported Card,Chip is inserted
        Then the dynamic prompt Unknown card is displayed on pump 1
        And the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @postive @wip
    Scenario: Verify a contact credit EMV transaction where EMV card is removed without selecting application #PEV-42
        Given I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When the card is removed
        Then the dynamic prompt Please Swipe Card is displayed on pump 1
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction where credit network is down #PEV-43
        Given I am using pump 1
        And ICR is ready for transactions
        When the credit controller goes offline
        And the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the configured prompt "CREDITDOWN" is displayed on pump "1"
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        And I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with receipt prompt and cancel before fueling #PEV-44
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with cancel at application selection #PEV-408
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the dynamic prompt Transaction Canceled is displayed on pump 1
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with cancel at PIN entry #PEV-407
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the dynamic prompt Transaction Canceled is displayed on pump 1
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        And the ICR receipt will contain declined item
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with carwash selection and cancel before fueling #PEV-46
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "ASKWASH PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then carwash items are displayed at ICR
        When I select first carwash at ICR
        And I lift the nozzle
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        When I hang up the nozzle
        And I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with carwash selection, receipt prompt suppressed, and attempt to cancel during fueling #PEV-47
        Given ICR timing event CARWASH,RECEIPT,ADVERTISEMENT is configured BEFOREFUELING,BEFOREFUELING,DURINGFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "ASKWASH PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then carwash items are displayed at ICR
        When I select first carwash at ICR
        When I lift the nozzle
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"
        When I select fuel grade 1
        And I start fueling
        Then ICR will display advertisement
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "CANNOTCANCEL" is displayed on pump "1"
        When I hang up the nozzle
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt does not contain carwash item
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a PAP EMV credit transaction with carwash prompt but do not select carwash #PEV-48
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,MultiApplication,PIN is inserted
        Then the Chip flow will prompt for Application entry
        When I select application 1 on chip card
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "ASKWASH PROMPT" is displayed on pump "1"
        When the customer presses "NO" key on pump "1" keypad
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt does not contain carwash item
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction where card cannot be read after three attempts #PEV-50
        Given ICR timing event CARWASH,RECEIPT,ADVERTISEMENT is configured BEFOREFUELING,BEFOREFUELING,DURINGFUELING
        And following ICR options are set in RCM
            | option           | value |
            | MAXCHIPFAILRETRY | 3     |
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "REINSERTCHIP" is displayed on pump "1"
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "REINSERTCHIP" is displayed on pump "1"
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the configured prompt "REINSERTCHIP" is displayed on pump "1"
        When the card with attributes Bad ChipCard,Chip is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the dynamic prompt Please Swipe Card is displayed on pump 1
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is cancelled by credit controller
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with receipt printer out of paper #PEV-51
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And the system is in a ready to sell state
        And the ICR receipt printer is out of paper
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "ASKWASH PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then carwash items are displayed at ICR
        When I select first carwash at ICR
        And I perform fueling at pump
        Then the configured prompt "RECEIPTFAIL" is displayed on pump "1"
        And the receipt is not printed at ICR
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction where carwash prompt is streamlined and receipt is printed #PEV-54
        Given ICR timing event CARWASH,RECEIPT is configured BEFOREFUELING,BEFOREFUELING
        And following ICR options are set in RCM
            | option      | value      |
            | CARWASHMODE | STREAMLINE |
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        # Then the configured prompt "STREAMLINECW" is displayed --> I do not see the configured prompt but I see the following
        Then the streamlined configured carwash prompt is displayed
        When I select first carwash at ICR
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the ICR receipt will contain carwash item
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with no carwash prompt and receipt fail #PEV-55
        Given ICR timing event RECEIPT is configured BEFOREFUELING
        And the system is in a ready to sell state
        And the ICR receipt printer is out of paper
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I perform fueling at pump
        Then the configured prompt "RECEIPTFAIL" is displayed on pump "1"
        And the receipt is not printed at ICR
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with PIN and receipt prompt before fueling #PEV-56
        Given ICR timing event RECEIPT is configured BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes MasterCard,Chip,SingleApplication,PIN is inserted
        Then the Chip flow will prompt for PIN entry
        When 1234E is entered for PIN on ICR keypad
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the receipt is printed at ICR
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with receipt prompt before fueling #PEV-57
        Given ICR timing event RECEIPT is configured BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I perform fueling at pump
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the receipt is printed at ICR
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario:  Verify a contact credit EMV transaction with receipt prompt after fueling #PEV-58
        Given ICR timing event RECEIPT is configured AFTERFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        When I perform fueling at pump
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the receipt is printed at ICR
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt


    @positive @wip
    Scenario: Verify a contact credit EMV transaction with receipt prompt before fueling and sale times out #PEV-59
        Given ICR timing event RECEIPT is configured BEFOREFUELING
        And the system is in a ready to sell state
        And I am using pump 1
        And ICR is ready for transactions
        When the card with attributes Visa,Chip,SingleApplication is inserted
        Then the configured prompt "REMOVECHIPCARD" is displayed on pump "1"
        When the card is removed
        Then the ICR transaction is approved by credit controller
        Then the configured prompt "RECEIPT PROMPT" is displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        And I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the configured prompt "SALETIMEDOUT" is displayed on pump "1"
        And the transaction is cancelled by the credit controller
        And the ICR receipt will contain declined item
        When I wait for the configured timeout PROMPTTIMEOUT seconds
        Then the pump "1" displays welcome prompt
