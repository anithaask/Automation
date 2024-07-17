@fuel @wip
Feature: Paying at pump with cobranded cards
# Requires cobranded cards to be recognized by simpumps

    Background:
        Given following POS options are set in RCM
            | option_name                         | option | value_text    | value |
            | Automatically charge cobranded card | 1903   | No            | 0     |
            | Loyalty prompt control              | 4214   | Always prompt | 1     |
        And following ICR options are set in RCM
            | option   | value |
            | TRANTYPE | SIGMA |
            # [SIGMA = loyalty RLM] in RCM
        And the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | BEFOREFUELING |
            | CARWASH | BEFOREFUELING |


    @positive @wip
    Scenario: 43 - CHARGECOBRANDED: No - AskCobranded: Yes - No carwash, no receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
            | CARWASHYESNO    | TRUE  |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And an MSR card "loyalty_cobranded_mc_new" was swiped at pump "1"
        # And the configured prompt "ASKCHARGECOBRANDED" was displayed on pump "1"
        # And the customer pressed "YES" key on pump "1" keypad
        And the configured prompt "ASKWASH PROMPT" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer dispenses grade "Midgrade" fuel for $6.00 price on pump "1"
        Then the configured prompt "THANKS" is displayed on pump "1"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "1"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        # 2.858 Gallons @ $2.100/Gal         $6.00 (without the loyalty discount)
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Midgrade            *           |
            | 12          | *2.858 Gallons @ $2.100/Gal         $6.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 44 - CHARGECOBRANDED: No - AskCobranded: Yes - Yes carwash, yes receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
            | CARWASHYESNO    | TRUE  |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "1"
        # And the configured prompt "ASKCHARGECOBRANDED" was displayed on pump "1"
        # And the customer pressed "YES" key on pump "1" keypad
        And the configured prompt "ASKWASH PROMPT" was displayed on pump "1"
        And carwash is accepted on pump "1" keypad
        And the customer pressed "1" key on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer dispenses grade "Midgrade" fuel for $4.00 price on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "1"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Midgrade            *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $4.00* |
        # check card type used for payment is loyalty_cobranded_mc_new
        # check contains carwash


    @positive @wip
    Scenario: 45 - CHARGECOBRANDED: No - AskCobranded: No - No carwash, yes receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "2"
        # And the configured prompt "ASKCHARGECOBRANDED" was displayed on pump "2"
        # And the customer pressed "NO" key on pump "2" keypad
        And the configured prompt "GREETING" was displayed on pump "2"
        And an MSR card "credit_discover" was swiped at pump "2"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "2"
        And the customer pressed "YES" key on pump "1" keypad
        When the customer dispenses grade "Regular" fuel for $12.00 price on pump "2"
        And the customer hangs up the nozzle on pump "2"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "2"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "2"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Regular             *           |
            | 12          | *x.000 Gallons @ $x.000/Gal        $12.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 46 - CHARGECOBRANDED: No - AskCobranded: Yes - No carwash, yes receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty" at pump "2"
        And the configured prompt "GREETING" was displayed on pump "2"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "2"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "2"
        And the customer pressed "YES" key on pump "1" keypad
        When the customer dispenses grade "Premium" fuel for $7.00 price on pump "2"
        And the customer hangs up the nozzle on pump "2"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "2"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "2"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Premium             *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $7.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 47 - CHARGECOBRANDED: No - AskCobranded: Yes - No carwash, yes receipt - Kroger Visa as Loyalty Kroger MC as MOP
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_visa_new_kroger" at pump "2"
        # And the configured prompt "ASKCHARGECOBRANDED" was displayed on pump "2"
        # And the customer pressed "NO" key on pump "1" keypad
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "2"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "2"
        And the customer pressed "YES" key on pump "1" keypad
        When the customer dispenses grade "Premium" fuel for $7.00 price on pump "2"
        And the customer hangs up the nozzle on pump "2"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "2"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "2"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Premium             *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $7.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 48 - CHARGECOBRANDED: No - AskCobranded: Yes - No carwash, yes receipt - Kroger MC as Loyalty Kroger Visa as MOP
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | FALSE |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "2"
        # And the configured prompt "ASKCHARGECOBRANDED" was displayed on pump "2"
        # And the customer pressed "NO" key on pump "1" keypad
        And a loyalty swipe was performed with "loyalty_cobranded_visa_new_kroger" at pump "2"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "2"
        And the customer pressed "YES" key on pump "1" keypad
        When the customer dispenses grade "Premium" fuel for $7.00 price on pump "2"
        And the customer hangs up the nozzle on pump "2"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "2"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "2"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Premium             *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $7.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 43a - CHARGECOBRANDED: Yes - AskCobranded: Yes - No carwash, no receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | TRUE  |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "1"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer dispenses grade "Midgrade" fuel for $6.00 price on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "THANKS" is displayed on pump "1"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "1"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Midgrade            *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $6.00* |
        # check card type used for payment is loyalty_cobranded_mc_new


    @positive @wip
    Scenario: 44a - CHARGECOBRANDED: Yes - AskCobranded: Yes - Yes carwash, yes receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | TRUE  |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "1"
        And the configured prompt "ASKWASH PROMPT" was displayed on pump "1"
        And carwash is accepted on pump "1" keypad
        And the customer pressed "1" key on pump "1" keypad
        And the customer selected the first carwash option at pump "1"
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer dispenses grade "Midgrade" fuel for $4.00 price on pump "1"
        And the customer hangs up the nozzle on pump "1"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "1"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Midgrade            *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $4.00* |
        # check card type used for payment is loyalty_cobranded_mc_new
        # check contains carwash


    @positive @wip
    Scenario: 46a - CHARGECOBRANDED: Yes - AskCobranded: Yes - No carwash, yes receipt
        Given following ICR options are set in RCM
            | option          | value |
            | CHARGECOBRANDED | TRUE  |
        And the system is in a ready to sell state
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" was displayed on pump "1"
        And a loyalty swipe was performed with "loyalty" at pump "2"
        And the configured prompt "GREETING" was displayed on pump "2"
        And a loyalty swipe was performed with "loyalty_cobranded_mc_new" at pump "2"
        And the configured prompt "ASKWASH" was displayed on pump "1"
        And the customer pressed "NO" key on pump "1" keypad
        And the configured prompt "RECEIPT" was displayed on pump "2"
        And the customer pressed "YES" key on pump "1" keypad
        When the customer dispenses grade "Premium" fuel for $7.00 price on pump "2"
        And the customer hangs up the nozzle on pump "2"
        Then the configured prompt "RCPTPRINTED" is displayed on pump "2"
        And the configured prompt "ASKLOYALTYMOPPOSTPAY" is displayed on pump "2"
        And the first line in Scroll previous contains following elements
            | element           | value       |
            | node type         | Pump        |
            | node number       | 1           |
            | transaction type  | Pay at Pump |
        And the scroll previous printed receipt contains
            | line_number | line                                       |
            | 11          | *Pump # 1  Premium             *           |
            | 12          | *x.000 Gallons @ $x.000/Gal         $7.00* |
        # check card type used for payment is loyalty_cobranded_mc_new
