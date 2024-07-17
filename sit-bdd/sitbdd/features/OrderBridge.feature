@sc @css @kps @wip
Feature: Order Bridge
    This feature file test scenarios with food orders being processed and passed to KPS Transport for delivery to the KPS.

    Background:
        Given the RPOS Order Bridge Import feature is enabled
        And the RPOS Order Bridge Export feature is enabled
        And the site controller has the Order Bridge feature enabled
        And there are no pending KPS orders


    @slow @positive @requires_kps
    Scenario: Make a food order, validate the order is processed and sent to the KPS.
        Given there is a sandwich item configured
        When the customer orders 3 sandwich items
        Then the site controller sent order to the KPS
