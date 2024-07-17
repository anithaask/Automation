# STPI-Automation-POS

This repository will contain Behave BDD automation framework with Python using WinappDriver.
Follow the below setup details to add/execute the Storepoint BDD automation test scripts,


**Pre-Requities to install**: 


python-3.7

pip install selenium==3.141.0

pip install Appium-Python-Client==1.1.0

pip install urllib3==1.26.6

pip install Behave

pip install jproperties

pip install allure-behave

Install PyCharm IDE (download from internet) 
* Download the automation project from git hub and open the project using PyCharm IDE.

Install winappdriver using  WindowsApplicationDriver_1.2.1.msi 

Windows Sdk kit  : https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/  -- Inspect application is installed to inspect the objects on POS UI.

**Automation reports:** 
  Download allurexx.zip and extract to c drive
  https://github.com/allure-framework/allure2/releases/tag/2.24.1   

**Run using command line :**
  * Navigate to the automation project folder and execute the below commands
  
      behave -f allure_behave.formatter:AllureFormatter -o Reports/ features
  
   **Note**:
     Reports folder automatically created .

  * After Reports folder generated, then  run below command from project folder. This will generate index html 

    allure serve Reports

    **Config & Object Repository:**
    
    Inside **Features**, there is a **config** property file contains all the application paths, system paths and winapp driver details.
    
    **objectRepository _XXX.property** file ---> contains all the customer specific object repository paths.
    
    **environment.py** ---> contains the methods to launch all the required applications like pos, gsimulator, winapp driver in before_all.
    
    

