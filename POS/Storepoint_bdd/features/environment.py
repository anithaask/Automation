import os
import allure
from allure_commons.types import AttachmentType
from behave.model import Feature
from behave.model import Scenario
from behave.model import Step
from behave.model import Tag
from behave.runner import Context
from appium import webdriver
from UtilClasses.commonUtils import CommonUtils
from UtilClasses.posObjUtils import PosObjFuncs
from UtilClasses.stp_logging import setup_logger
from features.configFiles.PropertyReader import ObjRepos, configValues


logger = setup_logger()


def before_all(context):
    print("From Before all function....")
    context.logger = setup_logger()

    context.paths = configValues(context)
    context.ObjRepo = ObjRepos(context)
    os.startfile(context.paths['win_app_driver'].data)
    os.startfile(context.paths['gsim_file_path'].data)
    os.startfile(context.paths['pos_app_path'].data)
    context.desired_caps = {}
    context.desired_caps['app'] = 'Root'
    context.desired_caps['platformName'] = "Windows"
    context.desired_caps['deviceName'] = "WindowsPC"
    CommonUtils.check_winapp_driver_connection(None)

    context.desktop_driver = webdriver.Remote(command_executor=context.paths['win_app_url'].data,
                                           desired_capabilities=context.desired_caps)
    CommonUtils.minimize_winapp_window(context)
    context.desktop_driver.find_element_by_name("GSim Configuration Screen").find_element_by_name("OK").click()
    CommonUtils.waitforelement(context.desktop_driver,context.ObjRepo['gsim_window'].data )
    CommonUtils.waitforelement(context.desktop_driver,context.ObjRepo['gsim_pumps_check'].data)
    CommonUtils.minimize_gsim_window(context)

    CommonUtils.waitforposlaunch(context.desktop_driver, context.ObjRepo['positive_main_dlg'].data)
    context.Pos_Window_Handle = context.desktop_driver.find_element_by_xpath(context.ObjRepo['positive_main_dlg'].data).get_attribute("NativeWindowHandle")
    context.Pos_Window_Handle_Hex = hex(int(context.Pos_Window_Handle))
    context.pos_cap = {}
    context.pos_cap['appTopLevelWindow'] = context.Pos_Window_Handle_Hex
    try:
        context.pos_driver = webdriver.Remote(command_executor=context.paths['win_app_url'].data,
                                              desired_capabilities=context.pos_cap)
        logger.info("POS Driver Object created..")
    except Exception as e:
        print(e)
        assert (u'Before all _failed ')

def before_feature(context: Context, feature: Feature):
    logger.info('Starting scenario "%s"' % feature)


def before_scenario(context: Context, scenario: Scenario):
    logger.info('Starting scenario "%s"' % scenario)

def before_step(context: Context, step: Step):
    pass

def before_tag(context: Context, tag: Tag):
    pass

def after_tag(context: Context, tag: Tag):
    pass

def after_step(context: Context, step: Step):
    # if step.status == 'failed':
    #     allure.attach(context.driver.get_screenshot_as_png()
    #                   ,name="failed_screenshot"
    #                   ,attachment_type=AttachmentType.PNG)
    pass

def after_scenario(context: Context, scenario: Scenario):
    logger.info('Finished with scenario "%s"' % scenario)

def after_feature(context: Context, feature: Feature):
    pass

def after_all(context: Context):
    # CommonUtils.waitforelement_clickable(context.pos_driver,context.ObjRepo['Functionmenu'].data)
    # PosObjFuncs.functionMenu(context).click()
    # CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['sign_in_out'].data)
    # PosObjFuncs.sign_in_out(context).click()
    # CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Quit'].data)
    # PosObjFuncs.quit_element(context).click()
    # CommonUtils.waitforelement(context.pos_driver, context.ObjRepo['Yes'].data)
    # PosObjFuncs.yesButton(context).click()

    context.desktop_driver.quit()
    context.pos_driver.quit()
    # os.system("taskkill /f /IM  WinAppDriver.exe")
    # os.system("taskkill /f /IM  GSimulator.exe")
    pass
