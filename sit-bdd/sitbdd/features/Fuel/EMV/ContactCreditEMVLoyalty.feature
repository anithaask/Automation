@credit @loyalty @emv @wip
Feature: ContactCreditEMVLoyalty
# ConcordATL payment network needs to be updated to support EMV.
# Pumps need to be changed to Wayne IXCAT since Wayne does not support EMV.
    I want to test the contact credit EMV with loyalty functionality.

    Background: Contact credit EMV with loyalty base configuration setup
        Given the pumps are configured for "Prepay,Postpay,ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 10    |
            | CREDITTIMEOUT      | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | NO    |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISNO         | NO    |


    @positive
    Scenario: Verify a contact credit EMV transaction with loyalty swipe and invalid EMV card #PEV-16
        Given following ICR options are set in RCM
            | option           | value |
            | MAXCHIPFAILRETRY | 1     |
        And the system is in a ready to sell state
        And a loyalty swipe was performed with "loyalty" at pump "1"
        And the customer lifted the nozzle on pump "1"
        And the customer inserted card "Bad ChipCard" at pump "1"
        And the customer removed card "Bad ChipCard" at pump "1"
        And the customer inserted card "Bad ChipCard" at pump "1"
        When the customer removes card "Bad ChipCard" at pump "1"
        Then the dynamic prompt "Please Swipe Card" is displayed on pump "1"
        And the configured prompt "SALECANCELLED" is displayed on pump "1"
        And the transaction is logged as "Chip Failure" by the credit controller


    @positive
    Scenario: Verify a contact credit EMV transaction with carwash and loyalty with price rollback #PEV-19
        Given following ICR options are set in RCM
            | option             | value |
            | ALLOWLYLTYAFTERMOP | YES   |
        And the pumps have the following timing events configured
            | option        | value         |
            | CARWASH       | BEFOREFUELING |
            | ADVERTISEMENT | DURINGFUELING |
        And the system is in a ready to sell state
        And the customer inserted card "Visa Chip" at pump "1"
        And the customer removed card "Visa Chip" at pump "1"
        And a loyalty swipe was performed with "loyalty" at pump "1"
        And the customer accepts price rollback on pump "1" keypad
        And carwash is accepted on pump "1" keypad
        And the customer selected the first carwash option at pump "1"
        And the customer lifted the nozzle on pump "1"
        When the customer dispenses grade "Midgrade" fuel for $4.00 price on pump "1" with advertisements
        Then the configured prompt "RCPT PRNTNG" is displayed on pump "1"
        And the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the receipt contains carwash item
        And the receipt contains discount fuel price
