@sitbdd @pos @fuel @mobilepay @prepay
# RPOS-64660: Epsilon needs to be updated for SITBDD systems.
Feature: Conexxus mobile sales - prepay without grade selection
    This feature file focuses on Conexxus mobile transactions.

    It contains prepay transaction without grade selection.
    Other transactions are tested in different feature files.

    Background:
        Given following POS options are set in RCM
            | option_name                  | option | value_text         | value |
            | Enable Mobile Payment on POS | 1240   | Yes                | 1     |
            | Fuel credit prepay method    | 1851   | Auth and Capture   | 1     |
            | Prepay Grade Select Type     | 5124   | None               | 0     |
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


    @positive @indoor
    Scenario: Conexxus mobile indoor - prepay fuel with local FPR - no grade selection - fully-dispensed
        Given the system is in a ready to sell state
        And the cashier prepaid fuel for price "6.00" at pump "1"
        And the cashier added the discount "$0.4 Local FPR"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer fully dispenses the prepay on pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "6.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "9.43"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "6.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.70"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "3.43"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.40"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "$0.4 Local FPR"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "6.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "9.43"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "6.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.70"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "3.43"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.40"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "$0.4 Local FPR"


    @positive @indoor
    Scenario: Conexxus mobile indoor - prepay fuel with local FPR - no grade selection - under-dispensed
        Given the system is in a ready to sell state
        And the cashier prepaid fuel for price "8.00" at pump "1"
        And the cashier added the discount "$0.4 Local FPR"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $1.00 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "1.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.57"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.70"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.57"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.40"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "$0.4 Local FPR"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.57"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.70"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.57"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.40"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "$0.4 Local FPR"


    @positive @indoor
    Scenario: Conexxus mobile indoor - MPPA provided discount - different discount for each grade - prepay fuel - without grade selection - partially dispensed
        Given following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112255                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR diesel          |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.14                     |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_001"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112256                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR Regular         |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.15                     |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_002"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112257                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR Midgrade        |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.16                     |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "20.0" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses "Diesel" for "14.50" price at pump "1"
        Then the Epsilon sends finalize request to Conexxus host
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "16.62"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.1"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "14.50"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.96"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with Quantity "15.1"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "2.11"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.14"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileFinalizeRequest" message has finalAmount "14.5"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "16.62"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.1"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "14.50"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.96"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with Quantity "15.1"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "2.11"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.14"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"


    @positive @indoor
    Scenario: Conexxus mobile indoor - MPPA provided discount - different discount for each grade - prepay fuel - fuel prices rolled back on ICR
        Given following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112255                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR diesel          |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.14                     |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_001"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112256                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR Regular         |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.15                     |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_002"
            | key                 | value                    |
            | Amount              | 0.00                     |
            | doNotRelieveTaxFlag | true                     |
            | MaximumQuantity     | 50                       |
            | priceAdjustmentID   | 112257                   |
            | programID           | Mobile Incentive Program |
            | PromotionReason     | loyaltyOffer             |
            | Quantity            | 0                        |
            | RebateLabel         | MPPA FPR Midgrade        |
            | rewardApplied       | false                    |
            | UnitPrice           | 0.16                     |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "20.0" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        Then the transaction on POS is finalized
        And price for grade "Diesel" on pump "1" is "0.96" for tier "Credit"
        And price for grade "Regular" on pump "1" is "3.95" for tier "Credit"
        And price for grade "Midgrade" on pump "1" is "1.94" for tier "Credit"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - tender discount - prepay fuel - without grade selection - partially dispensed
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value         |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "15.0" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses "Diesel" for "8.50" price at pump "1"
        Then the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "7.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "8.5"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"


@positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay transaction with transaction discount with MPPA FPR - no grade selection, underdispense
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
        And the cashier prepaid fuel for price "15.0" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses "Regular" for "8.50" price at pump "1"
        Then the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "7.00"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/Amount "8.74"
        And "MobileFinalizeRequest" message contains sale item "Regular" with OriginalAmount/UnitPrice "4.1"
        And "MobileFinalizeRequest" message contains sale item "Regular" with AdjustedAmount/Amount "8.5"
        And "MobileFinalizeRequest" message contains sale item "Regular" with AdjustedAmount/UnitPrice "3.99"
        And "MobileFinalizeRequest" message contains sale item "Regular" with Quantity "2.131"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Regular" with Amount "0.23"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Regular" with UnitPrice "0.11"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Regular" with RebateLabel "MPPA FPR regular"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with MPPA FPR - no grade selection - fully-dispensed - tender discount - MPPA provided merchandise item level discount
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                  | value                    |
            | Amount               | 0.10                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity"     | 10                       |
            | priceAdjustmentID    | 112233                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 1                        |
            | RebateLabel          | MPPA merchandise discount|
            | rewardApplied        | false                    |
            | UnitPrice            | 0.10                     |
            | PostponeAfterFueling | NO                       |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                    |
            | Amount               | 0.00                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity      | 50                       |
            | priceAdjustmentID    | 112255                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 0                        |
            | RebateLabel          | MPPA FPR diesel          |
            | rewardApplied        | false                    |
            | UnitPrice            | 0.20                     |   
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier prepaid fuel for price "8.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer fully dispenses the prepay on pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "7.46"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "9.78"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "8.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "1.78"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileLoyaltyAwardRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "7.46"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "9.78"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "8.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "1.78"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with MPPA FPR - no grade selection - under-dispensed - tender discount - MPPA provided merchandise item level discount
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                  | value                    |
            | Amount               | 0.10                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity"     | 10                       |
            | priceAdjustmentID    | 112233                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 1                        |
            | RebateLabel          | MPPA merchandise discount|
            | rewardApplied        | false                    |
            | UnitPrice            | 0.10                     |
            | PostponeAfterFueling | NO                       |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                    |
            | Amount               | 0.00                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity      | 50                       |
            | priceAdjustmentID    | 112255                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 0                        |
            | RebateLabel          | MPPA FPR diesel          |
            | rewardApplied        | false                    |
            | UnitPrice            | 0.20                     |
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier prepaid fuel for price "8.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $1.00 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "0.46"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.22"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.22"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileLoyaltyAwardRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "0.46"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.22"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.22"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with postfueling MPPA FPR - no grade selection - fully-dispensed - tender discount - postfueling MPPA provided merchandise item level discount
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                  | value                     |
            | Amount               | 0.10                      |
            | doNotRelieveTaxFlag  | true                      |
            | MaximumQuantity"     | 10                        |
            | priceAdjustmentID    | 112233                    |
            | programID            | Mobile Incentive Program  |
            | PromotionReason      | loyaltyOffer              |
            | Quantity             | 1                         |
            | RebateLabel          | MPPA merchandise discount |
            | rewardApplied        | false                     |
            | UnitPrice            | 0.10                      |
            | PostponeAfterFueling | YES                       |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                     |
            | Amount               | 0.00                      |
            | doNotRelieveTaxFlag  | true                      |
            | MaximumQuantity      | 50                        |
            | priceAdjustmentID    | 112255                    |
            | programID            | Mobile Incentive Program  |
            | PromotionReason      | loyaltyOffer              |
            | Quantity             | 0                         |
            | RebateLabel          | MPPA FPR diesel           |
            | rewardApplied        | false                     |
            | UnitPrice            | 0.20                      | 
            | PostponeAfterFueling | YES                       |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier prepaid fuel for price "8.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer fully dispenses the prepay on pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "7.56"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "8.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "8.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "6.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "8.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "8.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/Amount "1.46"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/UnitPrice "1.46"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/Amount "1.46"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/UnitPrice "1.46"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with postfueling MPPA FPR - no grade selection - under-dispensed - tender discount - postfueling MPPA provided merchandise item level discount
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_400"
            | key                  | value                     |
            | Amount               | 0.10                      |
            | doNotRelieveTaxFlag  | true                      |
            | MaximumQuantity"     | 10                        |
            | priceAdjustmentID    | 112233                    |
            | programID            | Mobile Incentive Program  |
            | PromotionReason      | loyaltyOffer              |
            | Quantity             | 1                         |
            | RebateLabel          | MPPA merchandise discount |
            | rewardApplied        | false                     |
            | UnitPrice            | 0.10                      |
            | PostponeAfterFueling | YES                       |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                     |
            | Amount               | 0.00                      |
            | doNotRelieveTaxFlag  | true                      |
            | MaximumQuantity      | 50                        |
            | priceAdjustmentID    | 112255                    |
            | programID            | Mobile Incentive Program  |
            | PromotionReason      | loyaltyOffer              |
            | Quantity             | 0                         |
            | RebateLabel          | MPPA FPR diesel           |
            | rewardApplied        | false                     |
            | UnitPrice            | 0.20                      | 
            | PostponeAfterFueling | YES                       |
        And the system is in a ready to sell state
        And the cashier added item "Sale Item A" to the transaction
        And the cashier prepaid fuel for price "8.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $1.00 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message has finalAmount "0.56"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.99"
        And "MobileLoyaltyAwardRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "0.28"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/Amount "0.18"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with OriginalAmount/UnitPrice "0.18"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/Amount "0.18"
        And "MobileFinalizeRequest" message contains linked discount for "Diesel" with AdjustedAmount/UnitPrice "0.18"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "0.99"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "0.89"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.10"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay with no grade selection with merchandise - MPPA item discount on item with quantity over 1
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
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                    |
            | Amount               | 0.00                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity      | 50                       |
            | priceAdjustmentID    | 112255                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 0                        |
            | RebateLabel          | MPPA FPR diesel          |
            | rewardApplied        | false                    |
            | UnitPrice            | 0.20                     |
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And an item "Sale Item A" is present in the transaction "4" times
        And the cashier prepaid fuel for price "2.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $1.00 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "3.96"
        And "MobileLoyaltyAwardRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "3.56"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.40"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with Quantity "4"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Sale Item A" with UnitPrice "0.10"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "3.31"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "1.22"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with OriginalAmount/Amount "3.96"
        And "MobileFinalizeRequest" message contains sale item "Sale Item A" with AdjustedAmount/Amount "3.56"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with RebateLabel "MPPA merchandise discount"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Amount "0.40"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with Quantity "4"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Sale Item A" with UnitPrice "0.10"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.50"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with MPPA FPR and transaction discount - small amount - zero discount amount after fueling
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                    |
            | Amount               | 0.00                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity      | 50                       |
            | priceAdjustmentID    | 112255                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 0                        |
            | RebateLabel          | MPPA FPR diesel          |
            | rewardApplied        | false                    |
            | UnitPrice            | 0.20                     |
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "2.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $0.01 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/Amount "0.01"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "0.01"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.00"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "0.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "0.01"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/UnitPrice "1.10"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "0.01"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.00"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay fuel with MPPA FPR - no grade selection - transaction discount - discount amount reduced to total
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
        And following values are set under "Software\...\Adjustment1" registry path for "Prod_019"
            | key                  | value                    |
            | Amount               | 0.00                     |
            | doNotRelieveTaxFlag  | true                     |
            | MaximumQuantity      | 50                       |
            | priceAdjustmentID    | 112255                   |
            | programID            | Mobile Incentive Program |
            | PromotionReason      | loyaltyOffer             |
            | Quantity             | 0                        |
            | RebateLabel          | MPPA FPR diesel          |
            | rewardApplied        | false                    |
            | UnitPrice            | 0.20                     |
            | PostponeAfterFueling | NO                       |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "2.00" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses fuel up to $1.02 on the pump "1" with grade "Diesel"
        Then the Epsilon sends loyalty award request to Conexxus host
        And "MobileLoyaltyAwardRequest" message contains discount sale item with AdjustedAmount/Amount "1.02"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under discount sale item with Amount "1.02"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under discount sale item with UnitPrice "1.02"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under discount sale item with Quantity "1"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.02"
        And "MobileLoyaltyAwardRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.23"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileLoyaltyAwardRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "0.00"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/Amount "1.02"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with AdjustedAmount/UnitPrice "0.90"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with Amount "0.23"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with UnitPrice "0.20"
        And "MobileFinalizeRequest" message contains PriceAdjustment under sale item "Diesel" with RebateLabel "MPPA FPR diesel"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.02"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with Amount "1.02"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with UnitPrice "1.02"
        And "MobileFinalizeRequest" message contains PriceAdjustment under discount sale item with Quantity "1"


    @positive @indoor @loyaltytender
    Scenario: Conexxus mobile indoor - prepay without grade selection - transaction discount with non-numeric item ID
        Given transaction discount is enabled in host simulator
        And the host simulator has set following registries
            | path                       | key                      | value            |
            | MerchantId\\0305-0767      | LoyaltyAwardItemData     | <POSCode>00000000000000</POSCode><POSCodeModifier>000</POSCodeModifier><POSCodeFormat>plu</POSCodeFormat><ProductCode>904</ProductCode><OriginalAmount><Amount>0</Amount></OriginalAmount><AdjustedAmount><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice></AdjustedAmount><UnitMeasure>EA</UnitMeasure><Quantity>1</Quantity><PriceAdjustment rewardApplied="false" priceAdjustmentID="Ticket Discount 1" programID="Discount Program 1"><PromotionReason doNotRelieveTaxFlag="false">loyaltyOffer</PromotionReason><Amount>1.5</Amount><UnitPrice>1.5</UnitPrice><Quantity>1</Quantity><MaximumQuantity>1</MaximumQuantity><RebateLabel>Ticket Rebate 1</RebateLabel></PriceAdjustment> |
            | MerchantId\\0305-0767      | LoyaltyAwardItemID       | FUEL_DISCOUNT_01 |
        And the system is in a ready to sell state
        And the cashier prepaid fuel for price "15.0" at pump "1"
        When the cashier scans a QR code "P97.087fdd1da30249718be499864ad72068" on Please scan mobile wallet QR code frame
        And the customer dispenses "Diesel" for "3.60" price at pump "1"
        Then the Epsilon sends finalize request to Conexxus host
        And "MobileFinalizeRequest" message has finalAmount "2.10"
        And "MobileFinalizeRequest" message contains discount sale item with ItemID "FUEL_DISCOUNT_01"
        And "MobileFinalizeRequest" message contains sale item "Diesel" with OriginalAmount/Amount "3.6"
        And "MobileFinalizeRequest" message contains discount sale item with AdjustedAmount/Amount "1.5"
