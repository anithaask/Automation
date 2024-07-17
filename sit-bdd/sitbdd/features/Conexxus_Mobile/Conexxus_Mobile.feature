@sitbdd @pos @fuel @mobilepay
# RPOS-64660: Epsilon needs to be updated for SITBDD systems.
Feature: Conexxus mobile non-prepay sales
    This feature file focuses on Conexxus mobile transactions.

    Contains dry stock, postpay and PaP scenarios.
    Prepay scenarios are in different feature file separated by prepay by grade setting
    in order to minimize configuration changes between scenarios.

    Background:
        Given following POS options are set in RCM
            | option_name                  | option | value_text | value |
            | Enable Mobile Payment on POS | 1240   | Yes        | 1     |
        And the pumps are configured for "Prepay,Postpay,ICR"
        And following ICR options are set in RCM
            | option                  | value   |
            | ALLOWMOPATLYLTY         | TRUE    |
            | ENTERAFTERBUFFEREDINPUT | FALSE   |
            | FUELSTARTTIMEOUT        | 10      |
            | PROMPTTIMEOUT           | 4       |
            | TRANTYPE                | DEFAULT |
        And ConMob settings are cleared in the host simulator
        And the host simulator has set following registries
            | path                       | key                     | value  |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData    |        |
            | MerchantId\\0305-0767      | SendLoyaltyOnAuth       | NO     |
            | MerchantId\\0305-0767      | AddTransactionDiscount  | NO     | 
        And following discounts are set in RCM            
            | name              | external_id   | type              | value |
            | $0.4 Local FPR    | LOCAL_FPR     | FuelPriceRollback | 0.4   |
            | $0.2 Local Preset | LOCAL_PRESET  | PresetAmount      | 0.2   |
        # The feature assumes fuel prices to be set by SIT BDD environment's default FGPT import. The prices are as following:
        #     | fuel_grade    | cash_price    | credit_price |
        #     | diesel        | 1.0           | 1.1          |
        #     | midgrade      | 2.0           | 2.1          |
        #     | premium       | 3.0           | 3.1          |
        #     | regular       | 4.0           | 4.1          |
        # Following background steps were copied from Site controller's manual BDD scenarios and are not implemented in SIT BDD. Putting in comment for now.
        # And following carwashes are available on the site:
        #     | carwash_name   | receipt_text   | retail_price | car_wash_controller_id | subcategory    | PLU                 | active | credit_category |
        #     | Full Car Wash  | Full Car Wash  |  9.99        |         1              | Car wash type  | 1234567890          | yes    | Car Wash        |
        #     | TEST CARWASH   | TEST CARWASH   |  4.44        |         2              | Car wash type  | 357159              | yes    | Car Wash        |
        #     | TEST CW DELUXE | TEST CW DELUXE |  6.77        |         3              | Car wash type  | 88887777            | yes    | Car Wash Deluxe |
        #     | TEST CARWASH 2 | TEST CARWASH 2 |  5.83        |         4              | Car wash type  | 1                   | yes    | Car Wash        |
        #     | TEST CARWASH 3 | TEST CARWASH 3 |  6.27        |         5              | Car wash type  | 1234567891011112131 | yes    | Car Wash        |
        #     | TEST CARWASH 4 | TEST CARWASH 4 |  6.41        |         6              | Car wash type  | 0000000002300       | yes    | Car Wash        |
        #     | TEST CARWASH 5 | TEST CARWASH 5 |  7.19        |         7              | Car wash type  | 0086528445845       | yes    | Car Wash        |
        #     | TEST CARWASH 6 | TEST CARWASH 6 |  3.88        |         8              | Car wash type  | 009                 | yes    | Car Wash        |
        #     | TEST CARWASH 7 | TEST CARWASH 7 |  5.62        |         9              | Car wash type  | 00845284            | yes    | Car Wash        |


    @positive @wip @manual
    Scenario Outline: Pump is automatically authorized after successful reservation
        # Presence of CustomerPromptData in MobileAuthRequest determines if code is required at the pump
        # See also HostSimulator registry setting AccessCodeValidationType 
        Given the system is in a ready to sell state
        And customer reserved pump "<pump_id>" via mobile application
        When Conexxus host sends authorization request without CustomerPromptData
        And the pump "<pump_id>" was successfully reserved without access code
        Then the pump "<pump_id>" was authorized by the Mobile Pay host

        Examples:
            | pump_id   |
            | 1         |
            | 2         |


    @positive @indoor
    Scenario Outline: Conexxus mobile indoor - sell drystock item
        Given the system is in a ready to sell state
        And the cashier added item <item> to the transaction
        When the cashier scans a QR code "<mobilepay_qrcode>" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "1.060"
        
        Examples:
            | mobilepay_qrcode                     | item          |
            | P97.087fdd1da30249718be499864ad72068 | "Sale Item A" |


    @positive @indoor
    Scenario Outline: Sell car wash for Conexxus indoor
        Given the system is in a ready to sell state
        And the cashier added carwash "<carwash_name>" to the transaction
        #And Cashier added carwash <carwash_name> with car wash code <car_wash_code> expiration <car_wash_code_expiration_date> into the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message contains sale item "<carwash_name>"
        And "MobileFinalizeRequest" message contains carwash item "<carwash_name>" with carwash code and expiration elements
        #And "MobileFinalizeRequest" message contains car wash code "<car_wash_code>" for sale item "<carwash_name>"
        #And "MobileFinalizeRequest" message contains car wash code expiration date "<car_wash_code_expiration_date>" for sale item "<carwash_name>"

        Examples:
            | carwash_name      | car_wash_code  | car_wash_code_expiration_date |
            | PDI Car Wash Item | 123            | 2022-10-24T00:00:00.000       |

    @negative @indoor
    Scenario: Conexxus mobile indoor - declined sale
        Given the host simulator has set following registries 
            | path                       | key      | value         |
            | ResponseCodes\\STACCapture | 1.06     | 00001,Decline |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the POS displays the "Transaction Failure" frame
        And sale item "Sale Item A" is in the POS virtual receipt
        And the transaction on POS is not finalized
        And tender "Credit" is not added to POS virtual receipt


    @positive @indoor @postpay
    Scenario: Conexxus mobile indoor - postpay transaction with local FPR
        Given the system is in a ready to sell state
        And the customer dispensed "Diesel" for "8.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        And the cashier added the discount "$0.4 Local FPR"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "4.80"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "8.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "8.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.00"
        And "MobileFinalizeRequest" message contains discount sale item with ProductCode "905"
        And "MobileFinalizeRequest" message contains discount sale item with OriginalAmount/Amount "3.20"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "3.20"


    @positive @indoor
    Scenario: Conexxus mobile indoor - MPPA provided item level discount - drystock item
        Given following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                   | value                     |
            | Amount                | 0.56                      |
            | doNotRelieveTaxFlag   | true                      |
            | MaximumQuantity"      | 10                        |
            | priceAdjustmentID     | 112233                    |
            | programID             | Mobile Incentive Program  |
            | PromotionReason       | loyaltyOffer              |
            | Quantity              | 1                         |
            | RebateLabel           | MPPA merchandise discount |
            | rewardApplied         | false                     |
            | UnitPrice             | 0.56                      |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "0.460"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.990" 
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.430"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.560"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"


    @positive @indoor
    Scenario: Conexxus mobile indoor - MPPA provided item level discount - drystock item - split tender
        Given following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                 | value                     |
            | Amount              | 0.56                      |
            | doNotRelieveTaxFlag | true                      |
            | MaximumQuantity"    | 10                        |
            | priceAdjustmentID   | 112233                    |
            | programID           | Mobile Incentive Program  |
            | PromotionReason     | loyaltyOffer              |
            | Quantity            | 1                         |
            | RebateLabel         | MPPA merchandise discount |
            | rewardApplied       | false                     |
            | UnitPrice           | 0.56                      |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction with $0.2 in cash
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "0.260"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.990" 
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.430"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.560"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"


    @positive @indoor
    Scenario: Conexxus mobile indoor - MPPA provided item level discount - drystock item and car wash discounts
        #discount for general merchandise product code
        Given following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                 | value                     |
            | Amount              | 0.56                      |
            | doNotRelieveTaxFlag | true                      |
            | MaximumQuantity"    | 10                        |
            | priceAdjustmentID   | 112233                    |
            | programID           | Mobile Incentive Program  |
            | PromotionReason     | loyaltyOffer              |
            | Quantity            | 1                         |
            | RebateLabel         | MPPA merchandise discount |
            | rewardApplied       | false                     |
            | UnitPrice           | 0.56                      |
        #discount for car wash product code
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_102"
            | key                 | value                     |
            | Amount              | 0.20                      |
            | doNotRelieveTaxFlag | true                      |
            | MaximumQuantity"    | 10                        |
            | priceAdjustmentID   | 112244                    |
            | programID           | Mobile Incentive Program  |
            | PromotionReason     | loyaltyOffer              |
            | Quantity            | 1                         |
            | RebateLabel         | MPPA carwash discount     |
            | rewardApplied       | false                     |
            | UnitPrice           | 0.2                       |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier added carwash "Full Car Wash" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "10.250"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.990" 
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.430"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.560"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains sale item "Full Car Wash" with OriginalAmount/Amount "9.990" 
        And "MobileFinalizeRequest" message contains sale item "Full Car Wash" with AdjustedAmount/Amount "9.790"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Full Car Wash" with Amount "0.200"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Full Car Wash" with RebateLabel "MPPA carwash discount"


    @positive @indoor @postpay
    Scenario: Conexxus mobile indoor - postpay transaction
        Given the system is in a ready to sell state
        And the customer dispensed "Regular" for "11.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "11.00"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/Amount "11.0"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/UnitPrice "4.0"


     @positive @indoor @postpay
     Scenario: Conexxus mobile indoor - MPPA provided discount - postpay fuel
         Given following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
             | key                 | value                    |
             | Amount              | 0.00                     |
             | doNotRelieveTaxFlag | true                     |
             | MaximumQuantity"    | 10                       |
             | priceAdjustmentID   | 112255                   |
             | programID           | Mobile Incentive Program |
             | PromotionReason     | loyaltyOffer             |
             | Quantity            | 0                        |
             | RebateLabel         | MPPA FPR diesel          |
             | rewardApplied       | false                    |
             | UnitPrice           | 0.14                     |
         And the system is in a ready to sell state
         And the customer dispensed "Diesel" for "11.00" price at pump "1"
         And the cashier added a postpay item to the transaction
         When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
         Then the transaction on POS is finalized
         And "MobileFinalizeRequest" message has finalAmount "9.46"
         And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "11.0"
         And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.0"
         And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "11.0"
         And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.0"
         And "MobileFinalizeRequest" message contains sale item "Diesel" with Quantity "11.0"
         # Postpay item is a sale item with LinkedItemId pointing to the fuel sale item
         And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/Amount "1.54"
         And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/UnitPrice "1.54"
         And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/Amount "1.54"
         And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/UnitPrice "1.54"
         # And "MobileFinalizeRequest" message contains linked discount for "Diesel" with RebateLabel "MPPA FPR diesel"


    @positive @indoor @postpay @loyaltytender
    Scenario: Conexxus mobile indoor - postpay transaction with transaction discount with MPPA FPR
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value         |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_001"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity"    | 10                       |
            | priceAdjustmentID   | 112233                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR regular         |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.11                     |
        And the system is in a ready to sell state
        And the customer dispensed "Regular" for "6.00" price at pump "1"
        And the cashier added a postpay item to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "4.33"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/Amount "6.00"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/UnitPrice "4.00"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"


    @positive @indoor @loyaltytender
    Scenario Outline: Conexxus mobile indoor - transaction discounta applied as tender - discount below/equals/higher than balance
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value         |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount><discount_amount></Amount><UnitPrice><discount_amount></UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount><discount_amount></Amount><UnitPrice><discount_amount></UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item B" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "<final_amount>"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "<applied_discount>"

        Examples:
            | discount_amount | final_amount | applied_discount |
            | 1.50            | 0.63         | 1.50             |
            | 2.13            | 0.00         | 2.13             |
            | 3.00            | 0.00         | 2.13             |


    @positive @indoor @loyaltytender
    Scenario Outline: Conexxus mobile indoor - transaction discounta applied as tender - various product codes
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value         |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode><discount_product_code></ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item B" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "0.63"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"
        And "MobileFinalizeRequest" message contains discount sale item with ProductCode "<discount_product_code>"

        Examples:
            | discount_product_code |
            | 900                   |
            | 904                   |
            | 913                   |


    @positive @indoor @loyaltytender
    Scenario Outline: Conexxus mobile indoor - transaction discount applied as tender - non-numeric item ID
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value     |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode><discount_product_code></ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
            | MerchantId\\0305-0767      | LoyaltyAwardItemID       | <item_id> |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item B" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "0.63"
        And "MobileFinalizeRequest" message contains discount sale item with ItemID "<item_id>"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"
        And "MobileFinalizeRequest" message contains discount sale item with ProductCode "<discount_product_code>"

        Examples:
            | discount_product_code | item_id          |
            | 900                   | AlphaID_12       |
            | 904                   | FUEL_DISCOUNT_01 |
            | 913                   | DISCOUNT_01      |


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - MPPA discount on merchandise with quantity higher than 1
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                  | value                    |
            | Amount               | 0.40                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity"     | 10                       |
            | priceAdjustmentID    | 112233                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 4                        |
            | RebateLabel          | MPPA merchandise discount|
            | rewardApplied        | false                    |
            | UnitPrice            | 0.10                     |
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And an item "Sale Item A" is present in the transaction "4" times
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "2.31"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "3.96"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "3.56"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.40"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Quantity "4"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with UnitPrice "0.10"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - transaction discount applied as tender - discount amount reduced to total
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value     |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And "MobileFinalizeRequest" message has finalAmount "0.00"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.06"
        And "MobileFinalizeRequest" message contains discount sale item with ProductCode "904"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with Amount "1.06"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with UnitPrice "1.06"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with Quantity "1"
