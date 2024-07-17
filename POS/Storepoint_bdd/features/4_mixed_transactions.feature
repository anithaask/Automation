@stp-bdd @mixedtransaction
Feature: Mixed Transaction feature
    Goal of this feature is to test different types of sale transactions using POS app.


    @mixedtransaction @wip1
    Scenario: Mixed trs, to test sale with dry and fuel items and pay with cash tender
        Given Add the dry and fuel items to POS sale trs
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed
