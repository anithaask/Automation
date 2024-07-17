'''
Created on 31 Oct 2023

@author: TS
'''
from appium import webdriver
#from appium.webdriver import WebElement;
from configFiles.PropertyReader import configValues,ObjRepos

desired_caps= {}
objRepo = ObjRepos()
paths = configValues()



class ScannerFuncs():
    """Scanner simulator object Mapping function .
    :return: Return code from the installation.
    """
    def __init__(self,posdriver):
        #print("Constructor Method")
        pass
        #self.posdriver = posdriver

    def ScannerFuncs(self, desktopDriver):
        self.desktop_driver = desktopDriver
        return self.desktop_driver

    def getScannerElement(self):
        scannerObj = self.desktop_driver.find_element_by_name(self.ObjRepo.get('scanner'))
        return scannerObj;
    def senddata(self,simulatorObj,itemCode):
        simulatorObj.find_element_by_xpath(self.ObjRepo.get('scanData')).clear()
        simulatorObj.find_element_by_xpath(self.ObjRepo.get('scanData')).send_keys(itemCode)
        simulatorObj.find_element_by_xpath(self.ObjRepo.get('transmitData')).click()


