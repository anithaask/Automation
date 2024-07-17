@sc @wip
Feature: This feature file test setting/storing/retrieving transaction numbers.
    Manual because: To be moved into SC BDD.
    SIT can have tests where the transaction number is changed with transactions
    created on POS.

    Background:
        Given the SC is in a ready to sell state
        And the POS is in a ready to sell state


    @positive @fast @zephyr_pending
    Scenario: Perform new transaction, verify the transaction number is correctly updated.
        Given the last transaction number was 1
        When the cashier sets new transaction number
        Then the last transaction number is 2


    @positive @fast @zephyr_pending
    Scenario: Transaction number already reached maximum. Perform new transaction, verify number of new transaction is captured as 1.
        Given the last transaction number was 16777214
        When the cashier sets new transaction number
        Then the last transaction number is 1


    @positive @fast @zephyr_pending
    Scenario: Get last transaction number.
        Given the last transaction number was 222
        When the cashier requests last transaction number
        Then the last transaction number is 222
