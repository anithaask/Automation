@fuel
Feature: Tank Offline
    Check fuel tank responsiveness on the POS


    @fast
    Scenario: Tank is set offline, the POS displays Tank alert.
        Given the Tank "1" is online
        When the Tank Online button is pressed on fuel tank "1"
        Then the "Tank" alert is shown on the menu bar


    @fast
    Scenario: Tank is set online, Tank alert is no longer displayed on POS.
        Given the Tank "1" is offline
        When the Tank Offline button is pressed on fuel tank "1"
        Then the "Tank" alert is not shown on the menu bar
