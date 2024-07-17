@sc @requires_sigma @wip
Feature: Batch Close
    Perform a batch close on loyalty transactions at EOD or via Dynamic Buttons

# Dynamic Buttons
# -------------------------------
# Install a Loyalty Package with Dynamic Buttons enabled.
# Author a button on the Other Functions screen associated
# with the “Loyalty Functions Dynamic” event and ensure that
# the Button grid with configured buttons come up and perform
# the selected loyalty action when pressed.

# Note to a loyalty transaction
# -------------------------------
# Run a transaction with a loyalty discount. Ensure the Loyalty Card Description
# and Batch/Sequence number is set properly for the transaction

    Background:
        Given I start a new business day
        And the "loyalty" host is "online"
        And the "loyalty" controller has a completed transaction


    @glacial @positive
    Scenario: Perform standard Loyalty Batch Close
        When I close current business day
        And I request a full NAXML POS Journal export
        Then the NAXML POS Journal should be exported
        And the exported journal should contain the merchandise batch total data with reason code as "2"


    @glacial @positive
    Scenario: Perform Forced Batch
        When I force a loyalty batch close
        And I request a full NAXML POS Journal export
        Then the NAXML POS Journal should be exported
        And the exported journal should contain the merchandise batch total data with reason code as "ForceBATCH"


    @glacial @negative
    Scenario: Attempt Loyalty BatchClose when Sigma is offline
        Given the loyalty controller is offline
        And I force a loyalty batch close
        And I request a full NAXML POS Journal export
        Then the NAXML POS Journal should be exported
        And the exported journal should not contain the merchandise batch total data


    @glacial @positive
    Scenario: Perform BatchClose when host is offline
        Given the "loyalty" host is "offline"
        And I force a loyalty batch close
        And I request a full NAXML POS Journal export
        Then the NAXML POS Journal should be exported
        And the exported journal should not contain host data
        And the exported journal should contain title "Batch Pending"
