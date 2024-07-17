@sitbdd @pos @fuel @sc @eps
Feature: EOS and EOD feature
    This feature is testing end of shift and end of day scenarios.

    Background:
        Given the NAXML Export schema is "3.4"
        And following POS options are set in RCM
            | option_name                        | option | value_text           | value |
            | Prohibit EOD Threshold             | 1471   | Threshold in minutes | 0     |
            | 24 Hour Mode - Manual Start of Day | 1494   | Yes                  | 1     |
            | Use Offline Shift Financial Report | 5121   | Yes                  | 1     |
            | Report At End Of Shift             | 1693   | Yes                  | 1     |
            | End shift - Safe drops             | 1908   | No safe drop on EOS  | 2     |
        And the system is in a ready to sell state


    @positive @glacial @wip
    # Requires printed start of shift report verification, couldn't find it
    Scenario: Verify start of shift headers
        Given the cashier ended the shift
        When the cashier starts the shift
        Then the start of shift report is verified


    @positive @glacial
    Scenario: Finish some transactions and verify end of shift reports
        Given the cashier ended the shift
        And the cashier started the shift
        And the cashier added item "Sale Item A" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the cashier added item "Sale Item B" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        And the cashier added item "Sale Item C" to the transaction
        And the cashier tendered the transaction for exact dollar with tender type "cash"
        When the cashier ends the shift
        Then all transactions are summarized
        And the previous printed EOS report contains
            | line_number | line                                        |
            | 1           | *         SHIFT FINANCIAL REPORT         *  |
            | 5           | *Cashier Name:         1234, Cashier     *  |
            | 10          | *              Main Summary              *  |
            | 11          | *                                        *  |
            | 12          | *    System Gross (+tax)            $4.78*  |
            | 13          | *                                        *  |
            | 14          | *Discounts & Refunds Summary:            *  |
            | 15          | *  0 Gross Disc & Coup   $0.00(+)*          |
            | 16          | *  0 Net Refunds         $0.00(+)*          |
            | 17          | *    Net Disc & Refunds          $0.00(-)*  |
            | 18          | *                              ----------*  |
            | 19          | *    Net Sales (+tax)               $4.78*  |
            | 20          | *                                        *  |
            | 21          | *Non-Sales Summary:                      *  |
            | 22          | *    Starting Amount     $0.00(+)*          |
            | 23          | *  0 Loans               $0.00(+)*          |
            | 24          | *  0 Pay-Ins             $0.00(+)*          |
            | 25          | *  0 Safe Drops          $0.00(-)*          |
            | 26          | *  0 Pay-Outs            $0.00(-)*          |
            | 27          | *  0 MO Pay-Outs         $0.00(+)*          |
            | 28          | *  0 Lottery Winners     $0.00(-)*          |
            | 29          | *  0 Container Redempti  $0.00(-)*          |
            | 30          | *    Net Non-Sales               $0.00(+)*  |
            | 31          | *                              ----------*  |
            | 32          | *    Total Tenders Due              $4.78*  |
            | 33          | *                                        *  |
            | 34          | *Tenders Summary:                        *  |
            | 35          | *  3 Cash                        $4.78(+)*  |
            | 36          | *                              ----------*  |
            | 37          | *  3 Total Collected                $4.78*  |
            | 38          | *                              ----------*  |
            | 39          | *    Due vs Collected +/-           $0.00*  |
            | 40          | *                                        *  |
            | 41          | *========================================*  |
            | 42          | *          Miscellaneous Totals          *  |
            | 43          | *                                        *  |
            | 44          | *  3 Gross Sales Avg (+tax)         $1.59*  |
            | 45          | *  3 Net Sales Avg (+tax)           $1.59*  |
            | 46          | *    Net Sales Tax                  $0.31*  |
            | 47          | *  0 No-Sale Transactions                *  |
            | 48          | *  0 Voided Sales Transactions      $0.00*  |
            | 49          | *  0 Voided Sales Items             $0.00*  |
            | 50          | *  0 Tax Exempt Transactions        $0.00*  |
            | 51          | *  0 Tax Modified Items             $0.00*  |
            | 52          | *  0 Open Items                     $0.00*  |
            | 53          | *  0 Price Overrides                $0.00*  |
            | 54          | *  0 Manual Cards                   $0.00*  |
            | 55          | *  0 EFT Surcharge Fee              $0.00*  |
            | 56          | *  0 Cash Back                      $0.00*  |
            | 57          | *  0 Cash Back Fee                  $0.00*  |
            | 58          | *========================================*  |
            | 59          | *========================================*  |
            | 60          | *       Over(+) / Short(-) Details       *  |
            | 61          | *                                        *  |
            | 62          | *Cash:                                   *  |
            | 63          | *    Amount Collected    $4.78(-)*          |
            | 64          | *    Amount Counted      $0.00(+)*          |
            | 65          | *    Tender +/-                 -$4.78(+)*  |
            | 66          | *                              ----------*  |
            | 67          | *    Net Over(+) / Short(-)        -$4.78*  |
            | 68          | *========================================*  |
            | 69          | *             Tender Details             *  |
            | 70          | *                                        *  |
            | 71          | *Cash:                                   *  |
            | 72          | *    Starting Amount                $0.00*  |
            | 73          | *  3 Sales Amount        $4.78(+)*          |
            | 74          | *  0 Pay-Ins             $0.00(+)*          |
            | 75          | *  0 Loans               $0.00(+)*          |
            | 76          | *  3 Tender In Total             $4.78(+)*  |
            | 77          | *                                        *  |
            | 78          | *  0 Refunds Amount      $0.00(+)*          |
            | 79          | *  0 Safe Drops          $0.00(+)*          |
            | 80          | *  0 Pay-Outs            $0.00(+)*          |
            | 81          | *  0 Tender Out Total            $0.00(-)*  |
            | 82          | *                              ----------*  |
            | 83          | *  3 Amount Collected               $4.78*  |
            | 84          | *========================================*  |
            | 85          | *      Discounts / Refunds Details       *  |
            | 86          | *                                        *  |
            | 87          | *Sales - Discounts & Coupons:            *  |
            | 88          | *  0 Gross Loyalty Disc.         $0.00(+)*  |
            | 89          | *  0 Gross Discounts             $0.00(+)*  |
            | 90          | *  0 Gross Coupons               $0.00(+)*  |
            | 91          | *                              ----------*  |
            | 92          | *  0 Gross Disc & Coup              $0.00*  |
            | 93          | *                                        *  |
            | 94          | *Refunds:                                *  |
            | 95          | *  0 Sales               $0.00(+)*          |
            | 96          | *  0 Tax                 $0.00(+)*          |
            | 97          | *  0 Loyalty Discounts   $0.00(-)*          |
            | 98          | *  0 Discounts           $0.00(-)*          |
            | 99          | *  0 Coupons             $0.00(-)*          |
            | 100         | *    Net Sales Refunds           $0.00(+)*  |
            | 101         | *                              ----------*  |
            | 102         | *    Net Disc & Refunds             $0.00*  |
            | 103         | *========================================*  |
            | 104         | *            Lottery Details             *  |
            | 105         | *                                        *  |
            | 106         | *No Lottery Activity                     *  |
            | 107         | *                                        *  |
            | 108         | *========================================*  |
            | 109         | *          Money Order Details           *  |
            | 110         | *                                        *  |
            | 111         | *                                        *  |
            | 112         | *No Money Order Activity                 *  |
            | 113         | *                                        *  |
            | 114         | *  0 MO & Vender Pay Outs           $0.00*  |
            | 115         | *========================================*  |
            | 116         | *                                        *  |
        # And the generated export "NAXML-POSJ ournal" matches "an end of day POS journal" template
        # And the generated export "PDICashierReport" matches "an end of day cashier summary" template
        # And the generated export "PDIMiscSumMvmt" matches "an end of day miscellaneous summary movement" template


    @positive @glacial @wip
    # Step undefined: the following transactions are captured
    Scenario: Validate export for a refunded postpay with discount
        Given the following transactions are captured
            | transaction |
            | a postpay with loyalty discount |
            | a postpay with loyalty discount and refund |
            | a postpay with loyalty discount and refund retendered |
        When the cashier ends the current business day
        Then all transactions are summarized
        And the generated export "PDIMiscSumMvmt" matches "a postpay with loyalty discount and refund retendered" template


    @positive @slow @wip
    # Step undefined: the following transactions are captured
    Scenario Outline: Validate full exports for various types of transactions
        Given the following transactions are captured
            | transaction |
            | <template>  |
        When the cashier ends the current business day
        Then all transactions are summarized
        And the generated export "NAXML-ItemSalesMovement" matches "<template>" template

        Examples:
            | template                                                                                          |
            | a refund of three merchandise items with a price override                                         |
            | a refund of three merchandise items                                                               |
            | a refund of three merchandise items that are consolidated with non-stacking discount              |
            | a refund of four of a merchandise item and two of another merchandise item that make an AutoCombo |
            | a sale of one merchandise item with two stacking discounts                                        |
            | a sale of one merchandise item with one stacking discount and one non-stacking discount           |
            | a sale of one merchandise item with one stacking discount                                         |
            | a sale of one merchandise item with different stacking discounts                                  |
            | a sale of two of a merchandise item and two of another merchandise item                           |
            | a sale of three merchandise items with a discount and price override                              |
            | a sale of three merchandise items with a price override                                           |
            | a sale of three merchandise items that are consolidated                                           |
            | a sale of three merchandise items that are unconsolidated                                         |
            | a sale of three merchandise items that are consolidated with non-stacking discount                |
            | a sale of three merchandise items that are unconsolidated with non-stacking discount              |
            | a sale of four of a merchandise item and two of another merchandise item that make an AutoCombo   |
            | a sale of five merchandise items                                                                  |
            | a sale of twenty-eight merchandise items                                                          |
            | a refund of three merchandise items with a price override |


    @positive @glacial @wip
    # Step undefined: the following transactions are captured
    Scenario: Validate end-of-day exports for various types of transactions
        Given the following transactions are captured
            | transaction |
            | a refund of three merchandise items with a price override |
        When the cashier ends the current business day
        Then all transactions are summarized
        And the generated export "NAXML-ItemSalesMovement" matches "a refund of three merchandise items with a price override" template


    @positive @glacial @wip
    # Step undefined: the following transactions are captured
    Scenario: Validate export for a refunded postpay with discount
        Given the following transactions are captured
            | transaction |
            | a postpay with loyalty discount |
            | a postpay with loyalty discount and refund |
            | a postpay with loyalty discount and refund retendered |
        When the cashier ends the current business day
        Then all transactions are summarized
        And the generated export "fuel grade movement" matches "a postpay with loyalty discount and refund retendered" template
