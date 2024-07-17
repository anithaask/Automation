@sitbdd @rcm @pos @fuel @sc
Feature: Rest In Gas transactions
    This feature file tests scenarios with Rest in gas feature being enabled.


    @glacial
    Scenario: RCM option Display Rest in Gas button is enabled. Tender the transaction with Rest in gas item,
              cancel the transaction on pump, the ICR is ready for a new transaction after few seconds.
        Given following POS options are set in RCM
            | option_name                | option | value_text | value |
            | Display Rest in Gas button | 5130   | Yes        | 1     |
            | Prepay Grade Select Type   | 5124   | None       | 0     |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item B" to the transaction
        And the cashier added Rest in gas on the POS for the pump "1" to the transaction
        And the manager tendered the transaction with $15.00 in cash
        When the customer lifts and hangs up the nozzle at pump "1"
        Then the pump "1" displays welcome prompt
