@sitbdd @jag @pos @sc
Feature: Feature includes example scenarios for different export comparison solution.

    Background:
        Given the system is in a ready to sell state
        And the system is configured for NAXML exports with schema version "3.4"


    @glacial @wip
    # RPOS-52576: Currently do not have pinpad for new systems.
    Scenario: Customer dispensed fuel at pump. Cashier adds postpay to the transaction and customer tenders transaction using SVC card, 
              transaction is finalized and transaction data are correct (new export prototype).
        Given the "credit_svc" SVC card was activated for $100
        And the customer dispensed "Regular" for "5.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the customer swiped a credit card "credit_svc" on the pinpad
        When the cashier tenders the transaction for exact dollar with tender type "credit"
        Then all transactions are summarized
        And the section "FuelLine" in generated export POSJournal matches data values
            | field            | value       |
            | FuelGradeID      | unl-91      |
            | FuelPositionID   | 1           |
            | PriceTierCode    | 1           |
            | ServiceLevelCode | 1           |
            | Description      | Regular     |
            | ActualSalesPrice | 1.889       |
            | MerchandiseCode  | cat_natural |
            | RegularSellPrice | 1.889       |
            | SalesQuantity    | 2.647       |
            | SalesAmount      | 5           |


    @glacial
    Scenario: Cashier adds a dry stock and tenders with cash, 
              transaction is finalized and generated export matches xsd template.
        Given the cashier added item "Sale Item A" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the generated "NAXML-POSJournal34RadiantExtension" matches XSD schema


    @glacial
    Scenario: Customer adds a dry stock and tenders with cash,
              transaction is finalized and generated export matches template.
        Given the cashier added item "Sale Item A" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the generated export "NAXML-POSJournal" matches "drystock with cash" template


    @glacial
    Scenario: Customer adds a dry stock and tenders with cash,
              transaction is finalized and generated export has correct values.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "ItemLine" in generated export "NAXML-POSJournal" matches the following values
            | field            | value        |
            | Description      | Sale Item B  |
            | POSCode          | 088888888880 |
            | ActualSalesPrice | 1.99         |
            | SellingUnits     | 1            |
            | RegularSellPrice | 1.99         |
            | SalesQuantity    | 1            |
            | SalesAmount      | 1.99         |


    @glacial
    Scenario: Customer adds a dry stock and tenders with cash,
              transaction is finalized and generated export has correct values.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "ItemCode" in generated export "NAXML-POSJournal" matches exactly the following values
            | field            | value        |
            | POSCodeFormat    |              |
            | POSCode          | 099999999990 |
            | POSCodeModifier  | 1            |
            | InventoryItemID  |              |


    @glacial
    Scenario: Customer adds a dry stock and tenders with cash,
              transaction is finalized and generated export has correct values.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "ItemLine" with namespace "radiant" in generated export "NAXML-POSJournal" matches the following values
            | field                 | value |
            | RecalledTransactionID | 0     |
            | TaxItemizerMask       | 14    |


    @glacial
    Scenario: Customer adds a dry stock and tenders with cash,
              transaction is finalized and generated export has correct values.
        Given the cashier added item "Sale Item A" to the transaction
        And the cashier added item "Sale Item B" to the transaction
        When the cashier tenders the transaction for exact dollar with tender type "cash"
        Then all transactions are summarized
        And the section "ItemLine" with namespace "radiant" in generated export "NAXML-POSJournal" matches exactly the following values
            | field                   | value                |
            | RecalledTransactionID   | 0                    |
            | TaxItemizerMask         | 14                   |
            | OriginalTaxItemizerMask | 0                    |
            | External_Reference_Id   | ITT-088888888880-0-1 |


    @glacial
    Scenario: Pay In transaction, NAXMLexport
        Given the cashier navigated to the other functions frame
        When the cashier performs a "cash" Pay In with amount of "15.00"
        Then all transactions are summarized
        And the section "PayInDetail" in generated export "NAXML-POSJournal" matches the following values
            | field         | value         |
            | DetailAmount  | 15            |
            | PayInReason   | 70000000016   |


    @glacial
    Scenario: Pay Out transaction, NAXMLexport
        Given the cashier navigated to the other functions frame
        When the cashier performs a "cash" Pay Out with amount of "15.00"
        Then all transactions are summarized
        And the section "PayOutDetail" in generated export "NAXML-POSJournal" matches the following values
            | field         | value         |
            | DetailAmount  | 15            |
            | PayOutReason  | 70000000017   |
