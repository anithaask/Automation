@fuel @mobile_pay @wip
# Need mobile pay implemented from the EPS package.
Feature: Mobile Pay.

    Background: Mobile Pay base configuration setup
        Given the Epsilon has following global options configured
            | option                     | value |
            | SendAvailableProductExport | YES   |
        And updated configuration is loaded by credit controller
        And the pumps are configured for "Prepay,Postpay,ICR"
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 4     |
            | CREDITTIMEOUT      | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | NO    |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISNO         | NO    |


    @positive @glacial @reserve_pump
    Scenario: Reserve request approved by fuel controller.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends approval for reserve pump request to credit controller for pump "1"


    @positive @glacial @reserve_pump
    Scenario: Reserve request approved without prompt for access code.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the Mobile Pay host does not prompt for access code
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends approval for reserve pump request to credit controller for pump "1"


    @positive @glacial @reserve_pump
    Scenario: Reserve request approved and then pump released by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the Mobile Pay host releases the pump "1"
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @reserve_pump
    Scenario: Reserve request approved and pump is authorized by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the Mobile Pay host tries to authorize the pump "1"
        Then the configured prompt "CHOOSEGRADE" is displayed on pump "1"


    @positive @slow @reserve_pump
    Scenario: Reserve request approved, pump is authorized, and then released by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        When the Mobile Pay host releases the pump "1"
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @reserve_pump
    Scenario: Reserve request approved with loyalty from Mobile Pay host, pump is authorized,then apply loyalty discount prompt.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the pump "1" is authorized for Mobile Pay transaction with loyalty
        Then the dynamic prompt "Would you like   to accept a discount" is displayed on pump "1"


    @positive @slow @reserve_pump
    Scenario: Reserve request approved with loyalty from Mobile Pay host, pump is authorized, apply loyalty discount prompt, then released by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized for Mobile Pay transaction with loyalty
        When the Mobile Pay host releases the pump "1"
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @negative @slow @reserve_pump 
    Scenario: Reserve request failure: loyalty Card Swiped at Pump first.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And a loyalty swipe was performed with "loyalty" at pump "1"
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "1"


    @negative @slow @reserve_pump
    Scenario: Reserve request failure: Postpay transaction started at pump.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And a postpay transaction was started on pump "1"
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "1"


    @negative @slow @reserve_pump 
    Scenario: Reserve request failure: Payment Card Swiped at Pump first.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And an MSR card "credit_discover" was swiped at pump "1"
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "1"


    @negative @slow @reserve_pump
    Scenario: Reserve request failure: Active Prepay at pump
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "4.00" at pump "2"
        And the configured prompt "BEGINFUELING" was displayed on pump "2"
        When the Mobile Pay host tries to reserve the pump "2"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "2"


    @negative @slow @reserve_pump @wip
    Scenario: Reserve request failure: Active PAP at pump.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And an MSR card "credit_discover" was swiped at pump "2"
        And the configured prompt "CHOOSEGRADE" was displayed on pump "2"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 2
        When the Mobile Pay host tries to reserve the pump "2"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "2"


    @negative @slow @reserve_pump @wip
    Scenario: Reserve request failure: Try to reserve at receipt prompt.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And an MSR card "credit_discover" was swiped at pump "2"
        And the configured prompt "CHOOSEGRADE" was displayed on pump "2"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 2
        And the nozzle is hung up on pump "2"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "2"
        When the Mobile Pay host tries to reserve the pump "2"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "2"


    @negative @slow @reserve_pump 
    Scenario: Reserve request failure: Pump Offline
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the pump "1" went offline
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "1"


    @negative @slow @reserve_pump 
    Scenario: Reserve request failure: ICR Offline.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the system is in a ready to sell state
        And the ICR on pump "1" went offline
        When the Mobile Pay host tries to reserve the pump "1"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "1"


    @negative @glacial @reserve_pump 
    Scenario: Reserve request failure: auth mode set to CLOSED.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the pumps are configured for "CLOSED"
        And the system is in a ready to sell state
        When the Mobile Pay host tries to reserve the pump "2"
        Then the fuel controller sends rejection for reserve pump request to credit controller for the pump "2"


    @positive @glacial @auth_modes 
    Scenario: Available Product Export - requested by Epsilon. fuel and carwash items available.
        Given the pumps are configured for "ICR"
        And the fuel controller is configured to sell "fuel,carwash"
        And the system is in a ready to sell state
        When the Mobile Pay host requests available products export
        Then the export with items available to sell by the fuel controller is sent to the credit controller


    @positive @glacial @auth_modes @wip
    Scenario: Available Product Export - requested by Epsilon - auth mode set to Closed.
        Given the fuel controller is configured to sell "fuel,carwash"
        And the pumps are configured for "CLOSED"
        And the system is in a ready to sell state
        When the Mobile Pay host requests available products export
        Then the export with items available to sell by the fuel controller is sent to the credit controller
        And the pump "2" is reported as available in credit controller product export


    @positive @glacial @auth_modes @wip
    Scenario: Available Product Export - initiated by fuel controller - after auth mode change from closed to ICR.
        Given the fuel controller is configured to sell "fuel,carwash"
        And the pumps have the following timing events configured:
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And following ICR options are set in RCM
            | option                   | value |
            | PROMPTTIMEOUT            | 4     |
            | CREDITTIMEOUT            | 15    |
            | TRANTYPE                 | SIGMA |
        And the pumps are configured for "CLOSED"
        And the system is in a ready to sell state
        When the fuel controller loads pump auth mode as "ICR"
        Then the configured prompt "ASKLOYALTYMOP" is displayed on pump "2"
        And the export with items available to sell by the fuel controller is sent to the credit controller
        And the pump "2" is reported as available in credit controller product export


    @positive @glacial @auth_modes @wip
    Scenario: Available Product Export - initiated by fuel controller - after auth mode change from ICR to closed.
        Given the fuel controller is configured to sell "fuel,carwash"
        And the pumps are configured for "ICR"
        And the system is in a ready to sell state
        When the fuel controller loads pump auth mode as "CLOSED"
        Then the configured prompt "CLOSED" is displayed on pump "2"
        And the export with items available to sell by the fuel controller is sent to the credit controller
        And the pump "2" is reported as available in credit controller product export


    @positive @glacial @auth_modes 
    Scenario: Available Product Export - requested by Epsilon, fuel and carwash (Invalid EPS credit code) items.
        Given the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel,carwashwithinvalidcreditcode"
        And the system is in a ready to sell state
        When the Mobile Pay host requests available products export
        Then the export with items available to sell by the fuel controller is sent to the credit controller


    @positive @glacial @auth_modes 
    Scenario: Available Product Export - initiated by fuel controller - fuel controller reboot.
        Given the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        When the fuel controller is available after restarting applications
        Then the export with items available to sell by the fuel controller is sent to the credit controller
        And the pumps available to start transactions are reported as available in credit controller product export


    @positive @glacial @fuel_only
    Scenario: Available Product Export - requested by Epsilon. Only fuel products available.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured:
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        When the Mobile Pay host requests available products export
        Then the export with items available to sell by the fuel controller is sent to the credit controller


    @positive @glacial @fuel_only
    Scenario: Available Product Export - requested by Epsilon. Pump Offline.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured:
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the pump "1" went offline
        And the configured prompt "PUMPOFFLINE" was displayed on pump "1"
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as unavailable in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon after loyalty Card is Swiped at Pump.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And a loyalty swipe was performed with "loyalty" at pump "1"
        And the configured prompt "ICRGREETING" was displayed on pump "1"
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as available in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon after Payment Card Swiped at Pump.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And am MSR card "credit_discover" is swiped at pump "1"
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as available in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon after Pump Reserved by Mobile Pay host.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as available in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon after pump has active prepay.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the cashier prepaid the fuel grade "Regular" for price "4.00" at pump "2"
        And the configured prompt "BEGINFUELING" was displayed on pump "2"
        When the Mobile Pay host requests available products export
        Then the pump "2" is reported as available in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon - Pump Authorized, but not fueling.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as available in credit controller product export


    @positive @slow @fuel_only @wip
    Scenario: Available Product Export - requested by Epsilon - Pump Fueling PAP.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the pump "2" was successfully reserved without access code
        And the pump "2" was authorized by the Mobile Pay host
        And the configured prompt "CHOOSEGRADE" was displayed on pump "2"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 2
        When the Mobile Pay host requests available products export
        Then the pump "2" is reported as available in credit controller product export


    @positive @slow @fuel_only @wip
    Scenario: Available Product Export - requested by Epsilon - Pump Fueling Complete, but receipt is not yet printed.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And an MSR card "credit_discover" was swiped at pump "2"
        And the configured prompt "CHOOSEGRADE" was displayed on pump "2"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 2
        And the nozzle is hung up on pump "2"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "2"
        When the Mobile Pay host requests available products export
        Then the pump "2" is reported as available in credit controller product export


    @positive @slow @fuel_only
    Scenario: Available Product Export - requested by Epsilon. ICR Offline.
        Given the pumps are configured for "ICR"
        And the pumps have the following timing events configured
            | option  | value        |
            | RECEIPT | AFTERFUELING |
        And the fuel controller is configured to sell "fuel"
        And the system is in a ready to sell state
        And the ICR on pump "1" went offline
        When the Mobile Pay host requests available products export
        Then the pump "1" is reported as available in credit controller product export


    @positive @glacial @carwash
    Scenario: Transaction Flow - No loyalty in transaction, carwash configured during fueling and suppressed due to mobilepay transaction.
        Given the pumps have the following timing events configured
            | option  | value         |
            | CARWASH | DURINGFUELING |
            | RECEIPT | AFTERFUELING  |
        And the fuel controller is configured to sell "fuel,carwash"
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer dispensed grade "Midgrade" for 6 seconds at pump 1
        Then the configured prompt "ASKWASH PROMPT" is not displayed on pump "1"


    @positive @glacial @carwash
    Scenario: Transaction Flow - No loyalty in transaction, carwash configured before fueling and suppressed due to mobilepay transaction.
        Given the pumps have the following timing events configured
            | option  | value         |
            | CARWASH | BEFOREFUELING |
            | RECEIPT | AFTERFUELING  |
        And following ICR options are set in RCM
            | option             | value |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | NO    |
        And the fuel controller is configured to sell "fuel,carwash"
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the Mobile Pay host tries to authorize the pump "1"
        Then the configured prompt "ASKWASH PROMPT" is not displayed on pump "1"


    @positive @glacial @loyalty_after_payment
    Scenario: Transaction Flow - No loyalty from Mobile Pay host, User swipes loyalty card at pump after mobile auth, loyalty entry is allowed after payment.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 4     |
            | CREDITTIMEOUT      | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | YES   |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISNO         | NO    |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "ASKLOYALTY" was displayed on pump "1"
        When a loyalty swipe is performed with "loyalty" at pump "1"
        Then the dynamic prompt "Would you like   to accept a discount" is displayed on pump "1"


    @positive @slow @loyalty_after_payment
    Scenario: Transaction Flow - loyalty provided by Mobile Pay host, loyalty entry is allowed after payment.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 4     |
            | CREDITTIMEOUT      | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | YES   |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISN          | NO    |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        When the pump "1" is authorized for Mobile Pay transaction with loyalty
        Then the dynamic prompt "Would you like   to accept a discount" is displayed on pump "1"


    @positive @glacial @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - User NOT prompted for access code. Receipt export validation.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And the pump "1" displays welcome prompt
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller
        And the captured credit transaction has mobile wallet entry method


    @positive @slow @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - User prompted for access code (Valid access code entered by the user). Receipt export validation.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        And the correct access code was entered on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "NO" key on pump "1" keypad
        Then the configured prompt "THANKS" is displayed on pump "1"
        And the pump "1" displays welcome prompt
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller


    @positive @slow @no_loyalty_after_payment
    Scenario: Transaction Flow - User prompted for access code (Invalid access code by the user).
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized for Mobile Pay transaction with loyalty
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        When the customer presses "123E" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @no_loyalty_after_payment
    Scenario: Transaction Flow - User cancels the transaction after pump is reserved.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the configured prompt "CREDITAUTH" was displayed on pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @no_loyalty_after_payment
    Scenario: Transaction Flow - User cancels the transaction at the prompt for access code.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @no_loyalty_after_payment
    Scenario: Transaction Flow - User cancels the transaction after entering access code.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized by the Mobile Pay host
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        And the correct access code was entered on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        When the customer presses "CANCEL" key on pump "1" keypad
        Then the configured prompt "SALECANCELLED" is displayed on pump "1"


    @positive @slow @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - No access code, loyalty is provided by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized for Mobile Pay transaction with loyalty
        And discount is accepted on pump 1 keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller


    @positive @slow @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - access code prompting, loyalty is provided by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized for Mobile Pay transaction with loyalty
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        And the correct access code was entered on pump "1" keypad
        And discount is accepted on pump 1 keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller


    @positive @slow @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - No access code, Invalid loyalty is provided by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized for Mobile Pay transaction with invalid loyalty
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller


    @positive @slow @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - access code prompting, Invalid loyalty is provided by Mobile Pay host.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved with access code
        And the pump "1" was authorized for Mobile Pay transaction with invalid loyalty
        And the configured prompt "PLEASE ENTER    ACCESS CODE" was displayed on pump "1"
        And the correct access code was entered on pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller


    @positive @glacial @no_loyalty_after_payment @wip
    Scenario: Transaction Flow - No loyalty from Mobile Pay host, loyalty entry is allowed after payment.
        Given the pumps have the following timing events configured
            | option  | value         |
            | RECEIPT | AFTERFUELING  |
        And following ICR options are set in RCM
            | option             | value |
            | PROMPTTIMEOUT      | 4     |
            | CREDITTIMEOU       | 15    |
            | TRANTYPE           | SIGMA |
            | ALLOWLYLTYAFTERMOP | YES   |
            | ALLOWMOPATLYLTY    | YES   |
            | CANCELISNO         | NO    |
        And the system is in a ready to sell state
        And the pump "1" was successfully reserved without access code
        And the pump "1" was authorized by the Mobile Pay host
        And the customer declines loyalty at pump "1" keypad
        And the configured prompt "CHOOSEGRADE" was displayed on pump "1"
        And the customer dispensed grade "Midgrade" for 3 seconds at pump 1
        And the nozzle is hung up on pump "1"
        And the configured prompt "RECEIPT PROMPT" was displayed on pump "1"
        When the customer presses "YES" key on pump "1" keypad
        Then the configured prompt "RCPTPRINTED" is displayed on pump "1"
        And Mobile PAP transaction is captured in credit controller
        And Mobile PAP receipt is sent to credit controller
