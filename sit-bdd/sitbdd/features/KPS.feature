@sitbdd @pos @kps @wip
# RPOS-68084: Needs a food item button added to POS as well as changes in LHDevCfg to become fully functional.
Feature: KPS Scenarios
    Goal of this feature is to test KPS functionality.

    Background:
        Given the system is in a ready to sell state

    @positive @glacial @wip
    Scenario: Food item is ordered and bumped on the KPS.
        Given the cashier added a food item "Food Item" to the transaction
        And the cashier tenders the transaction for exact dollar with tender type "cash"
        When the most recent transaction is bumped
        Then the KPS signals that the transaction was bumped
