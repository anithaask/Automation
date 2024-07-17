import re
from behave import *
from UtilClasses.commonUtils import CommonUtils
from UtilClasses.posObjUtils import PosObjFuncs
from UtilClasses.scannerSimulator import ScannerFuncs
from UtilClasses.stp_logging import setup_logger
from selenium.webdriver.common.action_chains import ActionChains
logger = setup_logger()


@given(u'Add multiple dry items to POS sale trs')
def step_impl(context):
    CommonUtils.maximize_pos(context)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['minimize'].data)
    CommonUtils.minimum_pos(context)

    simulatorObj = ScannerFuncs.getScannerElement(context)
    itemCode = context.ObjRepo['itemCode'].data
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['transmitData'].data)
    ScannerFuncs.senddata(context, simulatorObj, itemCode)
    itemCode2 = context.ObjRepo['itemCode2'].data
    CommonUtils.waitforelement(context.desktop_driver,context.ObjRepo['transmitData'].data)
    ScannerFuncs.senddata(context, simulatorObj, itemCode2)

    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['running_app'].data)
    CommonUtils.hover_to_element(context,context.ObjRepo['running_app'].data)
    CommonUtils.maximize_pos(context)
    assert(u'STEP: Given Add the below items to POS sale trs', True)


@when(u'line void one of the dry item')
def step_impl(context):
    logger.info("Perfrom line void one of the item from POS ")
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.line_void(context).click()
    # CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['line_void_pane'].data)
    PosObjFuncs.line_void_reason(context).click()
    assert(u'STEP: line void one of the dry item is performed', True)
