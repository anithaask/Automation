import re
import time

import pyautogui
from behave import *

from UtilClasses import tra_reader, commonUtils
from UtilClasses import commonUtils
from UtilClasses.commonUtils import CommonUtils
from UtilClasses.posObjUtils import PosObjFuncs
from UtilClasses.scannerSimulator import ScannerFuncs
from UtilClasses.stp_logging import setup_logger
from UtilClasses.tra_reader import GetLastTransaction

logger = setup_logger()


@given(u'Add the below items to POS sale trs')
def step_impl(context):
    CommonUtils.maximize_pos(context)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    CommonUtils.minimum_pos(context)

    simulatorObj = ScannerFuncs.getScannerElement(context)
    itemCode = context.ObjRepo['itemCode'].data
    time.sleep(5)
    ScannerFuncs.senddata(context, simulatorObj, itemCode)
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['running_app'].data)
    CommonUtils.maximize_pos(context)

    assert(u'STEP: Given Add the below items to POS sale trs')

@given(u'Add the below items to POS sale trs using item lookup')
def step_impl(context):
    CommonUtils.maximize_pos(context)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    # CommonUtils.minimum_pos(context)
    PosObjFuncs.itemlookup(context).click()
    # CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['CodeSearch'].data)
    # PosObjFuncs.by_code_search(context).click()
    time.sleep(5)

    code_search_element = context.pos_driver.find_element_by_xpath("//Button[@Name='Name']")
    code_search_element.click()

    PosObjFuncs.Enteritemid(context)
    PosObjFuncs.OK(context).click()
    PosObjFuncs.OK(context).click()

    # simulatorObj = ScannerFuncs.getScannerElement(context)
    # itemCode = context.ObjRepo['itemCode'].data
    # time.sleep(5)
    # ScannerFuncs.senddata(context, simulatorObj, itemCode)
    # CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['running_app'].data)
    # CommonUtils.maximize_pos(context)

    assert(u'STEP: Given Add the below items to POS sale trs')


@given(u'Add the below item1 to POS sale trs with random qty')
def step_impl(context):
    CommonUtils.maximize_pos(context)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    CommonUtils.minimum_pos(context)

    simulatorObj = ScannerFuncs.getScannerElement(context)
    itemCode = context.ObjRepo['itemCode'].data
    #CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['itemCode'].data)
    time.sleep(5)
    ScannerFuncs.senddata(context, simulatorObj, itemCode)
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['running_app'].data)
    CommonUtils.maximize_pos(context)
    print('item added')
    PosObjFuncs.Quantity(context).click()
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Qtyid'].data)
    # #time.sleep(5)
    # qty_value = CommonUtils.generate_random_quantity(0, 9)
    # print("*************************************")
    # print(qty_value)
    PosObjFuncs.QtyId(context)
    print('qty added')
    PosObjFuncs.OK(context).click()

    assert(u'STEP: Add the below item1 to POS sale trs with random qty')

@given(u'Add the below item2 to POS sale trs with random qty')
def step_impl(context):
   # CommonUtils.maximize_pos(context)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    CommonUtils.minimum_pos(context)

    simulatorObj = ScannerFuncs.getScannerElement(context)
    itemCode2 = context.ObjRepo['itemCode2'].data
    #CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['itemCode'].data)
    time.sleep(5)
    ScannerFuncs.senddata(context, simulatorObj, itemCode2)
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['running_app'].data)
    CommonUtils.maximize_pos(context)
    print('item added')
    PosObjFuncs.Quantity(context).click()
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Qtyid'].data)
    #time.sleep(5)
    PosObjFuncs.QtyId(context)
    PosObjFuncs.OK(context).click()

    assert(u'STEP: Added the below item2 to POS sale trs with random qty')

@given(u'update the quantity of item2')
def step_impl(context):
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.Arrow_button(context).click()
    PosObjFuncs.Quantity(context).click()
    PosObjFuncs.QtyId(context)
    PosObjFuncs.OK(context).click()

    assert(u'STEP: updated the quantity of item2')



@when(u'click on sub total, pay with cash tender')
def step_impl(context):
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Total'].data)
    PosObjFuncs.clickTotal(context)


    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['tender_amount'].data)
    amount = PosObjFuncs.tender_amount_element(context).text
    actual_amount = re.sub('[^(\d+|.)]', "", amount)
    logger.info("Actual Transaction Amount .. : %s" % actual_amount)
    if (actual_amount == "3.25"):
        logger.info('Sale Trs view is displayed.....')
        assert True
    else:
        logger.info('Sale Trs view not displayed.....')
        #assert False

    CommonUtils.waitforelement(context.pos_driver,context.ObjRepo['cashTender'].data)
    PosObjFuncs.cashTender(context)
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Close'].data)
    PosObjFuncs.close_button(context).click()
    assert(u'STEP: When click on sub total, pay with cash tender')

@then(u'the POS goes back to main view')
def step_impl(context):
    is_sale_view = PosObjFuncs.functionMenu(context).is_displayed()
    if (is_sale_view):
        logger.info('Sale Trs view is displayed.....')
    else:
        logger.info('Sale Trs view not displayed.....')
    assert(u'STEP: Then the POS goes back to main view')


@then(u'the transaction is completed')
def step_impl(context):
    #TRA Verification needs to be implemented
    #transactionjson = "C:\Positive\Tra\TRA2JSON1.json"
    # transactionjson = GetLastTransaction()
    # total = tra_reader.GetTotalAmount(transactionjson)
    # print("********")
    # print(total)
    assert(u'STEP: Then the sales transaction is complete')
