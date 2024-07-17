'''
Created on 22 Nov 2023

@author: Anitha Nagothu
'''
import string
import socket
import random

import pyautogui
from appium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class CommonUtils():
    """Scanner simulator object Mapping function .
    :return: Return code from the installation.
    """
    def __init__(context,posdriver):
        #print("Constructor Method")
        pass

    def check_winapp_driver_connection(self):
        connected = False
        while not connected:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(("127.0.0.1", 4723))
                connected = True
                print("Socket connection verified .. ")
                s.close()
            except ConnectionRefusedError:
                pass
            except OSError as e:
                print(e)

    def waitforelement(driver: webdriver, xpath: string):
        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    def waitforposlaunch(driver: webdriver, xpath: string):
        wait = WebDriverWait(driver, 300)
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    def waitforelement_clickable(driver: webdriver, xpath: string):
        wait = WebDriverWait(driver, 30)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))


    def minimum_pos(context):
        CommonUtils.waitforelement_clickable(context.pos_driver, context.ObjRepo['minimize'].data)
        context.pos_driver.find_element_by_xpath(context.ObjRepo['minimize'].data).click()

    def maximize_pos(context):
        context.desktop_driver.find_element_by_name(context.ObjRepo['maximize'].data).click()

    def minimize_gsim_window(context):
        Gsimwindow = context.desktop_driver.find_element_by_xpath(context.ObjRepo['gsim_window'].data)
        Gsimwindow.find_element_by_xpath(context.ObjRepo['minimize'].data).click()

    def minimize_winapp_window(context):
        print("minimize winapp window ..")
        winapp_window = context.desktop_driver.find_element_by_xpath(context.ObjRepo['winappdriver_window'].data)
        winapp_window.find_element_by_xpath(context.ObjRepo['minimize'].data).click()

    def hover_to_element(context,app_path):
        action = ActionChains(context.desktop_driver)
        action.move_to_element(context.desktop_driver.find_element_by_xpath(app_path))
        action.perform()

    def generate_random_quantity(min_value, max_value):
        Qtyid = random.randint(min_value, max_value)
        print('the Qty:', Qtyid)
        return Qtyid

    def move_cursor_up(distance=100):
        pyautogui.move(0, -distance)
