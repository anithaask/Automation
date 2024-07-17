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



class PosObjFuncs():
    """Pos object Mapping function .
    :return: Return code from the installation.
    """
    #print("from Pos Object mapping functions")
    def __init__(self,posdriver):
        #print("Constructor Method")
        pass
        #self.posdriver = posdriver
      

   # desired_caps['app'] = ""
   # desired_caps['platformName'] = "Windows"
    #desired_caps['deviceName'] = "WindowsPC"
    #self.posdriver = webdriver.Remote(command_executor='http://127.0.0.1:4723',desired_capabilities= desired_caps)
    
    def PosObjFuncs(self, posdriver):
        self.pos_driver = posdriver
        return self.pos_driver

    def clickCashier(self):
        TS = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('TS'))
        return TS;

    def enterPwd(self):
        editbox = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Pwrd'))
        editbox.send_keys(self.paths.get('password'))
    
    def OK(self):
        OK = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('OK'))
        return OK;

    def quit_element(self) :
        quitElement = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Quit'));
        return quitElement;
    def yesButton(self) :
        yesButton = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Yes'));
        return yesButton;

    def subtotal_element(self):
        subtotal_element = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Subtotal'));
        return subtotal_element;

    def  itemlookup(self):
        itemlookup_element = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('ItemLookupEntry'));
        return itemlookup_element;

    def functionMenu(self):
        functionMenu_element = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Functionmenu'));
        return functionMenu_element;

    def byCodeSearch(self):
        code_search_element = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('CodeSearch'));
        return code_search_element

    def Enteritemid(self):
        itemId_value = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Enteritemid'));
        itemId_value.send_keys("11204101")

    def Quantity(self):
        quantityElement = self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Quantity'));
        return quantityElement


    def clickTotal(self):
        self.pos_driver.find_element_by_xpath(self.ObjRepo.get('Total')).click()

    def cashTender(self):
        self.pos_driver.find_element_by_xpath(self.ObjRepo.get('cashTender')).click()


