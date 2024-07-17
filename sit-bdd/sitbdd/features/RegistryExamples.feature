@sitbdd
Feature: Test registry handler for SITBDD.
    This feature file tests the functions of the registry handler for SITBDD.


    @test1
    Scenario: Test setting of registry value.
        Given the "WriteEpsilonVersionIntervalMinutes" key at path "Software\\RadiantSystems\\ElectronicPayments\\CacheManager" is set to "45"
        And the "WriteEpsilonVersionIntervalMinutes" key at path "Software\\RadiantSystems\\ElectronicPayments\\CacheManager" is set to "30"


    @test2
    Scenario: Test retrieval of registry value.
        Given the "WriteEpsilonVersionIntervalMinutes" key at path "Software\\RadiantSystems\\ElectronicPayments\\CacheManager" is "30"


    @test3
    Scenario: Test creation and deletion of registry value.
        Given the "Test" key at path "Software\\RadiantSystems\\HostSimulator\\ConcordATL" is set to "45"
        And the "Test" key at path "Software\\RadiantSystems\\HostSimulator\\ConcordATL" is deleted
