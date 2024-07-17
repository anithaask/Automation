@stp-bdd @basic_test
Feature: Basic test scenario
    Goal of this feature is to run POS application and login into the app.


    @basic_test  @wip1
    Scenario: Basic scenario, to check POS application login is working
        Given POS application is Launched
        When cashier login is clicked
        Then the POS displays the "main" frame
        And the POP pump displays on POS main dialog
