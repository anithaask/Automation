@sitbdd @pos @fuel @sc @test_scenario
Feature: Basic test scenario
    Goal of this feature is to run it with builds and see if it passes for compatibility of packages.

    Background: Basic configuration
        Given the system is configured for NAXML exports with schema version "3.4"


    @positive @glacial
    Scenario: Basic scenario, only check if we can go to ready to sell state
        # With this change, it needs to be changed everywhere, RPOS-63957
        # After this change, it will use also SC BDD and RCM BDD with full potential
        # Given the RCM site "xxx" is linked
        Given the system is in a ready to sell state
        Then the POS displays the "main" frame
        And the pump "1" displays welcome prompt
