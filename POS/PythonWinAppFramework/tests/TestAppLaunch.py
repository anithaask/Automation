'''
Created on 28 Oct 2023

@author: TS
'''
import unittest
import time
import os
from appium import webdriver

from selenium.webdriver import DesiredCapabilities

from UtilClasses.scannerSimulator import ScannerFuncs
from configFiles.PropertyReader import configValues,ObjRepos
from UtilClasses.posObjUtils import PosObjFuncs 

paths = {}

class TestAppLaunch(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        global desktop_driver
        global pos_driver

        self.paths = configValues()
        self.ObjRepo = ObjRepos()
        os.startfile('C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe')
        os.startfile(self.paths.get('pospath'))
        time.sleep(180)
        desired_caps = {}

        desired_caps['app'] = 'Root'
        desired_caps['platformName'] = "Windows"
        desired_caps['deviceName'] = "WindowsPC"
        self.desktop_driver = webdriver.Remote(command_executor=self.paths.get('winappurl'),desired_capabilities= desired_caps)

        Pos_Window_Handle = self.desktop_driver.find_element_by_name('PositiveMainDlg').get_attribute('NativeWindowHandle')
        Pos_Window_Handle_Hex = hex(int(Pos_Window_Handle))
        pos_cap = {}
        pos_cap['appTopLevelWindow'] = Pos_Window_Handle_Hex
        try:
            self.pos_driver = webdriver.Remote(command_executor=self.paths.get('winappurl'), desired_capabilities=pos_cap)
        except Exception as e:
             print(e)
        PosObjFuncs.clickCashier(self).click()
        PosObjFuncs.enterPwd(self)
        PosObjFuncs.OK(self).click()

    #@classmethod
    #def tearDownClass(self):
     #   pass
        #self.pos_driver.quit()
        #self.desktop_driver.quit()
        #os.system("taskkill /f /IM  WinAppDriver.exe")
        #os.system("taskkill /f /IM  Positive32.exe")

        
    # def test_posLogin(self):
    #     pass
        # print("Login into POS Application...")
        #PosObjFuncs.clickCashier(self).click()
        #PosObjFuncs.enterPwd(self)
        #PosObjFuncs.OK(self).click()
        # PosObjFuncs.functionMenu(self).click()
        # PosObjFuncs.itemlookup(self).click()
        # PosObjFuncs.byCodeSearch(self).click()
        # PosObjFuncs.Enteritemid(self)
        # PosObjFuncs.OK(self).click()
        # PosObjFuncs.OK(self).click()
        # PosObjFuncs.clickTotal(self)
        # PosObjFuncs.cashTender(self)
        #


    def test_drySalebyScanner(self):

        print("Perform sale transaction with dry item..")
        time.sleep(5)
        simulatorObj = ScannerFuncs.getScannerElement(self)
        itemCode= self.ObjRepo.get('itemCode')
        ScannerFuncs.senddata(self,simulatorObj, itemCode)
        print("Simulator invoked .. & Item added.")
        PosObjFuncs.functionMenu(self).click()
        PosObjFuncs.itemlookup(self).click()
        PosObjFuncs.byCodeSearch(self).click()
        PosObjFuncs.Enteritemid(self)
        PosObjFuncs.OK(self).click()
        PosObjFuncs.OK(self).click()
        simulatorObj = ScannerFuncs.getScannerElement(self)
        itemCode = self.ObjRepo.get('itemCode')
        ScannerFuncs.senddata(self, simulatorObj, itemCode)
        print("Simulator invoked .. & Item added.2 time")
        PosObjFuncs.clickTotal(self)
        PosObjFuncs.cashTender(self)
        print("Cashier Logged into POS application...")
        PosObjFuncs.functionMenu(self).click()
        PosObjFuncs.quit_element(self).click()
        PosObjFuncs.yesButton(self).click()



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAppLaunch)
    unittest.TextTestRunner(verbosity=2).run(suite)
        

