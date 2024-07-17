@stp-bdd @fueltransaction
Feature: Fuel Transaction feature
    Goal of this feature is to test different types of sale transactions using POS app.


    @fueltransaction @wip1
    Scenario: fuel trs, to test sale with fuel items and pay with cash tender
        Given Add the fuel items to POS sale trs
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed
