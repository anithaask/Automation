'''
Created on 31 Oct 2023

@author: TS
'''


class ScannerFuncs():
    """Scanner simulator object Mapping function .
    :return: Return code from the installation.
    """
    def __init__(context):
        pass


    def ScannerFuncs(context, desktopDriver):
        context.desktop_driver = desktopDriver
        return context.desktop_driver

    def getScannerElement(context):
        scannerObj = context.desktop_driver.find_element_by_name(context.ObjRepo['scanner'].data)
        return scannerObj;
    def senddata(context,simulatorObj,itemCode):

        simulatorObj.find_element_by_xpath(context.ObjRepo['scanData'].data).clear()
        simulatorObj.find_element_by_xpath(context.ObjRepo['scanData'].data).send_keys(itemCode)
        simulatorObj.find_element_by_xpath(context.ObjRepo['transmitData'].data).click()
