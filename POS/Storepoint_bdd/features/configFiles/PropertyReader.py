'''
Created on 30 Oct 2023

@author: TS
'''
#!/usr/bin/python    

import os
from UtilClasses.stp_logging import setup_logger
from jproperties import Properties

 
paths = {}
objMap= {}
logger = setup_logger()
object_repo_file = " "
current_dir_path = os.path.dirname(os.path.abspath(__file__))

def configValues(context):
    """Reading Project urls & config paths from properties files  .
    :return: Return paths dictionary .
    """

    config_file = (os.path.join(current_dir_path + '\config.properties'))
    paths = Properties()
    with open(config_file, "r") as f:
        paths.load(f, None)
    return paths

def ObjRepos(context):
    """Reading object Mapping paths from properties files  .
    :return: Return ObjMap dictionary .
    """
    paths = configValues(context)
    customer = paths['customer'].data
    if customer == 'bp':
        object_repo_file = (os.path.join(current_dir_path + '\objectRepository_bp.properties'))
    elif customer == 'china':
        object_repo_file = (os.path.join(current_dir_path + '\objectRepository_china.properties'))
    elif customer == 'us':
        object_repo_file = (os.path.join(current_dir_path + '\objectRepository_us.properties'))
    else:
        object_repo_file = (os.path.join(current_dir_path + '\objectRepository.properties'))
    objMap = Properties()
    with open(object_repo_file, "r") as f:
        objMap.load(f, None)
    return objMap