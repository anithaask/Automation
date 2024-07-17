@stp-bdd @saletransaction
Feature: Sale Transaction feature
    Goal of this feature is to test different types of sale transactions using POS app.


    @saletransaction @wip 
    Scenario: Sale trs, to test sale with dry items using scanner and pay with cash tender
        Given Add the below items to POS sale trs
        |ItemCode|price|
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed

   saletransaction @wip
    Scenario: Sale trs, to test sale with dry items using item UPC Entry and pay with cash tender
        Given Add the below items to POS sale trs using item upc entry
        |ItemCode|price|
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed

    @saletransaction @wip1
    Scenario: Sale trs, to test sale with dry items using item lookup and pay with cash tender
        Given Add the below items to POS sale trs using item lookup
        |ItemCode|price|
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed


    @saletransaction
    Scenario: Sale trs, to test sale with dry items with mutilple quantity and pay with cash tender
        Given Add the below item1 to POS sale trs with random qty
        |ItemCode|price|
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed

    @saletransaction @wip2
    Scenario: Sale trs, to test sale with multiple dry items with mutilple quantity and pay with cash tender
        Given Add the below item1 to POS sale trs with random qty
        |ItemCode|price|
        And Add the below item2 to POS sale trs with random qty
        |ItemCode2|price|
        And update the quantity of item2
        When click on sub total, pay with cash tender
        Then the POS goes back to main view
        And the transaction is completed
