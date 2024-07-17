@sitbdd @pos @fuel @ulp @wip
Feature: ULP condiment discounts
    This feature file focuses on ULP (Unified Loyalty and Promotions) condiment level discounts.

    Background: POS is configured for ULP feature
        Given the POS has essential configuration
        And the POS is configured to communicate with ULP Cloud Loyalty
        And the nep-server has default configuration
        # Cloud Loyalty Interface is set to ULP
        And the POS option 5284 is set to 0
        # Allow transaction modification after loyalty authorization is set to Yes
        And the POS option 5275 is set to 1
        # Promotion Execution Service Get Mode is set to ULP Get After Subtotal
        And the POS option 5277 is set to 1
        # Send only loyalty transactions is set to No
        And the POS option 5279 is set to 0
        And RCM item is present in db
            | item_id    | item_description           | amount | catalog_id  |
            | 5070000318 | Burger Classic extra 150 g | 7.19   | 70000000517 |
            | 5070000290 | Sesame Bun                 | 0.00   | 70000000489 |
            | 5070000294 | Mayonnaise with Pepper     | 0.00   | 70000000493 |
            | 5070000300 | Gouda Slice                | 0.00   | 70000000499 |
            | 5070000304 | Bacon Chips                | 0.35   | 70000000503 |
            | 5070000307 | Pickle Slices              | 0.00   | 70000000506 |
            | 5070000312 | Red Onion Slices           | 0.00   | 70000000511 |
            | 5070000316 | Salad                      | 0.00   | 70000000515 |
            | 5070000305 | Baked Egg                  | 0.00   | 70000000504 |
            | 5070000302 | Blue Cheese                | 0.30   | 70000000501 |
        And the ULP loyalty host has following combo discounts configured
            | promotion_id  | discount_value | referenced_description | item_codes            | discount_level | unit_type       |
            | 15_cents_off  | 0.15           | Referenced Description | 5070000305;5070000302 | item           | SIMPLE_QUANTITY |
        And following ULP cards are configured in RCM
            | card_definition_id | card_name | barcode_range_from | card_definition_group_id |
            | 70000001142        | ULP card  | 3210321032103210   | 70000010042              |


    @positive @wip
    Scenario Outline: Burger classic with paid condiment discount
        Given the POS is in a ready to sell state
        And the cashier added item <item> to the transaction
        # paid condiment
        And the cashier added condiment <condiment> to the transaction under item <item>
        And ULP card <ulp_card> is added to the transaction
        When the cashier tenders the transaction with cash
        Then loyalty discount <discount_description> with value of <discount_value> is added to transaction on POS
        And loyalty discount <discount_description> with value of <discount_value> is printed on the receipt
        And loyalty discount <discount_description> with value of <discount_value> is visible in RSM transaction journal
        And loyalty discount <discount_description> with value of <discount_value> is included in NAXML-POSJournal export

        Examples:
        | item                       | condiment   | ulp_card         | discount_description | discount_value |
        | Burger Classic extra 150 g | Blue Cheese | 3210321032103210 | 15_cents_off         | 0.15           |
