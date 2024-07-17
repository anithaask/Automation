from UtilClasses.posObjUtils import PosObjFuncs


def get_tender_amount(context):
    tender_amount_element = PosObjFuncs.tender_amount_element(context)
    return tender_amount_element.text()



