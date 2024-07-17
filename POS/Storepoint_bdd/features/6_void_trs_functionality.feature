@stp-bdd @saletransaction
Feature: Void transaction functionality test feature
    Goal of this feature is to test different types of void transactions using POS app.

    @voidtrs  @wip
    Scenario: Void trs check, test void transaction functionality when dry items are added in sale
        Given Add different dry items to POS sale trs
        |ItemCode|price|
        When click on void transaction button
        Then the POS goes back to main view
        And the transaction is completed
