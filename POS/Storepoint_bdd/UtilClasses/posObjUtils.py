'''
Created on 22 Nov 2023

@author: Anitha Nagothu
'''
from UtilClasses import commonUtils
from UtilClasses.commonUtils import CommonUtils


class PosObjFuncs():
    """Pos object Mapping function .
    :return: Return code from the installation.
    """
    #print("from Pos Object mapping functions")
    def __init__(context):
        pass

    def PosObjFuncs(context, posdriver):
        context.pos_driver = posdriver
        return context.pos_driver

    def clickCashier(context):
        context.pos_driver.find_element_by_xpath(context.ObjRepo['TS'].data).click()

    def enterPwd(context):
        editbox = context.pos_driver.find_element_by_xpath(context.ObjRepo['Pwrd'].data)
        editbox.send_keys(context.ObjRepo['password'].data)
    
    def OK(context):
        OK = context.pos_driver.find_element_by_xpath(context.ObjRepo['OK'].data)
        return OK;

    def signout(context):
        Signout = context.pos_driver.find_element_by_xpath(context.ObjRepo['Signout'].data)
        return Signout;


    def sign_in_out(context):
        sign_in_out = context.pos_driver.find_element_by_xpath(context.ObjRepo['sign_in_out'].data)
        return sign_in_out;
    def quit_element(context) :
        quitElement = context.pos_driver.find_element_by_xpath(context.ObjRepo['Quit'].data);
        return quitElement;
    def yesButton(context) :
        yesButton = context.pos_driver.find_element_by_xpath(context.ObjRepo['Yes'].data);
        return yesButton;
    def close_button(context) :
        close_button = context.pos_driver.find_element_by_xpath(context.ObjRepo['Close'].data);
        return close_button;

    def Arrow_button(context) :
        Arrow_button = context.pos_driver.find_element_by_xpath(context.ObjRepo['Arrow'].data);
        return Arrow_button;

    def subtotal_element(context):
        subtotal_element = context.pos_driver.find_element_by_xpath(context.ObjRepo['Subtotal'].data);
        return subtotal_element;

    def  itemlookup(context):
        itemlookup_element = context.pos_driver.find_element_by_xpath(context.ObjRepo['item_lookup'].data);
        return itemlookup_element;item_lookup

    def functionMenu(context):
        functionMenu_element = context.pos_driver.find_element_by_xpath(context.ObjRepo['Functionmenu'].data);
        return functionMenu_element;

    def by_code_search(context):
        code_search_element = context.pos_driver.find_element_by_xpath(context.ObjRepo['CodeSearch'].data);
        return code_search_element

    def Enteritemid(context):
        itemId_value = context.pos_driver.find_element_by_xpath(context.ObjRepo['Enteritemid'].data);
        itemId_value.send_keys("11204101")

    def Quantity(context):
        quantityElement = context.pos_driver.find_element_by_xpath(context.ObjRepo['quantity'].data);
        return quantityElement

    def QtyId(context):
        qty_text_field = context.pos_driver.find_element_by_xpath(context.ObjRepo['Qtyid'].data);
        qty_value = CommonUtils.generate_random_quantity(0,30)
        qty_text_field.send_keys(qty_value)

    def ChangeQty(context):
        ChangeQty_value = context.pos_driver.find_element_by_xpath(context.ObjRepo['ChangeQty'].data);
        qty_value = CommonUtils.generate_random_quantity(0, 30)
        ChangeQty_value.send_keys(qty_value)

    def clickTotal(context):
        context.pos_driver.find_element_by_xpath(context.ObjRepo['Total'].data).click()

    def cashTender(context):
        context.pos_driver.find_element_by_xpath(context.ObjRepo['cashTender'].data).click()

    def pos_pump_icons_panel(context):
        context.pos_driver.find_element_by_xpath(context.ObjRepo['pos_pump_icons_panel'].data)

    def tender_amount_element(context):
        tender_amount = context.pos_driver.find_element_by_xpath(context.ObjRepo['tender_amount'].data)
        return tender_amount

    def line_void(context):
        line_void_element = context.pos_driver.find_element_by_xpath(context.ObjRepo['line_void'].data)
        return line_void_element

    def line_void_reason(context):
        line_void_pane = context.pos_driver.find_element_by_xpath(context.ObjRepo['line_void_pane'].data)
        line_void_reason_element = line_void_pane.find_element_by_xpath(context.ObjRepo['void_reason'].data)
        return line_void_reason_element

    def void_transaction(context):
        # Click void transaction
        void_trs_pane = context.pos_driver.find_element_by_xpath(context.ObjRepo['pos_btn_pane'].data)
        void_trs_pane.find_element_by_xpath(context.ObjRepo['void_trs_button'].data).click()
        # Click void Reason
        line_void_pane = context.pos_driver.find_element_by_xpath(context.ObjRepo['line_void_pane'].data)
        void_trs_reason_element = line_void_pane.find_element_by_xpath(context.ObjRepo['void_reason_1'].data)
        return void_trs_reason_element


