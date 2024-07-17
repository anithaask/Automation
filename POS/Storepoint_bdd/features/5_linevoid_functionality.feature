@stp-bdd @saletransaction
Feature: Line void functionality test feature
    Goal of this feature is to test different types of line void transactions using POS app.

    @linevoid @wip
    Scenario: Line void check, test line void when multiple dry items are added in sale
        Given Add multiple dry items to POS sale trs
        |ItemCode|price|
        When line void one of the dry item
        And click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed
