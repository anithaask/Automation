'''
Created on 30 Oct 2023

@author: TS
'''
#!/usr/bin/python    
import configparser


global pospath
global winapppath
global winappurl
 
paths = {}
objMap= {}     
def configValues():
    """Reading Project urls & config paths from properties files  .
    :return: Return paths dictionary .
    """

    config = configparser.ConfigParser()
    config.read('..\ConfigFiles\config.properties')
    
    paths['pospath'] =  config.get("paths", "pospath")
    paths['winapppath'] = config.get("paths", "winapppath")
    paths['winappurl'] = config.get("paths", "winappurl")
    paths['password'] = config.get("paths", "password")
    paths['Host'] = config.get("paths", "Host")
    paths['port'] = config.get("paths", "port")    
    return paths

def ObjRepos():
    """Reading object Mapping paths from properties files  .
    :return: Return ObjMap dictionary .
    """
    #print("Object Repository paths...")
    config = configparser.ConfigParser()
    config.read('..\ConfigFiles\objectRepository.properties')  
    
    objMap['TS'] =  config.get("objMap", "TS")
    objMap['Signin'] = config.get("objMap", "Signin")
    objMap['Signout'] = config.get("objMap", "Signout")
    objMap['Quit'] = config.get("objMap", "Quit")
    objMap['Pwrd'] = config.get("objMap", "Pwrd")
    objMap['OK'] = config.get("objMap", "OK")
    objMap['ItemLookupEntry'] = config.get("objMap", "ItemLookupEntry")
    objMap['CodeSearch'] = config.get("objMap", "CodeSearch")
    objMap['Enteritemid'] = config.get("objMap", "Enteritemid")
    objMap['Functionmenu'] = config.get("objMap", "Functionmenu")
    objMap['cashTender'] = config.get("objMap", "cashTender")
    objMap['Total'] = config.get("objMap", "Total")
    objMap['scanner'] = config.get("objMap", "scanner")
    objMap['scanData'] = config.get("objMap", "scanData")
    objMap['itemCode'] = config.get("objMap", "itemCode")
    objMap['transmitData'] = config.get("objMap", "transmitData")
    objMap['Yes'] = config.get("objMap", "Yes")
    objMap['Quantity'] = config.get("objMap", "Quantity")

    return objMap
  
