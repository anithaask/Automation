pos_journal_ignore_tag = ["RegisterDetail", "ShiftDetail", "CashierDetail"]


pos_journal_ignore_tag_content = [
            "TransmissionHeader",
            "JournalHeader",
            "TransactionID",
            "EventStartDate",
            "EventStartTime",
            "EventEndDate",
            "EventEndTime",
            "BusinessDate",
            "ReceiptDate",
            "ReceiptTime",
            "Authorization",
            "MoneyOrderNumber",
            "TillID",
            "DropNumber",
            "TransactionLineSequenceNumber",
            "radiant:TransactionLineExtension",
            "radiant:ShiftNumber",
            "radiant:TransactionCount",
            "radiant:OtherEventExtension",
            "radiant:OriginalTransaction",
        ]
msm_ignore_tag_content = [
            "TransmissionHeader",
            "BeginDate",
            "BeginTime",
            "EndDate",
            "EndTime",
            "BusinessDate",
            "TillID",
            "radiant:BusinessDate",
            "VendorModelVersion",
        ]
cashier_summary_ignore_tag_content = [
            "TransmissionHeader",
            "BeginDate",
            "BeginTime",
            "EndDate",
            "EndTime",
            "BusinessDate",
            "radiant:BusinessDate",
        ]
ism_ignore_tag_content = [
            "VendorModelVersion",
            "BusinessDate",
            "MovementHeader",
        ]