@sc @manual @wip
Feature: This feature file tests sending receipts to TDM and NCR Analytics

    Background:
        Given the SC is in a ready to sell state
        And SC is connected to TDM service
        And POS option 1557 is set to YES


    # {id} is RPOS transaction id
    @positive
    Scenario: Perform new transaction, verify the Receipt is uploaded to TDM raw export
        Given the transaction containg drystock was finalized
        And automatic TDM export to cloud was processed
        When the user calls TDM endpoint "/transaction-document/v2/transaction-documents/:{id}/raw"
        Then raw export contains Receipt Date, Receipt Time, Receipt Print Count and encoded Receipt Data


    # {id} is RPOS transaction id
    @positive
    Scenario: Perform new transaction, verify the Receipt is uploaded to TDM canonical export
        Given the transaction containg drystock was finalized
        And automatic TDM export to cloud was processed
        When the user calls TDM endpoint "/transaction-document/transaction-documents/{id}"
        Then canonical export contains Receipt ID, Receipt Info (encoding method) and encoded Receipt Data


    # {id} is RPOS transaction id
    @positive
    Scenario: Perform new transaction, verify the Receipt is retrievable by GetReceipt call in TDM
        Given the transaction containg drystock was finalized
        And automatic TDM export to cloud was processed
        When the user calls TDM endpoint "/transaction-document/transaction-documents/:{id}/receipt"
        Then GetReceipt call returns encoding method and encoded Receipt Data


    @positive
    Scenario Outline: Perform new transaction, verify the Receipt is retrievable in NCR Analytics
        Given the transaction <transaction_nr> containg drystock was finalized on the business day <business_day>
        And automatic TDM export to cloud was processed
        When the analytics user logs into NCR Analytics
        And analytics user navigates to Transaction Cash Office
        And analytics user selects business day <business_day>
        And analytics user selects transaction <transaction_nr>
        And analytics user selects Receipt Image
        Then Receipt Image is loaded for the analytics user

        Examples:
        | business_day | transaction_nr |
        | 10/31/2023   | 574            |
