from behave import *
from UtilClasses.commonUtils import CommonUtils
from UtilClasses.posObjUtils import PosObjFuncs


@given(u'Add the fuel items to POS sale trs')
def step_impl(context):

    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['posPumps_1'].data)
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    PosObjFuncs.functionMenu(context).click()
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['minimize'].data)
    CommonUtils.minimum_pos(context)

    CommonUtils.waitforelement(context.desktop_driver,"//*[@Name = 'Running applications']")
    context.desktop_driver.find_element_by_name(context.ObjRepo['gsim_window_active'].data).click()
    CommonUtils.waitforelement(context.desktop_driver,context.ObjRepo['gsim_pumps_check'].data)
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['gsim_pumps_check'].data).click()
    CommonUtils.waitforelement(context.desktop_driver,context.ObjRepo['gsim_pumps_slider'].data)
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['gsim_pumps_slider'].data).click()
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['gsim_pumps_check'].data).click()

    #add fuel item in POS by invoking pospump
    context.desktop_driver.find_element_by_name(context.ObjRepo['maximize'].data).click()
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['posPumps_1'].data)
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['posPumps_1'].data).click()
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['posPumps_2'].data).click()
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['pospump_trs_window'].data).find_element_by_xpath("//Button[@ClassName='Button'][1]").click()
    context.desktop_driver.find_element_by_xpath(context.ObjRepo['posPumps_2'].data).click()
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    assert (u'STEP: Given Add the fuel items to POS sale trs')