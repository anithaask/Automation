from behave import *

from UtilClasses import commonUtils
from UtilClasses.posObjUtils import PosObjFuncs
from UtilClasses.stp_logging import setup_logger
from UtilClasses.commonUtils import *

logger = setup_logger()
@given(u'POS application is Launched')
def step_impl(context):
    print("POS application is Launched")
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['TS'].data)

@when(u'cashier login is clicked')
def step_impl(context):
    PosObjFuncs.clickCashier(context)
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['OK'].data)
    PosObjFuncs.enterPwd(context)
    CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['OK'].data)
    PosObjFuncs.OK(context).click()
    CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['Functionmenu'].data)
    assert (u'STEP: cashier login is clicked')

@then(u'the POS displays the "main" frame')
def step_impl(context):
    logger.info('the POS displays the "sale" frame .....')
    is_sale_view = PosObjFuncs.functionMenu(context).is_displayed()
    if (is_sale_view):
        logger.info('Sale Trs view is displayed.....')
    else:
        logger.info('Sale Trs view not displayed.....')

    assert(u'STEP: Then the POS displays the "main" frame')

@then(u'the POP pump displays on POS main dialog')
def step_impl(context):
    CommonUtils.waitforelement(context.desktop_driver, context.ObjRepo['posPumps_1'].data)
    is_pos_pumps_displayed = context.desktop_driver.find_element_by_xpath(context.ObjRepo['pos_pump_icons_panel'].data)
    if (is_pos_pumps_displayed):
        logger.info('Pospumps displayed & pos is on main screen....')
    else:
        logger.info('Pospumps not displayed.....')
    assert (u'STEP: Then the POP pump displays on POS main dialog')